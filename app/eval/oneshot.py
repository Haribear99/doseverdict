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
    return {cid: {k: sum(r[cid][k] for r in runs) / len(runs) for k in KEYS} for cid in sorted(common)}   # 정렬 — set 순서가 실행마다 달라 부트스트랩이 흔들리지 않게


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


def _by_doc() -> dict[str, list[str]]:
    by_doc: dict[str, list[str]] = {}
    for line in CLAUSES.read_text(encoding="utf-8").splitlines():
        if line.strip():
            c = json.loads(line)
            by_doc.setdefault(c["doc_id"], []).append(c["text"])
    return by_doc


def quote_matches(f: dict, by_doc: dict[str, list[str]]) -> bool | None:
    """한 finding의 가이던스 문장이 같은 doc_id의 조항과 일치하면 True, 불일치 False, 문서 본문이 색인에 없으면 None(검사 불가)."""
    q = f.get("guidance_quote") or ""
    docs = by_doc.get(f.get("cited_doc_id") or "")
    if not q.strip() or not docs:
        return None
    gq, nq = _grams(q), _norm(q)
    best = 0.0
    for t in docs:
        if nq and nq in _norm(t):
            return True
        gt = _grams(t)
        inter = len(gq & gt)
        best = max(best, inter / max(1, len(gq | gt)), inter / max(1, len(gq)) if len(gq) >= 10 else 0)
    return best >= 0.5


_NLI_CACHE: dict[tuple[str, str], bool] = {}


def quote_supported(f: dict, by_doc: dict[str, list[str]], thr: float = 0.7) -> bool | None:
    """사후: 문자열 일치가 아니어도 인용 문서의 가까운 조항 3개 중 하나가 그 문장을 함의하면(NLI entailment ≥ 0.7) 충실한 의역으로 인정한다."""
    m = quote_matches(f, by_doc)
    if m is not False:
        return m
    q, doc = f.get("guidance_quote") or "", f.get("cited_doc_id") or ""
    key = (doc, q)
    if key not in _NLI_CACHE:
        from app.verify.nli import _is_korean, focus_window, nli
        gq = _grams(q)
        top = sorted(by_doc[doc], key=lambda t: -len(gq & _grams(t)))[:3]
        _NLI_CACHE[key] = any(nli(focus_window(t, q), q, multilingual=_is_korean(t)).scores.get("entailment", 0) >= thr for t in top)
    return _NLI_CACHE[key]


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
    chk = n - unknown_doc
    return {"n_quotes": n, "matched": ok, "rate": round(ok / n, 3) if n else None, "unknown_doc_id": unknown_doc,
            "rate_checkable": round(ok / chk, 3) if chk else None}


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
          "## 인용 충실도(베이스라인 가이던스 문장이 코퍼스 실제 조항과 일치하는 비율)", "",
          "| 실행 | 인용문 수 | 일치 | 비율(전체) | 본문 미색인 문서 인용(검사 불가) | 비율(검사 가능분) |", "|---|---|---|---|---|---|"]
    out["quote_fidelity"] = {}
    for cfg in ("oneshot", "oneshot_r2", "single_rag6"):
        if (RES / f"{cfg}.json").exists():
            q = quote_fidelity(cfg)
            out["quote_fidelity"][cfg] = q
            L.append(f"| {cfg} | {q['n_quotes']} | {q['matched']} | {q['rate']} | {q['unknown_doc_id']} | {q['rate_checkable']} |")
    L += ["", "에이전트의 인용문은 검색된 조항 원문에서만 오므로 구조적으로 일치한다(비교 대상 아님). 원샷 인용문은 모델 기억이다. "
          "검사 불가는 목록에는 있지만 코퍼스에 본문이 색인되지 않은 문서(CTTI-QBD 등)를 인용한 경우다."]
    # 사후(사전 등록 밖): 인용문이 실제 조항과 일치한 finding만 인정한 원샷 grounded — 에이전트 인용문은 원문이므로 같은 조건
    from app.eval.run_eval import _grounded
    gold = {c["case_id"]: c for c in (json.loads(l) for l in (RES.parent / "gold_axis1.jsonl").read_text(encoding="utf-8").splitlines() if l.strip())}
    bd, post = _by_doc(), {}
    for cfg in ("oneshot", "oneshot_r2"):
        for r in json.loads((RES / f"{cfg}.json").read_text(encoding="utf-8"))["rows"]:
            fs = [f for f in r.get("baseline_findings") or [] if quote_supported(f, bd)]
            texts = [f"{f.get('span', '')} {f.get('claim', '')} {f.get('guidance_quote', '')}" for f in fs]
            docs = [{f.get("cited_doc_id", "")} for f in fs]
            defs = gold[r["case_id"]]["defects"]
            post.setdefault(r["case_id"], []).append(sum(_grounded(d, docs, texts) for d in defs) / max(1, len(defs)))
    vg = {c: {"grounded_recall": sum(v) / len(v)} for c, v in post.items()}
    g = paired(agent, vg, "grounded_recall")
    vmean = sum(x["grounded_recall"] for x in vg.values()) / len(vg)
    out["post_hoc_verifiable_grounded"] = {"oneshot": round(vmean, 3), "diff": [round(x, 3) for x in g[:3]]}
    allq = [f for cfg in ("oneshot", "oneshot_r2") for r in json.loads((RES / f"{cfg}.json").read_text(encoding="utf-8"))["rows"] for f in r.get("baseline_findings") or []]
    chk = [f for f in allq if quote_matches(f, bd) is not None]
    exact = sum(quote_matches(f, bd) is True for f in chk)
    para = sum(quote_supported(f, bd) is True for f in chk) - exact
    out["post_hoc_quote_support"] = {"checkable": len(chk), "exact": exact, "nli_paraphrase": para, "unsupported": len(chk) - exact - para}
    L += ["", "## 사후 분석(사전 등록 밖)", "",
          f"- 원샷 인용문(2회, 검사 가능 {len(chk)}건): 원문 일치 {exact}, 원문 불일치지만 인용 문서의 가까운 조항 3개 중 하나가 함의(NLI ≥ 0.7, 충실한 의역) {para}, "
          f"어느 쪽도 아님 {len(chk) - exact - para}({(len(chk) - exact - para) / max(1, len(chk)):.1%}).",
          f"- 원문 일치 또는 충실한 의역인 finding만 인정한 원샷 grounded: 2회 평균 {vmean:.3f}, 에이전트 대비 {g[0]:+.3f} [{g[1]:+.3f}, {g[2]:+.3f}]. 검사 불가 인용은 불인정으로 셌다(원샷에 불리한 쪽)."]
    (RES / "oneshot_compare.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    (RES / "ONESHOT_REPORT.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
