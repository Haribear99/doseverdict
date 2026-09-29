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
    if len(nq) < 6:   # 영문 외(한국어) 인용은 정규화 후 비어 무조건 일치가 되므로 검사 불가로 둔다
        return None
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


def _agent_rows(cfg: str, gold: dict) -> list[tuple[str, list[dict], dict]]:
    """에이전트 저장 상태 → (case_id, finding 목록(guidance_quote=evidence_fact, cited_doc_ids), evidence) — 원샷과 같은 판정기에 넣기 위한 변환."""
    from app.corpus.manifest import DOCS
    t2id = {d.title: d.doc_id for d in DOCS}
    out = []
    for cid in sorted(gold):
        st = json.loads((RES / "states" / cfg / f"{cid}.json").read_text(encoding="utf-8"))
        ev = st["evidence"]
        fs = []
        for f in st["findings"]:
            docs = sorted({t2id.get(ev[e].get("document_title") or "", "") for e in f["evidence_ids"] if e in ev} - {""})
            fs.append({"span": f["protocol_span"]["text"], "claim": f.get("protocol_fact") or "", "guidance_quote": f.get("evidence_fact") or "",
                       "cited_doc_ids": docs, "verifier_status": f.get("verifier_status")})
        out.append((cid, fs, ev))
    return out


def _support(f: dict, bd: dict, mode: str) -> bool:
    """mode='exact': 문자열 일치만, 'nli': 문자열 일치 또는 NLI 의역. 여러 문서를 단 에이전트 finding은 하나라도 통과하면 인정."""
    fn = quote_matches if mode == "exact" else quote_supported
    ids = f.get("cited_doc_ids") or [f.get("cited_doc_id") or ""]
    return any(fn({"guidance_quote": f.get("guidance_quote") or "", "cited_doc_id": d}, bd) is True for d in ids if d in bd)


