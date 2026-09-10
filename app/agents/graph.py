"""
DoseVerdict 상태 그래프 (LangGraph 1.2).

compile → plan → tools → arena → findings → verify ─┬(기각 있고 재계획 여유)→ rewrite → verify
                                                     └→ gate(interrupt: 사람 승인) → finalize
종료 조건: 예산 초과 / Gap당 재계획 3회 / 결론 없음이 기본값.
LLM 호출은 GatewayClient 하나로만 나가며 감사로그(logs/*.jsonl)에 전부 남는다.
"""
from __future__ import annotations

import hashlib
import json
import os
import sqlite3
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt

from app.agents.compiler import compile_protocol
from app.agents.findings import draft_findings, rewrite_rejected, verify_findings
from app.agents.nodes import execute_tasks
from app.agents.planner import build_task_dag, plan_questions
from app.agents.reviewers import run_arena
from app.llm.client import GatewayClient, model_for
from app.schema.trial_schema import AuditMeta, Budget, HumanStatus, ReviewState

ROOT = Path(__file__).resolve().parents[2]
_gc: GatewayClient | None = None


def gateway() -> GatewayClient:
    global _gc
    if _gc is None:
        _gc = GatewayClient(audit_path=os.getenv("DV_AUDIT_LOG", str(ROOT / "logs" / "runs.jsonl")))
    return _gc


def _add_tokens(state: ReviewState, meta: dict[str, Any]) -> None:
    u = meta.get("usage") or {}
    state.budget.used_tokens += int(u.get("total_tokens") or 0)
    if meta.get("prompt_sha256") and state.audit:
        state.audit.prompt_hashes.append(meta["prompt_sha256"])


# ----------------------------------------------------------------- nodes
def node_compile(state: ReviewState) -> dict[str, Any]:
    if state.scratch.get("precompiled"):   # 사전 컴파일된 스키마(재실행·평가 캐시)면 LLM 호출 생략
        return {"trial": state.trial}
    ts, meta = compile_protocol(gateway(), state.raw_protocol_text, purpose=f"{state.run_id}:compile")
    state.trial = ts
    _add_tokens(state, meta)
    return {"trial": ts, "budget": state.budget, "audit": state.audit}


def node_plan(state: ReviewState) -> dict[str, Any]:
    tasks, unavailable = build_task_dag(state.trial)
    qs, meta = plan_questions(gateway(), state.trial, tasks, purpose=f"{state.run_id}:plan")
    _add_tokens(state, meta)
    state.replan_events.append({"event": "plan", "n_tasks": len(tasks), "unavailable": unavailable, "at": datetime.now().isoformat()})
    return {"tasks": tasks, "unavailable_axes": unavailable, "review_questions": qs, "trial": state.trial, "budget": state.budget, "replan_events": state.replan_events}


def node_tools(state: ReviewState) -> dict[str, Any]:
    execute_tasks(state)
    failed = [t.task_id for t in state.tasks if t.status == "failed"]
    if failed:
        state.replan_events.append({"trigger": "tool_failure", "tasks": failed, "action": "근거 미확보로 표기, 대체 소스 없음"})
    return {"tasks": state.tasks, "evidence": state.evidence, "tool_log": state.tool_log, "scratch": state.scratch, "budget": state.budget, "replan_events": state.replan_events}


def node_arena(state: ReviewState) -> dict[str, Any]:
    if state.budget.exhausted():
        state.terminal_status = "no_conclusion"
        return {"terminal_status": "no_conclusion"}
    usage = run_arena(gateway(), state, purpose=f"{state.run_id}:arena")
    for u in usage.values():
        _add_tokens(state, {"usage": u})
    return {"scratch": state.scratch, "budget": state.budget}


def node_findings(state: ReviewState) -> dict[str, Any]:
    meta = draft_findings(gateway(), state, purpose=f"{state.run_id}:findings")
    _add_tokens(state, meta)
    return {"findings": state.findings, "budget": state.budget, "scratch": state.scratch}


def node_verify(state: ReviewState) -> dict[str, Any]:
    events = verify_findings(state)
    for ev in events:
        state.replan_events.append(ev | {"at": datetime.now().isoformat()})
    return {"findings": state.findings, "replan_events": state.replan_events}


def route_after_verify(state: ReviewState) -> str:
    rejected = [f for f in state.findings if f.verifier_status == "rejected"]
    replans = sum(1 for e in state.replan_events if e.get("trigger") == "citation_rejected" and e.get("after"))
    if rejected and replans < state.budget.max_replans_per_gap and not state.budget.exhausted():
        return "rewrite"
    return "gate"


def node_rewrite(state: ReviewState) -> dict[str, Any]:
    n = rewrite_rejected(gateway(), state, purpose=f"{state.run_id}:rewrite")
    state.budget.used_tokens += 400 * n
    return {"findings": state.findings, "replan_events": state.replan_events, "budget": state.budget}


