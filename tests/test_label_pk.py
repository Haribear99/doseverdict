"""라벨 12.3 PK 파서 — 실제 openFDA 라벨 문장(2026-09 조회)으로 약물별 표현 차이를 검증(네트워크 없음)."""
import pytest

from app.tools.pharmacology import parse_label_pk

CASES = {
    "sotorasib": ("At 960 mg LUMAKRAS once daily, the sotorasib steady state apparent clearance is 26.2 L/hr (CV: 76%). "
                  "The sotorasib mean volume of distribution (V d ) at steady state is 211 L (CV: 135%). In vitro , sotorasib plasma protein binding is 89%. "
                  "The sotorasib mean elimination half-life is 5 hours (standard deviation (SD): 2).",
                  {"cl_f_L_per_hr": 26.2, "cl_cv_pct": 76.0, "protein_binding_pct": 89.0, "t_half_hr": 5.0, "vd_L": 211.0}),
    "adagrasib": ("Human plasma protein binding of adagrasib is approximately 98% in vitro. Elimination The adagrasib terminal elimination "
                  "half-life is 23 hours (16%) and the apparent oral clearance (CL/F) is 37 L/h (54%) in patients.",
                  {"cl_f_L_per_hr": 37.0, "cl_cv_pct": 54.0, "protein_binding_pct": 98.0, "t_half_hr": 23.0}),
    "osimertinib": ("Plasma protein binding of osimertinib was 95%. Plasma concentrations decreased with time and a population estimated mean "
                    "half-life of osimertinib was 48 hours, and oral clearance (CL/F) was 14.3 (L/h).",
                    {"cl_f_L_per_hr": 14.3, "protein_binding_pct": 95.0, "t_half_hr": 48.0}),
    "lorlatinib": ("Distribution Lorlatinib is 66% bound to plasma proteins, in vitro. Elimination The mean plasma half‑life (t ½ ) of lorlatinib "
                   "was 24 hours (40%) after a single oral 100 mg dose of LORBRENA. The mean oral clearance (CL/F) was 11 L/h (35%) following a "
                   "single oral 100 mg dose and increased to 18 L/h (39%) at steady state, suggesting autoinduction.",
                   {"cl_f_L_per_hr": 18.0, "cl_cv_pct": 39.0, "protein_binding_pct": 66.0, "t_half_hr": 24.0}),
    "capivasertib": ("Capivasertib plasma protein binding is 78% and the plasma-to-blood ratio is 0.71. Elimination The half-life is 8.3 hours, "
                     "and the steady-state oral clearance is 50 L/h (37% CV). Renal clearance was 21% of total clearance.",
                     {"cl_f_L_per_hr": 50.0, "cl_cv_pct": 37.0, "protein_binding_pct": 78.0, "t_half_hr": 8.3}),
    "alectinib": ("Alectinib and M4 are bound to human plasma proteins greater than 99%, independent of drug concentration. Elimination The "
                  "apparent clearance (CL/F) is 81.9 L/hour for alectinib and 217 L/hour for M4. The geometric mean elimination half-life is 33 hours.",
                  {"cl_f_L_per_hr": 81.9, "protein_binding_pct": 99.0, "t_half_hr": 33.0}),
}


@pytest.mark.parametrize("drug", list(CASES))
def test_parse_label_pk(drug):
    text, want = CASES[drug]
    pk, quotes = parse_label_pk(text)
    for k, v in want.items():
        assert pk.get(k) == v, (drug, k, pk)
        assert quotes[k if k != "cl_cv_pct" else "cl_f_L_per_hr"]


def test_creatinine_clearance_is_not_clf():
    pk, _ = parse_label_pk("No clinically meaningful effect was seen with creatinine clearance 30 to 89 mL/min.")
    assert "cl_f_L_per_hr" not in pk
