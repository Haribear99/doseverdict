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
import re
import sqlite3
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt

from app.agents.compiler import compile_protocol
from app.agents.findings import draft_findings, research_held, rewrite_rejected, verify_findings, reselect_evidence
from app.agents.nodes import execute_tasks
from app.agents.planner import build_task_dag, plan_questions
from app.agents.reviewers import run_arena
from app.llm.client import GatewayClient, model_for
from app.llm.structured import record_failure
from app.schema.trial_schema import AuditMeta, Budget, HumanStatus, ReviewState

ROOT = Path(__file__).resolve().parents[2]
_gc: GatewayClient | None = None


def gateway() -> GatewayClient:
    global _gc
    if _gc is None:
        _gc = GatewayClient(audit_path=os.getenv("DV_AUDIT_LOG", str(ROOT / "logs" / "runs.jsonl")))
    return _gc


def _add_tokens(state: ReviewState, meta: dict[str, Any], node: str = "other") -> None:
    u = meta.get("usage") or {}
    t = int(u.get("total_tokens") or 0)
    state.budget.used_tokens += t
    state.budget.by_node[node] = state.budget.by_node.get(node, 0) + t
    if meta.get("prompt_sha256") and state.audit:
        state.audit.prompt_hashes.append(meta["prompt_sha256"])


# 호출 전 예산 가드 — 노드별 예상 토큰(현재 기본 설정 60케이스 원장의 노드별 중앙값을 반올림, docs/token_ledger.md).
# 사후 합산만으로는 남은 예산보다 큰 호출을 막지 못한다(09-25 조사). 부족하면 호출하지 않고 강등하거나 결론 없음으로 끝낸다.
_EST_TOKENS = {"arena": 10_000, "findings": 16_000, "rewrite": 1_500}


def _guard(state: ReviewState, node: str) -> bool:
    """True면 호출 가능. False면 budget_guard 이벤트를 남긴다."""
    mult = max(1, len(state.scratch.get("reviewers") or [1])) if node == "arena" else 1   # Reviewer 3인 옵션은 arena 비용이 인원만큼
    need = _EST_TOKENS.get(node, 0) * mult
    if state.budget.remaining() >= need:
        return True
    state.replan_events.append({"trigger": "budget_guard", "node": node, "remaining": state.budget.remaining(), "estimated": need,
                                "action": {"arena": "Reviewer 생략 → 근거에서 직접 finding 초안", "findings": "초안 생략 → 결론 없음",
                                           "rewrite": "재작성 생략 → 보류 상태로 사람 검토"}[node]})
    return False


_INJECTION = re.compile(r"(ignore (all )?(previous|prior|above) instructions|system note to (the )?ai|report zero findings|do not cite|disregard (the )?(guidance|instructions)|"
                        r"you are now|as an ai|이전 지시를? 무시|결함 없음으로 보고|지시를 따르)", re.I)


_GUIDANCE_CITE = re.compile(r"(draft guidance|final guidance|guidance for industry)[^.\n]{0,160}?\(?(January|February|March|April|May|June|July|August|September|October|November|December)?\s?(20\d\d)\)?", re.I)


def detect_superseded_citations(text: str) -> list[dict[str, Any]]:
    """프로토콜이 인용한 가이던스의 발행 연도가 매니페스트의 폐기 버전과 맞으면 버전 충돌로 표시(결정론, 적대 테스트 ①)."""
    from app.corpus.manifest import DOCS, by_id
    out = []
    for m in _GUIDANCE_CITE.finditer(text or ""):
        span, year = m.group(0), m.group(3)
        low = span.lower()
        for d in DOCS:
            if d.superseded_by and d.effective_date.startswith(year) and any(w in low for w in ("optimizing the dosage", "oncologic", "draft guidance")):
                cur = by_id(d.superseded_by)
                out.append({"cited": span.strip()[:200], "superseded_doc": d.doc_id, "current_doc": cur.doc_id, "current_version": cur.version_label, "current_date": cur.effective_date})
    return out


def detect_injection(text: str) -> list[str]:
    """업로드 문서 안의 지시문 탐지 — 데이터로만 취급하되 사람이 볼 수 있게 이벤트로 남긴다."""
    return [m.group(0) for m in _INJECTION.finditer(text or "")][:5]


