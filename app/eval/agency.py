"""
자율성·도구 활용 집계(PRD P1-2·P1-3) — 저장된 평가 상태(ReviewState JSON)만 읽는다(토큰 0).

실행: .venv/Scripts/python.exe -m app.eval.agency [--configs lean_combo,lean_comboext]
출력: docs/agency.md

단위 규칙(제출물 전체 공통):
- 이벤트: replan_events 한 줄. 케이스: 해당 이벤트가 1회 이상 있었던 평가 케이스 수. finding: 이벤트가 가리킨 finding 수(중복 제외).
- 도구 호출: tool_log 한 줄(같은 도구의 반복 호출도 각각 센다). 도구 종류: tool 이름의 고유값.
"""
from __future__ import annotations

import argparse
import json
import statistics
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STATES = ROOT / "app" / "eval" / "data" / "results" / "states"
DEMO = ROOT / "app" / "demo" / "results"
TRIGGER_KO = {
    "citation_held": "인용 근거 불충분 → finding 보류(held)",
    "citation_rejected": "인용 기각 → 문장 재작성(재계획①)",
    "evidence_reselected": "근거 재선택(로컬 NLI, GPU 있을 때만)",
    "invariant_tcr_claim": "LLM finding이 TCR 판정을 담음 → 보류(held), 수치 판정은 도구 finding만",
    "invariant_conflict_abstain": "Reviewer 간 상충 미해소 → 기권(Reviewer 3인 옵션에서만 동작)",
    "prompt_injection_detected": "문서 내 지시문 탐지 → 데이터로만 처리",
    "source_version_conflict": "폐기된 초안 인용 → 최신 최종본 기준",
    "tool_failure": "도구 실패 → 근거 미확보 표기",
    "llm_output_failure": "LLM 구조화 출력 실패 → 결론 없음",
}


def load(cfgs: list[str]) -> list[tuple[str, dict]]:
    out = []
    for c in cfgs:
        for p in sorted((STATES / c).glob("*.json")):
            out.append((p.stem, json.loads(p.read_text(encoding="utf-8"))))
    return out


def replan_table(states: list[tuple[str, dict]]) -> list[str]:
    ev, cases, finds = Counter(), defaultdict(set), defaultdict(set)
    for cid, d in states:
        for e in d["replan_events"]:
            t = e.get("trigger")
            if not t:
                continue
            ev[t] += 1
            cases[t].add(cid)
            if e.get("finding_id"):
                finds[t].add((cid, e["finding_id"]))
    n = len(states)
    rows = ["| 트리거 | 의미 | 이벤트 | 케이스(/%d) | finding |" % n, "|---|---|---|---|---|"]
    for t in TRIGGER_KO:
        rows.append(f"| `{t}` | {TRIGGER_KO[t]} | {ev[t]} | {len(cases[t])} | {len(finds[t]) or '—'} |")
    return rows


def rewrite_outcomes(states: list[tuple[str, dict]]) -> str:
    """재작성된 finding이 최종적으로 검증을 통과했는가."""
    tot, ok = 0, 0
    for _, d in states:
        st = {f["finding_id"]: f["verifier_status"] for f in d["findings"]}
        for fid in {e["finding_id"] for e in d["replan_events"] if e.get("trigger") == "citation_rejected"}:
            tot += 1
            ok += st.get(fid) == "verified"
    return f"재작성 {tot}건 중 최종 검증 통과 {ok}건" if tot else "재작성 없음"


def finding_table(states: list[tuple[str, dict]]) -> list[str]:
    vs, vd = Counter(), Counter()
    non_abstain = non_abstain_ok = 0
    for _, d in states:
        for f in d["findings"]:
            vs[f["verifier_status"]] += 1
            vd[f["verdict"]] += 1
            if f["verdict"] != "abstain":
                non_abstain += 1
                non_abstain_ok += f["verifier_status"] == "verified"
    tot = sum(vs.values())
    return ["| 항목 | 값 |", "|---|---|",
            f"| finding 총수 | {tot} (케이스당 {tot / max(len(states), 1):.1f}) |",
            f"| 판정(verdict) | " + ", ".join(f"{k} {v}" for k, v in vd.most_common()) + " |",
            f"| 검증 상태 | " + ", ".join(f"{k} {v}" for k, v in vs.most_common()) + " |",
            f"| 비기권 finding 검증 통과율 | {non_abstain_ok}/{non_abstain} = {non_abstain_ok / max(non_abstain, 1):.3f} |"]


