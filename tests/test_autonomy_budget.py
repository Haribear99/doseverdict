"""3·4단계(09-26): 호출 전 예산 가드, 노드별 원장, rewrite 루프 안전장치 — LLM 없이 검증."""
from app.agents import graph
from app.schema.trial_schema import Finding, ProtocolSpan, ReviewState


def _finding(fid: str, status: str) -> Finding:
    return Finding(finding_id=fid, category="dose_optimization", severity="high", protocol_span=ProtocolSpan(section="x", text="y"),
                   claim="c", verdict="defect", verifier_status=status)


def test_add_tokens_by_node():
    st = ReviewState(run_id="t")
    graph._add_tokens(st, {"usage": {"total_tokens": 100}}, "plan")
    graph._add_tokens(st, {"usage": {"total_tokens": 50}}, "plan")
    graph._add_tokens(st, {"usage": {"total_tokens": 7}}, "arena")
    assert st.budget.used_tokens == 157 and st.budget.by_node == {"plan": 150, "arena": 7}


def test_guard_blocks_when_estimate_exceeds_remaining():
    st = ReviewState(run_id="t")
    st.budget.max_tokens, st.budget.used_tokens = 20_000, 12_000          # 남은 8k < arena 예상 10k
    assert graph._guard(st, "arena") is False
    ev = st.replan_events[-1]
    assert ev["trigger"] == "budget_guard" and ev["node"] == "arena" and ev["estimated"] == 10_000
    assert graph._guard(st, "rewrite") is True                           # 1.5k는 가능


def test_guard_scales_with_reviewers():
    st = ReviewState(run_id="t")
    st.scratch["reviewers"] = ["regulatory", "site", "patient"]
    st.budget.max_tokens, st.budget.used_tokens = 100_000, 75_000        # 남은 25k < 3인 30k
    assert graph._guard(st, "arena") is False


def test_arena_degrades_instead_of_calling(monkeypatch):
    st = ReviewState(run_id="t")
    st.budget.max_tokens, st.budget.used_tokens = 10_000, 5_000
    monkeypatch.setattr(graph, "run_arena", lambda *a, **k: (_ for _ in ()).throw(AssertionError("LLM called")))
    out = graph.node_arena(st)
    assert out["scratch"]["positions"] == {} and st.replan_events[-1]["trigger"] == "budget_guard"


def test_findings_guard_fails_closed(monkeypatch):
    st = ReviewState(run_id="t")
    st.budget.max_tokens, st.budget.used_tokens = 10_000, 5_000
    monkeypatch.setattr(graph, "draft_findings", lambda *a, **k: (_ for _ in ()).throw(AssertionError("LLM called")))
    graph.node_findings(st)
    assert st.scratch["llm_failures"][0]["node"] == "findings"
    assert graph.node_finalize(st)["terminal_status"] == "no_conclusion"


def test_rewrite_loop_counts_attempts_not_changes():
    st = ReviewState(run_id="t")
    st.findings = [_finding("F01", "rejected")]
    assert graph.route_after_verify(st) == "rewrite"
    st.scratch["rewrite_attempts"] = st.budget.max_replans_per_gap        # 재작성이 매번 실패·동일해도 3회에서 멈춘다
    assert graph.route_after_verify(st) == "gate"