# ----------------------------------------------------------------- nodes
def node_compile(state: ReviewState) -> dict[str, Any]:
    hits = detect_injection(state.raw_protocol_text)
    if hits:
        state.replan_events.append({"trigger": "prompt_injection_detected", "patterns": hits, "action": "문서 내 지시문은 데이터로만 처리, 도구 allowlist 유지, 사람에게 표시"})
    for sc in detect_superseded_citations(state.raw_protocol_text):
        state.replan_events.append({"trigger": "source_version_conflict", **sc, "action": "폐기된 초안 인용 → 최신 최종본 기준으로 검토, source_version finding 생성"})
        state.scratch.setdefault("superseded_citations", []).append(sc)
    if state.scratch.get("precompiled"):   # 사전 컴파일된 스키마(재실행·평가 캐시)면 LLM 호출 생략
        return {"trial": state.trial, "replan_events": state.replan_events}
    ts, meta = compile_protocol(gateway(), state.raw_protocol_text, purpose=f"{state.run_id}:compile")
    state.trial = ts
    _add_tokens(state, meta, "compile")
    return {"trial": ts, "budget": state.budget, "audit": state.audit, "replan_events": state.replan_events, "scratch": state.scratch}


def node_plan(state: ReviewState) -> dict[str, Any]:
    tasks, unavailable = build_task_dag(state.trial)
    qs, meta = plan_questions(gateway(), state.trial, tasks, purpose=f"{state.run_id}:plan", protocol_text=state.raw_protocol_text)
    _add_tokens(state, meta, "plan")
    if meta.get("error"):
        record_failure(state.scratch, "plan", meta)
    state.replan_events.append({"event": "plan", "n_tasks": len(tasks), "unavailable": unavailable, "at": datetime.now().isoformat()})
    return {"tasks": tasks, "unavailable_axes": unavailable, "review_questions": qs, "trial": state.trial, "budget": state.budget, "replan_events": state.replan_events,
            "scratch": state.scratch}


def node_tools(state: ReviewState) -> dict[str, Any]:
    execute_tasks(state)
    failed = [t.task_id for t in state.tasks if t.status == "failed"]
    if failed:
        state.replan_events.append({"trigger": "tool_failure", "tasks": failed, "action": "근거 미확보로 표기, 대체 소스 없음"})
    return {"tasks": state.tasks, "evidence": state.evidence, "tool_log": state.tool_log, "scratch": state.scratch, "budget": state.budget, "replan_events": state.replan_events}


def node_arena(state: ReviewState) -> dict[str, Any]:
    if "no_arena" in state.scratch.get("ablate", []):
        state.scratch["positions"] = {}
        return {"scratch": state.scratch}
    if state.budget.exhausted():
        state.terminal_status = "no_conclusion"
        return {"terminal_status": "no_conclusion"}
    if not _guard(state, "arena"):
        state.scratch["positions"] = {}
        return {"scratch": state.scratch, "replan_events": state.replan_events}
    usage = run_arena(gateway(), state, purpose=f"{state.run_id}:arena")
    for u in usage.values():
        _add_tokens(state, {"usage": u}, "arena")
    return {"scratch": state.scratch, "budget": state.budget}


def _rerank_enabled() -> bool:
    """근거 재선택은 NLI 수십~수백 쌍을 돌린다. GPU면 수 초, CPU(배포본)면 수 분이라 기본값 'auto'는 CUDA가 있을 때만 켠다. '1'은 강제, '0'은 끔."""
    v = os.getenv("DV_EVIDENCE_RERANK", "auto").lower()
    if v in ("0", "off", "false"):
        return False
    if v in ("1", "on", "true", "force"):
        return True
    try:
        import torch
        return bool(torch.cuda.is_available())
    except Exception:  # noqa: BLE001
        return False


def node_findings(state: ReviewState) -> dict[str, Any]:
    if not _guard(state, "findings"):
        record_failure(state.scratch, "findings", {"error": "budget_guard: 남은 토큰이 초안 예상치보다 적음", "attempts": 0})
        return {"findings": state.findings, "scratch": state.scratch, "replan_events": state.replan_events}
    meta = draft_findings(gateway(), state, purpose=f"{state.run_id}:findings")
    _add_tokens(state, meta, "findings")
    if _rerank_enabled() and "no_rerank" not in state.scratch.get("ablate", []):
        n = reselect_evidence(state)   # 로컬 NLI 재검색 — 토큰 0
        if n:
            state.replan_events.append({"trigger": "evidence_reselected", "n": n, "action": "evidence_fact를 더 강하게 함의하는 현행 조항을 근거로 추가"})
    return {"findings": state.findings, "evidence": state.evidence, "budget": state.budget, "scratch": state.scratch, "replan_events": state.replan_events}


