"""
특이도 평가 — 사전 등록 docs/specificity_prereg.md.

  python -m app.eval.specificity a            평가 A: 기존 저장 상태(lean_v3·lean_v3b·lean_mdrug3)의 문장 단위 민감도·특이도(토큰 0)
  python -m app.eval.specificity run_clean    평가 B: 결함 없는 기준 시놉시스 4종 × 3회 실행
  python -m app.eval.specificity run_patch    평가 C: 수정안 적용판(원 20 중 수정안 있는 케이스) 재검토 1회
  python -m app.eval.specificity report       A·B·C 합쳐 results/SPECIFICITY_REPORT.md, results/specificity.json
"""
from __future__ import annotations

import argparse
import json
import random
import re
from pathlib import Path

from app.eval.run_eval import matches

ROOT = Path(__file__).resolve().parents[2]
DATA = Path(__file__).resolve().parent / "data"
OUT = DATA / "results"
BASES = {"AX1": "sotorasib_synopsis_fixed.md", "AXD-ADAGRASIB": "adagrasib_synopsis_fixed.md",
         "AXD-LORLATINIB": "lorlatinib_synopsis_fixed.md", "AXD-DV505": "dv505_synopsis_fixed.md"}
RUNS_A = [("lean_v3", "gold_axis1.jsonl"), ("lean_v3b", "gold_axis1.jsonl"), ("lean_mdrug3", "gold_axis1_multidrug.jsonl")]


def base_for(case_id: str) -> str:
    key = "AX1" if case_id.startswith("AX1") else "-".join(case_id.split("-")[:2])
    return BASES[key]


def sentences(text: str) -> list[str]:
    """기준 시놉시스 → 문장 목록. 제목(#)·20자 미만·굵은 머리표 줄은 빼고, 글머리표를 벗긴다."""
    out = []
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or line.startswith(">") or re.match(r"^\*\*(Title|Sponsor)[:*]", line):
            continue   # 제목·스폰서·가상 약 고지 같은 메타데이터 줄은 지적 대상이 아니므로 뺀다(특이도 부풀림 방지)
        line = re.sub(r"^[-*]\s+", "", line)
        for sent in re.split(r"(?<=[.;])\s+(?=[A-Z(])", line):
            sent = sent.strip()
            if len(sent) >= 20:
                out.append(sent)
    return out


def flagged(sents: list[str], spans: list[str]) -> list[bool]:
    return [any(matches(s, [sp]) for sp in spans) for s in sents]


def defect_spans(st: dict) -> list[str]:
    return [f["protocol_span"]["text"] for f in st["findings"] if f.get("verdict") == "defect" and f["finding_id"] != "F00"]


def _boot(rows: list[dict], n: int = 5000, seed: int = 0) -> dict:
    rng = random.Random(seed)

    def stat(rs):
        tp = sum(r["inj_hit"] for r in rs); p = sum(r["inj_n"] for r in rs)
        fp = sum(r["base_hit"] for r in rs); ng = sum(r["base_n"] for r in rs)
        sens, spec = tp / max(1, p), 1 - fp / max(1, ng)
        return sens, spec, sens + spec - 1
    point = stat(rows)
    boots = sorted((stat([rng.choice(rows) for _ in rows]) for _ in range(n)), key=lambda x: x[2])
    js = sorted(b[2] for b in boots); ss = sorted(b[0] for b in boots); ps = sorted(b[1] for b in boots)
    ci = lambda xs: [round(xs[int(0.025 * n)], 3), round(xs[int(0.975 * n) - 1], 3)]
    return {"sensitivity": round(point[0], 3), "sensitivity_ci": ci(ss), "specificity": round(point[1], 3), "specificity_ci": ci(ps),
            "youden_j": round(point[2], 3), "youden_ci": ci(js), "n_cases": len(rows)}


