"""
평가 러너 — 축①(결함 주입 Silver Set) 위에서 Full / ablation / 베이스라인을 같은 지표로 비교한다.

설정:
  full          전체 파이프라인
  no_calc       계산 모듈(RDKit·ChEMBL·TCR·시뮬) 제거
  no_arena      Adversarial Reviewer 제거
  no_verifier   Citation Verifier 제거(모든 finding을 verified 처리)
  checklist     키워드·정규식 체크리스트(LLM 없음)
  single_rag    단일 LLM(Sol) + 코퍼스 검색 1회 후 답변(멀티에이전트 없음)

매칭: 주입 결함의 protocol_sentence가 finding의 protocol_span/protocol_fact와 겹치면(정규화 후 6-gram Jaccard ≥ 0.25 또는 부분 포함) 적중.
지표: 중증도 가중 Recall(critical 4·high 3·medium 2·low 1), Precision(적중 finding/전체 finding), 검증 통과율, 토큰/케이스, Time-to-first-gap.
실행: .venv/Scripts/python.exe -m app.eval.run_eval --configs full,no_calc,checklist --limit 5
"""
from __future__ import annotations

import argparse
import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DATA = Path(__file__).resolve().parent / "data"
OUT = DATA / "results"
W = {"critical": 4, "high": 3, "medium": 2, "low": 1}


def _norm(t: str) -> str:
    return re.sub(r"[^0-9a-z가-힣%]", "", (t or "").lower())


def _grams(t: str, n: int = 6) -> set[str]:
    t = _norm(t)
    return {t[i:i + n] for i in range(len(t) - n + 1)} if len(t) >= n else {t}


def matches(defect_sentence: str, finding_texts: list[str]) -> bool:
    d = _norm(defect_sentence)
    g = _grams(defect_sentence)
    for ft in finding_texts:
        f = _norm(ft)
        if not f:
            continue
        if d in f or f in d:
            return True
        gf = _grams(ft)
        if len(g & gf) / max(1, len(g | gf)) >= 0.25:
            return True
    return False


# ----------------------------------------------------------------- 베이스라인
_CHECKLIST = [
    (r"MTD (will|shall|is) (be )?(selected|used|taken|designated) as (the )?RP2D", "dose_optimization", "high"),
    (r"no randomi[sz]ed comparison|single (dose|expansion)|without (dose|dosage) comparison", "dose_optimization", "high"),
    (r"3\+3", "dose_optimization", "medium"),
    (r"every (6|8|12) weeks.*(liver|ALT|AST)|(liver|ALT|AST).*every (6|8|12) weeks", "safety_monitoring", "high"),
    (r"no washout|without (a )?washout|washout (is )?not required", "eligibility", "medium"),
    (r"sparse PK|pre-dose (and|only)|single PK sample", "dose_optimization", "medium"),
    (r"expansion cohort.*(without|no) (rationale|justification|endpoint)", "endpoint_ctq", "medium"),
]


def run_checklist(text: str) -> list[dict[str, Any]]:
    out = []
    for pat, cat, sev in _CHECKLIST:
        for m in re.finditer(pat, text, flags=re.I):
            line = text[max(0, text.rfind("\n", 0, m.start()) + 1): text.find("\n", m.end()) if text.find("\n", m.end()) > 0 else len(text)]
            out.append({"span": line.strip(), "category": cat, "severity": sev})
    return out


def run_single_rag(gc, text: str) -> tuple[list[dict[str, Any]], int]:
    from app.corpus.index import CorpusIndex
    idx = CorpusIndex.get()
    hits = idx.search("dose optimization expansion cohort escalation safety monitoring eligibility", k=8)
    ctx = "\n\n".join(f"[{h['doc_id']} · {h['heading']}] {h['text'][:700]}" for h in hits)
    schema = {"type": "json_schema", "name": "rag_findings", "strict": False, "schema": {"type": "object", "properties": {"findings": {"type": "array", "items": {"type": "object", "properties": {
        "span": {"type": "string"}, "category": {"type": "string"}, "severity": {"type": "string"}, "claim": {"type": "string"}}}}}}}
    resp, rec = gc.respond("planner", f"<guidance>\n{ctx}\n</guidance>\n<protocol_document>\n{text}\n</protocol_document>\nList protocol defects with verbatim spans.",
                           instructions="You are a single-pass protocol reviewer. Using only the guidance excerpts, list defects (verbatim span, category, severity, claim). JSON only.",
                           text_format=schema, reasoning_effort="low", max_output_tokens=3000, purpose="eval_single_rag")
    try:
        rows = json.loads(resp.output_text).get("findings", [])
    except json.JSONDecodeError:
        rows = []
    return rows, int((rec.usage or {}).get("total_tokens") or 0)


