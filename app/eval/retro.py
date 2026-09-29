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


def strip_input(text: str, variant: str) -> str:
    """사후 분석(사전 등록 밖): 재식별 단서 제거 변형. nosmiles = SMILES 삭제, noid = SMILES·표적·기전 삭제."""
    if variant in ("nosmiles", "noid"):
        text = re.sub(r" SMILES: [^ ]+\.", "", text)
    if variant == "noid":
        text = re.sub(r"\(([^)]*)\)\. Target: [^.\n]*\.", "(small-molecule targeted agent). Target: masked.", text)
    return text


def probe(variant: str = "") -> None:
    from app.agents.graph import gateway
    gc, rows = gateway(), []
    man = {m["case_id"]: m for m in _load("retro_manifest.jsonl")}
    for c in _load("retro_cases.jsonl"):
        c = dict(c, synopsis=strip_input(c["synopsis"], variant))
        resp, rec = gc.respond("planner", c["synopsis"], purpose=f"retro_probe{variant}:{c['case_id']}",
                               instructions="The drug name in this document is masked. Give your single best guess of the drug's generic (INN) name. Answer with the name only.",
                               reasoning_effort="low", max_output_tokens=400)
        guess = (resp.output_text or "").strip().lower()
        g = man[c["case_id"]]["generic"]
        rows.append({"case_id": c["case_id"], "guess": guess[:60], "correct": g in guess, "tokens": int((rec.usage or {}).get("total_tokens") or 0)})
        print(json.dumps(rows[-1], ensure_ascii=False), flush=True)
    (OUT / f"retro_probe{('_' + variant) if variant else ''}.json").write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")


