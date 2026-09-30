"""반박 모드(docs/refute_prereg.md) 오프라인 테스트 — 스위치, 기본 모드 불변, 반박된 질문의 결정론 필터."""
from app.agents import findings as F
from app.agents.graph import new_state
from app.agents.reviewers import refute_mode


def _state(refute):
    st = new_state("The MTD will be selected as the RP2D. Liver tests every 6 weeks.", run_id="t-refute")
    if refute is not None:
        st.scratch["refute"] = refute
    st.review_questions = [{"task_id": "T01", "hypothesis": "h1"}, {"task_id": "T02", "hypothesis": "h2"}]
    st.scratch["positions"] = {
        "T01": [{"reviewer": "regulatory", "severity": "high", "position": "gap", "evidence_ids_seen": [], "stance": "defect"}],
        "T02": [{"reviewer": "regulatory", "severity": "low", "position": "protocol already randomizes", "evidence_ids_seen": [], "stance": "no_defect"}],
    }
    return st


def test_switch_state_overrides_env(monkeypatch):
    monkeypatch.setenv("DV_ARENA_REFUTE", "1")
    assert refute_mode(_state(False)) is False
    monkeypatch.setenv("DV_ARENA_REFUTE", "0")
    assert refute_mode(_state(True)) is True
    assert refute_mode(_state(None)) is False


def test_default_mode_prompt_unchanged(monkeypatch):
    monkeypatch.delenv("DV_ARENA_REFUTE", raising=False)
    st = _state(None)
    assert F._COVER in F._instructions(st) and F._COVER_REFUTE not in F._instructions(st)
    assert F.refuted_tasks(st) == set()      # 기본 모드는 stance를 보지 않는다


def test_refuted_questions_removed_and_drafts_dropped(monkeypatch):
    st = _state(True)
    assert F.refuted_tasks(st) == {"T02"}
    assert F._COVER_REFUTE in F._instructions(st)
    seen = {}

    def fake_call(gc, role, ctx, **kw):
        import json
        seen["ctx"] = json.loads(ctx)
        row = dict(protocol_span_text="Liver tests every 6 weeks.", protocol_fact="p", evidence_fact="e", category="safety_monitoring", severity="high")
        out = F._FindingsOut(findings=[F._FindingOut(task_id="T01", **row), F._FindingOut(task_id="T02", **row)])
        return out, {"usage": {}}

    monkeypatch.setattr(F, "call_structured", fake_call)
    monkeypatch.setattr(F, "deterministic_tcr_finding", lambda s: None)
    monkeypatch.setattr(F, "deterministic_version_findings", lambda s: [])
    F.draft_findings(None, st)
    assert [q["task_id"] for q in seen["ctx"]["review_questions"]] == ["T01"]
    assert "T02" not in seen["ctx"]["reviewer_positions"]
    assert len(st.findings) == 1 and st.scratch["refuted_dropped"] == ["T02"]
