"""
실사례 후향 검증 입력 빌더 (결정론, LLM 호출 0).

질문: FDA가 승인 때 용량최적화 PMR/PMC를 부과한 약을, 승인 **전** 정보만으로 짚는가.
입력: 약물별 최초 1상(FIH) 결과 논문 초록(PubMed, 출판일 < FDA 승인일) + ChEMBL 구조·표적. 약물명·코드명은 가린다.
  - CT.gov 등록정보는 본문으로 쓰지 않는다. 현재 버전에는 승인 후 추가된 팔(예: 소토라십 NCT03600883의 'Phase 2 monotherapy dose comparison')이
    섞여 있고, 버전 이력 API는 403이라 승인 시점 버전을 받을 수 없다(2026-09-29 확인). NCT는 코드명 수집에만 쓴다.
출처 목록: app/eval/data/retro_sources_part*.json (NCT·PMID·SMILES, API로 실재 확인한 값) + pmr_ground_truth*.jsonl(정답).
출력: app/eval/data/retro_cases.jsonl (case_id·as-of·synopsis·정답), retro_manifest.jsonl(약물 식별 정보 — 분석에서만 사용)
실행: python -m app.eval.retro_build
"""
from __future__ import annotations

import json
import re
import sys
import time
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = Path(__file__).resolve().parent / "data"
sys.path.insert(0, str(ROOT / "evidence"))
import pharmacology_evidence as pe  # noqa: E402  재시도 포함 fetch_json

EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
CHEMBL = "https://www.ebi.ac.uk/chembl/api/data"
EXCLUDE = {"tofacitinib", "remibrutinib"}   # 비항암 적응증 — 지원 범위(항암 1/2상) 밖
_CODE = re.compile(r"\b(?!NCT\d)[A-Z]{2,6}[- ]?\d{3,7}[A-Z]?\b")   # 스폰서 코드명(AMG 510, MRTX849, LDK378, INCB018424). CYP3A4·HER2·G12C는 안 걸린다


def _get_text(url: str) -> str:
    import urllib.request
    req = urllib.request.Request(url, headers={"User-Agent": "DoseVerdict-retro/1.0"})
    for i in range(3):
        try:
            with urllib.request.urlopen(req, timeout=40) as r:
                return r.read().decode("utf-8", "replace")
        except Exception:  # noqa: BLE001
            if i == 2:
                raise
            time.sleep(2 * (i + 1))
    return ""


def abstract_of(pmid: str) -> tuple[str, str]:
    """PubMed efetch XML에서 초록 본문과 출판 연도만 꺼낸다(저자·저널·제목은 약물명을 담아 쓰지 않는다)."""
    xml = _get_text(f"{EUTILS}/efetch.fcgi?db=pubmed&id={pmid}&rettype=abstract&retmode=xml")
    parts = []
    for m in re.finditer(r"<AbstractText([^>]*)>(.*?)</AbstractText>", xml, flags=re.S):
        label = re.search(r'Label="([^"]+)"', m.group(1))
        body = re.sub(r"<[^>]+>", "", m.group(2)).strip()
        parts.append(f"{label.group(1).title()}: {body}" if label else body)
    year = re.search(r"<PubDate>\s*<Year>(\d{4})", xml) or re.search(r"<Year>(\d{4})</Year>", xml)
    import html
    return html.unescape("\n\n".join(parts)), (year.group(1) if year else "")


def target_of(chembl_id: str) -> tuple[str, str]:
    """ChEMBL 작용기전 → (유전자 기호, 기전 문구). 다중 표적이면 첫 기전."""
    mech = pe.fetch_json(f"{CHEMBL}/mechanism.json?molecule_chembl_id={chembl_id}&limit=5").get("mechanisms", [])
    if not mech:
        return "", ""
    m = mech[0]
    sym = ""
    if m.get("target_chembl_id"):
        t = pe.fetch_json(f"{CHEMBL}/target/{m['target_chembl_id']}.json")
        for comp in t.get("target_components", []):
            for syn in comp.get("target_component_synonyms", []):
                if syn.get("syn_type") == "GENE_SYMBOL":
                    sym = syn["component_synonym"]
                    break
            if sym:
                break
    return sym, m.get("mechanism_of_action") or ""


def code_names(nct_id: str | None) -> set[str]:
    """CT.gov 중재 이름·별칭에서 코드명을 모은다(마스킹 목록용 — 본문에는 쓰지 않는다)."""
    if not nct_id:
        return set()
    d = pe.fetch_json(f"https://clinicaltrials.gov/api/v2/studies/{nct_id}?fields=InterventionName,InterventionOtherName")
    names = set()
    for iv in ((d.get("protocolSection") or {}).get("armsInterventionsModule") or {}).get("interventions", []):
        names.update([iv.get("name", "")] + (iv.get("otherNames") or []))
    # 병용약·위약(Midazolam, Pembrolizumab…)은 가리지 않는다 — 코드명 형태이거나 이미 알려진 이름만
    return {n.strip() for n in names if n and n.strip() and _CODE.fullmatch(n.strip())}


