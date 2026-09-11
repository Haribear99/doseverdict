"""
DoseVerdict — Streamlit 시연 UI.

실행: .venv/Scripts/python.exe -m streamlit run app/ui/main.py  (파일명이 app.py면 패키지 app을 가린다)
화면: 상태 그래프(현재 노드 강조) · 타임라인(판단 전환 표시) · Trial Schema · 도구 호출 원문 · Evidence Card · Findings(Patch Diff) · Human Gate · Audit
그래프 실행은 동기 graph.stream() — Streamlit은 커스텀 스레드에서 st.* 호출을 지원하지 않는다.
"""
from __future__ import annotations

import difflib
import html
import json
import os
import sys
import time
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")

from app.agents.graph import gateway, resume_with_decision, run_until_gate  # noqa: E402
from app.schema.trial_schema import ReviewState  # noqa: E402

DEMOS = {
    "① 소토라십 유사 시놉시스 — 'The MTD will be selected as the RP2D.'": ROOT / "app/demo/sotorasib_synopsis.md",
    "② 같은 시험, 용량 비교 계획·라벨 기준 모니터링을 갖춘 판": ROOT / "app/demo/sotorasib_synopsis_fixed.md",
    "③ 프롬프트 인젝션이 삽입된 판 (적대 테스트)": ROOT / "app/demo/sotorasib_synopsis_injection.md",
}
NODES = ["compile", "plan", "tools", "arena", "findings", "verify", "rewrite", "gate", "finalize"]
NODE_LABEL = {"compile": "Protocol\nCompiler", "plan": "Orchestrator\n(과제 DAG)", "tools": "도구 호출\nRDKit·ChEMBL·openFDA\n시뮬·코퍼스·CT.gov",
              "arena": "Adversarial\nReview Arena", "findings": "Findings\n초안", "verify": "Citation\nVerifier", "rewrite": "재계획①\n재작성", "gate": "Human\nApproval Gate", "finalize": "완료"}

st.set_page_config(page_title="DoseVerdict", page_icon="⚖️", layout="wide")


@st.cache_resource(show_spinner="로컬 모델 예열 중(코퍼스 인덱스·NLI) — 최초 1회")
def _warm_models() -> bool:
    """컨테이너 기동 후 첫 검토가 모델 로드 시간(CPU에서 수십 초)을 물지 않도록 프로세스당 1회 미리 올린다."""
    from app.corpus.index import CorpusIndex
    from app.verify.nli import NLI_MODEL_EN, _pipeline
    CorpusIndex.get()
    _pipeline(NLI_MODEL_EN)
    return True


_warm_models()


# ----------------------------------------------------------------- helpers
def graph_dot(current: str | None, done: set[str]) -> str:
    lines = ['digraph G { rankdir=LR; node [shape=box, style="rounded,filled", fontname="Helvetica", fontsize=10];']
    for n in NODES:
        color = "#1f77b4" if n == current else ("#c7e9c0" if n in done else "#f0f0f0")
        font = "white" if n == current else "black"
        lines.append(f'"{n}" [label="{NODE_LABEL[n]}", fillcolor="{color}", fontcolor="{font}"];')
    edges = [("compile", "plan"), ("plan", "tools"), ("tools", "arena"), ("arena", "findings"), ("findings", "verify"), ("verify", "gate"), ("gate", "finalize")]
    for a, b in edges:
        lines.append(f'"{a}" -> "{b}";')
    lines.append('"verify" -> "rewrite" [style=dashed, color="#ff7f0e", label="기각"]; "rewrite" -> "verify" [style=dashed, color="#ff7f0e"];')
    lines.append("}")
    return "\n".join(lines)


def diff_html(a: str, b: str) -> str:
    sm = difflib.SequenceMatcher(None, a.split(), b.split())
    out = []
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op == "equal":
            out.append(html.escape(" ".join(a.split()[i1:i2])))
        if op in ("delete", "replace"):
            out.append(f'<del style="background:#fde0dd">{html.escape(" ".join(a.split()[i1:i2]))}</del>')
        if op in ("insert", "replace"):
            out.append(f'<ins style="background:#d9f2d9;text-decoration:none">{html.escape(" ".join(b.split()[j1:j2]))}</ins>')
    return " ".join(out)


def sev_badge(s: str) -> str:
    c = {"critical": "#b30000", "high": "#e6550d", "medium": "#fdae6b", "low": "#9ecae1"}.get(s, "#ccc")
    return f'<span style="background:{c};color:white;padding:2px 6px;border-radius:4px;font-size:12px">{s}</span>'


def init_state():
    for k, v in {"events": [], "done": set(), "current": None, "review": None, "graph": None, "config": None, "run_started": None}.items():
        st.session_state.setdefault(k, v)


