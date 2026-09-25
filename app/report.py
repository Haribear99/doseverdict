"""
검토 메모 — 한 번의 실행(ReviewState)을 사람이 읽는 마크다운으로 내보낸다. UI 다운로드와 CLI `--report`가 같은 함수를 쓴다(LLM 호출 없음).

구성: 요약 → 기권(결론 보류) → 결함 finding(근거·수정안) → 보류 → 재계획 이벤트 → 도구 호출 요약 → 토큰 원장 → 감사 메타.
판정 권한 표기: 수치 판정은 도구, 인용은 검증기, 승인은 사람 — 메모는 결론이 아니라 검토 초안이다.
"""
from __future__ import annotations

from collections import Counter

from app.schema.trial_schema import Finding, ReviewState

_VS = {"verified": "검증", "held": "보류", "rejected": "기각", "pending": "대기"}
_TRIGGER = {
    "citation_held": "인용 근거 불충분 → 보류", "citation_rejected": "인용 기각 → 재작성", "evidence_reselected": "근거 재선택(로컬 NLI)",
    "held_research": "보류 finding 표적 재검색", "invariant_tcr_claim": "LLM의 TCR 판정 보류(불변식)", "invariant_conflict_abstain": "Reviewer 상충 → 기권",
    "prompt_injection_detected": "문서 내 지시문 탐지", "source_version_conflict": "폐기 문서 인용 → 최신본 기준", "tool_failure": "도구 실패",
    "tool_fallback": "대체 소스 조회", "budget_guard": "호출 전 예산 가드", "llm_output_failure": "구조화 출력 실패 → 결론 없음",
}


def _cite(rs: ReviewState, f: Finding) -> list[str]:
    out = []
    for eid in f.evidence_ids:
        e = rs.evidence.get(eid)
        if e:
            src = " · ".join(x for x in (e.authority, e.document_title or "", e.section or "", e.version_date or "") if x)
            out.append(f"  - `{eid}` {src}: “{(e.quote or '')[:260].strip()}…”")
    return out


def _finding_block(rs: ReviewState, f: Finding) -> list[str]:
    lines = [f"### {f.finding_id} · {f.category} · {f.severity.value} · {_VS.get(f.verifier_status, f.verifier_status)}",
             f"- **원문**: “{f.protocol_span.text.strip()}”"]
    if f.verdict == "abstain":
        lines.append(f"- **기권 사유**: {f.abstain_reason}")
    lines.append(f"- **프로토콜 사실**: {f.protocol_fact or f.claim}")
    if f.evidence_fact:
        lines.append(f"- **근거 사실**: {f.evidence_fact}")
    cites = _cite(rs, f)
    if cites:
        lines += ["- **근거**:"] + cites
    if f.suggested_patch:
        lines.append(f"- **수정안**: {f.suggested_patch}")
    if f.required_additional_data:
        lines.append("- **요청 자료**: " + "; ".join(f.required_additional_data))
    lines.append(f"- 검증기: {f.verifier_note or '-'} · 사람 결정: {f.human_status.value if f.human_status else '대기'}")
    return lines + [""]


def render_memo(rs: ReviewState) -> str:
    ip = rs.trial.study.investigational_product
    vs = Counter(f.verifier_status for f in rs.findings)
    abst = [f for f in rs.findings if f.verdict == "abstain"]
    defects = [f for f in rs.findings if f.verdict == "defect" and f.verifier_status == "verified"]
    held = [f for f in rs.findings if f.verdict == "defect" and f.verifier_status != "verified"]
    ok_tools = sum(1 for c in rs.tool_log if c.ok)
    lines = [f"# DoseVerdict 검토 메모 — {rs.trial.study.title or rs.run_id}", "",
             "> 의사결정지원 초안이다. 수치 판정은 계산 도구, 인용은 검증기(NLI·규범 강도 규칙), 최종 결정은 사람이 한다.", "",
             "## 요약", "",
             f"- 시험약: {ip.name or '-'} · 표적: {ip.target or '-'} · 대상국: {', '.join(rs.trial.study.countries) or '-'}",
             f"- finding {len(rs.findings)}건: 검증 {vs.get('verified', 0)} · 보류 {vs.get('held', 0)} · 기각 {vs.get('rejected', 0)} · 기권 {len(abst)}",
             f"- 도구 호출 {len(rs.tool_log)}회(성공 {ok_tools}) · 근거 {len(rs.evidence)}건 · 토큰 {rs.budget.used_tokens:,} · 상태 {rs.terminal_status}",
             ""]
    if rs.unavailable_axes:
        lines += ["- 근거 미확보 축: " + " / ".join(rs.unavailable_axes), ""]
    if abst:
        lines += ["## 결론 보류(기권)", ""] + [x for f in abst for x in _finding_block(rs, f)]
    if defects:
        lines += ["## 결함(검증된 인용)", ""] + [x for f in defects for x in _finding_block(rs, f)]
    if held:
        lines += ["## 보류·기각(사람 검토 필요)", ""] + [x for f in held for x in _finding_block(rs, f)]
    ev = [e for e in rs.replan_events if e.get("trigger")]
    if ev:
        lines += ["## 재계획 이벤트", "", "| 트리거 | 대상 | 내용 |", "|---|---|---|"]
        for e in ev:
            tgt = e.get("finding_id") or e.get("node") or ", ".join(e.get("tasks", [])) or "-"
            body = e.get("action") or e.get("result") or e.get("reason") or ""
            lines.append(f"| {_TRIGGER.get(e['trigger'], e['trigger'])} | {tgt} | {str(body)[:160].replace('|', '/')} |")
        lines.append("")
    by_tool = Counter((c.tool, c.ok) for c in rs.tool_log)
    lines += ["## 도구 호출", "", "| 도구 | 성공 | 실패 |", "|---|---|---|"]
    for tool in sorted({t for t, _ in by_tool}):
        lines.append(f"| `{tool}` | {by_tool[(tool, True)]} | {by_tool[(tool, False)]} |")
    lines += ["", "## 토큰 원장(게이트웨이 usage.total_tokens)", "", "| 노드 | 토큰 |", "|---|---|"]
    lines += [f"| {n} | {t:,} |" for n, t in rs.budget.by_node.items()] + [f"| **합계** | **{rs.budget.used_tokens:,}** / 상한 {rs.budget.max_tokens:,} |", ""]
    if rs.audit:
        lines += ["## 감사 메타", "", f"- run `{rs.run_id}` · 모델 {rs.audit.models} · 코퍼스 {rs.audit.corpus_manifest_id}",
                  f"- 승인자 {rs.audit.approved_by or '-'} · 승인 시각 {rs.audit.approved_at or '-'} · 프롬프트 해시 {len(rs.audit.prompt_hashes)}개", ""]
    return "\n".join(lines)