def eval_a(runs: list[tuple[str, str]] | None = None) -> dict:
    res, base_counts = {}, {}
    for cfg, gold in runs or RUNS_A:
        cases = [json.loads(l) for l in (DATA / gold).read_text(encoding="utf-8").splitlines() if l.strip()]
        rows = []
        for c in cases:
            sp = OUT / "states" / cfg / f"{c['case_id']}.json"
            if not sp.exists():
                continue
            st = json.loads(sp.read_text(encoding="utf-8"))
            spans = defect_spans(st)
            base_s = sentences((ROOT / "app" / "demo" / base_for(c["case_id"])).read_text(encoding="utf-8"))
            inj_s = [d["protocol_sentence"] for d in c["defects"]]
            fb, fi = flagged(base_s, spans), flagged(inj_s, spans)
            for s, f in zip(base_s, fb):
                if f:
                    k = (base_for(c["case_id"]), s)
                    base_counts[k] = base_counts.get(k, 0) + 1
            rows.append({"case_id": c["case_id"], "inj_n": len(inj_s), "inj_hit": sum(fi), "base_n": len(base_s), "base_hit": sum(fb), "n_defect_findings": len(spans)})
        res[cfg] = {"summary": _boot(rows), "rows": rows}
    top = sorted(base_counts.items(), key=lambda kv: -kv[1])[:12]
    res["base_flag_top"] = [{"base": k[0], "sentence": k[1][:200], "n_flagged_cases": v} for k, v in top]
    return res


def run_clean(tag: str = "") -> None:
    from app.agents.graph import run_until_gate
    d = OUT / "states" / f"clean_base{tag}"
    d.mkdir(parents=True, exist_ok=True)
    for base in BASES.values():
        text = (ROOT / "app" / "demo" / base).read_text(encoding="utf-8")
        for rep in range(3):
            sp = d / f"{Path(base).stem}_{rep}.json"
            if sp.exists():
                continue
            _, _, st = run_until_gate(text, run_id=f"clean{tag}-{Path(base).stem}-{rep}", reviewers=["regulatory"])
            sp.write_text(st.model_dump_json(indent=1), encoding="utf-8")
            print(json.dumps({"base": base, "rep": rep, "tokens": st.budget.used_tokens, "findings": len(st.findings)}), flush=True)


def patched_cases() -> list[dict]:
    """원 20 × lean_v3 수정안을 원문 span에 치환한 수정판(결정론). 수정안이 하나도 없는 케이스는 뺀다."""
    out = []
    for line in (DATA / "gold_axis1.jsonl").read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        c = json.loads(line)
        st = json.loads((OUT / "states" / "lean_v3" / f"{c['case_id']}.json").read_text(encoding="utf-8"))
        from app.agents.patching import apply_patches   # UI "수정안 적용 후 재검토"와 같은 치환 규칙
        text, patches = apply_patches(c["synopsis"], st["findings"])
        if patches:
            out.append({"case_id": c["case_id"], "synopsis": text, "patches": patches, "defects": c["defects"], "holdout_chunk_ids": c.get("holdout_chunk_ids")})
    return out


def run_patch() -> None:
    from app.agents.graph import run_until_gate
    d = OUT / "states" / "patch_v3"
    d.mkdir(parents=True, exist_ok=True)
    cases = patched_cases()
    (DATA / "patched_cases.jsonl").write_text("\n".join(json.dumps(c, ensure_ascii=False) for c in cases) + "\n", encoding="utf-8")
    for c in cases:
        sp = d / f"{c['case_id']}.json"
        if sp.exists():
            continue
        _, _, st = run_until_gate(c["synopsis"], run_id=f"patch-{c['case_id']}", holdout_chunk_ids=c["holdout_chunk_ids"], reviewers=["regulatory"])
        sp.write_text(st.model_dump_json(indent=1), encoding="utf-8")
        print(json.dumps({"case": c["case_id"], "patches": len(c["patches"]), "tokens": st.budget.used_tokens, "findings": len(st.findings)}), flush=True)


def eval_b(tag: str = "") -> dict | None:
    d = OUT / "states" / f"clean_base{tag}"
    if not d.exists():
        return None
    rows = []
    for sp in sorted(d.glob("*.json")):
        st = json.loads(sp.read_text(encoding="utf-8"))
        base = sp.stem.rsplit("_", 1)[0] + ".md"
        base_s = sentences((ROOT / "app" / "demo" / base).read_text(encoding="utf-8"))
        fb = flagged(base_s, defect_spans(st))
        rows.append({"run": sp.stem, "base_n": len(base_s), "base_hit": sum(fb), "n_defect_findings": len(defect_spans(st)), "tokens": st["budget"]["used_tokens"]})
    ng, fp = sum(r["base_n"] for r in rows), sum(r["base_hit"] for r in rows)
    return {"runs": rows, "specificity": round(1 - fp / max(1, ng), 3), "mean_flagged_base_sentences": round(fp / max(1, len(rows)), 2),
            "mean_defect_findings": round(sum(r["n_defect_findings"] for r in rows) / max(1, len(rows)), 2), "tokens_total": sum(r["tokens"] for r in rows)}