init_state()

# ----------------------------------------------------------------- sidebar
with st.sidebar:
    st.title("⚖️ DoseVerdict")
    st.caption("MTD는 RP2D가 아니다 — 항암 1/2상 프로토콜의 용량 근거를 계산으로 검증하는 의사결정지원 에이전트")
    src = st.radio("입력 방식", ["예시 프로토콜", "직접 붙여넣기", "파일 업로드(.md/.txt)"])
    text = ""
    qp = st.query_params  # 실행 방법 ②: URL 파라미터 ?demo=1|2|3&autorun=1 (심사위원용 원클릭 링크)
    try:
        demo_idx = min(max(int(qp.get("demo", "1")) - 1, 0), len(DEMOS) - 1)
    except ValueError:
        demo_idx = 0
    if src == "예시 프로토콜":
        choice = st.selectbox("예시", list(DEMOS), index=demo_idx)
        p = DEMOS[choice]
        text = p.read_text(encoding="utf-8") if p.exists() else ""
    elif src == "직접 붙여넣기":
        text = st.text_area("프로토콜 시놉시스", height=240, placeholder="Protocol synopsis…")
    else:
        up = st.file_uploader("파일", type=["md", "txt"])
        if up:
            text = up.read().decode("utf-8", errors="replace")
    budget = st.number_input("run 토큰 상한", 20000, 300000, int(os.getenv("DV_RUN_TOKEN_BUDGET", "150000")), step=10000)
    three = st.checkbox("Reviewer 3인(규제·시험기관·환자) — 토큰 약 2배", value=False,
                        help="기본은 규제 Reviewer 1인. 본평가에서 3인은 토큰 48%를 쓰고 규범 결함 탐지 기여가 측정되지 않았다.")
    run = st.button("🔍 검토 실행", type="primary", disabled=not text.strip(), use_container_width=True)
    cached_path = (ROOT / "app/demo/results" / f"demo{demo_idx + 1}.json") if src == "예시 프로토콜" else None
    show_cached = st.button("⚡ 저장된 결과 즉시 보기 (LLM 호출 없음)", disabled=not (cached_path and cached_path.exists()), use_container_width=True,
                            help="같은 예시를 기본 설정으로 실행해 둔 결과(app/demo/results). 배포본(CPU)에서 3분을 기다리지 않아도 된다. 실행 방법 ③.")
    if qp.get("cached") == "1" and cached_path and cached_path.exists() and st.session_state.get("review") is None and not st.session_state.get("cached_done"):
        st.session_state["cached_done"] = True
        show_cached = True
    if qp.get("autorun") == "1" and text.strip() and st.session_state.get("review") is None and not st.session_state.get("autorun_done"):
        st.session_state["autorun_done"] = True
        run = True
    st.divider()
    st.markdown("**모델**  \n" + "  \n".join(f"`{r}` → `{os.getenv(e, d)}`" for r, e, d in
                                          [("planner", "DV_MODEL_PLANNER", "gpt-5.6-sol"), ("reviewer", "DV_MODEL_REVIEWER", "gpt-5.6-sol"), ("extract", "DV_MODEL_EXTRACT", "gpt-5.6-terra")]))
    st.caption("판정 권한: 계산·규칙은 도구, 최종 승인은 사람. LLM은 구조화·가설·문장 초안만.")

# ----------------------------------------------------------------- run
top = st.container()
if show_cached and cached_path:
    rs0 = ReviewState.model_validate_json(cached_path.read_text(encoding="utf-8"))
    st.session_state.update({"events": [f"저장된 실행 결과 로드 — run_id `{rs0.run_id}`, {rs0.budget.used_tokens:,} 토큰, 도구 {rs0.budget.used_tool_calls}회 (LLM 재호출 없음)"]
                             + [f"재계획 이벤트: {e}" for e in rs0.replan_events[:6]],
                             "done": set(NODES[:NODES.index("gate")]), "current": "gate", "review": rs0, "graph": None, "config": None, "run_started": time.perf_counter()})
    run = False
graph_box = top.empty()
timeline = st.container()

