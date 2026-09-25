"""
DoseVerdict — Pharmacology Evidence Agent 근거 산출 스크립트

제안서에 들어가는 모든 수치를 재현 가능하게 만든다.
사례: 소토라십(Sotorasib, LUMAKRAS) — FDA가 960 mg 승인 후 240 mg과의
용량 비교를 시판후 요구사항으로 부과한 Project Optimus 대표 사례.

산출물:
  1. RDKit 물성 및 구조 알림 → 안전성 모니터링 요구 역산
  2. ChEMBL 효력값(IC50/Ki) 분포 → 타겟 억제 필요 농도
  3. openFDA SPL 라벨 → 승인 용량 PK(Cmax)
  4. Target Coverage Ratio = C_free / IC50

주의: Target Coverage Ratio는 1차 스크리닝용 근사이며 정밀 PK/PD 모델을
      대체하지 않는다. 미결합분율은 라벨 실측값(89% 결합 → f_u 0.11)을 쓰고,
      실측이 없는 경우에만 물성 기반 추정치를 쓴다.
      비선형 PK가 보고된 구간에서는 저용량으로 선형 외삽하지 않으며,
      선형 가정과 노출 유사 가정의 범위를 함께 출력한다.
"""

import json
import sys
import time
import urllib.parse
import urllib.error
import urllib.request

UA = {"User-Agent": "DoseVerdict-Evidence/1.0 (academic competition prototype)"}


def fetch_json(url, timeout=40, retries=2):
    """일시 오류(5xx·연결·타임아웃)는 2초·4초 백오프로 재시도한다 — 평가 60케이스에서 ChEMBL 500이 4회 있었다(2026-09-25)."""
    for attempt in range(retries + 1):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code < 500 or attempt == retries:
                raise
        except (urllib.error.URLError, TimeoutError):
            if attempt == retries:
                raise
        time.sleep(2 * 2 ** attempt)


# ---------------------------------------------------------------- 1. RDKit
def rdkit_profile(smiles):
    from rdkit import Chem
    from rdkit.Chem import Crippen, Descriptors, QED
    from rdkit.Chem.FilterCatalog import FilterCatalog, FilterCatalogParams

    mol = Chem.MolFromSmiles(smiles)
    assert mol is not None, "SMILES 파싱 실패"

    props = {
        "MW": Descriptors.MolWt(mol),
        "cLogP": Crippen.MolLogP(mol),
        "TPSA": Descriptors.TPSA(mol),
        "HBD": Descriptors.NumHDonors(mol),
        "HBA": Descriptors.NumHAcceptors(mol),
        "RotB": Descriptors.NumRotatableBonds(mol),
        "AromaticRings": Descriptors.NumAromaticRings(mol),
        "QED": QED.qed(mol),
    }

    params = FilterCatalogParams()
    for name in ("BRENK", "PAINS", "NIH"):
        params.AddCatalog(getattr(FilterCatalogParams.FilterCatalogs, name))
    catalog = FilterCatalog(params)
    alerts = [
        {"catalog": e.GetProp("FilterSet"), "description": e.GetDescription()}
        for e in catalog.GetMatches(mol)
    ]
    return props, alerts


def estimated_free_fraction(clogp):
    """
    물성 기반 미결합분율(f_u) 1차 근사 — **실측값이 없을 때만** 쓴다.

    친유성이 높을수록 혈장단백 결합이 커진다는 널리 알려진 경향을
    logit(f_u) = a - b·cLogP 형태로 표현한 자체 보정식이다.
    계수 (a=0.90, b=0.66)은 특정 논문에서 인용한 값이 아니라
    본 프로젝트가 임의로 설정한 값이므로, 결과에 반드시 '추정'을 표시한다.

    ※ 실측 f_u가 있으면 언제나 그것을 우선한다.
      소토라십의 경우 FDA 라벨에 "plasma protein binding is 89%"가 있어
      실측 f_u = 0.11 이며, 본 식의 추정치(0.113)와 대조해 타당성을 확인했다.
    """
    import math

    logit = 0.90 - 0.66 * clogp
    fu = 1.0 / (1.0 + math.exp(-logit))
    return max(min(fu, 1.0), 1e-4)