def eval_c() -> dict | None:
    d = OUT / "states" / "patch_v3"
    pf = DATA / "patched_cases.jsonl"
    if not d.exists() or not pf.exists():
        return None
    rows = []
    for line in pf.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        c = json.loads(line)
        sp = d / f"{c['case_id']}.json"
        if not sp.exists():
            continue
        after = json.loads(sp.read_text(encoding="utf-8"))
        before = json.loads((OUT / "states" / "lean_v3" / f"{c['case_id']}.json").read_text(encoding="utf-8"))
        spans_after = defect_spans(after)
        re_flag = flagged([p["patch"] for p in c["patches"]], spans_after)
        patched_spans = {p["span"] for p in c["patches"]}
        unpatched_inj = [dd["protocol_sentence"] for dd in c["defects"] if not any(matches(dd["protocol_sentence"], [s]) for s in patched_spans)]
        keep_before = flagged(unpatched_inj, defect_spans(before))
        keep_after = flagged(unpatched_inj, spans_after)
        rows.append({"case_id": c["case_id"], "n_patches": len(c["patches"]), "re_flagged": sum(re_flag),
                     "defects_before": len(defect_spans(before)), "defects_after": len(spans_after),
                     "unpatched_inj_flag_before": sum(keep_before), "unpatched_inj_flag_after": sum(keep_after), "tokens": after["budget"]["used_tokens"]})
    n_p = sum(r["n_patches"] for r in rows)
    return {"rows": rows, "n_cases": len(rows), "n_patches": n_p, "re_flag_rate": round(sum(r["re_flagged"] for r in rows) / max(1, n_p), 3),
            "defects_before_mean": round(sum(r["defects_before"] for r in rows) / max(1, len(rows)), 2),
            "defects_after_mean": round(sum(r["defects_after"] for r in rows) / max(1, len(rows)), 2),
            "unpatched_inj_keep": [sum(r["unpatched_inj_flag_before"] for r in rows), sum(r["unpatched_inj_flag_after"] for r in rows)],
            "tokens_total": sum(r["tokens"] for r in rows)}


