"""
grounded recall 실패 원인 분류 — span은 맞췄지만 정답 규범 문서를 인용하지 못한 결함을
(a) 규제 근거 인용 없음 (b) 계산·라벨 등 비규제 근거만 인용 (c) 다른 규제 문서 인용 으로 나눈다. LLM 호출 없음.

전제: 평가 시 결함의 출처 절(hold-out chunk)은 검색에서 제외되므로, 정답 문서를 인용하려면 같은 문서의 다른 절을 찾아야 한다.

실행: .venv/Scripts/python.exe -m app.eval.diagnose --config full  →  app/eval/data/results/diagnose_<config>.md
"""
from __future__ import annotations

import argparse
import json
from collections import Counter

from app.corpus.manifest import DOCS
from app.eval.run_eval import DATA, OUT, _grams, matches

NON_REGULATORY = {"calculation", "database_record", "analog_trial", "label_statement"}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="full")
    a = ap.parse_args()
    title2id = {d.title: d.doc_id for d in DOCS}
    gold = {c["case_id"]: c for c in (json.loads(l) for l in (DATA / "gold_axis1.jsonl").read_text(encoding="utf-8").splitlines() if l.strip())}
    reasons: Counter = Counter(); missed_src: Counter = Counter(); cited_instead: Counter = Counter(); pairs: Counter = Counter()
    total = 0
    for p in sorted((OUT / "states" / a.config).glob("*.json")):
        case = gold.get(p.stem)
        if not case:
            continue
        st = json.loads(p.read_text(encoding="utf-8"))
        fs, ev = st["findings"], st["evidence"]
        for d in case["defects"]:
            hits = [f for f in fs if matches(d["protocol_sentence"], [f"{f['protocol_span']['text']} {f.get('protocol_fact') or ''} {f.get('evidence_fact') or ''}"])]
            if not hits:
                continue
            docs, kinds = set(), set()
            for f in hits:
                for e in f["evidence_ids"]:
                    docs.add(title2id.get(ev[e].get("document_title") or "", ev[e]["kind"])); kinds.add(ev[e]["kind"])
            g1 = _grams(d["source_sentence"])
            overlap = max((len(g1 & _grams(f.get("evidence_fact") or "")) / max(1, len(g1 | _grams(f.get("evidence_fact") or ""))) for f in hits), default=0)
            total += 1
            if d["source_doc"] in docs or overlap >= 0.15:
                reasons["grounded"] += 1
                continue
            missed_src[d["source_doc"]] += 1
            reg = {x for x in docs if x not in NON_REGULATORY}
            if not docs:
                reasons["no_evidence"] += 1
            elif not reg:
                reasons["non_regulatory_only"] += 1
            else:
                reasons["other_regulatory_doc"] += 1
                cited_instead.update(reg)
                for x in reg:
                    pairs[(d["source_doc"], x)] += 1
    # Verifier 변별력: 판정(verified/held/rejected)별로 finding이 주입 결함을 가리킨 비율 — 검증기는 recall이 아니라 이 차이로 평가한다
    hit_by: Counter = Counter(); tot_by: Counter = Counter()
    for p in sorted((OUT / "states" / a.config).glob("*.json")):
        case = gold.get(p.stem)
        if not case:
            continue
        st = json.loads(p.read_text(encoding="utf-8"))
        for f in st["findings"]:
            if f["finding_id"].startswith(("F00", "V")):
                continue
            t = f"{f['protocol_span']['text']} {f.get('protocol_fact') or ''} {f.get('evidence_fact') or ''}"
            tot_by[f["verifier_status"]] += 1
            if any(matches(d["protocol_sentence"], [t]) for d in case["defects"]):
                hit_by[f["verifier_status"]] += 1
    lines = [f"# grounded recall 실패 원인 — {a.config}", "",
             f"span 적중 결함 {total}건 중 grounded {reasons['grounded']}건 / 규제 근거 인용 없음 {reasons['no_evidence']}건 / 비규제 근거만 {reasons['non_regulatory_only']}건 / **다른 규제 문서 인용 {reasons['other_regulatory_doc']}건**.", "",
             "출처 절(hold-out)은 검색에서 제외되므로 정답 문서 인용은 같은 문서의 다른 절을 찾은 경우다.", "",
             "| 정답 문서 | 놓친 수 |", "|---|---|"] + [f"| {k} | {v} |" for k, v in missed_src.most_common()] + \
            ["", "| 정답 문서 → 대신 인용한 문서 | 건수 |", "|---|---|"] + [f"| {k[0]} → {k[1]} | {v} |" for k, v in pairs.most_common()]
    lines += ["", "## Verifier 판정별 주입 결함 적중률 (F00·V 제외)", "", "| 판정 | finding 수 | 결함 적중 | 적중률 |", "|---|---|---|---|"] +              [f"| {k} | {tot_by[k]} | {hit_by[k]} | {hit_by[k] / tot_by[k]:.2f} |" for k in sorted(tot_by)]
    out = OUT / f"diagnose_{a.config}.md"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