def mask(text: str, names: set[str], alias: str) -> str:
    for n in sorted(names, key=len, reverse=True):
        if len(n) >= 3:
            text = re.sub(re.escape(n), alias, text, flags=re.I)
    return _CODE.sub(alias, text)


def synopsis(case_id: str, alias: str, asof: str, year: str, sym: str, moa: str, smiles: str, abstract: str) -> str:
    moa_txt = mask(moa, set(), alias) if moa else "small-molecule targeted agent"
    return f"""# Protocol Synopsis — {case_id} (retrospective, as-of {asof})

**Title:** First-in-Human Phase 1 Study of {alias} in Patients with Advanced Cancer (retrospective review input)
**Sponsor:** masked · **Countries:** United States · **Phase:** 1

## Investigational Product
{alias} is an oral small molecule ({moa_txt}). SMILES: {smiles}. Target: {sym or 'not stated'}.

## Source of This Synopsis
This synopsis was assembled from the published results of the first-in-human Phase 1 study (published {year}), before regulatory approval.
Drug and sponsor code names are masked as {alias}. No other protocol text is available. The dose selected for later development is the dose under review.

## Phase 1 Study Report (published abstract, verbatim except masking)
{abstract}
"""


def build() -> None:
    truth = {}
    for fn in ("pmr_ground_truth.jsonl", "pmr_ground_truth_ext.jsonl"):
        p = DATA / fn
        if p.exists():
            for line in p.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    r = json.loads(line)
                    truth[r["generic"].lower()] = r
    sources = []
    for p in sorted(DATA.glob("retro_sources_part*.json")):
        sources += json.loads(p.read_text(encoding="utf-8"))
    cases, manifest, skipped = [], [], []
    for s in sorted(sources, key=lambda x: x["generic"].lower()):
        g = s["generic"].lower()
        t = truth.get(g)
        why = ("no_truth" if not t else "non_oncology" if g in EXCLUDE else "label_unknown" if not isinstance(t["pmr_dose_optimization"], bool)
               else "no_pmid" if not s.get("pmid") else "pmid_after_approval" if not s.get("pmid_before_approval") else "no_smiles" if not s.get("smiles") else "")
        if why:
            skipped.append({"generic": g, "reason": why})
            continue
        abstract, year = abstract_of(str(s["pmid"]))
        time.sleep(0.4)
        if len(abstract) < 400:
            skipped.append({"generic": g, "reason": "abstract_too_short"})
            continue
        sym, moa = target_of(s["chembl_id"]) if s.get("chembl_id") else ("", "")
        names = {g, t.get("brand", "")} | code_names(s.get("nct_id"))
        i = len(cases) + 1
        cid, alias = f"RETRO-{i:02d}", f"DV-R{i:02d}"
        syn = synopsis(cid, alias, t["initial_approval_date"], year, sym, moa, s["smiles"], mask(abstract, names, alias))
        leaked = [n for n in names if len(n) >= 3 and n.lower() in syn.lower()]
        if leaked:
            raise SystemExit(f"{g}: 마스킹 누락 {leaked}")
        cases.append({"case_id": cid, "asof": t["initial_approval_date"], "y": int(t["pmr_dose_optimization"]), "synopsis": syn})
        manifest.append({"case_id": cid, "generic": g, "brand": t.get("brand"), "asof": t["initial_approval_date"], "approval_year": int(t["initial_approval_date"][:4]),
                         "y": int(t["pmr_dose_optimization"]), "pmid": s["pmid"], "pmid_pubdate": s.get("pmid_pubdate"), "nct_id": s.get("nct_id"),
                         "chembl_id": s.get("chembl_id"), "target": sym, "masked_names": sorted(names - {""}), "truth_source": t.get("source_urls")})
        print(cid, g, "y=", cases[-1]["y"], "target", sym, "abstract", len(abstract))
    (DATA / "retro_cases.jsonl").write_text("\n".join(json.dumps(c, ensure_ascii=False) for c in cases) + "\n", encoding="utf-8")
    (DATA / "retro_manifest.jsonl").write_text("\n".join(json.dumps(m, ensure_ascii=False) for m in manifest) + "\n", encoding="utf-8")
    print(f"cases {len(cases)} (양성 {sum(c['y'] for c in cases)}), 제외 {skipped}")


if __name__ == "__main__":
    build()
