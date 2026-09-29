"""
수치 원천표 — 기술서·발표·영상·README에 쓰는 모든 수치의 단일 출처(PRD P0-7). 결과 파일에서 자동 생성한다(토큰 0).

실행: .venv/Scripts/python.exe -m app.eval.numbers  →  docs/numbers.md
규칙: 제출물의 수치는 이 표에서만 가져온다. 결과가 바뀌면 이 스크립트를 다시 돌리고 모든 제출물을 재대조한다.
"""
from __future__ import annotations

import json
import random
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RES = ROOT / "app" / "eval" / "data" / "results"


def _ci(xs: list[float], n_boot: int = 4000, seed: int = 0) -> tuple[float, float]:
    rng = random.Random(seed)
    b = sorted(sum(rng.choice(xs) for _ in xs) / len(xs) for _ in range(n_boot))
    return b[int(0.025 * n_boot)], b[int(0.975 * n_boot)]


def _subset(rows: list[dict]) -> str:
    """세트 이름은 case_id 접두어로 정한다(문자열 대소 비교는 새 접두어에서 틀린다)."""
    cid = rows[0]["case_id"] if rows else ""
    if cid.startswith("AXD-"):
        drugs = sorted({r["case_id"].split("-")[1].lower() for r in rows})
        return f"다약물 {len(rows)}({'·'.join(drugs)})"
    return "확장 40(AX1-021~060)" if cid >= "AX1-021" else "원 20(AX1-001~020)"


def config_rows(cfgs: list[tuple[str, str]]) -> list[str]:
    out = ["| 설정 | 설명 | 세트 | n | span recall | grounded (95% CI) | 검증 통과율 | 토큰/케이스 | LLM 실패 | 원천 |",
           "|---|---|---|---|---|---|---|---|---|---|"]
    for cfg, desc in cfgs:
        p = RES / f"{cfg}.json"
        if not p.exists():
            continue
        d = json.loads(p.read_text(encoding="utf-8"))
        rows, a = d["rows"], d["aggregate"]
        lo, hi = _ci([r["grounded_recall"] for r in rows])
        fails = sum(r.get("llm_failures", 0) for r in rows) if any("llm_failures" in r for r in rows) else "—"
        subset = _subset(rows)
        out.append(f"| {cfg} | {desc} | {subset} | {len(rows)} | {a['recall']:.3f} | {a['grounded_recall']:.3f} [{lo:.3f}, {hi:.3f}] | "
                   f"{a['verified_rate']:.3f} | {a['tokens']:,.0f} | {fails} | `app/eval/data/results/{cfg}.json` |")
    return out


PAIRS = [  # (기준, 비교, 설명) — 기술서·발표의 쌍대 비교 수치는 이 절에서만 가져온다
    ("lean", "lean_combo", "09-11 배포 기본 → 현재 기본(원 20)"),
    ("lean", "lean_d3", "09-11 배포 기본 → 09-23 경화 코드(원 20)"),
    ("lean_d3", "lean_g6all", "경화 코드 → 전 노드 gpt-6-sol(원 20)"),
    ("lean_d3", "lean_combo", "경화 코드 → 현재 기본(원 20)"),
    ("lean_g6all", "lean_combo", "gpt-6-sol → + strict·250자(원 20)"),
    ("lean_d3ext", "lean_g6allext", "경화 코드 → 전 노드 gpt-6-sol(확장 40)"),
    ("lean_d3ext", "lean_comboext", "경화 코드 → 현재 기본(확장 40)"),
    ("lean_g6allext", "lean_comboext", "gpt-6-sol → + strict·250자(확장 40)"),
    ("lean_combo", "lean_v2", "09-25 기본 → 09-26 업그레이드 코드(원 20, 회귀)"),
    ("lean", "lean_v2", "09-11 배포 기본 → 09-26 업그레이드 코드(원 20)"),
    ("lean_combo", "lean_v3", "09-25 기본 → 최종 코드 1차 실행(원 20, 회귀)"),
    ("lean_combo", "lean_v3b", "09-25 기본 → 최종 코드 2차 실행(원 20, 회귀)"),
    ("lean_v3", "lean_v3b", "최종 코드 같은 설정 반복(원 20) — 실행 간 변동 크기"),
    ("lean", "lean_v3", "09-11 배포 기본 → 최종 코드 1차(원 20)"),
    ("lean", "lean_v3b", "09-11 배포 기본 → 최종 코드 2차(원 20)"),
    ("lean_mdrug", "lean_mdrug3", "09-26 코드 → 최종 코드(다약물 30)"),
]


