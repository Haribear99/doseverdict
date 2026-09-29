"""
강한 LLM 원샷 베이스라인 분석 — 사전 등록 docs/oneshot_prereg.md.

실행(토큰 0): python -m app.eval.oneshot
입력: results/{lean_v3,lean_v3b}.json(에이전트 2회), results/{oneshot,oneshot_r2}.json(원샷 2회), results/single_rag6.json(현재 모델 single_rag 1회)
출력: results/ONESHOT_REPORT.md, results/oneshot_compare.json
"""
from __future__ import annotations

import json
import random
import re
from pathlib import Path

from app.eval.compare import load

RES = Path(__file__).resolve().parent / "data" / "results"
CLAUSES = Path(__file__).resolve().parents[1] / "corpus" / "index" / "clauses.jsonl"
KEYS = ("grounded_recall", "recall", "precision_proxy", "tokens")


def mean_runs(cfgs: list[str]) -> dict[str, dict]:
    runs = [load(c) for c in cfgs]
    common = set.intersection(*(set(r) for r in runs))
    return {cid: {k: sum(r[cid][k] for r in runs) / len(runs) for k in KEYS} for cid in common}


def paired(base: dict, arm: dict, key: str, n_boot: int = 5000, seed: int = 0) -> tuple[float, float, float, int]:
    d = [arm[c][key] - base[c][key] for c in arm if c in base]
    rng = random.Random(seed)
    boots = sorted(sum(rng.choice(d) for _ in d) / len(d) for _ in range(n_boot))
    return sum(d) / len(d), boots[int(0.025 * n_boot)], boots[int(0.975 * n_boot)], len(d)


def _norm(t: str) -> str:
    return re.sub(r"[^0-9a-z]", "", (t or "").lower())


def _grams(t: str, n: int = 6) -> set[str]:
    t = _norm(t)
    return {t[i:i + n] for i in range(len(t) - n + 1)} if len(t) >= n else {t}


def quote_fidelity(cfg: str) -> dict:
    """가이던스 문장이 같은 doc_id의 실제 조항과 일치하는가(6-gram Jaccard ≥ 0.5 또는 부분 포함). 조항 중 가장 잘 맞는 것 기준."""
    by_doc: dict[str, list[str]] = {}
    for line in CLAUSES.read_text(encoding="utf-8").splitlines():
        if line.strip():
            c = json.loads(line)
            by_doc.setdefault(c["doc_id"], []).append(c["text"])
    rows = json.loads((RES / f"{cfg}.json").read_text(encoding="utf-8"))["rows"]
    n = ok = unknown_doc = 0
    for r in rows:
        for f in r.get("baseline_findings") or []:
            q = f.get("guidance_quote") or ""
            if not q.strip():
                continue
            n += 1
            docs = by_doc.get(f.get("cited_doc_id") or "")
            if not docs:
                unknown_doc += 1
                continue
            gq, nq = _grams(q), _norm(q)
            best = 0.0
            for t in docs:
                if nq and nq in _norm(t):
                    best = 1.0
                    break
                # 조항이 길어 Jaccard가 희석되지 않도록 인용문 쪽 gram 기준 포함률(overlap / |quote grams|)과 Jaccard 중 큰 값
                gt = _grams(t)
                inter = len(gq & gt)
                best = max(best, inter / max(1, len(gq | gt)), inter / max(1, len(gq)) if len(gq) >= 10 else 0)
            ok += best >= 0.5
    return {"n_quotes": n, "matched": ok, "rate": round(ok / n, 3) if n else None, "unknown_doc_id": unknown_doc}


def main() -> None:
    agent = mean_runs(["lean_v3", "lean_v3b"])
    arms = {"oneshot(2회 평균)": mean_runs(["oneshot", "oneshot_r2"])}
    if (RES / "single_rag6.json").exists():
        arms["single_rag6(1회)"] = mean_runs(["single_rag6"])
    out = {"agent": "lean_v3+lean_v3b", "arms": {}}
    L = ["# 강한 LLM 원샷 베이스라인 결과 (`python -m app.eval.oneshot`)", "", "사전 등록: `docs/oneshot_prereg.md`. 원 세트 20케이스. 차이 = 베이스라인 − 에이전트(에이전트 2회 평균), 쌍대 부트스트랩 95% CI.", "",
         "| 팔 | n | grounded (에이전트 / 팔) | 차이 [95% CI] | span recall 차이 | precision 차이 | 토큰/케이스 (에이전트 / 팔) |", "|---|---|---|---|---|---|---|"]
    for name, arm in arms.items():
        g = paired(agent, arm, "grounded_recall")
        sp = paired(agent, arm, "recall")
        pr = paired(agent, arm, "precision_proxy")
        ta = sum(agent[c]["tokens"] for c in arm if c in agent) / g[3]
        tb = sum(arm[c]["tokens"] for c in arm if c in agent) / g[3]
        ga = sum(agent[c]["grounded_recall"] for c in arm if c in agent) / g[3]
        gb = sum(arm[c]["grounded_recall"] for c in arm if c in agent) / g[3]
        v = "에이전트 우위" if g[2] < 0 else "원샷 우위" if g[1] > 0 else "차이 확인 안 됨"
        out["arms"][name] = {"n": g[3], "grounded_agent": round(ga, 3), "grounded_arm": round(gb, 3), "grounded_diff": [round(x, 3) for x in g[:3]],
                             "span_diff": [round(x, 3) for x in sp[:3]], "precision_diff": [round(x, 3) for x in pr[:3]],
                             "tokens_agent": round(ta), "tokens_arm": round(tb), "verdict": v}
        L.append(f"| {name} | {g[3]} | {ga:.3f} / {gb:.3f} | {g[0]:+.3f} [{g[1]:+.3f}, {g[2]:+.3f}] | {sp[0]:+.3f} [{sp[1]:+.3f}, {sp[2]:+.3f}] | "
                 f"{pr[0]:+.3f} [{pr[1]:+.3f}, {pr[2]:+.3f}] | {ta:,.0f} / {tb:,.0f} |")
    L += ["", "1차 판정(grounded, 원샷 2회 평균): **" + out["arms"]["oneshot(2회 평균)"]["verdict"] + "** (CI 상한 < 0 → 에이전트 우위, 하한 > 0 → 원샷 우위)", "",
          "## 인용 충실도(베이스라인 가이던스 문장이 코퍼스 실제 조항과 일치하는 비율)", "", "| 실행 | 인용문 수 | 일치 | 비율 | 목록 밖 doc_id |", "|---|---|---|---|---|"]
    out["quote_fidelity"] = {}
    for cfg in ("oneshot", "oneshot_r2", "single_rag6"):
        if (RES / f"{cfg}.json").exists():
            q = quote_fidelity(cfg)
            out["quote_fidelity"][cfg] = q
            L.append(f"| {cfg} | {q['n_quotes']} | {q['matched']} | {q['rate']} | {q['unknown_doc_id']} |")
    L += ["", "에이전트의 인용문은 검색된 조항 원문에서만 오므로 구조적으로 일치한다(비교 대상 아님). 원샷 인용문은 모델 기억이다."]
    (RES / "oneshot_compare.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    (RES / "ONESHOT_REPORT.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