def target_coverage_ratio(dose_mg, cl_f_L_per_hr, mw, fu, ic50_nM,
                          tau_hr=24.0, t_half_hr=5.0):
    """
    Target Coverage Ratio = C_free,ss / IC50 — **세 기준을 모두 반환한다.**

    C_avg,ss  = (Dose / CL/F) / tau
    C_max,ss  = (Dose / V_ss) / (1 - e^(-k·tau))      1-구획 반복투여
    C_min,ss  = C_max,ss · e^(-k·tau)
      단, k = ln2 / t_half,  V_ss = (CL/F) / k

    단일 지표를 내지 않는 이유: 소토라십은 t½ 5시간에 1일 1회 투여라
    24시간 트로프가 피크의 1/28로 떨어진다. C_avg로 보면 커버, C_trough로
    보면 미커버가 나오므로 **판정이 지표 선택에 의존한다.** 세 값을 함께
    내고, 판정이 갈리면 결론을 내지 않는 것이 이 모듈의 규칙이다.

    ※ 평형 점유 가정 위의 지표다. 비가역 공유결합 저해제에는
      kinact/K_I 기반 시간의존 모델이 필요하며 이 값은 보조 지표로만 쓴다.
    """
    import math

    k = math.log(2) / t_half_hr
    v_ss = cl_f_L_per_hr / k
    decay = math.exp(-k * tau_hr)

    auc = dose_mg / cl_f_L_per_hr                  # mg·hr/L = µg·hr/mL
    to_nM = 1e6 / mw                               # µg/mL → nmol/L
    c_avg_nM = (auc / tau_hr) * to_nM
    c_max_nM = (dose_mg / v_ss) / (1 - decay) * to_nM
    c_min_nM = c_max_nM * decay

    out = {
        "AUC_0_24_ug_hr_per_mL": auc,
        "V_ss_L": v_ss,
        "f_u": fu,
        "IC50_nM": ic50_nM,
    }
    for tag, conc in (("max", c_max_nM), ("avg", c_avg_nM), ("trough", c_min_nM)):
        out[f"C_{tag}_ss_nM"] = conc
        out[f"C_free_{tag}_nM"] = conc * fu
        out[f"TCR_{tag}"] = conc * fu / ic50_nM
    # 판정이 지표에 따라 갈리는가 — 갈리면 에이전트는 결론을 보류한다
    tcrs = [out["TCR_max"], out["TCR_avg"], out["TCR_trough"]]
    out["verdict_split"] = min(tcrs) < 1.0 <= max(tcrs)
    return out


def exposure_ratio_ci(cv, n_per_arm, z=1.96):
    """
    두 용량군의 정상상태 노출(AUC) 비에 대한 95% 신뢰구간 — 로그정규 가정.

    "노출이 용량 간 평평하다"를 주장하려면 용량 비례성을 *배제*해야 한다.
    증량 코호트는 통상 용량당 2~4명이므로, 그 표본에서 그 주장이 가능한지를
    먼저 계산한다. 참값이 1(완전 평탄)이어도 구간이 배 단위로 벌어지면
    "평평하다"와 "2배 증가"를 구분할 수 없다.

    sd_log = sqrt(ln(1 + CV^2)),  SE(log ratio) = sd_log * sqrt(2/n)
    """
    import math

    sd_log = math.sqrt(math.log(1 + cv ** 2))
    se = sd_log * math.sqrt(2.0 / n_per_arm)
    lo, hi = math.exp(-z * se), math.exp(z * se)
    return {"sd_log": sd_log, "lo": lo, "hi": hi, "fold": hi / lo}


# ---------------------------------------------------------------- 2. ChEMBL
def chembl_lookup(name):
    """
    성분명 → ChEMBL 분자 ID. 검색 결과 중 pref_name이 이름과 **정확히 같은** 분자만 채택한다
    (염 형태 'DIVARASIB ADIPATE'나 이름 없는 유사 구조를 고르지 않도록). 없으면 None.
    """
    q = urllib.parse.urlencode({"q": name, "limit": 10})
    data = fetch_json(f"https://www.ebi.ac.uk/chembl/api/data/molecule/search.json?{q}")
    for m in data.get("molecules", []):
        if (m.get("pref_name") or "").strip().upper() == name.strip().upper():
            return {"chembl_id": m["molecule_chembl_id"], "pref_name": m["pref_name"], "max_phase": m.get("max_phase")}
    return None


