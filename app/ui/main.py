"""
DoseVerdict — Streamlit 시연 UI.

실행: .venv/Scripts/python.exe -m streamlit run app/ui/main.py  (파일명이 app.py면 패키지 app을 가린다)
화면: 상태 그래프(현재 노드 강조) · 타임라인(판단 전환 표시) · Trial Schema · 도구 호출 원문 · Evidence Card · Findings(Patch Diff) · Human Gate · Audit · 후향 검증
그래프 실행은 동기 graph.stream() — Streamlit은 커스텀 스레드에서 st.* 호출을 지원하지 않는다.
"""
from __future__ import annotations

import difflib
import html
import json
import os
import sys
import threading
import time
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")

from app.agents.graph import resume_with_decision, run_until_gate  # noqa: E402
from app.schema.trial_schema import ReviewState  # noqa: E402
from app.report import render_memo  # noqa: E402
from app.ui import tokens  # noqa: E402

DEMOS = {
    "① 소토라십 유사 시놉시스 — 'The MTD will be selected as the RP2D.'": ROOT / "app/demo/sotorasib_synopsis.md",
    "② 같은 시험, 용량 비교 계획·라벨 기준 모니터링을 갖춘 판": ROOT / "app/demo/sotorasib_synopsis_fixed.md",
    "③ 프롬프트 인젝션이 삽입된 판 (적대 테스트)": ROOT / "app/demo/sotorasib_synopsis_injection.md",
    "④ 다른 약물: 로를라티닙(ALK) — 매핑 표 밖 약물, DB·라벨 자동 조회": ROOT / "app/demo/lorlatinib_synopsis_fixed.md",
    "⑤ 미승인 후보 DV-505(가상) — 프로토콜 보고 PK로 계산": ROOT / "app/demo/dv505_synopsis_fixed.md",
    "⑥ 적대: 폐기된 초안 가이던스를 현행처럼 인용": ROOT / "app/demo/adversarial_superseded_guidance.md",
    "⑦ 적대: 한·미 규제 상충(식약처 의무화 주장)": ROOT / "app/demo/adversarial_kr_us_conflict.md",
    "⑧ 적대: 근거 없는 용량 주장(내부 모델링 90% 커버)": ROOT / "app/demo/adversarial_unsupported_dose.md",
}
NODES = ["compile", "plan", "tools", "arena", "findings", "verify", "rewrite", "gate", "finalize"]
NODE_LABEL = {"compile": "Protocol\nCompiler", "plan": "Orchestrator\n(과제 DAG)", "tools": "도구 호출\nRDKit·ChEMBL·openFDA\n시뮬·코퍼스·CT.gov",
              "arena": "Adversarial\nReview Arena", "findings": "Findings\n초안", "verify": "Citation\nVerifier", "rewrite": "재계획①\n재작성", "gate": "Human\nApproval Gate", "finalize": "완료"}

st.set_page_config(page_title="DoseVerdict", page_icon=":material/balance:", layout="wide")

# 색은 app/ui/tokens.py 한 곳에서 온다. 상태 4색은 .streamlit/config.toml의 green/orange/red/violetColor와 같아야 배지(:green-badge 등)와 카드 색이 일치한다.
# 형태 규칙(docs/DESIGN.md): 구분은 선으로 한다 — 카드 그림자·색 테두리 카드·알약형 칩·대문자 라벨을 쓰지 않는다. 라운드는 2px.
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Serif+KR:wght@400;600&display=swap');
:root { __VARS__ }
.dv-hero { border-top: 2px solid var(--dv-ink); padding: 1.1rem 0 0.4rem; margin-bottom: 0.6rem; }
.dv-eyebrow { font-size: 0.85rem; font-weight: 600; color: var(--dv-accent); margin: 0 0 0.4rem; }
.dv-hero h1 { font-size: clamp(1.7rem, 4.2vw, 2.5rem); line-height: 1.2; font-weight: 700; letter-spacing: -0.02em; color: var(--dv-ink); margin: 0 0 0.5rem; padding: 0; }
.dv-lede { font-size: clamp(1rem, 2.2vw, 1.12rem); color: var(--dv-ink); max-width: 46rem; line-height: 1.6; margin: 0; text-wrap: pretty; }
.dv-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); margin: 0.5rem 0 0.4rem; border-top: 1px solid var(--dv-ink); }
.dv-step { padding: 0.7rem 1.1rem 0.8rem 0; }
.dv-step + .dv-step { padding-left: 1.1rem; border-left: 1px solid var(--dv-line); }
.dv-step b { display: block; color: var(--dv-ink); margin-bottom: 0.25rem; }
.dv-step span { color: var(--dv-muted); font-size: 0.9rem; line-height: 1.55; }
.dv-step .dv-num { display: inline-block; font-variant-numeric: tabular-nums; color: var(--dv-accent); font-weight: 700; margin-right: 0.45rem; }
.dv-roles { display: grid; grid-template-columns: minmax(5.5rem, max-content) 1fr; margin: 0.5rem 0 0.4rem; border-top: 1px solid var(--dv-ink); }
.dv-role { display: contents; }
.dv-role b, .dv-role span { padding: 0.5rem 1rem 0.5rem 0; border-bottom: 1px solid var(--dv-line); }
.dv-role b { color: var(--dv-ink); }
.dv-role span { color: var(--dv-muted); font-size: 0.92rem; line-height: 1.5; }
.dv-section { font-size: 0.95rem; font-weight: 700; color: var(--dv-ink); margin: 1.8rem 0 0.1rem; }
.dv-note { color: var(--dv-muted); font-size: 0.85rem; line-height: 1.55; }
.dv-chip { display: inline-block; padding: 0.05rem 0.45rem; border-radius: 2px; font-size: 0.78rem; font-weight: 600; margin: 0 0.3rem 0.3rem 0; white-space: nowrap; border: 1px solid currentColor; }
.dv-chip.verified, .dv-chip.held, .dv-chip.rejected, .dv-chip.abstain { background: var(--dv-panel); }   /* 흰 바탕 + 상태색 글자·테두리(대비 4.5 이상) */
.dv-chip.verified { color: var(--dv-verified); }
.dv-chip.held { color: var(--dv-held-text); }
.dv-chip.rejected { color: var(--dv-rejected); }
.dv-chip.abstain { color: var(--dv-abstain); }
.dv-chip.pending, .dv-chip.cat { color: var(--dv-muted); background: transparent; border-color: var(--dv-line); }
.dv-sev { display: inline-block; padding: 0.05rem 0.45rem; border-radius: 2px; font-size: 0.75rem; font-weight: 600; border: 1px solid currentColor; margin: 0 0.3rem 0.3rem 0; }
.dv-sev.critical { color: var(--dv-sev-critical); font-weight: 800; border-width: 2px; } .dv-sev.high { color: var(--dv-sev-high); }
.dv-sev.medium { color: var(--dv-sev-medium); } .dv-sev.low { color: var(--dv-sev-low); }
.dv-quote { border-left: 2px solid var(--dv-muted); background: var(--dv-soft); padding: 0.6rem 0.9rem; margin: 0.4rem 0 0.8rem; font-family: __SERIF__;
  color: var(--dv-ink); line-height: 1.6; overflow-wrap: anywhere; font-variant-numeric: lining-nums; }
