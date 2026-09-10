"""
평가 결과 보고서 — results/<config>.json들을 모아 설정별 지표 표(부트스트랩 95% CI)와 ablation 기여도를 마크다운으로 만든다. LLM 호출 없음.

실행: .venv/Scripts/python.exe -m app.eval.report  →  app/eval/data/results/REPORT.md
"""
from __future__ import annotations

import json
import random
from pathlib import Path

from app.eval.run_eval import OUT

CONFIGS = ["checklist", "single_rag", "full", "no_calc", "no_arena", "no_verifier"]
METRICS = ["recall", "weighted_recall", "grounded_recall", "grounded_weighted_recall", "precision_proxy", "verified_rate", "tokens", "elapsed_s"]


def boot_ci(values: list[float], n: int = 2000, seed: int = 3) -> tuple[float, float]:
    if not values:
        return (0.0, 0.0)
    rng = random.Random(seed)
    means = sorted(sum(rng.choice(values) for _ in values) / len(values) for _ in range(n))
    return (round(means[int(0.025 * n)], 3), round(means[int(0.975 * n)] - 0.0005, 3))


def main() -> None:
    res = {}
    for c in CONFIGS:
        p = OUT / f"{c}.json"
        if p.exists():
            res[c] = json.load(p.open(encoding="utf-8"))
    lines = ["# 평가 결과 (축① 규범 유도 결함 주입 Silver Set)", "",
             "지표 정의: span recall = 주입 문장을 finding이 가리킴(어휘). grounded recall = 그 finding이 정답 규범 문서를 인용했거나 근거 사실이 원문과 겹침. "
             "가중 = critical 4·high 3·medium 2·low 1. precision proxy = 적중 finding / 전체 finding(정상판에 대한 지적은 '무관'으로 세므로 하한). 95% CI는 케이스 단위 부트스트랩(2,000회).", "",
             "| 설정 | n | span recall [CI] | 가중 span | grounded recall [CI] | 가중 grounded | precision | 검증 통과율 | 토큰/케이스 | 초/케이스 |", "|---|---|---|---|---|---|---|---|---|---|"]
    for c, r in res.items():
        rows = r["rows"]
        rec = [x["recall"] for x in rows]; grec = [x.get("grounded_recall", 0) for x in rows]
        ci1, ci2 = boot_ci(rec), boot_ci(grec)
        a = r["aggregate"]
        lines.append(f"| {c} | {len(rows)} | {a['recall']:.3f} [{ci1[0]:.2f}, {ci1[1]:.2f}] | {a['weighted_recall']:.3f} | {a.get('grounded_recall', 0):.3f} [{ci2[0]:.2f}, {ci2[1]:.2f}] | "
                     f"{a.get('grounded_weighted_recall', 0):.3f} | {a['precision_proxy']:.3f} | {a.get('verified_rate', 0):.3f} | {a['tokens']:,.0f} | {a['elapsed_s']:.0f} |")
    if "full" in res:
        lines += ["", "## Ablation 기여도 (full 대비 grounded weighted recall 차이)", "", "| 제거한 구성요소 | 설정 | Δ grounded w-recall | Δ 검증 통과율 | Δ 토큰 |", "|---|---|---|---|---|"]
        f = res["full"]["aggregate"]
        for c, label in [("no_calc", "계산 모듈"), ("no_arena", "Adversarial Reviewer"), ("no_verifier", "Citation Verifier")]:
            if c in res:
                a = res[c]["aggregate"]
                lines.append(f"| {label} | {c} | {a.get('grounded_weighted_recall', 0) - f.get('grounded_weighted_recall', 0):+.3f} | {a.get('verified_rate', 0) - f.get('verified_rate', 0):+.3f} | {a['tokens'] - f['tokens']:+,.0f} |")
        lines += ["", "해석 규칙(제안서 4장): 전체 시스템이 정규식 체크리스트 대비 grounded recall에서 15%p 이상 앞서지 못하면 멀티에이전트가 불필요하다고 보고한다."]
        if "checklist" in res:
            d = f.get("grounded_recall", 0) - res["checklist"]["aggregate"].get("grounded_recall", 0)
            lines.append(f"→ full − checklist (grounded recall) = {d:+.3f} ({'기준 충족' if d >= 0.15 else '기준 미달 — 그대로 보고'}).")
    out = OUT / "REPORT.md"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
