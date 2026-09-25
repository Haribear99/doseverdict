"""
실행 방법 ③: CLI.  .venv/Scripts/python.exe -m app.cli review app/demo/sotorasib_synopsis.md [--approve-all] [--out result.json] [--report memo.md]

Human Gate는 --approve-all이 없으면 findings를 출력하고 '승인 대기'로 끝낸다(비대화식 환경에서는 사람이 JSON을 보고 결정).
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="doseverdict")
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("review", help="프로토콜 시놉시스 검토")
    r.add_argument("path", help="프로토콜 .md/.txt")
    r.add_argument("--approve-all", action="store_true", help="검증된 finding을 자동 승인(시연·평가용; 실제 검토에서는 쓰지 않는다)")
    r.add_argument("--approver", default=os.getenv("USER", "cli"))
    r.add_argument("--out", help="결과 JSON 경로")
    r.add_argument("--report", help="검토 메모(마크다운) 경로 — UI 다운로드와 같은 내용")
    r.add_argument("--budget", type=int, default=int(os.getenv("DV_RUN_TOKEN_BUDGET", "150000")))
    a = ap.parse_args(argv)

    from app.agents.graph import resume_with_decision, run_until_gate
    text = Path(a.path).read_text(encoding="utf-8")
    os.environ["DV_RUN_TOKEN_BUDGET"] = str(a.budget)
    import time
    t_start = time.perf_counter(); t_last = [t_start]

    def _step(n, u):   # 노드별 소요시간(누적) — 배포 환경(CPU) 병목 진단용
        now = time.perf_counter()
        print(f"  · {n}  +{now - t_last[0]:.1f}s  (총 {now - t_start:.1f}s)", file=sys.stderr)
        t_last[0] = now

    graph, config, st = run_until_gate(text, on_step=_step)
    if a.approve_all:
        st = resume_with_decision(graph, config, {f.finding_id: "approved" for f in st.findings if f.verifier_status == "verified"}, a.approver)
    out = st.model_dump(mode="json")
    if a.out:
        Path(a.out).write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    if a.report:
        from app.report import render_memo
        Path(a.report).write_text(render_memo(st), encoding="utf-8")
    print(f"\nrun {st.run_id} · status {st.terminal_status} · tokens {st.budget.used_tokens:,} · tools {st.budget.used_tool_calls} · findings {len(st.findings)}")
    for f in st.scratch.get("llm_failures", []):
        print(f"  ! LLM 출력 실패 — node {f['node']}: {f.get('error')}")
    for f in st.findings:
        print(f"  {f.finding_id} [{f.severity.value}] {f.verdict}/{f.verifier_status} — {f.claim[:120]}")
    slow = sorted(st.tool_log, key=lambda c: -(c.latency_s or 0))[:6]
    print("  tool latency: " + ", ".join(f"{c.tool} {c.latency_s:.1f}s" for c in slow), file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