.dv-abstain-box { border-left: 5px solid var(--dv-abstain); background: var(--dv-abstain-bg); padding: 0.7rem 1rem; margin: 0.3rem 0 0.8rem; line-height: 1.55; }
.dv-abstain-box b { color: var(--dv-abstain); }
.dv-diff { line-height: 1.8; overflow-wrap: anywhere; background: var(--dv-panel); border: 1px solid var(--dv-line); border-radius: 2px; padding: 0.6rem 0.9rem; }
.dv-diff del { background: var(--dv-del-bg); color: var(--dv-rejected); }
.dv-diff ins { background: var(--dv-ins-bg); color: var(--dv-verified); text-decoration: none; }
.dv-runhead { border-top: 2px solid var(--dv-ink); padding: 0.75rem 0 0.2rem; margin-bottom: 0.2rem; }
.dv-runmeta { font-size: 0.8rem; color: var(--dv-muted); margin: 0 0 0.25rem; }
.dv-runtitle { font-size: clamp(1.4rem, 3vw, 2rem); font-weight: 700; letter-spacing: -0.015em; line-height: 1.3; color: var(--dv-ink); margin: 0 0 0.25rem; }
.dv-runsub { font-size: 0.92rem; color: var(--dv-muted); margin: 0; }
.dv-kpis { display: grid; grid-template-columns: repeat(auto-fit, minmax(96px, 1fr)); margin: 0.6rem 0 0.3rem; border-top: 1px solid var(--dv-ink); border-bottom: 1px solid var(--dv-line); }
.dv-kpi { padding: 0.5rem 0.8rem 0.55rem; }
.dv-kpi + .dv-kpi { border-left: 1px solid var(--dv-line); }
.dv-kpi.first { padding-left: 0; }
.dv-kpi-label { display: block; font-size: 0.78rem; color: var(--dv-muted); }
.dv-kpi-value { display: block; font-size: 1.3rem; font-weight: 700; color: var(--dv-ink); font-variant-numeric: tabular-nums; letter-spacing: -0.01em; }
.dv-kpi.verified .dv-kpi-value { color: var(--dv-verified); } .dv-kpi.held .dv-kpi-value { color: var(--dv-held-text); }
.dv-kpi.rejected .dv-kpi-value { color: var(--dv-rejected); } .dv-kpi.abstain .dv-kpi-value { color: var(--dv-abstain); }
.dv-kpi-sub { display: block; font-size: 0.75rem; color: var(--dv-muted); }
[data-testid="stMetric"] { border-top: 1px solid var(--dv-ink); padding: 0.5rem 0 0.2rem; }
[data-testid="stMetricValue"] { font-variant-numeric: tabular-nums; font-size: clamp(1.35rem, 2.1vw, 1.75rem); letter-spacing: -0.01em; font-weight: 700; }
[data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] * { color: var(--dv-muted); opacity: 1; }   /* Streamlit 기본 60% 불투명도를 끄고 muted(대비 5.7)로 */
[data-testid="stTable"] table { border: 0; font-variant-numeric: tabular-nums; }
[data-testid="stTable"] th, [data-testid="stTable"] td { border-left: 0; border-right: 0; border-top: 0; }
[data-testid="stTable"] thead th { border-bottom: 1px solid var(--dv-ink); color: var(--dv-muted); font-weight: 600; }
[data-testid="stMetricValue"] > div { white-space: normal; overflow: visible; text-overflow: clip; }
[data-testid="stExpander"] details { background: var(--dv-panel); }
@media (max-width: 640px) {
  .dv-hero { padding-top: 0.9rem; }
  .dv-grid { grid-template-columns: 1fr; }
  .dv-step + .dv-step { padding-left: 0; border-left: 0; border-top: 1px solid var(--dv-line); }
  .dv-kpi { padding-left: 0; }
  .dv-kpi + .dv-kpi { border-left: 0; }
}
</style>
""".replace("__VARS__", tokens.css_vars()).replace("__SERIF__", tokens.SERIF)
st.html(CSS)


def _warm() -> None:
    from app.corpus.index import CorpusIndex
    from app.verify.nli import NLI_MODEL_EN, _pipeline
    CorpusIndex.get()
    _pipeline(NLI_MODEL_EN)


@st.cache_resource(show_spinner=False)
def _warm_thread() -> threading.Thread:
    """컨테이너 기동 후 첫 검토가 모델 로드 시간(CPU에서 수십 초)을 물지 않도록 프로세스당 1회 미리 올린다.
    백그라운드 스레드라 화면·저장된 결과 보기는 예열을 기다리지 않는다. 라이브 실행만 시작 전에 join한다."""
    t = threading.Thread(target=_warm, name="dv-warm", daemon=True)
    t.start()
    return t


_warm_thread()


# ----------------------------------------------------------------- helpers
def graph_dot(current: str | None, done: set[str]) -> str:
    t = tokens
    font = t.SANS.replace('"', "")
    lines = [f'digraph G {{ rankdir=LR; nodesep=0.25; node [shape=box, style="filled", penwidth=0.8, margin="0.14,0.07", fontname="{font}", fontsize=10];']
    lines.append(f'bgcolor="transparent"; edge [color="{t.MUTED}", penwidth=0.8, arrowsize=0.6, fontname="{font}", fontsize=9];')
    for n in NODES:
        # 진행 상태는 중립색으로 — 초록(검증)을 쓰면 "전 단계 검증됨"으로 읽힌다
        color = t.ACCENT if n == current else (t.SOFT if n in done else t.PANEL)
        fc = "white" if n == current else (t.INK if n in done else t.MUTED)
        border = t.ACCENT if n == current else (t.MUTED if n in done else t.LINE)
        lines.append(f'"{n}" [label="{NODE_LABEL[n]}", fillcolor="{color}", fontcolor="{fc}", color="{border}"];')
    edges = [("compile", "plan"), ("plan", "tools"), ("tools", "arena"), ("arena", "findings"), ("findings", "verify"), ("verify", "gate"), ("gate", "finalize")]
    for a, b in edges:
        lines.append(f'"{a}" -> "{b}";')
    lines.append(f'"verify" -> "rewrite" [style=dashed, color="{t.REJECTED}", fontcolor="{t.REJECTED}", label="기각"]; "rewrite" -> "verify" [style=dashed, color="{t.REJECTED}"];')
    lines.append("}")
    return "\n".join(lines)


def diff_html(a: str, b: str) -> str:
    sm = difflib.SequenceMatcher(None, a.split(), b.split())
    out = []
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op == "equal":
            out.append(html.escape(" ".join(a.split()[i1:i2])))
        if op in ("delete", "replace"):
            out.append(f'<del>{html.escape(" ".join(a.split()[i1:i2]))}</del>')
        if op in ("insert", "replace"):
            out.append(f'<ins>{html.escape(" ".join(b.split()[j1:j2]))}</ins>')
    return '<div class="dv-diff">' + " ".join(out) + "</div>"


def sev_badge(s: str) -> str:
    return f'<span class="dv-sev {html.escape(s)}">{html.escape(s)}</span>'


# 상태 표시: 기권은 verdict로, 나머지는 검증기 상태로 정한다(F00 기권은 verifier_status가 verified여도 '기권'으로 보인다).
STATUS = {"verified": ("검증", "green"), "held": ("보류", "orange"), "rejected": ("기각", "red"), "abstain": ("기권", "violet"), "pending": ("미검증", "gray")}
CATEGORY = {"dose_optimization": "용량 최적화", "safety_monitoring": "안전성 모니터링", "eligibility": "선정·제외 기준", "endpoint_ctq": "평가변수·CTQ",
            "burden": "환자 부담", "source_version": "근거 버전", "feasibility": "실행 가능성"}


REPLAN_LABEL = {"evidence_reselected": "근거 재선택", "citation_held": "인용 보류", "citation_rejected": "인용 기각", "held_research": "보류 재검색",
                "tool_fallback": "대체 조회", "prompt_injection_detected": "프롬프트 인젝션 탐지", "source_version_conflict": "근거 버전 상충",
                "budget_guard": "예산 가드", "llm_failure": "LLM 출력 실패"}


def replan_line(e: dict) -> str:
    """저장된 결과의 재계획 이벤트를 타임라인 한 줄로(dict 원문을 그대로 찍지 않는다)."""
    t = e.get("trigger")
    if not t:
        if e.get("event") == "plan":
            return f"계획 — 과제 {e.get('n_tasks')}개, 근거 미확보 축 {len(e.get('unavailable') or [])}개"
        return f"이벤트 `{e.get('event')}`"
    detail = [str(x) for x in (e.get("finding_id"), f"{e['n']}건" if "n" in e else None, e.get("reason"), e.get("action"),
                                f"결과 {e['result']}" if e.get("result") else None) if x]
    return f"재계획 이벤트: **{REPLAN_LABEL.get(t, t)}** `{t}`" + (" — " + " · ".join(d[:160] for d in detail) if detail else "")


def finding_status(f) -> str:
    return "abstain" if f.verdict == "abstain" else f.verifier_status


def status_chip(key: str) -> str:
    return f'<span class="dv-chip {key}">{STATUS[key][0]}</span>'


def section(title: str) -> None:
    st.markdown(f'<div class="dv-section">{html.escape(title)}</div>', unsafe_allow_html=True)


RESULTS = ROOT / "app/eval/data/results"


def _load_json(name: str) -> dict | None:
    p = RESULTS / name
    try:
        return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None
    except (OSError, ValueError):
        return None


def _span(vals: list[float]) -> str:
    return f"{vals[0]:.3f}" if len(vals) == 1 or min(vals) == max(vals) else f"{min(vals):.3f}–{max(vals):.3f}"


def eval_tiles() -> list[tuple[str, str, str]]:
    """평가 결과 JSON의 aggregate에서 첫 화면 타일을 만든다(수치 하드코딩 금지). 파일이 없으면 해당 타일을 뺀다."""
    base = [(n, d) for n in ("lean_v3", "lean_v3b") if (d := _load_json(f"{n}.json")) and d.get("aggregate")]
    multi = _load_json("lean_mdrug3.json")
    tiles = []
    if base:
        names = "·".join(n for n, _ in base)
        n = f"{base[0][1]['n_cases']}" + (f" × {len(base)}회 반복" if len(base) > 1 else "")
        tiles.append(("결함 위치 재현율 (span recall)", _span([d["aggregate"]["recall"] for _, d in base]),
                      f"주입 결함 문장을 finding이 가리킨 비율 · {names} · n={n}"))
        tiles.append(("근거까지 일치 (grounded recall)", _span([d["aggregate"]["grounded_recall"] for _, d in base]),
                      f"결함을 짚고 정답 규범 문서까지 인용한 비율 · {names} · n={n}"))
    if multi and multi.get("aggregate"):
        drugs = {r["case_id"].split("-")[1] for r in multi.get("rows", []) if r.get("case_id", "").count("-") >= 2}
        tiles.append(("다약물 세트 span recall", _span([multi["aggregate"]["recall"]]),
                      f"약물 {len(drugs)}종 결함 주입 변형 · lean_mdrug3 · n={multi['n_cases']}"))
    allsets = base + ([("lean_mdrug3", multi)] if multi and multi.get("aggregate") else [])
    if allsets:
        tiles.append(("인용 검증 통과율", _span([d["aggregate"]["verified_rate"] for _, d in allsets]),
                      f"검증기 통과 finding 비율 · {'·'.join(n for n, _ in allsets)}"))
    return tiles


RETRO_DESC = {"S1": "1차: 검증된 용량최적화 finding 수", "S2": "2차: 용량최적화 finding 중증도 가중합(검증+보류)", "B1": "키워드 규칙(초록, LLM 없음)",
              "B2": "승인연도(시대 교란 점검)", "B3": "축③ 라벨 규칙(승인 후 라벨 — 참고용, 누설 있음)",
              "B4": "사후 대조군: 약 이름을 준 모델 기억(도구 없음)"}


def render_retro() -> None:
    """실사례 후향 검증(사전 등록 docs/retro_prereg.md) 결과 — app/eval/data/results/retro.json이 있을 때만 수치를 보인다."""
    res = _load_json("retro.json")
    st.markdown("**실사례 후향 검증** — FDA가 최초 승인 때 용량최적화 PMR/PMC를 부과한 항암제를, 승인 전 공개된 1상 초록(약물명 마스킹)만으로 더 자주 짚는가. "
                "판정 규칙·비교 기준은 실행 전에 고정했다(`docs/retro_prereg.md`).")
    if not res:
        st.info("결과 준비 중 — `python -m app.eval.retro analyze`가 `app/eval/data/results/retro.json`을 만들면 여기에 표시된다.")
        return
    m = res.get("metrics", {})
    c1, c2, c3 = st.columns(3)
    c1.metric("표본", f"{res.get('n', 0)}건", help="사전 등록 기준으로 확보된 케이스 수")
    c2.metric("PMR 양성", f"{res.get('n_pos', 0)}건")
    if "reidentification_rate" in res:
        c3.metric("재식별률(P1 탐침)", f"{res['reidentification_rate']:.3f}", help="마스킹 입력에서 LLM이 성분명을 맞힌 비율")
    st.markdown(f"**판정(사전 규칙)**: {res.get('verdict', '—')}")
    table = [{"점수": k, "설명": RETRO_DESC[k] + (f" (n={m[k]['n']})" if "n" in m[k] else ""), "AUROC": f"{m[k]['auroc']:.3f}",
              "95% CI": f"[{m[k]['ci'][0]:.3f}, {m[k]['ci'][1]:.3f}]", "PR-AUC": f"{m[k]['pr_auc']:.3f}" if m[k].get("pr_auc") is not None else "—"}
             for k in ("S1", "S2", "B1", "B2", "B3", "B4") if k in m]
    if table:
        st.table(table)
    notes = [f"S1−{k} AUROC 차이 95% CI [{m[f'S1-{k}']['ci'][0]:.3f}, {m[f'S1-{k}']['ci'][1]:.3f}]" for k in ("B1", "B2") if f"S1-{k}" in m]
    if "S1_not_reidentified" in m:
        s = m["S1_not_reidentified"]
        notes.append(f"재식별되지 않은 부분집합(n={s['n']}, 양성 {s['n_pos']}) S1 AUROC {s['auroc']:.3f} [{s['ci'][0]:.3f}, {s['ci'][1]:.3f}]")
    if res.get("n"):
        notes.append(f"PR-AUC 무작위 기준 = 양성 비율 {res.get('n_pos', 0) / res['n']:.3f}")
    if notes:
        st.caption(" · ".join(notes) + " — 차이 CI는 기술용이며 표본이 작아 유의성 주장에 쓰지 않는다.")
    d, post = res.get("descriptive_post_hoc") or {}, res.get("reidentification_post_hoc") or {}
    if d:
        st.markdown(f"**해석(사후 기술)** — 에이전트는 {d.get('flagged_S1_ge1')}/{res.get('n')}건 모두에서 검증된 용량최적화 결함을 지적했다"
                    f"(평균 S1 양성 {d.get('mean_S1_pos')} · 음성 {d.get('mean_S1_neg')}). 지적의 정확성은 평가하지 않았고({d.get('S1_template')}/{d.get('S1_total')}건은 입력 템플릿 문장이 유발), "
                    f"결과는 판별력 없음과 구별되지 않는다 — 이 설정에서 용량 지적은 FDA의 PMR 부과를 예측하지 못했다. F00은 {d.get('f00_abstain')}/{res.get('n')}건 기권(라벨 차단·IC50 미확보 → 전형값 없이 멈춤).")
    if post or d.get("spearman_S1_B4"):
        st.caption(f"기억 오염: 사후 탐침에서 SMILES 제거 {post.get('nosmiles')}, SMILES·표적·기전 제거 {post.get('noid')}로 재식별된다 — 출판 초록은 모델 기억과 분리할 수 없다. "
                   f"S1과 기억 대조군(B4)의 Spearman ρ {(d.get('spearman_S1_B4') or ['—'])[0]}: 점수 수준의 상관은 확인되지 않았다. 다만 파이프라인이 {d.get('name_restored')}/{res.get('n')}건에서 약 이름을 스스로 복원해 검색했다 — 오염을 배제할 수 없다.")
    rows = res.get("rows", [])
    if rows:
        st.markdown("**케이스별**")
        st.dataframe([{"케이스": r.get("case_id"), "약물": r.get("generic"), "승인연도": r.get("year"), "PMR": "예" if r.get("y") else "아니오",
                       "S1": r.get("S1"), "S2": r.get("S2"), "B1": r.get("B1"), "F00": r.get("f00") or "—",
                       "재식별": {True: "예", False: "아니오"}.get(r.get("reidentified"), "—")}
                      for r in sorted(rows, key=lambda r: (-int(r.get("y") or 0), -float(r.get("S1") or 0)))],
                     hide_index=True, use_container_width=True)
        pos = [r for r in rows if r.get("y")]
        if pos:
            with st.expander(f"양성 사례 {len(pos)}건의 용량최적화 finding 원문"):
                for r in pos:
                    st.markdown(f"**{r.get('case_id')} {r.get('generic')}**")
                    for f in r.get("dose_findings") or []:
                        st.markdown(f"- {f.get('id')} [{f.get('status')}/{f.get('severity')}] {f.get('claim')}")
                    if not r.get("dose_findings"):
                        st.caption("용량최적화 finding 없음")


def render_oneshot() -> None:
    """강한 LLM 원샷 베이스라인(사전 등록 docs/oneshot_prereg.md) — app/eval/data/results/oneshot_compare.json이 있을 때만."""
    res = _load_json("oneshot_compare.json")
    if not res:
        return
    st.markdown("**같은 모델을 한 번 부르면?** — 같은 모델(gpt-6-sol)을 도구·검색·검증 없이 한 번 호출한 원샷을 합성 평가 원 20케이스에 2회 돌려 에이전트와 짝지어 비교했다.")
    rows = []
    for name, a in res.get("arms", {}).items():
        g = a["grounded_diff"]
        rows.append({"비교": name, "grounded 에이전트 / 비교": f"{a['grounded_agent']:.3f} / {a['grounded_arm']:.3f}",
                     "차이 [95% CI]": f"{g[0]:+.3f} [{g[1]:+.3f}, {g[2]:+.3f}]", "토큰/케이스 에이전트 / 비교": f"{a['tokens_agent']:,} / {a['tokens_arm']:,}",
                     "판정": a["verdict"] if name.startswith("oneshot") else "기술용(1회)"})
    st.table(rows)
    msg = "사전 등록 판정은 차이 없음 — 탐지율(span)은 원샷도 같은 수준이고 토큰은 약 8분의 1이다."
    ph = res.get("post_hoc") or {}
    if ph:
        fa, fo, sy = ph["fidelity"]["agent"], ph["fidelity"]["oneshot"], ph["symmetric_grounded"]
        pct = lambda n, d: f"{n / max(1, d):.1%}"
        msg += (f" 사후 분석(같은 인용 판정기를 양쪽에): 근거 문장이 인용 문서의 조항으로 확인된 비율은 에이전트 {pct(fa['exact'], fa['checkable'])}–{pct(fa['exact_or_nli'], fa['checkable'])}, "
                f"원샷 {pct(fo['exact'], fo['checkable'])}–{pct(fo['exact_or_nli'], fo['checkable'])}(원문 일치만–NLI 의역 포함). "
                f"같은 필터를 건 grounded 차이(원샷 − 에이전트) 원문 일치만 {sy['exact']['diff'][0]:+.3f} / NLI 포함 {sy['nli']['diff'][0]:+.3f}. 판정 NLI가 에이전트 검증기와 같은 모델이라 에이전트에 유리한 비교다.")
    st.caption(msg + " 반대로 hold-out 조건은 원샷에 유리하다(에이전트는 결함 출처 조항을 검색에서 뺀 채 평가).")


def render_abstain() -> None:
    """기권 평가(사전 등록 docs/abstain_prereg.md) — app/eval/data/results/abstain.json이 있을 때만."""
    res = _load_json("abstain.json")
    if not res:
        return
    A, B = res["A"], res["B"]
    st.markdown("**같은 모델에게 약리 판정을 물으면?** — 용량군 20개의 표적 커버리지를 도구 없이 같은 모델에게 3회씩 물었다(A: 시놉시스만, B: 도구가 쓴 PK 입력까지).")
    st.table([{"지표": "판정 보류가 정답인 용량군에서 확정 판정(1차)", "A": f"{A['definite_on_indeterminate']['mean']:.3f}", "B": f"{B['definite_on_indeterminate']['mean']:.3f}"},
              {"지표": "커버가 정답인 용량군에서 판단 보류", "A": f"{A['abstain_on_covered']['mean']:.3f}", "B": f"{B['abstain_on_covered']['mean']:.3f}"},
              {"지표": "도구 판정 일치율", "A": f"{A['agreement']['mean']:.3f}", "B": f"{B['agreement']['mean']:.3f}"}])
    M = res.get("A_mem") or {}
    cap = ("지시문에 기권 선택지를 준 조건에서, 같은 모델은 자료가 없으면 멈췄다(PK가 라벨에만 있는 약 3종은 판정 불가). "
           "정답을 같은 도구로 만들어 에이전트 일치율은 정의상 1이다(순환성) — 에이전트와의 정확도 비교가 아니다.")
    if M:
        cap += (f" 사후 조건 A′(기억·추정 권장)에서는 모두 판정했지만 도구 판정 일치율 {M['agreement']['mean']:.3f}, "
                f"라벨에만 PK가 있는 약에서 같은 질문 3회의 판정이 일치하지 않는 경우가 많았다 — 기억한 PK는 대체로 같았고(아다그라십은 Cmax 약 2배 차이) IC50·용량 외삽 가정을 매번 다시 골랐다. "
                f"에이전트의 재현성은 이 입력 규약을 코드로 고정한 데서 오며, 규약이 옳다는 근거는 아니다(ABSTAIN_REPORT 사후 절).")
    st.caption(cap)


def init_state():
    for k, v in {"events": [], "done": set(), "current": None, "review": None, "graph": None, "config": None, "run_started": None}.items():
        st.session_state.setdefault(k, v)


init_state()

# ----------------------------------------------------------------- sidebar
with st.sidebar:
    st.title("DoseVerdict")
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
    three = st.checkbox("Reviewer 3인(규제·시험기관·환자) — 토큰 약 1.3배", value=False,
                        help="기본은 규제 Reviewer 1인. 본평가에서 3인은 토큰 48%를 쓰고 규범 결함 탐지 기여가 측정되지 않았다.")
    conservative = st.checkbox("보수적 지적 모드(인용 요건 위반만 보고)", value=False,
                               help="09-30 사전 등록 A/B(docs/calibration_prereg.md): 결함 없는 프로토콜의 오경보는 줄지만(문장 특이도 0.64→0.91) "
                                    "주입 결함 탐지도 크게 준다(민감도 0.962→0.583, 판별력 Youden J 0.761→0.559로 오히려 낮아짐). 사전 규칙상 기본값으로 채택하지 않았다. 잘 쓴 최종 초안을 훑을 때만 권한다.")
    run = st.button("검토 실행", type="primary", disabled=not text.strip(), use_container_width=True)
    cached_path = (ROOT / "app/demo/results" / f"demo{demo_idx + 1}.json") if src == "예시 프로토콜" else None
    show_cached = st.button("저장된 결과 즉시 보기 (LLM 호출 없음)", disabled=not (cached_path and cached_path.exists()), use_container_width=True,
                            help="같은 예시를 기본 설정으로 실행해 둔 결과(app/demo/results). 라이브 검토(배포본 CPU 약 1.5분)를 기다리지 않아도 된다.")
    if qp.get("cached") == "1" and cached_path and cached_path.exists() and st.session_state.get("review") is None and not st.session_state.get("cached_done"):
        st.session_state["cached_done"] = True
        show_cached = True
    if qp.get("autorun") == "1" and text.strip() and st.session_state.get("review") is None and not st.session_state.get("autorun_done"):
        st.session_state["autorun_done"] = True
        run = True
    st.divider()
    st.markdown("**모델**  \n" + "  \n".join(f"`{r}` → `{os.getenv(e, d)}`" for r, e, d in
                                          [("planner", "DV_MODEL_PLANNER", "gpt-6-sol"), ("reviewer", "DV_MODEL_REVIEWER", "gpt-6-sol"), ("extract", "DV_MODEL_EXTRACT", "gpt-6-sol")]))
    st.caption("판정 권한: 계산·규칙은 도구, 최종 승인은 사람. LLM은 구조화·가설·문장 초안만.")

# ----------------------------------------------------------------- run
hero_box = st.container()
top = st.container()
if show_cached and cached_path:
    rs0 = ReviewState.model_validate_json(cached_path.read_text(encoding="utf-8"))
    st.session_state.update({"events": [f"저장된 실행 결과 로드 — run_id `{rs0.run_id}`, {rs0.budget.used_tokens:,} 토큰, 도구 {rs0.budget.used_tool_calls}회 (LLM 재호출 없음)"]
                             + [replan_line(e) for e in rs0.replan_events[:6]],
                             "done": set(NODES[:NODES.index("gate")]), "current": "gate", "review": rs0, "graph": None, "config": None, "run_started": time.perf_counter()})
    run = False
graph_box = top.empty()
timeline = st.container()

if run:
    st.session_state.update({"events": [], "done": set(), "current": None, "review": None, "run_started": time.perf_counter()})
    os.environ["DV_RUN_TOKEN_BUDGET"] = str(budget)
    status = timeline.status("에이전트 실행 중…", expanded=True)

    def on_step(node: str, upd: dict):
        if node == "__interrupt__":   # Human Gate 진입 신호(tuple) — 노드가 아니므로 타임라인에 쓰지 않는다
            return
        t = time.perf_counter() - st.session_state.run_started
        st.session_state.done.add(node)
        nxt = NODES[NODES.index(node) + 1] if node in NODES and NODES.index(node) + 1 < len(NODES) else None
        st.session_state.current = nxt
        msg = f"{t:5.1f}s  **{node}** 완료"
        if node == "compile":
            inj = [e for e in upd.get("replan_events", []) if e.get("trigger") == "prompt_injection_detected"]
            if inj:
                msg += f" — **프롬프트 인젝션 탐지 {inj[0]['patterns']} → 데이터로만 처리**"
        if node == "plan":
            msg += f" — 과제 {len(upd.get('tasks', []))}개, 근거 미확보 축 {len(upd.get('unavailable_axes', []))}개"
        if node == "tools":
            msg += f" — 도구 호출 {len(upd.get('tool_log', []))}회, 근거 {len(upd.get('evidence', {}))}건"
            fb = [e for e in upd.get("replan_events", []) if e.get("trigger") == "tool_fallback"]
            if fb:
                msg += " · **대체 조회 " + " / ".join(e["tool"] for e in fb) + "**"
        if node == "findings":
            fs = upd.get("findings", [])
            rs_ev = [e for e in upd.get("replan_events", []) if e.get("trigger") == "evidence_reselected"]
            msg += f" — finding {len(fs)}건" + (f" · 근거 재선택 {rs_ev[0]['n']}건(로컬 NLI)" if rs_ev else "") + (" · **기권(TCR 지표 의존)**" if any(getattr(f, 'verdict', '') == 'abstain' for f in fs) else "")
        if node == "verify":
            fs = upd.get("findings", [])
            rej = [f.finding_id for f in fs if f.verifier_status == "rejected"]
            msg += f" — 검증 {sum(1 for f in fs if f.verifier_status == 'verified')}/{len(fs)}" + (f" · **인용 기각 {rej}**" if rej else "")
            hr = [e for e in upd.get("replan_events", []) if e.get("trigger") == "held_research"]
            if hr:
                msg += f" · **보류 재검색 {len(hr)}건 → 검증 {sum(1 for e in hr if e.get('result') == 'verified')}건**"
        bg = [e for e in (upd.get("replan_events") or []) if e.get("trigger") == "budget_guard" and e.get("node") == node] if isinstance(upd, dict) else []
        if bg:
            msg += f" — **예산 가드: 남은 {bg[0]['remaining']:,} < 예상 {bg[0]['estimated']:,} → {bg[0]['action']}**"
        if node == "rewrite":
            msg += " — **재계획①: 기각 문장 재작성**"
        fails = (upd.get("scratch") or {}).get("llm_failures") if isinstance(upd, dict) else None  # __interrupt__ 업데이트는 tuple
        if fails and node in ("plan", "arena", "findings", "rewrite"):
            msg += f" — **LLM 출력 실패 {[f['node'] for f in fails]} → 해당 결과 불완전(결론 없음 처리)**"
        st.session_state.events.append(msg)
        status.write(msg)
        graph_box.graphviz_chart(graph_dot(st.session_state.current, st.session_state.done), use_container_width=True)

    graph_box.graphviz_chart(graph_dot("compile", set()), use_container_width=True)
    if _warm_thread().is_alive():
        status.write("로컬 모델 예열이 끝나기를 기다리는 중(코퍼스 인덱스·NLI, 기동 후 최초 1회)…")
        _warm_thread().join()
    try:
        g, cfg, rs = run_until_gate(text, on_step=on_step, reviewers=["regulatory", "site", "patient"] if three else ["regulatory"], calibrated=conservative)
        st.session_state.update({"graph": g, "config": cfg, "review": rs, "current": "gate"})
        status.update(label=f"Human Gate 대기 — {rs.budget.used_tokens:,} 토큰, 도구 {rs.budget.used_tool_calls}회", state="complete", expanded=False)
    except Exception as e:  # noqa: BLE001
        status.update(label=f"실패: {e}", state="error")
        st.exception(e)

rs: ReviewState | None = st.session_state.review
if rs is None and not run:
    with hero_box:
        st.markdown(
            '<div class="dv-hero"><p class="dv-eyebrow">DoseVerdict · 항암 1/2상 프로토콜 용량 근거 검토</p>'
            '<h1>MTD는 RP2D가 아니다</h1>'
            '<p class="dv-lede">프로토콜의 용량 근거를 실제 약리 계산과 규제 조항 인용으로 검증하고, 근거가 얇으면 결론을 만들지 않고 멈춘다. '
            '최종 판단은 사람이 Human Gate에서 내린다.</p></div>', unsafe_allow_html=True)
        section("사용 방법")
        st.markdown(
            '<div class="dv-grid">'
            '<div class="dv-step"><b><span class="dv-num">1</span>예시 선택</b><span>사이드바(모바일은 왼쪽 위 » 버튼)에서 예시 프로토콜을 고른다. 직접 붙여넣기·파일 업로드도 된다.</span></div>'
            '<div class="dv-step"><b><span class="dv-num">2</span>저장 결과 보기 / 라이브 실행</b><span>저장된 결과는 LLM 호출 없이 즉시 열린다. 라이브 검토는 배포본(CPU)에서 약 1.5분, 3~4만 토큰(Reviewer 3인 옵션 시 약 1.3배).</span></div>'
            '<div class="dv-step"><b><span class="dv-num">3</span>Human Gate</b><span>finding별로 승인·기각·보류를 정해 감사로그에 남긴다. 에이전트는 승인하지 않는다.</span></div>'
            '</div>', unsafe_allow_html=True)
        section("판정 권한 분리")
        st.markdown(
            '<div class="dv-roles">'
            '<div class="dv-role"><b>LLM</b><span>프로토콜 구조화, 가설, 문장 초안까지만</span></div>'
            '<div class="dv-role"><b>도구</b><span>수치 — RDKit·ChEMBL·openFDA·시뮬레이션 계산</span></div>'
            '<div class="dv-role"><b>검증기</b><span>인용 — 원문 span 일치와 근거 조항 대조(NLI)</span></div>'
            '<div class="dv-role"><b>사람</b><span>승인 — 최종 결정과 감사로그 기록</span></div>'
            '</div>', unsafe_allow_html=True)
        tiles = eval_tiles()
        if tiles:
            section("평가 결과 (Silver Set 측정치)")
            for col, (label, value, cap) in zip(st.columns(len(tiles)), tiles):
                col.metric(label, value)
                col.caption(cap)
            st.markdown('<p class="dv-note">Silver Set은 기준 시놉시스에 결함을 주입한 합성 평가 세트다. 임상·규제 전문가가 판정한 Gold Set이 아니다. '
                        '값이 범위로 표시된 것은 같은 설정을 2회 반복 실행한 결과다. 원천: <code>app/eval/data/results/</code>, <code>docs/numbers.md</code>.</p>',
                        unsafe_allow_html=True)
        section("에이전트 흐름")
    graph_box.graphviz_chart(graph_dot(None, set()), use_container_width=True)
    section("후향 검증")
    render_retro()
    render_oneshot()
    render_abstain()
    st.stop()
if rs is None:
    st.stop()

# 결과 머리줄: 결론(기권 여부)과 지적 상태를 먼저 보이고, 근거는 아래 탭에 둔다(CDS "결론 → 근거 → 한계" 순서). 문구는 데이터에서 만든다.
_cnt = {k: sum(1 for f in rs.findings if finding_status(f) == k) for k in STATUS}
_abst = [f for f in rs.findings if getattr(f, "verdict", "") == "abstain"]
with hero_box:
    _src = "저장 결과 · LLM 재호출 없음" if st.session_state.get("graph") is None else "라이브 실행"
    _k = len(rs.findings) - len(_abst)
    _tally = f'검증 {_cnt["verified"]} · 보류 {_cnt["held"]} · 기각 {_cnt["rejected"]}'
    _head = (f"기권 {len(_abst)}건: 판정이 지표·가정에 따라 갈려 결론 대신 추가 자료를 요청했다" if _abst else f"지적 {_k}건: {_tally}")
    _sub = (f"그 밖의 지적 {_k}건: {_tally}. " if _abst else "기권 없음. ") + "이 화면은 검토 보조이며, 승인은 Human Gate에서 사람이 한다."
    st.markdown(
        f'<div class="dv-runhead"><div class="dv-runmeta">{html.escape(_src)} · run <code>{html.escape(rs.run_id)}</code></div>'
        f'<div class="dv-runtitle">{html.escape(_head)}</div><div class="dv-runsub">{html.escape(_sub)}</div></div>', unsafe_allow_html=True)

graph_box.graphviz_chart(graph_dot(st.session_state.current, st.session_state.done), use_container_width=True)
if st.session_state.events:
    with timeline.expander("타임라인 (판단 전환 지점은 굵게)", expanded=False):
        for m in st.session_state.events:
            dot = next((c for k, c in (("기각", "red"), ("기권", "violet"), ("보류", "orange")) if k in m), "gray")
            st.markdown(f":{dot}[●] " + m)

# ----------------------------------------------------------------- summary bar
_n = _cnt
_fail = sum(1 for c in rs.tool_log if not c.ok)
_kpis = [("Findings", f"{len(rs.findings)}건", "", "")] + [(f"{STATUS[k][0]}", f"{_n[k]}건", k if _n[k] else "", "") for k in ("verified", "held", "rejected", "abstain")] + [
    ("토큰", f"{rs.budget.used_tokens:,}", "", f"상한 {rs.budget.max_tokens:,}"),
    ("도구 호출", f"{len(rs.tool_log)}회", "", f"실패 {_fail}회" if _fail else "실패 0회"),
    ("재계획 이벤트", f"{sum(1 for e in rs.replan_events if e.get('trigger'))}건", "", "스스로 경로를 바꾼 지점")]
st.markdown('<div class="dv-kpis">' + "".join(
    f'<div class="dv-kpi {k}{" first" if i == 0 else ""}"><span class="dv-kpi-label">{html.escape(label)}</span><span class="dv-kpi-value">{html.escape(v)}</span>'
    + (f'<span class="dv-kpi-sub">{html.escape(sub)}</span>' if sub else "") + "</div>" for i, (label, v, k, sub) in enumerate(_kpis)) + "</div>"
    + '<p class="dv-note">검증·보류·기각은 기권(F00 등 결론을 만들지 않은 항목)을 뺀 finding의 검증기 상태다.</p>', unsafe_allow_html=True)

# ----------------------------------------------------------------- tabs
tabs = st.tabs(["Findings", "Human Gate", "근거", "도구 호출", "스키마", "Audit", "후향 검증"])   # 7개가 한 줄에 들어가도록 짧게(1366px에서 마지막 탭이 잘리던 문제)

with tabs[0]:
    st.subheader(f"Findings {len(rs.findings)}건 — 검증 {_n['verified']} / 보류 {_n['held']} / 기각 {_n['rejected']} / 기권 {_n['abstain']}")
    for f in rs.findings:
        sk = finding_status(f)
        cat = CATEGORY.get(f.category, f.category)
        with st.expander(f"**{f.finding_id}** · :{STATUS[sk][1]}-badge[{STATUS[sk][0]}] · {cat} · {f.severity.value}", expanded=(f.finding_id in ("F00", "F01"))):
            st.markdown(status_chip(sk) + sev_badge(f.severity.value) + f'<span class="dv-chip cat">{html.escape(cat)}</span>'
                        + ('<span class="dv-chip pending">검증기: 검증</span>' if sk == "abstain" and f.verifier_status == "verified" else ""), unsafe_allow_html=True)
            if f.verdict == "abstain":
                st.markdown(f'<div class="dv-abstain-box"><b>기권 — 결론을 만들지 않음</b><br>{html.escape(f.abstain_reason or "")}</div>', unsafe_allow_html=True)
            st.markdown(f'**원문 span**<div class="dv-quote">{html.escape(f.protocol_span.text)}</div>', unsafe_allow_html=True)
            st.markdown(f"**프로토콜 사실**: {f.protocol_fact or f.claim}")
            if f.evidence_fact:
                st.markdown(f"**근거 사실**: {f.evidence_fact}")
            st.caption(f"검증기: {f.verifier_note}  ·  span 원문 일치: {'검사 안 함' if f.span_verified is None else f.span_verified}")
            if f.reviewer_positions:
                cols = st.columns(len(f.reviewer_positions))
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

    # 수정안 적용 후 재검토 — 에이전트가 자기 수정안을 적용한 판을 다시 검토해, 고친 문장이 다시 지적되는지와 남은 문제를 보여 준다
    from app.agents.patching import apply_patches, still_flagged
    patched_text, applied = apply_patches(rs.raw_protocol_text or "", rs.findings)
    st.markdown('<p class="dv-section">수정안 적용 후 재검토</p>', unsafe_allow_html=True)
    if not applied:
        st.caption("적용할 수정안이 없다(수정안이 붙은 결함 finding이 없거나 원문 span이 일치하지 않음).")
    else:
        st.caption(f"수정안 {len(applied)}건을 원문에 적용한 판을 같은 설정으로 다시 검토한다(라이브 실행, 토큰 약 3~4만). 특이도 평가 C(`docs/specificity_prereg.md`)와 같은 절차다.")
        if st.button(f"수정안 {len(applied)}건 적용 후 재검토", key="repatch"):
            if _warm_thread().is_alive():
                _warm_thread().join()
            with st.spinner("수정판 재검토 중…"):
                _, _, rs2 = run_until_gate(patched_text, reviewers=["regulatory"], calibrated=bool(rs.scratch.get("calibrated", False)))
            st.session_state["repatch"] = {"run_id": rs.run_id, "applied": applied, "review": rs2}
        rp = st.session_state.get("repatch")
        if rp and rp["run_id"] == rs.run_id:
            rs2 = rp["review"]
            again = still_flagged(rp["applied"], rs2.findings)
            n_def = lambda r: sum(1 for x in r.findings if x.verdict == "defect")
            c1, c2, c3 = st.columns(3)
            c1.metric("결함 finding", f"{n_def(rs)} → {n_def(rs2)}")
            c2.metric("고친 문장 재지적", f"{sum(again)}/{len(again)}")
            c3.metric("재검토 토큰", f"{rs2.budget.used_tokens:,}")
            st.table([{"finding": a["finding_id"], "수정안": a["patch"][:120], "재검토에서 다시 지적": "예" if g else "아니오"} for a, g in zip(rp["applied"], again)])
            with st.expander(f"재검토 finding {len(rs2.findings)}건"):
                for x in rs2.findings:
                    st.markdown(f"- `{x.finding_id}` [{x.verdict}/{x.verifier_status}] {x.protocol_span.text[:140]}")

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
        st.markdown(f"{'성공' if c.ok else ':red[**실패**]'} `{c.tool_call_id}` **{c.tool}** {c.latency_s}s  \n args: `{json.dumps(c.args, ensure_ascii=False)[:160]}`  \n {c.result_summary or c.error or ''}")
    st.markdown("**과제 DAG**")
    st.table([{"task": t.task_id, "status": t.status, "tools": ", ".join(t.tools), "depends": ", ".join(t.depends_on)} for t in rs.tasks])
    if rs.unavailable_axes:
        st.warning("근거 미확보 축: " + " / ".join(rs.unavailable_axes))

with tabs[4]:
    st.json(rs.trial.model_dump(exclude_none=True))

with tabs[5]:
    st.markdown(f"**run** `{rs.run_id}` · 토큰 {rs.budget.used_tokens:,}/{rs.budget.max_tokens:,} · 도구 {rs.budget.used_tool_calls}/{rs.budget.max_tool_calls}")
    st.caption("팀 누적 사용량은 감사로그 합으로 집계한다(docs/numbers.md §4). 게이트웨이 쿼터 헤더는 09-22 한도 재설정 이후 값만 보여 누적과 대조할 수 없다.")
    st.download_button("검토 메모 내려받기(마크다운)", render_memo(rs).encode("utf-8"), file_name=f"doseverdict_{rs.run_id}.md", mime="text/markdown")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**노드별 토큰**(게이트웨이 usage.total_tokens, 호출 전 예산 가드 기준)")
        if rs.budget.by_node:
            st.bar_chart({"토큰": rs.budget.by_node}, horizontal=True)
        else:
            st.caption("이 결과는 노드별 원장 도입(09-26) 전에 저장됐다.")
    with c2:
        st.markdown("**도구 호출 요약**")
        agg: dict[str, list[int]] = {}
        for c in rs.tool_log:
            agg.setdefault(c.tool, [0, 0])[0 if c.ok else 1] += 1
        st.table([{"도구": k, "성공": v[0], "실패": v[1]} for k, v in sorted(agg.items())])
    ev = [e for e in rs.replan_events if e.get("trigger")]
    st.markdown(f"**재계획 이벤트 {len(ev)}건** — 에이전트가 스스로 경로를 바꾼 지점")
    if ev:
        st.table([{"트리거": e["trigger"], "대상": e.get("finding_id") or e.get("node") or ", ".join(e.get("tasks", [])) or "—",
                   "내용": str(e.get("action") or e.get("result") or e.get("reason") or "")[:140]} for e in ev])
    with st.expander("감사 메타(JSON)"):
        st.json({"models": rs.audit.models if rs.audit else {}, "corpus_manifest": rs.audit.corpus_manifest_id if rs.audit else None,
                 "prompt_hashes": rs.audit.prompt_hashes if rs.audit else [], "replan_events": rs.replan_events, "terminal_status": rs.terminal_status})

with tabs[6]:
    render_retro()
    render_oneshot()
    render_abstain()
