"""F00·노출 근거의 증량 코호트 문장 — 인원을 프로토콜에서 읽는지(10-01: '용량당 2~4명' 고정 문구 결함)."""
from app.agents.nodes import cohort_exposure_sentences
from app.schema.trial_schema import ReviewState
from app.tools import pharmacology


def _state(method: str | None, text: str) -> ReviewState:
    st = ReviewState(run_id="t", raw_protocol_text=text)
    st.trial.design.dose_strategy.escalation_method = method
    return st


ROWS_HIGH_CV = pharmacology.exposure_power(0.76).data["rows"]   # 소토라십 라벨 CL/F CV
ROWS_LOW_CV = pharmacology.exposure_power(0.10).data["rows"]


def test_three_plus_three_uses_protocol_cohort():
    tail, claim = cohort_exposure_sentences(_state("3+3", "Cohorts of 3 subjects; DLT evaluation period is 21 days."), ROWS_HIGH_CV)
    assert "용량당 3명, DLT 확인 시 6명" in claim and "2~4" not in tail + claim
    assert "n=3" in tail and "n=6" in tail


def test_explicit_cohort_size_without_three_plus_three():
    tail, claim = cohort_exposure_sentences(_state("BOIN", "Cohorts of 6 subjects."), ROWS_HIGH_CV)
    assert "용량당 6명" in claim and "n=6" in tail


def test_unstated_cohort_size_invents_no_number():
    tail, claim = cohort_exposure_sentences(_state("BOIN", "maximum of 36 subjects"), ROWS_HIGH_CV)
    assert "명시되지 않" in claim and not any(ch.isdigit() for ch in claim)


def test_narrow_ci_makes_no_saturation_claim():
    tail, claim = cohort_exposure_sentences(_state("3+3", "Cohorts of 3 subjects"), ROWS_LOW_CV)
    assert claim == "" and "확정할 수 없다" not in tail