def _err_kind(e: str) -> str:
    if "HTTP Error" in e:
        return "HTTP " + e.split("HTTP Error", 1)[1].split(":", 1)[0].strip()
    if "timed out" in e.lower() or "timeout" in e.lower():
        return "타임아웃"
    return e.split(":", 1)[0][:40] or "기타"


def tool_table(states: list[tuple[str, dict]]) -> list[str]:
    by = defaultdict(list)
    for _, d in states:
        for t in d["tool_log"]:
            by[t["tool"]].append(t)
    n = len(states)
    rows = [f"| 도구 | 호출 | 케이스당 | 성공률 | 지연 중앙값(s) | 지연 최대(s) | 실패 유형 |", "|---|---|---|---|---|---|---|"]
    tot = ok = 0
    for name, ts in sorted(by.items(), key=lambda kv: -len(kv[1])):
        lat = [t["latency_s"] for t in ts if t.get("latency_s") is not None]
        good = sum(1 for t in ts if t["ok"])
        err = Counter(_err_kind(t.get("error") or "") for t in ts if not t["ok"]).most_common()
        tot += len(ts)
        ok += good
        rows.append(f"| `{name}` | {len(ts)} | {len(ts) / n:.1f} | {good / len(ts):.3f} | {statistics.median(lat) if lat else 0:.3f} | "
                    f"{max(lat) if lat else 0:.3f} | {', '.join(f'{k} {v}' for k, v in err) if err else '—'} |")
    rows.append(f"| **합계** | {tot} | {tot / max(n, 1):.1f} | {ok / max(tot, 1):.3f} | | | 도구 종류 {len(by)}개 |")
    return rows


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--configs", default="lean_combo,lean_comboext")
    a = ap.parse_args()
    cfgs = [c.strip() for c in a.configs.split(",") if c.strip()]
    states = load(cfgs)
    demos = [(p.stem, json.loads(p.read_text(encoding="utf-8"))) for p in sorted(DEMO.glob("demo*.json"))]
    lines = [f"# 자율성·도구 활용 집계 (자동 생성 {datetime.now():%Y-%m-%d %H:%M}, `python -m app.eval.agency`)", "",
             f"원천: `app/eval/data/results/states/{{{','.join(cfgs)}}}/*.json` ({len(states)}케이스, 현재 기본 설정) · 데모: `app/demo/results/demo*.json`. 단위 규칙은 스크립트 머리말 참조.", "",
             "## 1. 재계획 이벤트 — 평가 세트", ""] + replan_table(states) + [
             "", f"- {rewrite_outcomes(states)}.",
             "- `evidence_reselected`는 CUDA가 있을 때만 켜진다(`DV_EVIDENCE_RERANK=auto`). 평가는 GPU PC에서 돌았고 배포본(CPU)에서는 꺼진다.",
             "- 평가 세트에는 인젝션·폐기 초안이 없어 해당 트리거가 0이다. 이 경로는 아래 데모·적대 테스트로 보인다.",
             "- 도구 실패 5건(4절)은 평가 당시 `tool_failure`로 기록되지 않았다. 과제가 다른 도구 결과로 `done` 처리됐기 때문이다(09-25 수정 전 코드). openFDA 실패 1건(AX1-046)에서는 라벨 PK 미확보로 240 mg 기권 finding이 빠졌다(기권 59/60의 이유).", "",
             "## 2. 재계획 이벤트 — 시연 데모 3종", ""] + replan_table(demos) + [
             "", "## 3. finding 판정·검증 — 평가 세트", ""] + finding_table(states) + [
             "", "## 4. 도구 호출 — 평가 세트", ""] + tool_table(states) + [
             "", "성공률은 `ok` 필드 기준이다. 실패도 관측값으로 저장·표시한다(UI 도구 호출 탭)."]
    (ROOT / "docs" / "agency.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