def report() -> None:
    a, b, c = eval_a(), eval_b(), eval_c()
    res = {"A": a, "B": b, "C": c}
    (OUT / "specificity.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    L = ["# 특이도 평가 결과 (`python -m app.eval.specificity report`)", "", "사전 등록: `docs/specificity_prereg.md`. 기준 문장 = 결함 없음으로 가정(특이도는 하한).", "",
         "## A. 문장 단위 민감도·특이도(기존 저장 상태)", "", "| 실행 | n | 민감도 [95% CI] | 특이도 [95% CI] | Youden J [95% CI] | 판정 |", "|---|---|---|---|---|---|"]
    for cfg, _ in RUNS_A:
        s = a[cfg]["summary"]
        v = "주입 문장을 골라 짚는다" if s["youden_ci"][0] > 0 else "구별 확인 안 됨"
        L.append(f"| {cfg} | {s['n_cases']} | {s['sensitivity']:.3f} {s['sensitivity_ci']} | {s['specificity']:.3f} {s['specificity_ci']} | {s['youden_j']:.3f} {s['youden_ci']} | {v} |")
    L += ["", "여러 케이스에서 반복 지적된 기준 문장(실제 결함 후보이거나 체계적 오경보 — 사람 확인용):", ""]
    for t in a["base_flag_top"]:
        L.append(f"- [{t['base']}] {t['n_flagged_cases']}케이스: \"{t['sentence']}\"")
    if b:
        L += ["", "## B. 결함 없는 기준 시놉시스 실행(음성 대조)", "",
              f"12회 중 {len(b['runs'])}회 완료. 특이도 {b['specificity']}, 실행당 지적된 기준 문장 {b['mean_flagged_base_sentences']}, defect finding {b['mean_defect_findings']}, 토큰 {b['tokens_total']:,}.", "",
              "| 실행 | 기준 문장 | 지적된 기준 문장 | defect finding |", "|---|---|---|---|"] + [f"| {r['run']} | {r['base_n']} | {r['base_hit']} | {r['n_defect_findings']} |" for r in b["runs"]]
    if c:
        L += ["", "## C. 수정안 적용 후 재검토", "",
              f"{c['n_cases']}케이스, 수정안 {c['n_patches']}건. 수정된 문장 재지적률 {c['re_flag_rate']}(1차). defect finding {c['defects_before_mean']} → {c['defects_after_mean']}(케이스 평균). "
              f"수정하지 않은 주입 문장의 지적 {c['unpatched_inj_keep'][0]} → {c['unpatched_inj_keep'][1]}건. 토큰 {c['tokens_total']:,}."]
    (OUT / "SPECIFICITY_REPORT.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


def calibration() -> None:
    """보정 A/B(사전 등록 docs/calibration_prereg.md): 현재(clean_base·lean_v3+v3b) 대 보정판(clean_base_cal·lean_cal)."""
    from app.eval.oneshot import mean_runs, paired
    b0, b1 = eval_b(""), eval_b("_cal")
    a0 = eval_a([("lean_v3", "gold_axis1.jsonl"), ("lean_v3b", "gold_axis1.jsonl")])
    a1 = eval_a([("lean_cal", "gold_axis1.jsonl")])
    sens0 = (a0["lean_v3"]["summary"]["sensitivity"] + a0["lean_v3b"]["summary"]["sensitivity"]) / 2
    sens1 = a1["lean_cal"]["summary"]["sensitivity"]
    spec_inj0 = (a0["lean_v3"]["summary"]["specificity"] + a0["lean_v3b"]["summary"]["specificity"]) / 2
    spec_inj1 = a1["lean_cal"]["summary"]["specificity"]
    g = paired(mean_runs(["lean_v3", "lean_v3b"]), mean_runs(["lean_cal"]), "grounded_recall")
    sp = paired(mean_runs(["lean_v3", "lean_v3b"]), mean_runs(["lean_cal"]), "recall")
    d_spec = b1["specificity"] - b0["specificity"]
    adopt = d_spec >= 0.10 and (sens0 - sens1) <= 0.05 and g[0] >= -0.05
    res = {"clean_specificity": [b0["specificity"], b1["specificity"]], "clean_defects_per_run": [b0["mean_defect_findings"], b1["mean_defect_findings"]],
           "orig_sentence_sensitivity": [round(sens0, 3), round(sens1, 3)], "orig_sentence_specificity": [round(spec_inj0, 3), round(spec_inj1, 3)],
           "orig_youden_j": [round(sens0 + spec_inj0 - 1, 3), round(sens1 + spec_inj1 - 1, 3)],
           "grounded_diff": [round(x, 3) for x in g[:3]], "span_diff": [round(x, 3) for x in sp[:3]],
           "tokens": [b1["tokens_total"], None], "verdict": "채택" if adopt else "기각(현재 설정 유지)"}
    (OUT / "calibration.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(res, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["a", "run_clean", "run_patch", "report", "check", "calibration"])
    ap.add_argument("--tag", default="", help="run_clean 저장 폴더 접미사(예: _cal)")
    a_ = ap.parse_args()
    if a_.cmd == "check":   # 실행 전 점검: 문장 분할·수정판 수(LLM 0)
        for b in BASES.values():
            ss = sentences((ROOT / "app" / "demo" / b).read_text(encoding="utf-8"))
            print(b, len(ss), ss[:2])
        pc = patched_cases()
        print("patched cases", len(pc), "patches", sum(len(c["patches"]) for c in pc))
    else:
        {"a": lambda: print(json.dumps({k: v["summary"] for k, v in eval_a().items() if k != "base_flag_top"}, indent=1)),
         "run_clean": lambda: run_clean(a_.tag), "run_patch": run_patch, "report": report, "calibration": calibration}[a_.cmd]()