if run:
    st.session_state.update({"events": [], "done": set(), "current": None, "review": None, "run_started": time.perf_counter()})
    os.environ["DV_RUN_TOKEN_BUDGET"] = str(budget)
    status = timeline.status("에이전트 실행 중…", expanded=True)

    def on_step(node: str, upd: dict):
        t = time.perf_counter() - st.session_state.run_started
        st.session_state.done.add(node)
        nxt = NODES[NODES.index(node) + 1] if node in NODES and NODES.index(node) + 1 < len(NODES) else None
        st.session_state.current = nxt
        msg = f"{t:5.1f}s  **{node}** 완료"
        if node == "compile":
            inj = [e for e in upd.get("replan_events", []) if e.get("trigger") == "prompt_injection_detected"]
            if inj:
                msg += f" — **🛡️ 프롬프트 인젝션 탐지 {inj[0]['patterns']} → 데이터로만 처리**"
        if node == "plan":
            msg += f" — 과제 {len(upd.get('tasks', []))}개, 근거 미확보 축 {len(upd.get('unavailable_axes', []))}개"
        if node == "tools":
            msg += f" — 도구 호출 {len(upd.get('tool_log', []))}회, 근거 {len(upd.get('evidence', {}))}건"
        if node == "findings":
            fs = upd.get("findings", [])
            rs_ev = [e for e in upd.get("replan_events", []) if e.get("trigger") == "evidence_reselected"]
            msg += f" — finding {len(fs)}건" + (f" · 🔎 근거 재선택 {rs_ev[0]['n']}건(로컬 NLI)" if rs_ev else "") + (" · **🛑 기권(TCR 지표 의존)**" if any(getattr(f, 'verdict', '') == 'abstain' for f in fs) else "")
        if node == "verify":
            fs = upd.get("findings", [])
            rej = [f.finding_id for f in fs if f.verifier_status == "rejected"]
            msg += f" — 검증 {sum(1 for f in fs if f.verifier_status == 'verified')}/{len(fs)}" + (f" · **⛔ 인용 기각 {rej}**" if rej else "")
        if node == "rewrite":
            msg += " — **🔁 재계획①: 기각 문장 재작성**"
        st.session_state.events.append(msg)
        status.write(msg)
        graph_box.graphviz_chart(graph_dot(st.session_state.current, st.session_state.done), use_container_width=True)

    graph_box.graphviz_chart(graph_dot("compile", set()), use_container_width=True)
    try:
        g, cfg, rs = run_until_gate(text, on_step=on_step, reviewers=["regulatory", "site", "patient"] if three else ["regulatory"])
        st.session_state.update({"graph": g, "config": cfg, "review": rs, "current": "gate"})
        status.update(label=f"Human Gate 대기 — {rs.budget.used_tokens:,} 토큰, 도구 {rs.budget.used_tool_calls}회", state="complete", expanded=False)
    except Exception as e:  # noqa: BLE001
        status.update(label=f"실패: {e}", state="error")
        st.exception(e)

rs: ReviewState | None = st.session_state.review
if rs is None and not run:
    graph_box.graphviz_chart(graph_dot(None, set()), use_container_width=True)
    st.info("왼쪽에서 예시 프로토콜을 고르고 **검토 실행**을 누르세요. 약 3분이 걸리고 25~35k 토큰을 씁니다(Reviewer 3인 옵션 시 약 2배).")
    st.stop()
if rs is None:
    st.stop()

graph_box.graphviz_chart(graph_dot(st.session_state.current, st.session_state.done), use_container_width=True)
if st.session_state.events:
    with timeline.expander("타임라인 (판단 전환 지점은 굵게)", expanded=False):
        for m in st.session_state.events:
            st.markdown("- " + m)

# ----------------------------------------------------------------- tabs
tabs = st.tabs(["Findings", "Human Gate", "Evidence Cards", "도구 호출", "Trial Schema", "Audit"])

