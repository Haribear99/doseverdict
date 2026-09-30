"""
반박 모드 A/B 실행기 — 사전 등록 docs/refute_prereg.md. 목표 개수가 찰 때까지 이어 실행한다(로컬 DNS 장애 대비, 완료분은 건너뜀).

  python -m app.eval.refute_run pilot     파일럿 2회(집계 제외): clean_base_refute_pilot, lean_refute_pilot
  python -m app.eval.refute_run all       결함 없는 판 12 + 원 20 + 다약물 30
"""
from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path

os.environ["DV_ARENA_REFUTE"] = "1"

from app.eval.specificity import BASES, DATA, OUT, ROOT  # noqa: E402


def _run(text: str, sp: Path, run_id: str, holdout=None) -> None:
    from app.agents.graph import run_until_gate
    if sp.exists():
        return
    sp.parent.mkdir(parents=True, exist_ok=True)
    _, _, st = run_until_gate(text, run_id=run_id, holdout_chunk_ids=holdout, reviewers=["regulatory"], refute=True)
    sp.write_text(st.model_dump_json(indent=1), encoding="utf-8")
    print(json.dumps({"run": run_id, "tokens": st.budget.used_tokens, "findings": len(st.findings),
                      "refuted": st.scratch.get("refuted_tasks", []), "dropped": st.scratch.get("refuted_dropped", [])}, ensure_ascii=False), flush=True)


def _cases(gold: str) -> list[dict]:
    return [json.loads(l) for l in (DATA / gold).read_text(encoding="utf-8").splitlines() if l.strip()]


def pilot() -> None:
    base = BASES["AX1"]
    _run((ROOT / "app" / "demo" / base).read_text(encoding="utf-8"), OUT / "states" / "clean_base_refute_pilot" / f"{Path(base).stem}_0.json", "refute-pilot-clean")
    c = _cases("gold_axis1.jsonl")[0]
    _run(c["synopsis"], OUT / "states" / "lean_refute_pilot" / f"{c['case_id']}.json", "refute-pilot-orig", c.get("holdout_chunk_ids"))


def all_runs() -> None:
    for base in BASES.values():
        text = (ROOT / "app" / "demo" / base).read_text(encoding="utf-8")
        for rep in range(3):
            _run(text, OUT / "states" / "clean_base_refute" / f"{Path(base).stem}_{rep}.json", f"clean_refute-{Path(base).stem}-{rep}")
    for gold, cfg in (("gold_axis1.jsonl", "lean_refute"), ("gold_axis1_multidrug.jsonl", "lean_mdrug_refute")):
        for c in _cases(gold):
            _run(c["synopsis"], OUT / "states" / cfg / f"{c['case_id']}.json", f"eval-{cfg}-{c['case_id']}", c.get("holdout_chunk_ids"))


def until_done(fn, tries: int = 20) -> None:
    for i in range(tries):
        try:
            fn()
            return
        except Exception as e:   # DNS·게이트웨이 일시 장애 — 완료분은 건너뛰고 이어서
            print(json.dumps({"retry": i + 1, "error": repr(e)[:300]}), flush=True)
            time.sleep(30)
    raise SystemExit("목표 개수 미달")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["pilot", "all"])
    until_done({"pilot": pilot, "all": all_runs}[ap.parse_args().cmd])