def multidrug_lines(cfg: str = "lean_mdrug3") -> list[str]:
    """다약물 세트의 약물별 지표와 약리 축 도달(저장 상태에서 집계). 원 세트와 결함 풀은 같고 기준 시놉시스만 다르다."""
    from collections import Counter, defaultdict
    p = RES / f"{cfg}.json"
    if not p.exists():
        return []
    rows = json.loads(p.read_text(encoding="utf-8"))["rows"]
    by = defaultdict(list)
    for r in rows:
        by[r["case_id"].split("-")[1]].append(r)
    reach: dict[str, Counter] = defaultdict(Counter)
    tools: dict[str, list[int]] = defaultdict(lambda: [0, 0])
    for sp in sorted((RES / "states" / cfg).glob("*.json")):
        d = json.loads(sp.read_text(encoding="utf-8"))
        drug = sp.stem.split("-")[1]
        src = d["scratch"].get("tcr_source")
        st = next((t["status"] for t in d["tasks"] if t["kind"] == "exposure_dose_relationship"), "없음")
        reach[drug][f"{'TCR 계산' if src else 'TCR 기권(입력 부족)'}·{st}"] += 1
        for c in d["tool_log"]:
            tools[drug][0 if c["ok"] else 1] += 1
    out = ["| 약물(기준 시놉시스) | n | span recall | grounded (95% CI) | 검증 통과율 | precision proxy | 토큰/케이스 | 도구 성공/실패 | 약리 축(TCR) |",
           "|---|---|---|---|---|---|---|---|---|"]
    for drug, v in sorted(by.items()):
        lo, hi = _ci([r["grounded_recall"] for r in v])
        m = lambda k: sum(r[k] for r in v) / len(v)
        out.append(f"| {drug.lower()} | {len(v)} | {m('recall'):.3f} | {m('grounded_recall'):.3f} [{lo:.3f}, {hi:.3f}] | {m('verified_rate'):.3f} | "
                   f"{m('precision_proxy'):.3f} | {m('tokens'):,.0f} | {tools[drug][0]}/{tools[drug][1]} | {', '.join(f'{k} {n}' for k, n in reach[drug].most_common())} |")
    return out + ["", "도구 실패의 대부분은 미승인 후보(DV-505)의 openFDA 라벨 404(라벨이 없는 것이 정상)다. 약리 축 'TCR 기권(입력 부족)'은 PK·구조·IC50 중 하나를 얻지 못해 전형값 없이 멈춘 경우다.", ""]


def pair_lines() -> list[str]:
    from app.eval.compare import load, paired, verdict
    out = ["| 비교 | n | 토큰/케이스 차이 [95% CI] | 토큰 비율 | grounded [95% CI] | 검증 [95% CI] | precision [95% CI] | 사전 규칙 |",
           "|---|---|---|---|---|---|---|---|"]
    for b, a, desc in PAIRS:
        if not ((RES / f"{b}.json").exists() and (RES / f"{a}.json").exists()):
            continue
        base, arm = load(b), load(a)
        t, tl, th, n = paired(base, arm, "tokens")
        rel = sum(arm[c]["tokens"] for c in arm if c in base) / sum(base[c]["tokens"] for c in arm if c in base) - 1
        cells = []
        for k in ("grounded_recall", "verified_rate", "precision_proxy"):
            m, lo, hi, _ = paired(base, arm, k)
            cells.append(f"{m:+.3f} [{lo:+.3f}, {hi:+.3f}]")
        out.append(f"| {desc} (`{b}`→`{a}`) | {n} | {t:+,.0f} [{tl:+,.0f}, {th:+,.0f}] | {rel:+.1%} | " + " | ".join(cells)
                   + f" | {verdict(base, arm).split(' ')[0]} |")
    return out + ["", "쌍대 부트스트랩 5,000회(`app/eval/compare.py`, seed 0). 사전 규칙: 기각 = 토큰 +2% 초과 또는 grounded·검증 점추정 −5pp 초과 하락, 채택 = 토큰 −15% 이하 또는 grounded CI 하한 > 0, 그 외 보류.", ""]


def usage_lines() -> list[str]:
    """원천 = 감사로그 공개 집계본(`app/eval/data/audit_usage.jsonl`, `python -m app.eval.audit_export`로 갱신). 쿼터 헤더는 09-22 한도 재설정 이후 값만 보여 누적 사용량과 대조할 수 없다."""
    from collections import Counter

    from app.eval.audit_export import iter_audit
    tot, last_ts, by_day, by_model = 0, "", Counter(), Counter()
    for r in iter_audit():
        u = r["usage"]["total_tokens"]
        tot += u
        by_day[r["ts"][:10]] += u
        by_model[r.get("model")] += u
        last_ts = max(last_ts, r["ts"])
    out = [f"- 합계 **{tot:,}** 토큰(총 쿼터 6,000만의 {tot / 60_000_000:.1%}), 마지막 호출 {last_ts[:16]} UTC.",
           "- 일자별(UTC): " + ", ".join(f"{d} {v:,}" for d, v in sorted(by_day.items())),
           "- 모델별: " + ", ".join(f"{m} {v:,}" for m, v in by_model.most_common())]
    return out + ["- 원본 `logs/`는 git·Docker에서 제외되고, 재현에 필요한 필드(시각·모델·용도·usage)만 공개 집계본으로 커밋한다. 이 절이 제출물의 누적 토큰 단일 출처다.", ""]


