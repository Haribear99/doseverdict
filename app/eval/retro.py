"""
실사례 후향 검증 실행·분석 — 사전 등록 docs/retro_prereg.md.

  python -m app.eval.retro run [--resume] [--suffix S]   케이스마다 DV_ASOF_DATE=승인일, DV_BLIND_LABEL=1로 현재 기본(lean) 실행
  python -m app.eval.retro probe                       재식별 탐침 P1(마스킹 입력 → 성분명 추측, 도구 없음)
  python -m app.eval.retro analyze [--suffix S]        S1·S2·B1·B2·B3 AUROC → results/RETRO_REPORT.md, results/retro.json
"""
from __future__ import annotations

import argparse
import json
import os
import random
import re
from datetime import datetime, timezone
from pathlib import Path

from app.eval.axis3 import auroc, pr_auc

DATA = Path(__file__).resolve().parent / "data"
OUT = DATA / "results"
SEV = {"critical": 4, "high": 3, "medium": 2, "low": 1}
B1_PATTERNS = [
    r"MTD (was |were )?(not|never) (reached|identified|established|determined)",
    r"maximum tolerated dose (was |were )?(not|never)",
    r"no dose[- ]limiting toxicit",
    r"no DLTs?\b",
    r"(highest|maximum) (dose|dose level) (tested|evaluated|studied|administered)",
]


def _load(fn: str) -> list[dict]:
    return [json.loads(l) for l in (DATA / fn).read_text(encoding="utf-8").splitlines() if l.strip()]


def _state_dir(suffix: str) -> Path:
    d = OUT / "states" / f"retro{suffix}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def run(resume: bool, suffix: str) -> None:
    from app.agents.graph import run_until_gate
    os.environ["DV_BLIND_LABEL"] = "1"
    for c in _load("retro_cases.jsonl"):
        sp = _state_dir(suffix) / f"{c['case_id']}.json"
        if resume and sp.exists():
            continue
        os.environ["DV_ASOF_DATE"] = c["asof"]   # 도구가 호출 시점에 읽는다
        _, _, st = run_until_gate(c["synopsis"], run_id=f"retro{suffix}-{c['case_id']}", reviewers=["regulatory"])
        sp.write_text(st.model_dump_json(indent=1), encoding="utf-8")
        dose = [f for f in st.findings if f.category == "dose_optimization"]
        print(json.dumps({"case": c["case_id"], "tokens": st.budget.used_tokens, "findings": len(st.findings),
                          "dose_verified": sum(f.verdict == "defect" and f.verifier_status == "verified" for f in dose)}, ensure_ascii=False), flush=True)


def probe() -> None:
    from app.agents.graph import gateway
    gc, rows = gateway(), []
    man = {m["case_id"]: m for m in _load("retro_manifest.jsonl")}
    for c in _load("retro_cases.jsonl"):
        resp, rec = gc.respond("planner", c["synopsis"], purpose=f"retro_probe:{c['case_id']}",
                               instructions="The drug name in this document is masked. Give your single best guess of the drug's generic (INN) name. Answer with the name only.",
                               reasoning_effort="low", max_output_tokens=400)
        guess = (resp.output_text or "").strip().lower()
        g = man[c["case_id"]]["generic"]
        rows.append({"case_id": c["case_id"], "guess": guess[:60], "correct": g in guess, "tokens": int((rec.usage or {}).get("total_tokens") or 0)})
        print(json.dumps(rows[-1], ensure_ascii=False), flush=True)
    (OUT / "retro_probe.json").write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")


def _boot_auc(scores: list[float], y: list[int], n: int = 5000, seed: int = 0) -> tuple[float, float]:
    rng = random.Random(seed)
    pos = [i for i, t in enumerate(y) if t]
    neg = [i for i, t in enumerate(y) if not t]
    vals = []
    for _ in range(n):
        idx = [rng.choice(pos) for _ in pos] + [rng.choice(neg) for _ in neg]
        vals.append(auroc([scores[i] for i in idx], [y[i] for i in idx]))
    vals.sort()
    return round(vals[int(0.025 * n)], 3), round(vals[int(0.975 * n) - 1], 3)


