"""
원샷 + 같은 인용 판정기, 결함 없는 판 비교 — 사전 등록 docs/hybrid_prereg.md.

  python -m app.eval.hybrid run       원샷 12회(기준 시놉시스 4종 × 3회) → results/states/clean_oneshot/
  python -m app.eval.hybrid report    results/HYBRID_REPORT.md, results/hybrid.json (토큰 0)
"""
from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

from app.eval.oneshot import _by_doc, _support
from app.eval.specificity import BASES, OUT, ROOT, defect_spans, eval_b, flagged, sentences

D = OUT / "states" / "clean_oneshot"


def run() -> None:
    from app.eval.run_eval import run_oneshot
    from app.llm.client import GatewayClient
    gc = GatewayClient(audit_path="logs/eval_runs.jsonl")
    D.mkdir(parents=True, exist_ok=True)
    for base in BASES.values():
        text = (ROOT / "app" / "demo" / base).read_text(encoding="utf-8")
        for rep in range(3):
            sp = D / f"{Path(base).stem}_{rep}.json"
            if sp.exists():
                continue
            fs, tokens = run_oneshot(gc, text)
            sp.write_text(json.dumps({"base": base, "rep": rep, "tokens": tokens, "findings": fs}, ensure_ascii=False, indent=1), encoding="utf-8")
            print(json.dumps({"base": base, "rep": rep, "tokens": tokens, "findings": len(fs)}), flush=True)


def _arm_rows(filter_mode: str | None, bd: dict) -> list[dict]:
    rows = []
    for sp in sorted(D.glob("*.json")):
        r = json.loads(sp.read_text(encoding="utf-8"))
        fs = r["findings"]
        if filter_mode:
            fs = [f for f in fs if _support(f, bd, filter_mode)]
        base_s = sentences((ROOT / "app" / "demo" / r["base"]).read_text(encoding="utf-8"))
        rows.append({"run": sp.stem, "base_n": len(base_s), "base_hit": sum(flagged(base_s, [f.get("span") or "" for f in fs])),
                     "n_findings": len(fs), "tokens": r["tokens"]})
    return rows


def _agent_rows(verified_only: bool) -> list[dict]:
    rows = []
    for sp in sorted((OUT / "states" / "clean_base").glob("*.json")):
        st = json.loads(sp.read_text(encoding="utf-8"))
        spans = defect_spans(st) if not verified_only else [
            f["protocol_span"]["text"] for f in st["findings"] if f.get("verdict") == "defect" and f["finding_id"] != "F00" and f.get("verifier_status") == "verified"]
        base_s = sentences((ROOT / "app" / "demo" / (sp.stem.rsplit("_", 1)[0] + ".md")).read_text(encoding="utf-8"))
        rows.append({"run": sp.stem, "base_n": len(base_s), "base_hit": sum(flagged(base_s, spans)), "n_findings": len(spans), "tokens": st["budget"]["used_tokens"]})
    return rows


def _summ(rows: list[dict]) -> dict:
    n = max(1, len(rows))
    ng, fp = sum(r["base_n"] for r in rows), sum(r["base_hit"] for r in rows)
    return {"n_runs": len(rows), "flagged_per_run": round(fp / n, 2), "specificity": round(1 - fp / max(1, ng), 3),
            "findings_per_run": round(sum(r["n_findings"] for r in rows) / n, 2), "tokens_per_run": round(sum(r["tokens"] for r in rows) / n)}


def _diff(arm: list[dict], agent: list[dict], n: int = 5000, seed: int = 0) -> list[float]:
    """(팔 − 에이전트) 실행당 지적 기준 문장 수 평균 차이, 두 팔 각각 복원 추출 부트스트랩 95% CI."""
    rng = random.Random(seed)
    a, b = [r["base_hit"] for r in arm], [r["base_hit"] for r in agent]
    point = sum(a) / len(a) - sum(b) / len(b)
    boots = sorted(sum(rng.choice(a) for _ in a) / len(a) - sum(rng.choice(b) for _ in b) / len(b) for _ in range(n))
    return [round(point, 2), round(boots[int(0.025 * n)], 2), round(boots[int(0.975 * n) - 1], 2)]


def report() -> None:
    bd = _by_doc()
    agent = _agent_rows(False)
    arms = {"원샷 + 판정기(1차, 원문 일치 또는 NLI)": _arm_rows("nli", bd), "원샷 + 판정기(원문 일치만)": _arm_rows("exact", bd),
            "원샷(원)": _arm_rows(None, bd), "에이전트 verified만(참고)": _agent_rows(True)}
    b = eval_b()
    assert b and abs(_summ(agent)["flagged_per_run"] - b["mean_flagged_base_sentences"]) < 1e-6   # 평가 B와 같은 정의인지 확인
    res = {"agent": _summ(agent), "arms": {}}
    L = ["# 원샷 + 같은 인용 판정기, 결함 없는 판 비교 (`python -m app.eval.hybrid report`)", "",
         "사전 등록: `docs/hybrid_prereg.md`. 결함 없는 기준 시놉시스 4종 × 3회. 차이 = 팔 − 에이전트(실행당 지적된 기준 문장 수), 부트스트랩 95% CI.", "",
         "| 팔 | 실행 | 지적된 기준 문장/실행 | 특이도 | finding/실행 | 토큰/실행 | 차이 [95% CI] |", "|---|---|---|---|---|---|---|"]
    s = res["agent"]
    L.append(f"| 에이전트(clean_base, 평가 B) | {s['n_runs']} | {s['flagged_per_run']} | {s['specificity']} | {s['findings_per_run']} | {s['tokens_per_run']:,} | — |")
    for name, rows in arms.items():
        s, d = _summ(rows), _diff(rows, agent)
        res["arms"][name] = {**s, "diff": d}
        L.append(f"| {name} | {s['n_runs']} | {s['flagged_per_run']} | {s['specificity']} | {s['findings_per_run']} | {s['tokens_per_run']:,} | {d[0]:+.2f} [{d[1]:+.2f}, {d[2]:+.2f}] |")
    d = res["arms"]["원샷 + 판정기(1차, 원문 일치 또는 NLI)"]["diff"]
    v = "원샷+판정기가 결함 없는 판에서 더 조용하다" if d[2] < 0 else "에이전트가 결함 없는 판에서 더 조용하다" if d[1] > 0 else "차이 확인 안 됨"
    res["verdict"] = v
    L += ["", f"1차 판정: **{v}** (사전 등록 규칙: CI 상한 < 0 → 원샷+판정기가 더 조용, 하한 > 0 → 에이전트가 더 조용, 그 외 차이 확인 안 됨).", "",
          "판정기는 인용 판정기(가이던스 문장 ↔ 인용 문서 조항)이며 에이전트 검증기 전체가 아니다. '에이전트 verified만'은 사전 등록의 2차 참고값이다."]
    (OUT / "hybrid.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    (OUT / "HYBRID_REPORT.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["run", "report"])
    {"run": run, "report": report}[ap.parse_args().cmd]()