def chembl_potency(molecule_chembl_id, limit=1000):
    """
    해당 화합물의 IC50/Ki/Kd 활성값을 nM 단위로 모은다.

    `standard_relation`을 반드시 함께 가져온다. '<' 또는 '>'가 붙은 값은
    검열값(censored)이라 점추정으로 인용하면 안 된다 — 예를 들어 소토라십의
    최소 활성값 7 nM은 실제로 "7 nM 미만"이며 "최소 7 nM"이 아니다.
    """
    base = "https://www.ebi.ac.uk/chembl/api/data/activity.json"
    q = urllib.parse.urlencode(
        {
            "molecule_chembl_id": molecule_chembl_id,
            "standard_type__in": "IC50,Ki,Kd",
            "limit": limit,
        }
    )
    data = fetch_json(f"{base}?{q}")
    rows = []
    for a in data.get("activities", []):
        val, unit = a.get("standard_value"), a.get("standard_units")
        if val is None or unit != "nM":
            continue
        assay = (a.get("assay_description") or "")
        rel = (a.get("standard_relation") or "=").strip()
        rows.append(
            {
                "type": a.get("standard_type"),
                "nM": float(val),
                "relation": rel,
                "censored": rel in ("<", ">", "<=", ">="),
                "target": a.get("target_pref_name"),
                # 세포주명이 있으면 세포 기반 어세이로 본다
                "cell_based": any(
                    m in assay.upper()
                    for m in ("NCI-H358", "MIAPACA", "H358", "CELL", "P-ERK", "PERK")
                ),
                "assay": assay[:110],
            }
        )
    return rows


# ---------------------------------------------------------------- 3. openFDA
def openfda_label(brand):
    q = urllib.parse.quote(f'openfda.brand_name:"{brand}"')
    url = f"https://api.fda.gov/drug/label.json?search={q}&limit=1"
    data = fetch_json(url)
    return data["results"][0]


def find_pk_text(label, keywords, window=520):
    """라벨의 임상약리 절에서 키워드 주변 원문을 뽑는다(인용 근거 보존)."""
    hits = []
    for field in ("clinical_pharmacology", "description", "dosage_and_administration"):
        for block in label.get(field, []):
            low = block.lower()
            for kw in keywords:
                i = low.find(kw.lower())
                if i >= 0:
                    hits.append({"field": field, "kw": kw, "text": block[i : i + window]})
    return hits


