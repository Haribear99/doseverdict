"""
사후 재채점 — 저장된 평가 상태(results/states/<config>/*.json)에 근거 재선택(reselect_evidence, 로컬 NLI)과 검증기를 다시 적용해
LLM 재호출 없이 새 설정의 지표를 만든다. 기각 finding의 재작성(LLM)은 하지 않으므로 검증 통과율은 하한이다.

실행: .venv/Scripts/python.exe -m app.eval.rescore --config full --suffix rerank  →  results/full_rerank.json, states/full_rerank/
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone

from app.agents.findings import reselect_evidence, verify_findings
from app.corpus.manifest import DOCS
from app.eval.run_eval import DATA, OUT, elapsed_from_audit, score_case
from app.schema.trial_schema import ReviewState


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="full")
    ap.add_argument("--suffix", default="rerank")
    a = ap.parse_args()
    title2id = {d.title: d.doc_id for d in DOCS}
    gold = {c["case_id"]: c for c in (json.loads(l) for l in (DATA / "gold_axis1.jsonl").read_text(encoding="utf-8").splitlines() if l.strip())}
    src, dst = OUT / "states" / a.config, OUT / "states" / f"{a.config}_{a.suffix}"
    dst.mkdir(parents=True, exist_ok=True)
    rows = []
    for p in sorted(src.glob("*.json")):
        c = gold.get(p.stem)
        if not c:
            continue
        st = ReviewState.model_validate_json(p.read_text(encoding="utf-8"))
        n_added = reselect_evidence(st)
        verify_findings(st)
        (dst / p.name).write_text(st.model_dump_json(indent=1), encoding="utf-8")
        fs = st.findings
        texts = [f"{f.protocol_span.text} {f.protocol_fact or ''} {f.evidence_fact or ''}" for f in fs]
        docs = [{title2id.get(st.evidence[e].document_title or "", "") for e in f.evidence_ids if e in st.evidence} for f in fs]
        row = {"case_id": c["case_id"], "config": f"{a.config}_{a.suffix}", "tokens": st.budget.used_tokens,
               "elapsed_s": elapsed_from_audit(f"eval-{a.config}-{c['case_id']}") or 0.0,
               "verified_rate": round(sum(1 for f in fs if f.verifier_status == "verified") / max(1, len(fs)), 3), "n_reselected": n_added} | score_case(c, texts, len(fs), docs)
        rows.append(row)
        print(json.dumps(row, ensure_ascii=False))
    agg = {k: round(sum(r[k] for r in rows) / len(rows), 3) for k in ("recall", "weighted_recall", "grounded_recall", "grounded_weighted_recall", "precision_proxy", "tokens", "elapsed_s")}
    agg["verified_rate"] = round(sum(r["verified_rate"] for r in rows) / len(rows), 3)
    agg["n_reselected"] = sum(r["n_reselected"] for r in rows)
    out = {"config": f"{a.config}_{a.suffix}", "n_cases": len(rows), "aggregate": agg, "rows": rows, "at": datetime.now(timezone.utc).isoformat(),
           "note": "사후 재채점: 저장 상태 + reselect_evidence + verify_findings(재작성 없음)"}
    (OUT / f"{a.config}_{a.suffix}.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print("aggregate:", json.dumps(agg, ensure_ascii=False))


if __name__ == "__main__":
    main()