def _boot_diff(a: list[float], b: list[float], y: list[int], n: int = 5000, seed: int = 0) -> tuple[float, float]:
    rng = random.Random(seed)
    pos = [i for i, t in enumerate(y) if t]
    neg = [i for i, t in enumerate(y) if not t]
    vals = []
    for _ in range(n):
        idx = [rng.choice(pos) for _ in pos] + [rng.choice(neg) for _ in neg]
        yy = [y[i] for i in idx]
        vals.append(auroc([a[i] for i in idx], yy) - auroc([b[i] for i in idx], yy))
    vals.sort()
    return round(vals[int(0.025 * n)], 3), round(vals[int(0.975 * n) - 1], 3)


def b1_score(text: str) -> int:
    return sum(1 for p in B1_PATTERNS if re.search(p, text, flags=re.I))


def analyze(suffix: str) -> None:
    from app.schema.trial_schema import ReviewState
    from app.eval.axis3 import risk_score
    cases = {c["case_id"]: c for c in _load("retro_cases.jsonl")}
    man = {m["case_id"]: m for m in _load("retro_manifest.jsonl")}
    labels = {}
    if (DATA / "oncology_labels.jsonl").exists():
        for r in _load("oncology_labels.jsonl"):
            labels[(r.get("generic_name") or "").lower()] = r
    probe_rows = {r["case_id"]: r for r in json.loads((OUT / "retro_probe.json").read_text(encoding="utf-8"))} if (OUT / "retro_probe.json").exists() else {}
    rows = []
    for cid, c in cases.items():
        sp = _state_dir(suffix) / f"{cid}.json"
        if not sp.exists():
            continue
        st = ReviewState.model_validate_json(sp.read_text(encoding="utf-8"))
        dose = [f for f in st.findings if f.category == "dose_optimization" and f.verdict == "defect"]
        s1 = sum(f.verifier_status == "verified" for f in dose)
        s2 = sum(SEV.get(str(getattr(f.severity, "value", f.severity)), 1) for f in dose if f.verifier_status in ("verified", "held"))
        m = man[cid]
        lab = labels.get(m["generic"])
        rows.append({"case_id": cid, "generic": m["generic"], "year": m["approval_year"], "y": c["y"], "S1": s1, "S2": s2,
                     "B1": b1_score(c["synopsis"]), "B2": m["approval_year"], "B3": risk_score(lab)[0] if lab else None,
                     "n_findings": len(st.findings), "tokens": st.budget.used_tokens,
                     "f00": next((f.verdict for f in st.findings if f.finding_id == "F00"), None),
                     "reidentified": (probe_rows.get(cid) or {}).get("correct"),
                     "dose_findings": [{"id": f.finding_id, "status": f.verifier_status, "severity": str(getattr(f.severity, "value", f.severity)),
                                        "claim": f.claim[:220], "span": f.protocol_span.text[:160]} for f in dose]})
    y = [r["y"] for r in rows]
    res = {"n": len(rows), "n_pos": sum(y), "at": datetime.now(timezone.utc).isoformat(), "suffix": suffix, "metrics": {}}
    for k in ("S1", "S2", "B1", "B2"):
        sc = [float(r[k]) for r in rows]
        res["metrics"][k] = {"auroc": round(auroc(sc, y), 3), "ci": _boot_auc(sc, y), "pr_auc": round(pr_auc(sc, y), 3)}
    b3 = [r for r in rows if r["B3"] is not None]
    if b3 and 0 < sum(r["y"] for r in b3) < len(b3):
        sc, yy = [r["B3"] for r in b3], [r["y"] for r in b3]
        res["metrics"]["B3"] = {"auroc": round(auroc(sc, yy), 3), "ci": _boot_auc(sc, yy), "pr_auc": round(pr_auc(sc, yy), 3), "n": len(b3)}
    s1 = [float(r["S1"]) for r in rows]
    for k in ("B1", "B2"):
        res["metrics"][f"S1-{k}"] = {"ci": _boot_diff(s1, [float(r[k]) for r in rows], y)}
    sub = [r for r in rows if r["reidentified"] is False]
    if sub and 0 < sum(r["y"] for r in sub) < len(sub):
        sc, yy = [float(r["S1"]) for r in sub], [r["y"] for r in sub]
        res["metrics"]["S1_not_reidentified"] = {"auroc": round(auroc(sc, yy), 3), "ci": _boot_auc(sc, yy), "n": len(sub), "n_pos": sum(yy)}
    if probe_rows:
        res["reidentification_rate"] = round(sum(bool(r["correct"]) for r in probe_rows.values()) / len(probe_rows), 3)
    lo = res["metrics"]["S1"]["ci"][0]
    res["verdict"] = "신호 있음(S1 AUROC CI 하한 > 0.5)" if lo > 0.5 else "신호 확인 안 됨(null) — S1 AUROC CI가 0.5를 포함"
    res["rows"] = rows
    (OUT / f"retro{suffix}.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    _report(res, suffix)
    print(json.dumps({k: v for k, v in res.items() if k != "rows"}, ensure_ascii=False, indent=1))


def _report(res: dict, suffix: str) -> None:
    m = res["metrics"]
    L = [f"# 실사례 후향 검증 결과 (`retro{suffix}`, 자동 생성 {res['at'][:16]}, `python -m app.eval.retro analyze`)", "",
         f"사전 등록: `docs/retro_prereg.md`. n = {res['n']}(양성 {res['n_pos']}). 판정: **{res['verdict']}**", "",
         "| 점수 | 설명 | AUROC [95% CI] | PR-AUC (무작위 기준 %.3f) |" % (res["n_pos"] / max(1, res["n"])), "|---|---|---|---|"]
    desc = {"S1": "1차: 검증된 용량최적화 finding 수", "S2": "2차: 용량최적화 finding 중증도 가중합(검증+보류)", "B1": "키워드 규칙(초록, LLM 없음)",
            "B2": "승인연도(시대 교란 점검)", "B3": "축③ 라벨 규칙(승인 후 라벨 — 참고용)"}
    for k in ("S1", "S2", "B1", "B2", "B3"):
        if k in m:
            L.append(f"| {k} | {desc[k]}{' (n=' + str(m[k]['n']) + ')' if 'n' in m[k] else ''} | {m[k]['auroc']:.3f} [{m[k]['ci'][0]:.3f}, {m[k]['ci'][1]:.3f}] | {m[k]['pr_auc']:.3f} |")
    L += ["", f"S1−B1 AUROC 차이 95% CI {m['S1-B1']['ci']}, S1−B2 {m['S1-B2']['ci']} (기술용)."]
    if "reidentification_rate" in res:
        L.append(f"재식별 탐침: gpt-6-sol이 마스킹 입력에서 성분명을 맞힌 비율 {res['reidentification_rate']:.3f}.")
    if "S1_not_reidentified" in m:
        s = m["S1_not_reidentified"]
        L.append(f"재식별되지 않은 부분집합(n={s['n']}, 양성 {s['n_pos']}) S1 AUROC {s['auroc']:.3f} [{s['ci'][0]:.3f}, {s['ci'][1]:.3f}].")
    L += ["", "## 케이스별", "", "| 케이스 | 약물 | 승인 | PMR | S1 | S2 | B1 | F00 | 재식별 | 토큰 |", "|---|---|---|---|---|---|---|---|---|---|"]
    for r in sorted(res["rows"], key=lambda r: (-r["y"], -r["S1"])):
        L.append(f"| {r['case_id']} | {r['generic']} | {r['year']} | {'●' if r['y'] else '○'} | {r['S1']} | {r['S2']} | {r['B1']} | {r['f00'] or '—'} | {'예' if r['reidentified'] else '아니오' if r['reidentified'] is False else '—'} | {r['tokens']:,} |")
    L += ["", "## 양성 사례의 용량최적화 finding 원문", ""]
    for r in [r for r in res["rows"] if r["y"]]:
        L.append(f"**{r['case_id']} {r['generic']}**")
        for f in r["dose_findings"] or [{"id": "—", "status": "", "severity": "", "claim": "용량최적화 finding 없음", "span": ""}]:
            L.append(f"- {f['id']} [{f['status']}/{f['severity']}] {f['claim']} — span: \"{f['span']}\"")
        L.append("")
    (OUT / f"RETRO_REPORT{suffix}.md").write_text("\n".join(L) + "\n", encoding="utf-8")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["run", "probe", "analyze"])
    ap.add_argument("--resume", action="store_true")
    ap.add_argument("--suffix", default="")
    a = ap.parse_args()
    {"run": lambda: run(a.resume, a.suffix), "probe": probe, "analyze": lambda: analyze(a.suffix)}[a.cmd]()
