"""
평가 축 ① — 규범 문장에서 기계적으로 유도한 결함 주입 (Silver Set 생성기).

절차(제안서 4장):
  1) 코퍼스 청크의 normative_sentences(should/must/권장…)에서 요구사항을 뽑는다 → 정답 라벨의 근거는 공식 문서 원문 그 자체
  2) 각 요구사항을 위반하는 프로토콜 문장을 Luna가 합성(원문과 어휘 중복이 낮도록 재작성) → 주입기(luna) ≠ 검출기(sol/terra)
  3) 주입에 쓴 규범 문장의 chunk_id는 해당 인스턴스의 검색에서 hold-out(누수 차단) → gold.jsonl의 holdout_chunk_ids
  4) 합성 synopsis = 기준 시놉시스(정상판) + 주입 문장 N개 치환

실행:  .venv/Scripts/python.exe -m app.eval.inject --n-cases 20 --defects-per-case 6  →  app/eval/data/gold_axis1.jsonl
"""
from __future__ import annotations

import argparse
import json
import random
import re
from datetime import datetime, timezone
from pathlib import Path

from app.corpus.index import CorpusIndex
from app.llm.client import GatewayClient

DATA = Path(__file__).resolve().parent / "data"
BASE = Path(__file__).resolve().parents[1] / "demo" / "sotorasib_synopsis_fixed.md"

_SCHEMA = {"type": "json_schema", "name": "injected_defect", "strict": False,
           "schema": {"type": "object", "properties": {
               "requirement": {"type": "string", "description": "the normative requirement restated in plain words"},
               "protocol_sentence": {"type": "string", "description": "a realistic protocol sentence that VIOLATES the requirement; do not reuse the guidance wording"},
               "target_section": {"type": "string", "enum": ["Dose Escalation", "Dose Optimization and Expansion", "Pharmacokinetics", "Eligibility (key)", "Safety Monitoring", "Visit Schedule", "Objectives"]},
               "defect_category": {"type": "string", "enum": ["dose_optimization", "safety_monitoring", "eligibility", "endpoint_ctq", "burden", "source_version", "feasibility"]},
               "severity": {"type": "string", "enum": ["critical", "high", "medium", "low"]},
               "lexical_overlap_note": {"type": "string"}}}}

_INSTR = """You generate evaluation data for a clinical-protocol review agent. Given ONE normative sentence from a regulatory document,
write ONE realistic oncology Phase 1/2 protocol sentence that violates it. Rules: paraphrase — do not copy the guidance wording (keep lexical overlap low);
the violation must be checkable from the sentence alone; pick the protocol section it belongs to; rate severity from the participant-safety/decision impact.
Return JSON only."""


_EXCLUDE_DOCS = {"FDA-AI-CREDIBILITY-2025-DRAFT"}   # 우리 시스템 자신에 대한 문서 — 프로토콜 결함 주입 대상 아님
_BOILERPLATE = re.compile(r"use of the word should|nonbinding recommendations|does not establish any rights|contains nonbinding|^\d+\s", re.I)


def candidate_requirements(min_len: int = 60, max_per_doc: int = 40, seed: int = 7) -> list[dict]:
    idx = CorpusIndex(load_dense=False)
    rng = random.Random(seed)
    by_doc: dict[str, list[dict]] = {}
    for c in idx.clauses:
        if c["doc_id"] in _EXCLUDE_DOCS:
            continue
        for s in c.get("normative_sentences", []):
            s = re.sub(r"\s+\d{1,3}\s+", " ", re.sub(r"\s+", " ", s)).strip()   # 초안 PDF 행번호 제거
            if len(s) < min_len or "....." in s or _BOILERPLATE.search(s):
                continue
            by_doc.setdefault(c["doc_id"], []).append({"chunk_id": c["chunk_id"], "doc_id": c["doc_id"], "section": c["heading"],
                                                       "jurisdiction": c["jurisdiction"], "norm_strength": c["norm_strength"], "sentence": s})
    out = []
    for doc, rows in by_doc.items():
        rng.shuffle(rows)
        out.extend(rows[:max_per_doc])
    rng.shuffle(out)
    return out


def inject_one(gc: GatewayClient, req: dict) -> dict | None:
    resp, rec = gc.respond("bulk", json.dumps({"normative_sentence": req["sentence"], "document": req["doc_id"], "section": req["section"]}, ensure_ascii=False),
                           instructions=_INSTR, text_format=_SCHEMA, reasoning_effort="none", max_output_tokens=400, purpose="eval_inject")
    try:
        d = json.loads(resp.output_text)
    except json.JSONDecodeError:
        return None
    if not d.get("protocol_sentence"):
        return None
    return d | {"holdout_chunk_id": req["chunk_id"], "source_doc": req["doc_id"], "source_section": req["section"], "source_sentence": req["sentence"],
                "jurisdiction": req["jurisdiction"], "norm_strength": req["norm_strength"], "usage": rec.usage}