def main() -> None:
    cfgs = [
        ("full", "09-11 본평가: Reviewer 3인"), ("lean", "09-11 기본: Reviewer 1인 + 재선택"),
        ("no_arena", "ablation: Reviewer 없음"), ("no_calc", "ablation: 계산 도구 없음"), ("no_verifier", "ablation: 검증기 없음"),
        ("lean_d3", "09-23 새 코드 기준선(구조화 출력 경화·불변식·범주 필터)"), ("lean_cnone", "A/B: compile effort none"),
        ("lean_strict", "A/B: reviewers·findings strict"), ("lean_q250", "A/B: 근거 인용문 250자"), ("lean_notopic", "A/B: 주제 태그 프롬프트 제거"), ("lean_fmed", "A/B: findings effort medium"),
        ("lean_c6sol", "A/B: compile gpt-6-sol"), ("lean_g6all", "A/B: 전 노드 gpt-6-sol"), ("lean_combo", "09-25 기본: gpt-6-sol + strict + 인용문 250자"),
        ("lean_d3ext", "09-23 새 코드, 확장 세트"), ("lean_g6allext", "전 노드 gpt-6-sol, 확장 세트"), ("lean_comboext", "09-25 기본, 확장 세트"),
        ("lean_v2", "09-26 업그레이드 코드(약물 무관화·보류 재검색·예산 가드)"), ("lean_mdrug", "09-26 업그레이드 코드, 다약물 세트"),
        ("lean_v3", "최종 코드(c7dc0be, 투여 간격 수정) 1차"), ("lean_v3b", "최종 코드 2차(같은 설정 반복)"), ("lean_mdrug3", "최종 코드, 다약물 세트"),
    ]
    tcr = json.loads((ROOT / "evidence" / "tcr_240mg.json").read_text(encoding="utf-8"))
    lines = [f"# 수치 원천표 (자동 생성 {datetime.now():%Y-%m-%d %H:%M}, `python -m app.eval.numbers`)", "",
             "제출물(기술서·발표·영상·README·데모 화면)의 모든 수치는 이 표에서만 가져온다. 점추정 간 차이는 n=20에서 대부분 신뢰구간이 겹친다 — 유의 여부는 `python -m app.eval.compare`로 확인한 것만 주장한다.", "",
             "## 1. 평가(축① Silver Set — 원·확장 세트는 기준 시놉시스 DV-DEMO-002, 다약물 세트는 아다그라십·로를라티닙·DV-505(가상) 시놉시스의 결함 주입 변형)", ""] + config_rows(cfgs) + [
             "", "## 1-1. 다약물 세트 약물별(`lean_mdrug3`, 최종 코드)", ""] + multidrug_lines() + [
             "", "## 1-2. 쌍대 비교(같은 케이스끼리)", ""] + pair_lines() + [
             "## 2. 소토라십 240 mg TCR (`evidence/tcr_240mg.json`)", "",
             "| 가정 | C_max | C_avg | C_trough | 판정 |", "|---|---|---|---|---|"]
    for r in tcr["rows"]:
        lines.append(f"| {r['assumption']} | {r['TCR_max']} | {r['TCR_avg']} | {r['TCR_trough']} | {r['verdict']} |")
    lines += [f"\n종합: **{tcr['overall']}** — {tcr['overall_reason']}", "",
              "## 3. 게이트웨이 실측 (`docs/gateway_probe.md`)", "",
              "- 쿼터: 총 6,000만(09-22 공지). 09-23 13:45 헤더 잔여 59,999,986. 과금 = usage.total_tokens 1:1(모델별 가중치 없음, reasoning 포함).",
              "- 캐시: gpt-6-luna 적중 2,780토큰에도 차감 2,788 → 캐시 절감 0(⑩-b).",
              "- 모델: gpt-5.6-sol/terra/luna, gpt-6-sol/luna 200 / gpt-6-astra 404(09-11·09-23). 기본값은 09-24부터 planner·reviewer·extract 모두 gpt-6-sol.",
              "- 토큰 구성: reasoning 비중 gpt-5.6 세대 3.7~4.9%, gpt-6-sol 0.9~1.0%. 입력이 약 70~80%(`docs/token_ledger.md`).", "",
              "## 4. 누적 사용량 (감사로그 공개 집계본 `app/eval/data/audit_usage.jsonl`의 usage.total_tokens 합)", ""] + usage_lines()
    (ROOT / "docs" / "numbers.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
