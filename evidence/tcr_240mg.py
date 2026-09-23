"""
소토라십 240 mg TCR — 두 PK 가정 × 세 기준(C_max·C_avg·C_trough) (PRD P0-4a)

(가) 선형 CL/F 가정: 960 mg에서 보고된 CL/F를 240 mg에 그대로 적용한다.
(나) 노출 유사 가정: 라벨 12.3 "180 mg to 960 mg … with similar systemic exposure
     (i.e., AUC 0-24h and C max ) across doses at steady state"를 따라 240 mg의
     정상상태 노출을 960 mg과 같다고 둔다. 도구의 linear_assumption 인자는 계산을
     바꾸지 않으므로, 입력 용량을 960 mg 노출 등가로 명시적으로 바꿔 계산한다.

두 가정의 판정이 다르면 결론을 내지 않는다(프로젝트 규칙: 약리 지표 단일 값 금지).

실행:  .venv/Scripts/python.exe evidence/tcr_240mg.py
출력:  evidence/tcr_240mg.json
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.tools import pharmacology  # noqa: E402

# 입력값 출처: app/demo/results/demo1.json scratch.label_pk·scratch.chembl (openFDA LUMAKRAS 라벨 20250122, ChEMBL 세포 기반 IC50 중앙값)
PK = {"cl_f_L_per_hr": 26.2, "t_half_hr": 5.0, "fu": 0.11}
IC50_NM = 30.0
MW = 560.605
LABEL_URL = 'https://api.fda.gov/drug/label.json?search=openfda.brand_name:"LUMAKRAS"'
LABEL_QUOTE = ("Sotorasib exhibited non-linear, time-dependent, pharmacokinetics over the dose range of 180 mg to 960 mg "
               "(0.19 to 1 time the approved recommended dosage) once daily with similar systemic exposure "
               "(i.e., AUC 0-24h and C max ) across doses at steady state.")


def _row(assumption: str, dose_label: float, dose_for_exposure: float, linear: bool) -> dict:
    r = pharmacology.tcr_three_metrics(dose_for_exposure, PK["cl_f_L_per_hr"], MW, PK["fu"], IC50_NM,
                                       t_half_hr=PK["t_half_hr"], linear_assumption=linear)
    if not r.ok:
        raise RuntimeError(r.error)
    d = r.data
    return {"assumption": assumption, "dose_mg": dose_label, "exposure_input_dose_mg": dose_for_exposure,
            "TCR_max": d["TCR_max"], "TCR_avg": d["TCR_avg"], "TCR_trough": d["TCR_trough"], "verdict": d["verdict"]}


def main() -> int:
    rows = [
        _row("(가) 선형 CL/F", 240, 240, True),
        _row("(나) 노출 유사(라벨 12.3)", 240, 960, False),
    ]
    verdicts = {r["verdict"] for r in rows}
    out = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "drug": "sotorasib (LUMAKRAS)",
        "inputs": {**PK, "ic50_nM": IC50_NM, "ic50_basis": "ChEMBL 세포 기반 중앙값", "mw": MW, "tau_hr": 24.0},
        "sources": {"label_url": LABEL_URL, "label_effective_time": "20250122", "label_section": "12.3 Pharmacokinetics",
                    "label_quote": LABEL_QUOTE, "inputs_from": "app/demo/results/demo1.json scratch.label_pk / scratch.chembl"},
        "rows": rows,
        "overall": "abstain_assumption_dependent" if len(verdicts) > 1 else rows[0]["verdict"],
        "overall_reason": ("PK 가정에 따라 판정이 달라짐 — 240 mg 결론을 만들지 않고 용량군별 반복투여 PK를 요청한다"
                           if len(verdicts) > 1 else "두 가정의 판정이 같음"),
        "thresholds_note": "TCR<1 미커버 / >10 포화 의심 — 본 프로젝트 잠정 기준(문헌값 아님)",
    }
    path = ROOT / "evidence" / "tcr_240mg.json"
    path.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for r in rows:
        print(f"{r['assumption']}: Cmax {r['TCR_max']} / Cavg {r['TCR_avg']} / Ctrough {r['TCR_trough']} → {r['verdict']}")
    print("overall:", out["overall"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