def node_gate(state: ReviewState) -> dict[str, Any]:
    """Human Approval Gate — interrupt로 멈추고 사람의 결정(dict: finding_id → approved/rejected/on_hold, approver)을 기다린다."""
    for f in state.findings:
        if f.verifier_status in ("rejected", "held"):
            f.human_status = HumanStatus.on_hold
    state.terminal_status = "awaiting_human"
    decision = interrupt({"run_id": state.run_id, "findings": [f.model_dump() for f in state.findings], "budget": state.budget.model_dump()})
    approver = decision.get("approver", "unknown")
    for f in state.findings:
        st = decision.get("decisions", {}).get(f.finding_id)
        if st in HumanStatus.__members__:
            f.human_status = HumanStatus(st)
    if state.audit:
        state.audit.approved_by = approver
        state.audit.approved_at = datetime.now().astimezone().isoformat()
    return {"findings": state.findings, "audit": state.audit, "terminal_status": "completed"}


def node_finalize(state: ReviewState) -> dict[str, Any]:
    if state.terminal_status != "completed":
        state.terminal_status = "no_conclusion" if state.budget.exhausted() else state.terminal_status
    return {"terminal_status": state.terminal_status}


# ----------------------------------------------------------------- graph
def build_graph(checkpointer=None):
    g = StateGraph(ReviewState)
    g.add_node("compile", node_compile)
    g.add_node("plan", node_plan)
    g.add_node("tools", node_tools)
    g.add_node("arena", node_arena)
    g.add_node("findings", node_findings)
    g.add_node("verify", node_verify)
    g.add_node("rewrite", node_rewrite)
    g.add_node("gate", node_gate)
    g.add_node("finalize", node_finalize)
    g.add_edge(START, "compile")
    g.add_edge("compile", "plan")
    g.add_edge("plan", "tools")
    g.add_edge("tools", "arena")
    g.add_conditional_edges("arena", lambda s: "finalize" if s.terminal_status == "no_conclusion" else "findings", {"finalize": "finalize", "findings": "findings"})
    g.add_edge("findings", "verify")
    g.add_conditional_edges("verify", route_after_verify, {"rewrite": "rewrite", "gate": "gate"})
    g.add_edge("rewrite", "verify")
    g.add_edge("gate", "finalize")
    g.add_edge("finalize", END)
    return g.compile(checkpointer=checkpointer or MemorySaver())


def new_state(protocol_text: str, run_id: str | None = None, token_budget: int | None = None) -> ReviewState:
    run_id = run_id or f"run-{datetime.now():%Y%m%d-%H%M%S}-{uuid.uuid4().hex[:6]}"
    budget = Budget(max_tokens=token_budget or int(os.getenv("DV_RUN_TOKEN_BUDGET", "150000")))
    audit = AuditMeta(run_id=run_id, models={r: model_for(r) for r in ("planner", "reviewer", "extract", "bulk")},
                      corpus_manifest_id="MANIFEST-2026-09-11")
    audit.prompt_hashes.append("protocol:" + hashlib.sha256(protocol_text.encode()).hexdigest()[:16])
    return ReviewState(run_id=run_id, raw_protocol_text=protocol_text, budget=budget, audit=audit)


def sqlite_checkpointer(path: str | None = None) -> SqliteSaver:
    p = path or str(ROOT / "logs" / "checkpoints.sqlite")
    Path(p).parent.mkdir(parents=True, exist_ok=True)
    return SqliteSaver(sqlite3.connect(p, check_same_thread=False))


def run_until_gate(protocol_text: str, *, run_id: str | None = None, checkpointer=None, on_step=None, precompiled=None) -> tuple[Any, dict[str, Any], ReviewState]:
    """그래프를 Human Gate까지 실행. 반환: (graph, config, 현재 상태). on_step(node_name, state_dict)로 UI 갱신. precompiled=TrialSchema면 compile 생략."""
    graph = build_graph(checkpointer)
    state = new_state(protocol_text, run_id)
    if precompiled is not None:
        state.trial = precompiled
        state.scratch["precompiled"] = True
    config = {"configurable": {"thread_id": state.run_id}}
    for chunk in graph.stream(state, config, stream_mode="updates"):
        for node, upd in chunk.items():
            if on_step:
                on_step(node, upd)
    snap = graph.get_state(config)
    return graph, config, ReviewState.model_validate(snap.values)


def resume_with_decision(graph, config, decisions: dict[str, str], approver: str) -> ReviewState:
    for _ in graph.stream(Command(resume={"decisions": decisions, "approver": approver}), config, stream_mode="updates"):
        pass
    return ReviewState.model_validate(graph.get_state(config).values)
