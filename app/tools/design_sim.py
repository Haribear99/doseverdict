"""
Trial Design Simulator 도구 — evidence/dose_escalation_sim.py 래퍼.

출력은 "설계를 바꿔라"가 아니라 운영 특성(PCS·미확정률·과다노출 비율)과
목표 PCS 달성에 필요한 표본수다(제안서 1장 통계 규칙).
"""
from __future__ import annotations

from typing import Any

import numpy as np

import dose_escalation_sim as des  # evidence/

from app.tools import ToolResult, run_tool


def _design_fn(name: str, n_max: int | None):
    if name == "3+3":
        return des.run_3p3
    if name.upper() == "BOIN":
        return lambda p, rng: des.run_boin(p, rng, n_max=n_max or 36)
    raise ValueError(f"지원하지 않는 설계: {name} (3+3, BOIN)")


def operating_characteristics(true_dlt: list[float], design: str, n_max: int | None = None,
                              n_sim: int = 2000, seed: int = 20260807) -> ToolResult:
    def _run(**kw) -> dict[str, Any]:
        fn = _design_fn(kw["design"], kw["n_max"])
        r = des.evaluate(fn, kw["true_dlt"], kw["n_sim"], kw["seed"])
        lam_e, lam_d = des.boin_boundaries(des.TARGET)
        return {"design": kw["design"], "n_max": kw["n_max"], "n_sim": kw["n_sim"], "target_dlt": des.TARGET,
                "boin_boundaries": {"escalate_le": round(lam_e, 3), "deescalate_ge": round(lam_d, 3)},
                **{k: round(float(v), 2) for k, v in r.items()}}

    return run_tool("design.operating_characteristics", _run, true_dlt=true_dlt, design=design, n_max=n_max, n_sim=n_sim, seed=seed)


def compare_sample_matched(true_dlt: list[float], n_sim: int = 2000, seed: int = 20260807) -> ToolResult:
    """3+3 vs 표본 정합 BOIN vs 통상 BOIN — 조건을 통제한 비교만 내놓는다."""
    def _run(**kw) -> dict[str, Any]:
        r33 = des.evaluate(des.run_3p3, kw["true_dlt"], kw["n_sim"], kw["seed"])
        n_match = max(6, int(round(r33["N"] / 3.0)) * 3)  # 3+3 평균 표본에 코호트 단위로 맞춘다
        rb_m = des.evaluate(lambda p, rng: des.run_boin(p, rng, n_max=n_match), kw["true_dlt"], kw["n_sim"], kw["seed"])
        rb_36 = des.evaluate(lambda p, rng: des.run_boin(p, rng, n_max=36), kw["true_dlt"], kw["n_sim"], kw["seed"])
        rows = {"3+3": r33, f"BOIN(n={n_match})": rb_m, "BOIN(n=36)": rb_36}
        return {"n_matched": n_match,
                "rows": {k: {m: round(float(v), 2) for m, v in r.items()} for k, r in rows.items()},
                "reading": "표본을 맞춘 행끼리만 정확도를 비교한다. 과다노출은 절대수(N_over)가 아니라 비율(pct_over)로 본다."}

    return run_tool("design.compare_sample_matched", _run, true_dlt=true_dlt, n_sim=n_sim, seed=seed)


def required_sample_for_pcs(true_dlt: list[float], target_pcs: float = 50.0, design: str = "BOIN",
                            n_grid: tuple[int, ...] = (15, 18, 21, 24, 27, 30, 36, 42, 48), n_sim: int = 1500, seed: int = 20260807) -> ToolResult:
    """목표 정확 MTD 선택률을 만족하는 최소 n_max — '설계 교체'가 아니라 '요구량 산출'."""
    def _run(**kw) -> dict[str, Any]:
        grid = []
        found = None
        for n in kw["n_grid"]:
            r = des.evaluate(lambda p, rng, n=n: des.run_boin(p, rng, n_max=n), kw["true_dlt"], kw["n_sim"], kw["seed"])
            grid.append({"n_max": n, "PCS": round(float(r["PCS"]), 1), "none": round(float(r["none"]), 1), "N": round(float(r["N"]), 1)})
            if found is None and r["PCS"] >= kw["target_pcs"]:
                found = n
        return {"design": kw["design"], "target_pcs": kw["target_pcs"], "required_n_max": found, "grid": grid,
                "note": "3+3은 알고리즘상 표본을 늘릴 수 없으므로 목표 PCS가 3+3의 실측 PCS보다 높으면 표본과 설계를 함께 바꿔야 한다."}

    return run_tool("design.required_sample_for_pcs", _run, true_dlt=true_dlt, target_pcs=target_pcs, design=design, n_grid=n_grid, n_sim=n_sim, seed=seed)