with tabs[0]:
    st.subheader(f"Findings {len(rs.findings)}건 — 검증 {sum(1 for f in rs.findings if f.verifier_status == 'verified')} / 보류 {sum(1 for f in rs.findings if f.verifier_status == 'held')} / 기각 {sum(1 for f in rs.findings if f.verifier_status == 'rejected')}")
    for f in rs.findings:
        icon = {"abstain": "🛑", "defect": "⚠️", "no_issue": "✅"}[f.verdict]
        vs = {"verified": "✔ 검증", "held": "⏸ 보류", "rejected": "✖ 기각", "pending": "…"}[f.verifier_status]
        with st.expander(f"{icon} {f.finding_id} · {f.category} · {vs} · {f.severity.value}", expanded=(f.finding_id in ("F00", "F01"))):
            st.markdown(f"**원문 span**  \n> {f.protocol_span.text}")
            if f.verdict == "abstain":
                st.error(f"**기권** — {f.abstain_reason}")
            st.markdown(f"**프로토콜 사실**: {f.protocol_fact or f.claim}")
            if f.evidence_fact:
                st.markdown(f"**근거 사실**: {f.evidence_fact}")
            st.caption(f"검증기: {f.verifier_note}  ·  span 원문 일치: {f.span_verified}")
            if f.reviewer_positions:
                cols = st.columns(3)
                for c, p in zip(cols, f.reviewer_positions):
                    c.markdown(f"**{ {'regulatory': '규제', 'site': '시험기관', 'patient': '환자 부담'}[p.reviewer] }** {sev_badge(p.severity.value)}", unsafe_allow_html=True)
                    c.caption(p.position)
                if f.conflict_unresolved:
                    st.warning("Reviewer 간 중증도 2단계 이상 상충 — 합의를 강제하지 않고 그대로 전달")
            for eid in f.evidence_ids:
                e = rs.evidence.get(eid)
                if e:
                    st.markdown(f"- `{eid}` [{e.authority} · {e.applicability.value if e.applicability else '-'} · {e.norm_strength.value if e.norm_strength else '-'}] {e.quote[:220]}…")
            if getattr(f, "related_evidence_ids", None):
                st.caption("관련 조항 후보(로컬 NLI 자동 검색 · 인용 아님 · 사람 확인 필요):")
                for eid in f.related_evidence_ids:
                    e = rs.evidence.get(eid)
                    if e:
                        st.caption(f"· `{eid}` [{e.authority}] {e.quote[:160]}…")
            if f.suggested_patch:
                st.markdown("**Patch Diff**")
                st.markdown(diff_html(f.protocol_span.text, f.suggested_patch), unsafe_allow_html=True)
            if f.required_additional_data:
                st.markdown("**요청 자료**: " + " · ".join(f.required_additional_data))

with tabs[1]:
    st.subheader("Human Approval Gate — 최종 결정은 사람만")
    if rs.terminal_status == "completed":
        st.success(f"승인 완료 — {rs.audit.approved_by} @ {rs.audit.approved_at}")
    else:
        approver = st.text_input("승인자", value="reviewer@site")
        decisions = {}
        for f in rs.findings:
            default = 0 if f.verifier_status == "verified" else 2
            decisions[f.finding_id] = st.radio(f"{f.finding_id} · {f.claim[:90]}", ["approved", "rejected", "on_hold"], index=default, horizontal=True, key=f"dec_{f.finding_id}")
        if st.session_state.get("graph") is None:
            st.info("저장된 결과 보기 모드 — 승인은 라이브 실행에서만 감사로그에 기록됩니다.")
        if st.button("승인 확정 → 감사로그 기록", type="primary", disabled=st.session_state.get("graph") is None):
            rs2 = resume_with_decision(st.session_state.graph, st.session_state.config, decisions, approver)
            st.session_state.review = rs2
            st.session_state.done.update({"gate", "finalize"}); st.session_state.current = None
            st.rerun()

with tabs[2]:
    st.subheader(f"Evidence Cards {len(rs.evidence)}건 (우선순위: 1 직접측정 > 2 문서 규범 > 3 파생 지표)")
    for e in rs.evidence.values():
        st.markdown(f"**{e.evidence_id}** · {e.kind} · {e.authority} · {e.section or ''} · {e.applicability.value if e.applicability else '-'} · 규범강도 {e.norm_strength.value if e.norm_strength else '-'} · tier {e.priority_tier} · {e.version_date or ''}")
        st.caption(e.quote)

with tabs[3]:
    st.subheader(f"도구 호출 {len(rs.tool_log)}회 — 요청·응답 요약 (실패도 관측값)")
    for c in rs.tool_log:
        st.markdown(f"{'✅' if c.ok else '❌'} `{c.tool_call_id}` **{c.tool}** {c.latency_s}s  \n args: `{json.dumps(c.args, ensure_ascii=False)[:160]}`  \n {c.result_summary or c.error or ''}")
    st.markdown("**과제 DAG**")
    st.table([{"task": t.task_id, "status": t.status, "tools": ", ".join(t.tools), "depends": ", ".join(t.depends_on)} for t in rs.tasks])
    if rs.unavailable_axes:
        st.warning("근거 미확보 축: " + " / ".join(rs.unavailable_axes))

with tabs[4]:
    st.json(rs.trial.model_dump(exclude_none=True))

with tabs[5]:
    tot = gateway().audit_totals()
    st.markdown(f"**run** `{rs.run_id}` · 토큰 {rs.budget.used_tokens:,}/{rs.budget.max_tokens:,} · 도구 {rs.budget.used_tool_calls}/{rs.budget.max_tool_calls} · 팀 잔여 쿼터(헤더) {tot.get('last_quota')}")
    st.json({"models": rs.audit.models if rs.audit else {}, "corpus_manifest": rs.audit.corpus_manifest_id if rs.audit else None,
             "prompt_hashes": rs.audit.prompt_hashes if rs.audit else [], "replan_events": rs.replan_events, "terminal_status": rs.terminal_status})
