"""검토 메모 렌더러 — 저장된 데모 결과로 구조·필수 항목을 검증(LLM·네트워크 없음)."""
from pathlib import Path

import pytest

from app.report import render_memo
from app.schema.trial_schema import ReviewState

DEMO1 = Path(__file__).resolve().parents[1] / "app" / "demo" / "results" / "demo1.json"


@pytest.mark.skipif(not DEMO1.exists(), reason="cached demo missing")
def test_memo_sections_and_counts():
    rs = ReviewState.model_validate_json(DEMO1.read_text(encoding="utf-8"))
    m = render_memo(rs)
    for h in ("## 요약", "## 결론 보류(기권)", "## 결함(검증된 인용)", "## 도구 호출", "## 토큰 원장", "## 감사 메타"):
        assert h in m, h
    assert f"finding {len(rs.findings)}건" in m and f"{rs.budget.used_tokens:,}" in m
    assert "최종 결정은 사람" in m                          # 판정 권한 표기
    assert m.count("### F") == len(rs.findings)              # finding 누락 없음


def test_memo_minimal_state():
    m = render_memo(ReviewState(run_id="empty"))
    assert "finding 0건" in m and "## 재계획 이벤트" not in m