def post_hoc(agent: dict, out: dict) -> list[str]:
    """사후 분석(사전 등록 밖, red-judge 09-29 지적 반영): 같은 인용 판정기를 에이전트(evidence_fact)와 원샷(guidance_quote)에 대칭으로 건다."""
    from app.eval.run_eval import _grounded
    gold = {c["case_id"]: c for c in (json.loads(l) for l in (RES.parent / "gold_axis1.jsonl").read_text(encoding="utf-8").splitlines() if l.strip())}
    gold = {k: v for k, v in gold.items() if k in agent}
    bd = _by_doc()
    runs = {"agent": [_agent_rows(c, gold) for c in ("lean_v3", "lean_v3b")],
            "oneshot": [[(r["case_id"], r.get("baseline_findings") or [], None)
                         for r in sorted(json.loads((RES / f"{c}.json").read_text(encoding="utf-8"))["rows"], key=lambda r: r["case_id"])]
                        for c in ("oneshot", "oneshot_r2")]}
    fid = {}
    for side, rs in runs.items():
        allf = [f for run in rs for _, fs, _ in run for f in fs if (f.get("guidance_quote") or "").strip()]
        chk = [f for f in allf if any(quote_matches({"guidance_quote": f.get("guidance_quote"), "cited_doc_id": d}, bd) is not None
                                      for d in (f.get("cited_doc_ids") or [f.get("cited_doc_id") or ""]))]
        ex = sum(_support(f, bd, "exact") for f in chk)
        nl = sum(_support(f, bd, "nli") for f in chk)
        fid[side] = {"quotes": len(allf), "checkable": len(chk), "exact": ex, "exact_or_nli": nl, "unsupported": len(chk) - nl}
    # 에이전트가 근거로 붙인 규제 조항 인용문(evidence.quote)이 코퍼스 원문인가
    clause_texts = [_norm(t) for ts in bd.values() for t in ts]
    evq = [_norm(e.get("quote") or "") for run in runs["agent"] for _, _, ev in run for e in ev.values() if e.get("kind") == "regulatory_clause"]
    evq = [q for q in evq if q]
    evq_ok = sum(any(q[:200] in t for t in clause_texts) for q in evq)
    fid["agent_evidence_quote"] = {"n": len(evq), "verbatim": evq_ok}
    res = {}
    for mode in ("exact", "nli"):
        for side, rs in runs.items():
            per: dict[str, list[float]] = {}
            for run in rs:
                for cid, fs, _ in run:
                    keep = [f for f in fs if _support(f, bd, mode)]
                    texts = [f"{f.get('span', '')} {f.get('claim', '')} {f.get('guidance_quote', '')}" for f in keep]
                    docs = [set(f.get("cited_doc_ids") or [f.get("cited_doc_id") or ""]) for f in keep]
                    defs = gold[cid]["defects"]
                    per.setdefault(cid, []).append(sum(_grounded(d, docs, texts) for d in defs) / max(1, len(defs)))
            res[(side, mode)] = {c: {"grounded_recall": sum(v) / len(v)} for c, v in sorted(per.items())}
    sym = {}
    for mode in ("exact", "nli"):
        a, o = res[("agent", mode)], res[("oneshot", mode)]
        g = paired(a, o, "grounded_recall")
        sym[mode] = {"agent": round(sum(x["grounded_recall"] for x in a.values()) / len(a), 3),
                     "oneshot": round(sum(x["grounded_recall"] for x in o.values()) / len(o), 3), "diff": [round(x, 3) for x in g[:3]]}
    out["post_hoc"] = {"fidelity": fid, "symmetric_grounded": sym}
    fa, fo, fe = fid["agent"], fid["oneshot"], fid["agent_evidence_quote"]

    def row(name: str, f: dict) -> str:
        c = max(1, f["checkable"])
        return (f"| {name} | {f['quotes']} | {f['checkable']} | {f['exact']} ({f['exact'] / c:.1%}) | {f['exact_or_nli']} ({f['exact_or_nli'] / c:.1%}) | "
                f"{f['unsupported']} ({f['unsupported'] / c:.1%}) |")

    def srow(name: str, m: dict) -> str:
        d = m["diff"]
        return f"| {name} | {m['agent']:.3f} | {m['oneshot']:.3f} | {d[0]:+.3f} [{d[1]:+.3f}, {d[2]:+.3f}] |"

    return ["", "## 사후 분석(사전 등록 밖) — 같은 인용 판정기를 양쪽에 대칭으로", "",
            "에이전트는 finding의 근거 문장(evidence_fact, LLM이 쓴 요약)을, 원샷은 가이던스 문장(guidance_quote, 모델 기억)을 인용 문서의 조항과 대조한다. "
            "NLI 의역 판정은 인용 문서 안에서 6-gram이 가장 많이 겹치는 조항 3개만 보고(entailment ≥ 0.7), 판정 모델은 에이전트 검증기와 같은 DeBERTa다 "
            "(에이전트는 이 판정기를 통과하도록 보류·재작성 루프를 거치므로 에이전트에 유리한 비대칭).", "",
            "| 쪽 | 인용 문장 | 검사 가능 | 원문 일치 | 일치 또는 NLI 의역 | 둘 다 아님 |", "|---|---|---|---|---|---|",
            row("에이전트(2회)", fa), row("원샷(2회)", fo), "",
            f"에이전트가 근거로 붙인 규제 조항 인용문(evidence.quote) 자체는 {fe['verbatim']}/{fe['n']}건이 코퍼스 원문이다(정규화한 앞 200자 포함 기준, 검색 결과를 그대로 싣는 구조).", "",
            "| 인용 필터(양쪽 동일) | 에이전트 grounded | 원샷 grounded | 차이(원샷 − 에이전트) [95% CI] |", "|---|---|---|---|",
            srow("원문 일치만 인정", sym["exact"]), srow("원문 일치 또는 NLI 의역 인정", sym["nli"]), "",
            "판정 기준(문자열만 / NLI 포함)에 따라 원샷 값이 크게 달라진다. 임계값·조항 3개는 결과를 본 뒤 정한 단일 설정이다. "
            "'둘 다 아님'은 '인용 문서의 가까운 조항 3개로 확인되지 않음'이지 '어느 원문으로도 뒷받침되지 않음'이 아니다. 사후 분석이므로 1차 판정(차이 확인 안 됨)을 바꾸지 않는다."]


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
        v = ("에이전트 우위" if g[2] < 0 else "원샷 우위" if g[1] > 0 else "차이 확인 안 됨") if name.startswith("oneshot") else "기술용(1회)"   # 사전 등록: single_rag6는 기술용
        out["arms"][name] = {"n": g[3], "grounded_agent": round(ga, 3), "grounded_arm": round(gb, 3), "grounded_diff": [round(x, 3) for x in g[:3]],
                             "span_diff": [round(x, 3) for x in sp[:3]], "precision_diff": [round(x, 3) for x in pr[:3]],
                             "tokens_agent": round(ta), "tokens_arm": round(tb), "verdict": v}
        L.append(f"| {name} | {g[3]} | {ga:.3f} / {gb:.3f} | {g[0]:+.3f} [{g[1]:+.3f}, {g[2]:+.3f}] | {sp[0]:+.3f} [{sp[1]:+.3f}, {sp[2]:+.3f}] | "
                 f"{pr[0]:+.3f} [{pr[1]:+.3f}, {pr[2]:+.3f}] | {ta:,.0f} / {tb:,.0f} |")
    L += ["", "1차 판정(grounded, 원샷 2회 평균): **" + out["arms"]["oneshot(2회 평균)"]["verdict"] + "** (CI 상한 < 0 → 에이전트 우위, 하한 > 0 → 원샷 우위). "
          "사전 등록 문서는 '에이전트 − 원샷'으로 적었고 이 표는 부호가 반대(팔 − 에이전트)다. 판정은 같다.", "",
          "## 인용 충실도(베이스라인 가이던스 문장이 코퍼스 실제 조항과 일치하는 비율)", "",
          "| 실행 | 인용문 수 | 일치 | 비율(전체) | 본문 미색인 문서 인용(검사 불가) | 비율(검사 가능분) |", "|---|---|---|---|---|---|"]
    out["quote_fidelity"] = {}
    for cfg in ("oneshot", "oneshot_r2", "single_rag6"):
        if (RES / f"{cfg}.json").exists():
            q = quote_fidelity(cfg)
            out["quote_fidelity"][cfg] = q
            L.append(f"| {cfg} | {q['n_quotes']} | {q['matched']} | {q['rate']} | {q['unknown_doc_id']} | {q['rate_checkable']} |")
    L += ["", "검사 불가는 목록에는 있지만 코퍼스에 본문이 색인되지 않은 문서(CTTI-QBD 등)를 인용한 경우다. '일치' = 정규화 문자열 포함, 인용문 6-gram의 50% 이상이 한 조항에 있음, 또는 Jaccard ≥ 0.5."]
    L += post_hoc(agent, out)
    (RES / "oneshot_compare.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    (RES / "ONESHOT_REPORT.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
