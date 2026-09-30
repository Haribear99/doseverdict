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