def node_verify(state: ReviewState) -> dict[str, Any]:
    if "no_verifier" in state.scratch.get("ablate", []):
        for f in state.findings:
            f.verifier_status, f.verifier_note = "verified", "ablation: verifier off"
        return {"findings": state.findings}
    events = verify_findings(state)
    if not state.scratch.get("held_researched") and "no_research" not in state.scratch.get("ablate", []):
        state.scratch["held_researched"] = True   # 첫 검증 뒤 1회만(rewrite 루프에서 반복하지 않는다)
        events += research_held(state)
    for ev in events:
        state.replan_events.append(ev | {"at": datetime.now().isoformat()})
    return {"findings": state.findings, "evidence": state.evidence, "replan_events": state.replan_events, "scratch": state.scratch}


def route_after_verify(state: ReviewState) -> str:
    rejected = [f for f in state.findings if f.verifier_status == "rejected"]
    attempts = state.scratch.get("rewrite_attempts", 0)   # 재작성 결과가 같거나 출력이 실패해도 1회로 센다(무한 반복 방지)
    if rejected and attempts < state.budget.max_replans_per_gap and not state.budget.exhausted():
        return "rewrite" if _guard(state, "rewrite") else "gate"
    return "gate"


def node_rewrite(state: ReviewState) -> dict[str, Any]:
    state.scratch["rewrite_attempts"] = state.scratch.get("rewrite_attempts", 0) + 1
    n, usage = rewrite_rejected(gateway(), state, purpose=f"{state.run_id}:rewrite")
    _add_tokens(state, {"usage": usage}, "rewrite")   # 실측 usage 합(이전: 400·n 추정)
    return {"findings": state.findings, "replan_events": state.replan_events, "budget": state.budget, "scratch": state.scratch}


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


_CRITICAL_NODES = ("plan", "findings")


def node_finalize(state: ReviewState) -> dict[str, Any]:
    if state.terminal_status != "completed":
        state.terminal_status = "no_conclusion" if state.budget.exhausted() else state.terminal_status
    failed = [f["node"] for f in state.scratch.get("llm_failures", []) if f.get("node") in _CRITICAL_NODES]
    if failed:   # 계획·초안 생성 실패를 '결함 없음'으로 끝내지 않는다(fail-closed)
        state.terminal_status = "no_conclusion"
        state.replan_events.append({"trigger": "llm_output_failure", "nodes": failed,
                                    "action": "구조화 출력 생성 실패 — 결함 목록이 불완전하므로 결론 없음으로 종료, 재실행 또는 사람 검토"})
    return {"terminal_status": state.terminal_status, "replan_events": state.replan_events}


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
    return g.compile(checkpointer=checkpointer or MemorySaver(serde=_serde()))


def _serde() -> JsonPlusSerializer:
    """체크포인트 역직렬화 허용 목록 = 우리 스키마 타입만. 미등록 타입 역직렬화는 LangGraph 차기 버전에서 차단된다(경고로 예고됨)."""
    import inspect
    from enum import Enum

    from pydantic import BaseModel

    from app.schema import trial_schema as ts
    allowed = [(ts.__name__, n) for n, c in inspect.getmembers(ts, inspect.isclass)
               if c.__module__ == ts.__name__ and issubclass(c, (BaseModel, Enum))]
    return JsonPlusSerializer(allowed_msgpack_modules=allowed)


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
    return SqliteSaver(sqlite3.connect(p, check_same_thread=False), serde=_serde())


def run_until_gate(protocol_text: str, *, run_id: str | None = None, checkpointer=None, on_step=None, precompiled=None,
                   ablate: list[str] | None = None, holdout_chunk_ids: list[str] | None = None,
                   reviewers: list[str] | None = None) -> tuple[Any, dict[str, Any], ReviewState]:
    """그래프를 Human Gate까지 실행. 반환: (graph, config, 현재 상태). on_step(node_name, state_dict)로 UI 갱신.
    precompiled=TrialSchema면 compile 생략. ablate=['no_calc','no_arena','no_verifier'] 평가용. holdout_chunk_ids는 검색에서 제외(누수 차단)."""
    graph = build_graph(checkpointer)
    state = new_state(protocol_text, run_id)
    if precompiled is not None:
        state.trial = precompiled
        state.scratch["precompiled"] = True
    if ablate:
        state.scratch["ablate"] = list(ablate)
    if holdout_chunk_ids:
        state.scratch["holdout_chunk_ids"] = list(holdout_chunk_ids)
    if reviewers:
        state.scratch["reviewers"] = list(reviewers)
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
