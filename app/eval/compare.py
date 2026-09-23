"""
A/B 비교 — 같은 케이스에서 두 설정을 쌍대 부트스트랩으로 비교한다(토큰 0).

사전 등록한 판정 규칙(docs/리서치_요약_0923.md §7):
- 채택: 토큰 −15% 이상 절감 + grounded·검증 통과율 하락이 5pp 이내(점추정), 또는 grounded CI 하한 > 0
- 기각: 토큰 증가 또는 grounded/검증 하락 5pp 초과
- 그 외: 판정 보류(n=20 검정력 부족 — 확장 세트로 재확인)

실행: .venv/Scripts/python.exe -m app.eval.compare lean_d3 lean_cnone lean_strict ...
"""
from __future__ import annotations

import json
import random
import sys
from pathlib import Path

RES = Path(__file__).resolve().parent / "data" / "results"
METRICS = ("grounded_recall", "recall", "verified_rate", "precision_proxy", "tokens")


def load(cfg: str) -> dict[str, dict]:
    d = json.loads((RES / f"{cfg}.json").read_text(encoding="utf-8"))
    return {r["case_id"]: r for r in d["rows"]}


def paired(base: dict, arm: dict, key: str, n_boot: int = 5000, seed: int = 0) -> tuple[float, float, float, int]:
    diffs = [arm[c][key] - base[c][key] for c in arm if c in base and arm[c].get(key) is not None and base[c].get(key) is not None]
    rng = random.Random(seed)
    boots = sorted(sum(rng.choice(diffs) for _ in diffs) / len(diffs) for _ in range(n_boot))
    return sum(diffs) / len(diffs), boots[int(0.025 * n_boot)], boots[int(0.975 * n_boot)], len(diffs)


def verdict(base: dict, arm: dict) -> str:
    tok_rel = sum(arm[c]["tokens"] for c in arm if c in base) / sum(base[c]["tokens"] for c in arm if c in base) - 1
    g, g_lo, _, _ = paired(base, arm, "grounded_recall")
    v, _, _, _ = paired(base, arm, "verified_rate")
    if tok_rel > 0.02 or g < -0.05 or v < -0.05:
        return f"기각 (토큰 {tok_rel:+.1%}, grounded {g:+.3f}, 검증 {v:+.3f})"
    if tok_rel <= -0.15 or g_lo > 0:
        return f"채택 (토큰 {tok_rel:+.1%}, grounded {g:+.3f}, 검증 {v:+.3f})"
    return f"보류 (토큰 {tok_rel:+.1%}, grounded {g:+.3f}, 검증 {v:+.3f})"


def main() -> None:
    base_cfg, *arms = sys.argv[1:]
    base = load(base_cfg)
    for a in arms:
        p = RES / f"{a}.json"
        if not p.exists():
            print(f"{a}: 결과 없음")
            continue
        arm = load(a)
        print(f"\n## {a} vs {base_cfg}  →  {verdict(base, arm)}")
        print("| 지표 | 차이 | 95% CI | n |\n|---|---|---|---|")
        for k in METRICS:
            m, lo, hi, n = paired(base, arm, k)
            fmt = "{:+,.0f}" if k == "tokens" else "{:+.3f}"
            print(f"| {k} | {fmt.format(m)} | [{fmt.format(lo)}, {fmt.format(hi)}] | {n} |")


if __name__ == "__main__":
    main()