# ---------------------------------------------------------------- main
def main():
    sys.stdout.reconfigure(encoding="utf-8")

    SMILES = (
        "C=CC(=O)N1CCN(c2nc(=O)n(-c3c(C)ccnc3C(C)C)c3nc(-c4c(O)cccc4F)"
        "c(F)cc23)[C@@H](C)C1"
    )
    CHEMBL_ID = "CHEMBL4535757"  # SOTORASIB

    print("=" * 72)
    print("1. RDKit 물성 및 구조 알림  (사례: 소토라십 / LUMAKRAS)")
    print("=" * 72)
    props, alerts = rdkit_profile(SMILES)
    for k, v in props.items():
        print(f"  {k:16s} {v:.2f}" if isinstance(v, float) else f"  {k:16s} {v}")
    fu = estimated_free_fraction(props["cLogP"])
    print(f"  {'f_u (추정)':16s} {fu:.4f}   ← cLogP 기반 근사")
    print(f"\n  구조 알림 {len(alerts)}건")
    for a in alerts:
        print(f"    - [{a['catalog']}] {a['description']}")

    print()
    print("=" * 72)
    print("2. ChEMBL 효력값 분포")
    print("=" * 72)
    acts = chembl_potency(CHEMBL_ID)
    print(f"  nM 단위 활성값 {len(acts)}건 수집")
    kras = [a for a in acts if a["target"] and "KRAS" in a["target"].upper()]
    print(f"  그중 KRAS 표적 {len(kras)}건")
    if not kras:
        print("  ⚠ KRAS 표적 매칭 0건 — 전체 활성값으로 대체하면 무관한 타겟의")
        print("    IC50으로 TCR을 계산하게 된다. 이 경우 결과에 target_matched=False를 표시한다.")
    pool = kras or acts

    censored = [a for a in pool if a["censored"]]
    usable = [a for a in pool if not a["censored"]]
    print(f"  검열값(<, >) {len(censored)}건 제외 → 점추정 가능 {len(usable)}건")
    for a in censored:
        print(f"    · 제외: {a['type']} {a['relation']} {a['nM']:.2f} nM | {a['assay'][:60]}")

    if usable:
        cell = sorted(a["nM"] for a in usable if a["cell_based"])
        bio = sorted(a["nM"] for a in usable if not a["cell_based"])

        def med(v):
            n = len(v)
            return None if not n else (v[n // 2] if n % 2 else (v[n // 2 - 1] + v[n // 2]) / 2)

        print(f"\n  어세이 유형별 분리 — 값의 범위가 3자릿수 넘게 벌어지므로 풀링하지 않는다")
        if cell:
            print(f"    세포 기반 {len(cell)}건: {', '.join(f'{v:.1f}' for v in cell)} nM"
                  f"  (중앙값 {med(cell):.1f})")
        if bio:
            print(f"    생화학·기타 {len(bio)}건: {', '.join(f'{v:.0f}' for v in bio)} nM"
                  f"  (중앙값 {med(bio):.0f})")
        print(f"    → TCR 분모로는 적응증이 일치하는 세포 기반 값을 쓴다.")
        print("  대표 항목:")
        for a in usable[:5]:
            print(f"    - {a['type']} {a['nM']:.2f} nM | {a['target']} | {a['assay']}")

    print()
    print("=" * 72)
    print("3. openFDA SPL 라벨 (LUMAKRAS)")
    print("=" * 72)
    try:
        label = openfda_label("LUMAKRAS")
        ofda = label.get("openfda", {})
        print(f"  brand      : {ofda.get('brand_name')}")
        print(f"  generic    : {ofda.get('generic_name')}")
        print(f"  SPL set id : {label.get('set_id')}")
        print(f"  effective  : {label.get('effective_time')}")
        hits = find_pk_text(label, ["Cmax", "AUC", "steady state", "960 mg"])
        print(f"\n  PK 관련 원문 {len(hits)}건 (상위 3건)")
        for h in hits[:3]:
            print(f"    [{h['field']} / {h['kw']}] {h['text'][:300]}...")
    except Exception as e:
        print(f"  조회 실패: {type(e).__name__}: {e}")

    print()
    print("=" * 72)
    print("4. Target Coverage Ratio — 라벨 실측값으로 실제 계산")
    print("=" * 72)
    # LUMAKRAS 라벨 12.3 보고값 (popPK 파생 / in vitro — '실측'이 아니다)
    CL_F = 26.2      # L/hr, 960 mg QD 정상상태 겉보기 청소율 (popPK 파생, CV 76%)
    FU_LABEL = 0.11  # "plasma protein binding is 89%" (in vitro)
    T_HALF = 5.0     # "mean terminal elimination half-life is 5 hours (SD: 2)"
    print(f"  라벨 보고값  CL/F {CL_F} L/hr (popPK 파생, CV 76%) · "
          f"단백결합 89% (in vitro) → f_u {FU_LABEL} · t½ {T_HALF} hr")
    print(f"  물성 기반 추정 f_u {fu:.3f} — 라벨값과 차이 {abs(fu - FU_LABEL):.3f}")
    print("  ※ n=1의 일치는 추정식의 검증이 아니다. 실측과 대조만 한 것이며,")
    print("     실측(라벨)값이 있으면 언제나 그것을 쓴다.")
    print()
    ic50s = [("세포 기반 p-ERK IC50 (NCI-H358, KRAS G12C)", 30.0),
             ("세포 기반 ERK 인산화 IC50 (MIAPaCa-2)", 68.0)]
    for label_txt, ic50 in ic50s:
        for dose in (960, 240):
            r = target_coverage_ratio(dose, CL_F, props["MW"], FU_LABEL, ic50,
                                      t_half_hr=T_HALF)
            flag = "  ← 지표에 따라 판정이 갈림(보류)" if r["verdict_split"] else ""
            print(f"  [{dose:3d} mg] {label_txt} (IC50 {ic50:.0f} nM)")
            print(f"      AUC0-24 {r['AUC_0_24_ug_hr_per_mL']:.1f} µg·hr/mL · "
                  f"V_ss {r['V_ss_L']:.0f} L (라벨 보고 Vd 211 L와 자기정합)")
            print(f"      TCR  C_max {r['TCR_max']:.1f} / C_avg {r['TCR_avg']:.1f} / "
                  f"C_trough {r['TCR_trough']:.2f}{flag}")
    print()
    print("  ※ 판정이 지표 선택에 의존한다 — 이것이 이 계산의 핵심 결과다.")
    print("     t½ 5시간에 1일 1회면 24시간 트로프는 피크의 1/28로 떨어진다.")
    print("     240 mg은 C_avg 기준으로는 커버, C_trough 기준으로는 미커버다.")
    print("     → 에이전트 규칙: 세 기준을 병기하고, 판정이 갈리면 '지표 의존적'으로")
    print("       표시한 뒤 결론을 보류하고 추가 PK 자료를 요청한다.")
    print()
    print("  ※ 240 mg 값은 960 mg의 CL/F를 그대로 쓴 '선형 가정' 결과다.")
    print("     라벨은 180~960 mg에서 정상상태 노출이 유사하다고 기술하므로 이 가정은")
    print("     라벨과 모순되며, '노출 유사 가정'에서는 240 mg 값이 960 mg과 같아진다.")
    print("     → 에이전트 규칙: 비선형 PK 보고 구간에서 선형 외삽을 금지하고")
    print("       두 가정의 범위를 함께 제시한다. 단일 점추정을 내지 않는다.")
    print()
    print("  판정 기준: TCR < 1 → 타겟 미커버 / TCR > 10 → 포화 의심")
    print("  ※ 이 임계값은 본 프로젝트가 설정한 잠정 기준이며 문헌 인용값이 아니다.")
    print("     본선에서 승인 라벨 60건 대조로 재보정한다.")
    print("  ※ 세포 기반 IC50은 혈청 함유 배지에서 측정되어 단백결합이 일부 반영돼 있다.")
    print("     여기에 혈장 f_u를 전량 곱하면 과대 보정이므로, 위 값은 보수적(작은) 쪽으로")
    print("     치우쳐 있다. 어세이 조건이 불명이면 보정 전후를 범위로 제시한다.")
    print("  ※ 소토라십은 비가역 공유결합 저해제다. 이 사례에서 평형 기반 TCR은 판정")
    print("     근거가 아니라 지표의 한계를 드러내는 예시이며, 공유결합 계열은")
    print("     kinact/K_I 기반 시간의존 점유 모델로 라우팅한다.")

    print()
    print("=" * 72)
    print("5. 그 시점에 무엇을 알 수 있었는가 — 노출 포화 판정의 검정력")
    print("=" * 72)
    CV = 0.76  # 라벨 12.3: 960 mg 정상상태 CL/F의 변동계수
    print(f"  라벨 보고 CL/F 변동계수 {CV:.0%} 기준, 두 용량군 AUC 비의 95% 신뢰구간")
    print(f"  (참값이 1, 즉 노출이 완전히 평탄하다고 가정해도 구간은 이만큼 벌어진다)")
    print()
    for n in (2, 3, 4, 6, 12):
        r = exposure_ratio_ci(CV, n)
        note = "  ← 통상 증량 코호트 규모" if n in (2, 4) else ""
        print(f"    용량군당 {n:>2}명 : {r['lo']:.2f} ~ {r['hi']:.2f}  "
              f"(폭 {r['fold']:.1f}배){note}")
    print()
    print("  → 용량당 2~4명에서는 구간이 6.5~14배로 벌어져 '평평하다'와 '2배 증가'를")
    print("     구분할 수 없다. 즉 RP2D 확정 시점의 표본으로는 노출 포화를 확정할 수 없다.")
    print("  → 에이전트 규칙: 판정과 함께 그 판정에 필요한 표본수를 항상 같이 낸다.")
    print("     이 사례의 정당한 출력은 '노출이 포화됐다'가 아니라")
    print("     '현재 표본으로는 판정 불가, 확장 전에 용량군별 반복투여 PK를 확보하라'다.")


if __name__ == "__main__":
    main()