def memory_probe() -> None:
    """사후 대조군(사전 등록 밖): 약 이름을 그대로 주고 모델 기억만으로 PMR 부과 여부를 0~100 확률로 답하게 한다.
    기억만으로 정답을 맞힌다면, 재식별 가능한 입력(탐침 42~43/43)에서 나온 에이전트 점수는 기억에 오염됐을 수 있다."""
    from app.agents.graph import gateway
    gc, rows = gateway(), []
    for m in _load("retro_manifest.jsonl"):
        q = (f"Drug: {m['generic']} (brand {m['brand']}), initial FDA approval {m['asof']}. In the initial FDA approval letter, did FDA issue a "
             "postmarketing requirement or commitment to compare or evaluate a different (e.g. lower) dosage in the general indicated population "
             "(dose optimization)? Answer only with an integer 0-100: your probability that it did.")
        resp, rec = gc.respond("planner", q, purpose=f"retro_memory:{m['case_id']}", instructions="Answer from memory only. Integer only.",
                               reasoning_effort="low", max_output_tokens=400)
        mm = re.search(r"\d{1,3}", resp.output_text or "")
        rows.append({"case_id": m["case_id"], "p": int(mm.group(0)) if mm else None, "tokens": int((rec.usage or {}).get("total_tokens") or 0)})
        print(json.dumps(rows[-1]), flush=True)
    (OUT / "retro_memory.json").write_text(json.dumps(rows, indent=1), encoding="utf-8")


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
    mem = {r["case_id"]: r["p"] for r in json.loads((OUT / "retro_memory.json").read_text(encoding="utf-8"))} if (OUT / "retro_memory.json").exists() else {}
    probes_post = {}
    for v in ("nosmiles", "noid"):   # 사후: 단서 제거 변형 재식별률
        fp = OUT / f"retro_probe_{v}.json"
        if fp.exists():
            pr = json.loads(fp.read_text(encoding="utf-8"))
            probes_post[v] = round(sum(bool(r["correct"]) for r in pr) / len(pr), 3)
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
        # 사후(red-judge 09-29): 입력 템플릿 문장("No other protocol text…", SMILES 줄 등)을 span으로 삼은 S1 지적 — 초록 본문 밖
        body = c["synopsis"].split("## Phase 1 Study Report", 1)[-1]
        s1_tmpl = sum(1 for f in dose if f.verifier_status == "verified" and f.protocol_span.text.strip()[:60] not in body)
        # 사후: 파이프라인 LLM이 가려진 약 이름을 스스로 복원해 검색 질의·도구 인자에 넣었는가(기억이 추론에 들어간 직접 증거)
        trace = json.dumps(st.model_dump(include={"review_questions", "tool_log", "scratch"}), ensure_ascii=False, default=str).lower()
        name_restored = m["generic"] in trace
        lab = labels.get(m["generic"])
        rows.append({"case_id": cid, "generic": m["generic"], "year": m["approval_year"], "y": c["y"], "S1": s1, "S2": s2,
                     "B1": b1_score(c["synopsis"]), "B2": m["approval_year"], "B3": risk_score(lab)[0] if lab else None,
                     "B4": mem.get(cid), "n_findings": len(st.findings), "S1_template": s1_tmpl, "name_restored": name_restored,
                     "protocol_pk": bool((cp := st.trial.study.investigational_product.clinical_pk) and any(v is not None for v in cp.model_dump().values())), "tokens": st.budget.used_tokens,
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
    b4 = [r for r in rows if r["B4"] is not None]
    if b4 and 0 < sum(r["y"] for r in b4) < len(b4):   # 사후 대조군: 모델 기억만으로 PMR 여부
        sc, yy = [float(r["B4"]) for r in b4], [r["y"] for r in b4]
        res["metrics"]["B4"] = {"auroc": round(auroc(sc, yy), 3), "ci": _boot_auc(sc, yy), "pr_auc": round(pr_auc(sc, yy), 3), "n": len(b4)}
    if probes_post:
        res["reidentification_post_hoc"] = probes_post
    s1 = [float(r["S1"]) for r in rows]
    for k in ("B1", "B2"):
        res["metrics"][f"S1-{k}"] = {"ci": _boot_diff(s1, [float(r[k]) for r in rows], y)}
    sub = [r for r in rows if r["reidentified"] is False]
    if sub and 0 < sum(r["y"] for r in sub) < len(sub):
        sc, yy = [float(r["S1"]) for r in sub], [r["y"] for r in sub]
        res["metrics"]["S1_not_reidentified"] = {"auroc": round(auroc(sc, yy), 3), "ci": _boot_auc(sc, yy), "n": len(sub), "n_pos": sum(yy)}
    if probe_rows:
        res["reidentification_rate"] = round(sum(bool(r["correct"]) for r in probe_rows.values()) / len(probe_rows), 3)
    from scipy.stats import spearmanr   # 사후 기술통계(사전 등록 밖)
    pos, neg = [r for r in rows if r["y"]], [r for r in rows if not r["y"]]
    rho = spearmanr([r["S1"] for r in b4], [r["B4"] for r in b4]) if b4 else None
    res["descriptive_post_hoc"] = {
        "flagged_S1_ge1": sum(r["S1"] >= 1 for r in rows), "f00_abstain": sum(r["f00"] == "abstain" for r in rows),
        "mean_S1_pos": round(sum(r["S1"] for r in pos) / max(1, len(pos)), 2), "mean_S1_neg": round(sum(r["S1"] for r in neg) / max(1, len(neg)), 2),
        "spearman_S1_B4": [round(float(rho.statistic), 3), round(float(rho.pvalue), 3)] if rho else None,
        "protocol_pk_cases": sum(r["protocol_pk"] for r in rows),
        "S1_total": sum(r["S1"] for r in rows), "S1_template": sum(r["S1_template"] for r in rows),
        "flagged_excl_template": sum(r["S1"] - r["S1_template"] >= 1 for r in rows),
        "name_restored": sum(r["name_restored"] for r in rows), "name_restored_pos": sum(r["name_restored"] and r["y"] for r in rows),
        "tokens_total": sum(r["tokens"] for r in rows), "tokens_per_case": round(sum(r["tokens"] for r in rows) / max(1, len(rows)))}
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
         f"| 점수 | 설명 | AUROC [95% CI] | PR-AUC (무작위 기준 {res['n_pos'] / max(1, res['n']):.3f}) |", "|---|---|---|---|"]
    desc = {"S1": "1차: 검증된 용량최적화 finding 수", "S2": "2차: 용량최적화 finding 중증도 가중합(검증+보류)", "B1": "키워드 규칙(초록, LLM 없음)",
            "B2": "승인연도(시대 교란 점검)", "B3": "축③ 라벨 규칙(승인 후 라벨 — 참고용)", "B4": "사후 대조군: 약 이름을 준 모델 기억(도구 없음)"}
    for k in ("S1", "S2", "B1", "B2", "B3", "B4"):
        if k in m:
            L.append(f"| {k} | {desc[k]}{' (n=' + str(m[k]['n']) + ')' if 'n' in m[k] else ''} | {m[k]['auroc']:.3f} [{m[k]['ci'][0]:.3f}, {m[k]['ci'][1]:.3f}] | {m[k]['pr_auc']:.3f} |")
    L += ["", f"S1−B1 AUROC 차이 95% CI {m['S1-B1']['ci']}, S1−B2 {m['S1-B2']['ci']} (기술용)."]
    if "reidentification_rate" in res:
        L.append(f"재식별 탐침: gpt-6-sol이 마스킹 입력에서 성분명을 맞힌 비율 {res['reidentification_rate']:.3f}.")
    if res.get("reidentification_post_hoc"):
        L.append(f"사후 탐침(사전 등록 밖): SMILES 제거 {res['reidentification_post_hoc'].get('nosmiles')}, SMILES·표적·기전 제거 {res['reidentification_post_hoc'].get('noid')} — 출판 초록 본문만으로도 재식별된다.")
    if "S1_not_reidentified" in m:
        s = m["S1_not_reidentified"]
        L.append(f"재식별되지 않은 부분집합(n={s['n']}, 양성 {s['n_pos']}) S1 AUROC {s['auroc']:.3f} [{s['ci'][0]:.3f}, {s['ci'][1]:.3f}].")
    d = res.get("descriptive_post_hoc") or {}
    if d:
        L += ["", "## 사후 기술통계(사전 등록 밖)", "",
              f"- 검증된 용량최적화 finding이 1개 이상인 케이스 {d['flagged_S1_ge1']}/{res['n']} — 양성·음성 가리지 않고 지적한다(평균 S1 양성 {d['mean_S1_pos']}, 음성 {d['mean_S1_neg']}).",
              f"- F00(TCR) 기권 {d['f00_abstain']}/{res['n']} — 라벨 차단, 마스킹으로 ChEMBL 이름 조회(IC50) 실패, 초록 PK는 {d['protocol_pk_cases']}건에서 일부만 추출 → 입력 부족으로 전형값 없이 멈춤.",
              f"- S1과 모델 기억(B4)의 Spearman ρ = {d['spearman_S1_B4'][0]} (p = {d['spearman_S1_B4'][1]}) — 점수 수준의 상관은 확인되지 않았다(오염 배제의 증거는 아님).",
              f"- 입력 템플릿 문장(초록 밖)을 span으로 삼은 S1 지적 {d['S1_template']}/{d['S1_total']}건. 템플릿 유발분을 빼면 지적 케이스 {d['flagged_excl_template']}/{res['n']}.",
              f"- 지적의 정확성(precision)은 평가하지 않았다. 대부분 '초록에 PK 채혈·용량 비교 정보가 없다'는 지적이라, 43/43 지적은 판별력 없음(특이도 0)과 구별되지 않는다.",
              f"- 파이프라인 LLM이 가려진 약 이름을 스스로 복원해 검색 질의·도구 인자에 넣은 케이스 {d['name_restored']}/{res['n']}(그중 양성 {d['name_restored_pos']}) — 기억이 추론에 들어간 직접 증거.",
              f"- 토큰 합계 {d['tokens_total']:,}(케이스당 {d['tokens_per_case']:,}), 탐침·기억 대조군 별도."]
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
    ap.add_argument("cmd", choices=["run", "probe", "memory", "analyze"])
    ap.add_argument("--resume", action="store_true")
    ap.add_argument("--suffix", default="")
    ap.add_argument("--variant", default="", choices=["", "nosmiles", "noid"], help="사후 분석: 재식별 단서 제거 변형")
    a = ap.parse_args()
    {"run": lambda: run(a.resume, a.suffix), "probe": lambda: probe(a.variant), "memory": memory_probe, "analyze": lambda: analyze(a.suffix)}[a.cmd]()