def build_cases(defects: list[dict], n_cases: int, per_case: int, seed: int = 11, start: int = 1) -> list[dict]:
    base = BASE.read_text(encoding="utf-8")
    rng = random.Random(seed)
    cases = []
    for i in range(n_cases):
        chosen = rng.sample(defects, min(per_case, len(defects)))
        text = base
        injected = []
        for d in chosen:
            sec = d["target_section"]
            m = re.search(rf"^## {re.escape(sec)}\n(.*?)(?=^## |\Z)", text, flags=re.S | re.M)
            if not m:
                continue
            body = m.group(1).rstrip("\n")
            new_body = body + f"\n{d['protocol_sentence']}\n\n"
            text = text[:m.start(1)] + new_body + text[m.end(1):]
            injected.append(d)
        cases.append({"case_id": f"AX1-{i + start:03d}", "synopsis": text, "defects": [{k: v for k, v in d.items() if k != "usage"} for d in injected],
                      "holdout_chunk_ids": [d["holdout_chunk_id"] for d in injected], "created_at": datetime.now(timezone.utc).isoformat()})
    return cases


def extend(gc: GatewayClient, n_cases: int, per_case: int, e6r3_max: int = 20) -> None:
    """확장 세트: 기존 결함에 쓰지 않은 규범 문장만 새로 주입해 AX1-021부터 케이스를 만든다(원 20케이스와 결함 비중복).

    코퍼스 규범 문장 702개 중 71%가 ICH E6(R3) 일반 GCP 문장이라 상한 없이 늘리면 용량 특이성이 희석된다
    (interim-report-eval-budget-cases-vs-repeats-and-silver-set-validity) → E6(R3)만 e6r3_max로 제한하고 나머지 문서는 전부 쓴다.
    """
    old = [json.loads(l) for l in (DATA / "defects_axis1.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    used = {d["source_sentence"] for d in old}
    n_old = sum(1 for l in (DATA / "gold_axis1.jsonl").read_text(encoding="utf-8").splitlines() if l.strip())
    fresh = [r for r in candidate_requirements(max_per_doc=10**6, seed=23) if r["sentence"] not in used]
    e6 = [r for r in fresh if r["doc_id"] == "ICH-E6R3-2025"][:e6r3_max]
    reqs = [r for r in fresh if r["doc_id"] != "ICH-E6R3-2025"] + e6
    print(f"fresh normative sentences: {len(reqs)} (E6R3 {len(e6)})")
    defects = [d for d in (inject_one(gc, r) for r in reqs) if d]
    (DATA / "defects_axis1_ext.jsonl").write_text("\n".join(json.dumps(d, ensure_ascii=False) for d in defects) + "\n", encoding="utf-8")
    cases = build_cases(defects, n_cases, per_case, seed=23, start=n_old + 1)
    (DATA / "gold_axis1_ext.jsonl").write_text("\n".join(json.dumps(c, ensure_ascii=False) for c in cases) + "\n", encoding="utf-8")
    tot = gc.audit_totals()
    print(f"ext defects {len(defects)}, cases {len(cases)} (injected {sum(len(c['defects']) for c in cases)}), audit tokens {sum(v['total'] for v in tot['by_model'].values()):,}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-cases", type=int, default=20)
    ap.add_argument("--defects-per-case", type=int, default=6)
    ap.add_argument("--max-requirements", type=int, default=140)
    ap.add_argument("--extend", action="store_true", help="기존 결함과 비중복인 확장 세트 생성 → gold_axis1_ext.jsonl")
    a = ap.parse_args()
    DATA.mkdir(parents=True, exist_ok=True)
    gc = GatewayClient(audit_path="logs/eval_inject.jsonl")
    if a.extend:
        extend(gc, a.n_cases, a.defects_per_case)
        return
    reqs = candidate_requirements()[: a.max_requirements]
    print(f"candidate normative sentences: {len(reqs)}")
    defects = []
    for i, r in enumerate(reqs, 1):
        d = inject_one(gc, r)
        if d:
            defects.append(d)
        if i % 20 == 0:
            print(f"  {i}/{len(reqs)} → defects {len(defects)}")
    (DATA / "defects_axis1.jsonl").write_text("\n".join(json.dumps(d, ensure_ascii=False) for d in defects) + "\n", encoding="utf-8")
    cases = build_cases(defects, a.n_cases, a.defects_per_case)
    (DATA / "gold_axis1.jsonl").write_text("\n".join(json.dumps(c, ensure_ascii=False) for c in cases) + "\n", encoding="utf-8")
    tot = gc.audit_totals()
    print(f"defects {len(defects)}, cases {len(cases)} (total injected {sum(len(c['defects']) for c in cases)}), tokens {sum(v['total'] for v in tot['by_model'].values()):,}")


if __name__ == "__main__":
    main()
