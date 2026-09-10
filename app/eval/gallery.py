"""
실패 사례 갤러리 — 평가 상태 파일(results/states/<config>/*.json)과 gold set을 대조해
놓친 결함(miss)·근거 없이 경고한 finding(false alarm 후보)·기권/보류를 표로 만든다. LLM 호출 없음.

실행: .venv/Scripts/python.exe -m app.eval.gallery --config full  →  app/eval/data/results/gallery_<config>.md
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from app.eval.run_eval import DATA, OUT, _grounded, matches


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="full")
    a = ap.parse_args()
    gold = {c["case_id"]: c for c in (json.loads(l) for l in (DATA / "gold_axis1.jsonl").read_text(encoding="utf-8").splitlines() if l.strip())}
    sdir = OUT / "states" / a.config
    lines = [f"# 실패 사례 갤러리 — {a.config}", "", "놓친 결함과 잘못 경고한 사례를 그대로 공개한다(제안서 4장 약속).", ""]
    tot_miss = tot_fa = tot_def = tot_find = 0
    for p in sorted(sdir.glob("*.json")):
        st = json.loads(p.read_text(encoding="utf-8"))
        case = gold.get(p.stem)
        if not case:
            continue
        fs = st["findings"]
        texts = [f"{f['protocol_span']['text']} {f.get('protocol_fact') or ''} {f.get('evidence_fact') or ''}" for f in fs]
        lines.append(f"## {p.stem} — finding {len(fs)}건, 주입 결함 {len(case['defects'])}건, 토큰 {st['budget']['used_tokens']:,}")
        lines.append("")
        lines.append("| 결과 | 주입 결함(요약) | 원 규범 문서 | 매칭 finding |")
        lines.append("|---|---|---|---|")
        for d in case["defects"]:
            hit_ids = [f["finding_id"] for f, t in zip(fs, texts) if matches(d["protocol_sentence"], [t])]
            g = _grounded(d, [set() for _ in fs], texts)
            tag = "✅ 근거까지 적중" if g else ("🟡 span만 적중" if hit_ids else "❌ 놓침")
            tot_def += 1; tot_miss += 0 if hit_ids else 1
            lines.append(f"| {tag} | {d['protocol_sentence'][:110]} | {d['source_doc']} · {d['source_section'][:30]} | {', '.join(hit_ids) or '-'} |")
        lines.append("")
        matched = {f["finding_id"] for f, t in zip(fs, texts) for d in case["defects"] if matches(d["protocol_sentence"], [t])}
        extra = [f for f in fs if f["finding_id"] not in matched and not f["finding_id"].startswith(("F00", "V"))]
        tot_find += len(fs); tot_fa += len(extra)
        if extra:
            lines.append("주입 결함과 무관한 finding(정상판 기준 잘못 경고 후보, 사람 검토 필요):")
            for f in extra:
                lines.append(f"- {f['finding_id']} [{f['severity']}/{f['verifier_status']}] {f['claim'][:140]}")
            lines.append("")
    lines.insert(3, f"합계: 주입 결함 {tot_def}건 중 놓침 {tot_miss}건, finding {tot_find}건 중 무관 {tot_fa}건.")
    out = OUT / f"gallery_{a.config}.md"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"→ {out}  (defects {tot_def}, miss {tot_miss}, findings {tot_find}, unrelated {tot_fa})")


if __name__ == "__main__":
    main()
