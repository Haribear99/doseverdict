"""수정안 적용(결정론) — 원문에 있는 span만 치환하고, 기권·빈 수정안은 건너뛴다."""
from app.agents.patching import apply_patches


def test_apply_patches_only_defect_with_patch():
    text = "The MTD will be selected as the RP2D. LFTs every 6 weeks."
    fs = [{"finding_id": "F01", "verdict": "defect", "protocol_span": {"text": "LFTs every 6 weeks."}, "suggested_patch": "LFTs every 3 weeks for 3 months."},
          {"finding_id": "F00", "verdict": "abstain", "protocol_span": {"text": "The MTD will be selected as the RP2D."}, "suggested_patch": "x"},
          {"finding_id": "F02", "verdict": "defect", "protocol_span": {"text": "not in text"}, "suggested_patch": "y"},
          {"finding_id": "F03", "verdict": "defect", "protocol_span": {"text": "The MTD will be selected as the RP2D."}, "suggested_patch": None}]
    new, applied = apply_patches(text, fs)
    assert new == "The MTD will be selected as the RP2D. LFTs every 3 weeks for 3 months."
    assert [a["finding_id"] for a in applied] == ["F01"]


def test_calibrated_state_overrides_env(monkeypatch):
    """UI '보수적 지적 모드'는 실행 상태로 전달 — 환경변수(다른 세션)보다 우선한다."""
    from app.agents.findings import _calibrated, _instructions
    from app.agents.graph import new_state
    monkeypatch.setenv("DV_FINDINGS_CALIBRATED", "1")
    st = new_state("x", "t")
    st.scratch["calibrated"] = False
    assert _calibrated(st) is False and "ONLY when" not in _instructions(st)
    st.scratch["calibrated"] = True
    monkeypatch.setenv("DV_FINDINGS_CALIBRATED", "0")
    assert _calibrated(st) is True and "ONLY when" in _instructions(st)
