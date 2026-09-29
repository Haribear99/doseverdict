"""
Pharmacology Evidence 도구 — evidence/pharmacology_evidence.py 래퍼.

산출:
  structure_profile   RDKit 물성 + 구조 알림 → "반응성 계열 분류"까지만 (독성 장기 추론 금지)
  chembl_potency      검열값 제외·어세이 유형 분리·중앙값
  openfda_label       라벨 원문 + PK 파라미터 정규식 추출 (근거 인용 보존)
  tcr_three_metrics   C_max/C_avg/C_trough 세 기준 TCR, 판정 갈림 플래그
  exposure_power      노출비 95% CI (표본수별) — "판정과 함께 필요한 표본수"
"""
from __future__ import annotations

import re
import urllib.error
from datetime import datetime, timezone
from statistics import median
from typing import Any

import pharmacology_evidence as pe  # evidence/ (sys.path는 __init__에서 추가)

from app.tools import ToolResult, label_blinded, run_tool

_WARHEAD_CLASSES = {
    # 구조 알림 → 계열 분류. 여기서 멈춘다. 독성은 동일 계열 승인 라벨을 조회해 확인한다.
    "michael_acceptor": "irreversible_covalent_inhibitor_candidate",
    "acrylate": "irreversible_covalent_inhibitor_candidate",
    "halo_acrylate": "irreversible_covalent_inhibitor_candidate",
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


# ----------------------------------------------------------------- RDKit
def structure_profile(smiles: str) -> ToolResult:
    def _run(smiles: str) -> dict[str, Any]:
        props, alerts = pe.rdkit_profile(smiles)
        classes: set[str] = set()
        for a in alerts:
            key = a["description"].lower()
            for k, v in _WARHEAD_CLASSES.items():
                if k in key:
                    classes.add(v)
        return {
            "properties": {k: (round(v, 3) if isinstance(v, float) else v) for k, v in props.items()},
            "alerts": alerts,
            "structural_class": sorted(classes) or ["no_reactive_warhead_alert"],
            "fu_estimated": round(pe.estimated_free_fraction(props["cLogP"]), 4),
            "note": "구조 알림은 HTS 어세이 간섭 필터(BRENK/PAINS/NIH)이며 임상 독성 예측용으로 검증되지 않았다. 계열 분류까지만 사용한다.",
        }

    return run_tool("rdkit.structure_profile", _run, smiles=smiles)


# ----------------------------------------------------------------- ChEMBL
def chembl_potency(molecule_chembl_id: str, target_keyword: str | None = None) -> ToolResult:
    def _run(molecule_chembl_id: str, target_keyword: str | None) -> dict[str, Any]:
        rows = pe.chembl_potency(molecule_chembl_id)
        pool = rows
        target_matched = True
        if target_keyword:
            hit = [r for r in rows if r["target"] and target_keyword.upper() in r["target"].upper()]
            target_matched = bool(hit)
            pool = hit or rows
        censored = [r for r in pool if r["censored"]]
        usable = [r for r in pool if not r["censored"]]
        cell = sorted(r["nM"] for r in usable if r["cell_based"])
        bio = sorted(r["nM"] for r in usable if not r["cell_based"])
        return {
            "n_total_nM": len(rows),
            "n_target": len(pool),
            "target_matched": target_matched,
            "n_censored_excluded": len(censored),
            "censored": censored,
            "cell_based_nM": cell,
            "cell_based_median_nM": median(cell) if cell else None,
            "biochemical_nM": bio,
            "biochemical_median_nM": median(bio) if bio else None,
            "usable_rows": usable,
            "note": "검열값(<, >)은 점추정에서 제외. 세포 기반과 생화학 값은 풀링하지 않는다. 공유결합 저해제 IC50은 전배양 시간 의존.",
        }

    r = run_tool("chembl.potency", _run, molecule_chembl_id=molecule_chembl_id, target_keyword=target_keyword)
    r.source = {"url": "https://www.ebi.ac.uk/chembl/api/data/activity.json", "license": "CC BY-SA 3.0", "retrieved_at": _now()}
    return r


def chembl_lookup(name: str) -> ToolResult:
    """성분명 → ChEMBL ID(정확한 pref_name 일치만). 매핑 표에 없는 약의 대체 경로."""
    def _run(drug: str) -> dict[str, Any]:
        hit = pe.chembl_lookup(drug)
        return {"query": drug, "found": bool(hit), **(hit or {})}

    r = run_tool("chembl.lookup", _run, drug=name)
    r.source = {"url": "https://www.ebi.ac.uk/chembl/api/data/molecule/search.json", "license": "CC BY-SA 3.0", "retrieved_at": _now()}
    return r


# ----------------------------------------------------------------- openFDA
_NUM = r"(\d[\d,]*(?:\.\d+)?)"


def _sentences(text: str) -> list[str]:
    """소수점("26.2")에서 끊기지 않는 문장 분할."""
    return [x.strip() for x in re.split(r"(?<!\d)\.(?!\d)\s+", text) if x.strip()]


def _num(x: str) -> float:
    return float(x.replace(",", ""))


def parse_label_pk(text: str) -> tuple[dict[str, float], dict[str, str]]:
    """
    라벨 12.3 PK 문장에서 CL/F·t½·Vd·단백결합·CL/F CV를 뽑는다. 라벨마다 표현이 달라(09-25 조사: sotorasib·adagrasib·
    osimertinib·lorlatinib·capivasertib·alectinib) 문장 단위 규칙으로 처리한다.
    - CL/F: "clearance"와 "L/h(our)"가 같은 문장. 크레아티닌 청소율(mL/min)은 단위로 걸러진다.
      값이 여럿이면 "steady"가 있는 문장에서는 마지막(정상상태) 값, 아니면 첫 값.
    - CV: 그 값 바로 뒤 괄호 "(CV: 76%)", "(54%)", "(37% CV)".
    """
    pk: dict[str, float] = {}
    quotes: dict[str, str] = {}
    text = re.sub(r"[‐‑‒–]", "-", text)   # "half‑life"(U+2011) 등 — 로를라티닙 라벨
    for sent in _sentences(text):
        low = sent.lower()
        if "cl_f_L_per_hr" not in pk and "clearance" in low:
            hits = list(re.finditer(_NUM + r"\s*\(?\s*L/h(?:our|r)?\b\)?(?:\s*\((?:CV:?\s*)?" + _NUM + r"%(?:\s*CV)?\))?", sent))
            if hits:
                m = hits[-1] if "steady" in low else hits[0]
                pk["cl_f_L_per_hr"] = _num(m.group(1))
                if m.group(2):
                    pk["cl_cv_pct"] = _num(m.group(2))
                quotes["cl_f_L_per_hr"] = sent[:300]
        if "t_half_hr" not in pk and "half-life" in low:
            m = re.search(r"half-life" + r"[^%]*?(?:is|was|of)\s+(?:approximately\s+|about\s+)?" + _NUM + r"\s*(?:hours?|h)\b", sent, flags=re.I)
            if m:
                pk["t_half_hr"] = _num(m.group(1))
                quotes["t_half_hr"] = sent[:300]
        if "vd_L" not in pk and "volume of distribution" in low:
            m = re.search(r"volume of distribution.*?(?:is|was)\s+(?:approximately\s+)?" + _NUM + r"\s*L\b", sent, flags=re.I)
            if m:
                pk["vd_L"] = _num(m.group(1))
                quotes["vd_L"] = sent[:300]
        if "protein_binding_pct" not in pk and "protein" in low and "%" in sent:
            m = (re.search(r"protein binding.*?(?:is|was)\s+(?:approximately\s+|about\s+)?(?:greater than\s+|>\s*)?" + _NUM + r"%", sent, flags=re.I)
                 or re.search(_NUM + r"%\s+bound to (?:human )?plasma proteins?", sent, flags=re.I)
                 or re.search(r"bound to (?:human )?plasma proteins?.*?(?:greater than|>)\s*" + _NUM + r"%", sent, flags=re.I))
            if m:
                pk["protein_binding_pct"] = _num(m.group(1))
                quotes["protein_binding_pct"] = sent[:300]
    return pk, quotes


_NONLINEAR = r"non-?linear[^.]*pharmacokinetics[^.]*\."
_ER_UNKNOWN = r"exposure-response relationships?[^.]*unknown[^.]*\."
_MONITOR = r"(monitor[^.]*(liver|hepatic|ALT|AST)[^.]*\.)"


def _openfda_query(brand: str | None, generic: str | None) -> str:
    return f'openfda.brand_name:"{brand}"' if brand else f'openfda.generic_name:"{generic}"'


def _openfda_label_raw(brand: str | None = None, generic: str | None = None) -> dict[str, Any]:
    """openFDA 라벨 조회(브랜드명 또는 성분명). OPENFDA_API_KEY가 있으면 일 한도 1,000 → 120,000으로 상향(open.fda.gov/apis/authentication)."""
    import os
    import urllib.error
    import urllib.parse

    key = os.getenv("OPENFDA_API_KEY")
    try:
        return _openfda_fetch(_openfda_query(brand, generic), key)
    except urllib.error.HTTPError as e:
        if e.code != 404:
            raise
    # 필드 검색 404 → 전문 검색. 라벨 개정본에 openfda 조화 필드(brand_name 등)가 비면 필드 검색에 안 잡힌다(09-26 TAGRISSO 실측).
    # 오탐을 막기 위해 제품 데이터 요소(spl_product_data_elements) 첫 단어가 그 이름인 라벨만 채택한다.
    name = (brand or generic or "").upper()
    for r in pe.fetch_json(f"https://api.fda.gov/drug/label.json?search={urllib.parse.quote(name)}&limit=5"
                           + (f"&api_key={key}" if key else ""))["results"]:
        prod = " ".join(r.get("spl_product_data_elements") or []).upper().split()
        if prod and (prod[0] == name or (generic and name in prod[:3])):
            return r
    raise urllib.error.HTTPError("", 404, f"no label for {name}", {}, None)


def _openfda_fetch(query: str, key: str | None) -> dict[str, Any]:
    import urllib.parse

    q = urllib.parse.quote(query)
    url = f"https://api.fda.gov/drug/label.json?search={q}&limit=1" + (f"&api_key={key}" if key else "")
    return pe.fetch_json(url)["results"][0]


def openfda_label(brand: str | None = None, generic: str | None = None) -> ToolResult:
    """브랜드명이 없으면 성분명(openfda.generic_name)으로 찾는다 — 매핑 표에 없는 약의 대체 경로."""
    def _run(brand: str | None, generic: str | None) -> dict[str, Any]:
        if label_blinded():   # 후향 검증: 라벨은 승인 후 문서 — 조회하지 않고 '라벨 없음'과 같게 처리
            raise urllib.error.HTTPError("", 404, "label blinded (DV_BLIND_LABEL, as-of review)", {}, None)
        label = _openfda_label_raw(brand, generic)
        brand = brand or ((label.get("openfda") or {}).get("brand_name") or [generic])[0]
        text = " ".join(label.get("clinical_pharmacology", []) + label.get("pharmacokinetics", []) + label.get("description", []))
        pk, quotes = parse_label_pk(text)
        if "protein_binding_pct" in pk:
            pk["fu_label"] = round(1 - pk["protein_binding_pct"] / 100, 3)
        nonlinear = re.search(_NONLINEAR, text, flags=re.I)
        er_unknown = re.search(_ER_UNKNOWN, text, flags=re.I)
        warn = " ".join(label.get("warnings_and_cautions", []) + label.get("boxed_warning", []))
        monitor = re.findall(_MONITOR, warn, flags=re.I)
        return {
            "brand": brand,
            "generic": (label.get("openfda") or {}).get("generic_name") or ([generic] if generic else None),
            "set_id": label.get("set_id"),
            "effective_time": label.get("effective_time"),
            "pk": pk,
            "pk_quotes": quotes,
            "nonlinear_pk_statement": nonlinear.group(0) if nonlinear else None,
            "exposure_response_unknown_statement": er_unknown.group(0) if er_unknown else None,
            "liver_monitoring_statements": [m[0] for m in monitor],
            "has_liver_monitoring": bool(monitor),
            "raw_sections": {k: label.get(k) for k in ("clinical_pharmacology", "warnings_and_cautions", "dosage_and_administration", "adverse_reactions")},
        }

    r = run_tool("openfda.label", _run, brand=brand, generic=generic)
    r.source = {"url": f"https://api.fda.gov/drug/label.json?search={_openfda_query(brand, generic)}", "license": "public domain", "retrieved_at": _now()}
    return r


# ----------------------------------------------------------------- TCR
def tcr_three_metrics(dose_mg: float, cl_f_L_per_hr: float, mw: float, fu: float, ic50_nM: float,
                      t_half_hr: float, tau_hr: float = 24.0, linear_assumption: bool = True) -> ToolResult:
    def _run(**kw) -> dict[str, Any]:
        out = pe.target_coverage_ratio(kw["dose_mg"], kw["cl_f_L_per_hr"], kw["mw"], kw["fu"], kw["ic50_nM"], tau_hr=kw["tau_hr"], t_half_hr=kw["t_half_hr"])
        out = {k: (round(v, 4) if isinstance(v, float) else v) for k, v in out.items()}
        out["assumption"] = "linear_CL" if kw["linear_assumption"] else "exposure_similar_to_reference"
        out["thresholds_note"] = "TCR<1 미커버 / >10 포화 의심 — 본 프로젝트 잠정 기준(문헌값 아님)"
        out["verdict"] = "abstain_metric_dependent" if out["verdict_split"] else ("covered" if out["TCR_trough"] >= 1 else "not_covered")
        return out

    return run_tool("pharm.tcr_three_metrics", _run, dose_mg=dose_mg, cl_f_L_per_hr=cl_f_L_per_hr, mw=mw, fu=fu, ic50_nM=ic50_nM,
                    t_half_hr=t_half_hr, tau_hr=tau_hr, linear_assumption=linear_assumption)


def exposure_power(cv: float, n_per_arm_list: tuple[int, ...] = (2, 3, 4, 6, 12)) -> ToolResult:
    def _run(cv: float, n_per_arm_list) -> dict[str, Any]:
        rows = [{"n_per_arm": n, **{k: round(v, 3) for k, v in pe.exposure_ratio_ci(cv, n).items()}} for n in n_per_arm_list]
        return {"cv": cv, "rows": rows, "note": "참값이 1(완전 평탄)일 때 두 용량군 AUC 비의 95% CI. 폭이 배 단위면 '평평하다'와 '2배 증가'를 구분할 수 없다."}

    return run_tool("pharm.exposure_power", _run, cv=cv, n_per_arm_list=n_per_arm_list)
