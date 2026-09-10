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
from datetime import datetime, timezone
from statistics import median
from typing import Any

import pharmacology_evidence as pe  # evidence/ (sys.path는 __init__에서 추가)

from app.tools import ToolResult, run_tool

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


# ----------------------------------------------------------------- openFDA
_PK_PATTERNS = {
    "cl_f_L_per_hr": r"apparent clearance[^.]*?is\s+([\d.]+)\s*L/h",
    "t_half_hr": r"half-life[^.]*?is\s+([\d.]+)\s*hours?",
    "vd_L": r"volume of distribution[^.]*?is\s+([\d.]+)\s*L\b",
    "protein_binding_pct": r"plasma protein binding is\s+([\d.]+)%",
    "cl_cv_pct": r"apparent clearance[^.]*?\(CV:\s*([\d.]+)%\)",
}
_NONLINEAR = r"non-?linear[^.]*pharmacokinetics[^.]*\."
_ER_UNKNOWN = r"exposure-response relationships?[^.]*unknown[^.]*\."
_MONITOR = r"(monitor[^.]*(liver|hepatic|ALT|AST)[^.]*\.)"


def _openfda_label_raw(brand: str) -> dict[str, Any]:
    """openFDA 라벨 조회. OPENFDA_API_KEY가 있으면 일 한도 1,000 → 120,000으로 상향(open.fda.gov/apis/authentication)."""
    import os
    import urllib.parse

    key = os.getenv("OPENFDA_API_KEY")
    q = urllib.parse.quote(f'openfda.brand_name:"{brand}"')
    url = f"https://api.fda.gov/drug/label.json?search={q}&limit=1" + (f"&api_key={key}" if key else "")
    return pe.fetch_json(url)["results"][0]


def openfda_label(brand: str) -> ToolResult:
    def _run(brand: str) -> dict[str, Any]:
        label = _openfda_label_raw(brand)
        text = " ".join(label.get("clinical_pharmacology", []) + label.get("description", []))
        pk: dict[str, Any] = {}
        quotes: dict[str, str] = {}
        for k, pat in _PK_PATTERNS.items():
            m = re.search(pat, text, flags=re.I)
            if m:
                pk[k] = float(m.group(1))
                quotes[k] = text[max(0, m.start() - 40): m.end() + 40]
        if "protein_binding_pct" in pk:
            pk["fu_label"] = round(1 - pk["protein_binding_pct"] / 100, 3)
        nonlinear = re.search(_NONLINEAR, text, flags=re.I)
        er_unknown = re.search(_ER_UNKNOWN, text, flags=re.I)
        warn = " ".join(label.get("warnings_and_cautions", []) + label.get("boxed_warning", []))
        monitor = re.findall(_MONITOR, warn, flags=re.I)
        return {
            "brand": brand,
            "generic": (label.get("openfda") or {}).get("generic_name"),
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

    r = run_tool("openfda.label", _run, brand=brand)
    r.source = {"url": f'https://api.fda.gov/drug/label.json?search=openfda.brand_name:"{brand}"', "license": "public domain", "retrieved_at": _now()}
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