# ----------------------------------------------------------------- 평가
def score_case(case: dict, finding_texts: list[str], n_findings: int) -> dict[str, Any]:
    defs = case["defects"]
    hit = [matches(d["protocol_sentence"], finding_texts) for d in defs]
    wsum = sum(W.get(d["severity"], 1) for d in defs) or 1
    wrec = sum(W.get(d["severity"], 1) for d, h in zip(defs, hit) if h) / wsum
    rec = sum(hit) / max(1, len(defs))
    return {"n_defects": len(defs), "n_hit": sum(hit), "recall": round(rec, 3), "weighted_recall": round(wrec, 3),
            "n_findings": n_findings, "precision_proxy": round(sum(hit) / n_findings, 3) if n_findings else 0.0}


def evaluate(config: str, cases: list[dict], gc=None) -> dict[str, Any]:
    from app.agents.graph import run_until_gate
    rows = []
    for c in cases:
        t0 = time.perf_counter()
        tokens, first_gap, verified_rate = 0, None, None
        if config == "checklist":
            fs = run_checklist(c["synopsis"])
            texts = [f["span"] for f in fs]
        elif config == "single_rag":
            fs, tokens = run_single_rag(gc, c["synopsis"])
            texts = [f"{f.get('span', '')} {f.get('claim', '')}" for f in fs]
        else:
            ablate = {"full": [], "no_calc": ["no_calc"], "no_arena": ["no_arena"], "no_verifier": ["no_verifier"]}[config]
            _, _, st = run_until_gate(c["synopsis"], run_id=f"eval-{config}-{c['case_id']}", ablate=ablate, holdout_chunk_ids=c.get("holdout_chunk_ids"))
            fs = st.findings
            texts = [f"{f.protocol_span.text} {f.protocol_fact or ''}" for f in fs]
            tokens = st.budget.used_tokens
            verified_rate = round(sum(1 for f in fs if f.verifier_status == "verified") / max(1, len(fs)), 3)
        elapsed = round(time.perf_counter() - t0, 1)
        row = {"case_id": c["case_id"], "config": config, "tokens": tokens, "elapsed_s": elapsed, "verified_rate": verified_rate} | score_case(c, texts, len(fs))
        rows.append(row)
        print(json.dumps(row, ensure_ascii=False))
    agg = {k: round(sum(r[k] for r in rows) / len(rows), 3) for k in ("recall", "weighted_recall", "precision_proxy", "tokens", "elapsed_s")}
    agg["verified_rate"] = round(sum(r["verified_rate"] or 0 for r in rows) / len(rows), 3)
    return {"config": config, "n_cases": len(rows), "aggregate": agg, "rows": rows, "at": datetime.now(timezone.utc).isoformat()}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--configs", default="checklist,full")
    ap.add_argument("--limit", type=int, default=5)
    ap.add_argument("--gold", default=str(DATA / "gold_axis1.jsonl"))
    a = ap.parse_args()
    cases = [json.loads(l) for l in Path(a.gold).read_text(encoding="utf-8").splitlines() if l.strip()][: a.limit]
    OUT.mkdir(parents=True, exist_ok=True)
    gc = None
    if any(c in ("single_rag",) for c in a.configs.split(",")):
        from app.llm.client import GatewayClient
        gc = GatewayClient(audit_path="logs/eval_runs.jsonl")
    summary = []
    for cfg in a.configs.split(","):
        res = evaluate(cfg.strip(), cases, gc)
        (OUT / f"{cfg.strip()}.json").write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")
        summary.append({"config": cfg.strip(), **res["aggregate"], "n": res["n_cases"]})
    print("\n| config | n | recall | weighted_recall | precision_proxy | verified | tokens/case | s/case |")
    print("|---|---|---|---|---|---|---|---|")
    for s in summary:
        print(f"| {s['config']} | {s['n']} | {s['recall']} | {s['weighted_recall']} | {s['precision_proxy']} | {s['verified_rate']} | {s['tokens']:,.0f} | {s['elapsed_s']} |")
    (OUT / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
