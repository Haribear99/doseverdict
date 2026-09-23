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
        subset = "확장 40(AX1-021~060)" if rows and rows[0]["case_id"] >= "AX1-021" else "원 20(AX1-001~020)"
        out.append(f"| {cfg} | {desc} | {subset} | {len(rows)} | {a['recall']:.3f} | {a['grounded_recall']:.3f} [{lo:.3f}, {hi:.3f}] | "
                   f"{a['verified_rate']:.3f} | {a['tokens']:,.0f} | {fails} | `app/eval/data/results/{cfg}.json` |")
    return out


def main() -> None:
    cfgs = [
        ("full", "09-11 본평가: Reviewer 3인"), ("lean", "09-11 기본: Reviewer 1인 + 재선택"),
        ("no_arena", "ablation: Reviewer 없음"), ("no_calc", "ablation: 계산 도구 없음"), ("no_verifier", "ablation: 검증기 없음"),
        ("lean_d3", "09-23 새 코드 기준선(구조화 출력 경화·불변식·범주 필터)"), ("lean_cnone", "A/B: compile effort none"),
        ("lean_strict", "A/B: reviewers·findings strict"), ("lean_q250", "A/B: 근거 인용문 250자"), ("lean_notopic", "A/B: 주제 태그 프롬프트 제거"),
        ("lean_c6sol", "A/B: compile gpt-6-sol"), ("lean_g6all", "A/B: 전 노드 gpt-6-sol"), ("lean_combo", "최종 후보 결합 설정"),
        ("lean_d3ext", "09-23 새 코드, 확장 세트"), ("lean_comboext", "최종 후보, 확장 세트"),
    ]
    tcr = json.loads((ROOT / "evidence" / "tcr_240mg.json").read_text(encoding="utf-8"))
    lines = [f"# 수치 원천표 (자동 생성 {datetime.now():%Y-%m-%d %H:%M}, `python -m app.eval.numbers`)", "",
             "제출물(기술서·발표·영상·README·데모 화면)의 모든 수치는 이 표에서만 가져온다. 점추정 간 차이는 n=20에서 대부분 신뢰구간이 겹친다 — 유의 여부는 `python -m app.eval.compare`로 확인한 것만 주장한다.", "",
             "## 1. 평가(축① Silver Set, 단일 기준 시놉시스 DV-DEMO-002의 결함 주입 변형)", ""] + config_rows(cfgs) + [
             "", "## 2. 소토라십 240 mg TCR (`evidence/tcr_240mg.json`)", "",
             "| 가정 | C_max | C_avg | C_trough | 판정 |", "|---|---|---|---|---|"]
    for r in tcr["rows"]:
        lines.append(f"| {r['assumption']} | {r['TCR_max']} | {r['TCR_avg']} | {r['TCR_trough']} | {r['verdict']} |")
    lines += [f"\n종합: **{tcr['overall']}** — {tcr['overall_reason']}", "",
              "## 3. 게이트웨이 실측 (`docs/gateway_probe.md`)", "",
              "- 쿼터: 총 6,000만(09-22 공지). 09-23 13:45 헤더 잔여 59,999,986. 과금 = usage.total_tokens 1:1(모델별 가중치 없음, reasoning 포함).",
              "- 캐시: gpt-6-luna 적중 2,780토큰에도 차감 2,788 → 캐시 절감 0(⑩-b).",
              "- 모델: gpt-5.6-sol/terra/luna, gpt-6-sol/luna 200 / gpt-6-astra 404(09-11·09-23).",
              "- 토큰 구성: 케이스당 reasoning 3.7~4.9%, 입력 약 70~80%(`docs/token_ledger.md`).", ""]
    (ROOT / "docs" / "numbers.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
