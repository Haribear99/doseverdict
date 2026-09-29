"""
도구 계층 — 예선 `evidence/` 스크립트를 수정하지 않고 import 가능한 함수로 감싼다.

규칙(제안서 2장): 도구 실패는 예외가 아니라 관측값이다. 모든 도구는 ToolResult를 돌려주고,
Orchestrator가 실패를 보고 대체 소스로 재계획한다.
"""
from __future__ import annotations

import os
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE_DIR = ROOT / "evidence"
if str(EVIDENCE_DIR) not in sys.path:
    sys.path.insert(0, str(EVIDENCE_DIR))


@dataclass
class ToolResult:
    tool: str
    ok: bool
    data: Any = None
    error: str | None = None
    latency_s: float = 0.0
    source: dict[str, Any] = field(default_factory=dict)  # url, retrieved_at 등 근거 메타


def run_tool(name: str, fn: Callable[..., Any], **kwargs) -> ToolResult:
    t0 = time.perf_counter()
    try:
        data = fn(**kwargs)
        return ToolResult(tool=name, ok=True, data=data, latency_s=round(time.perf_counter() - t0, 3))
    except Exception as e:  # noqa: BLE001 — 실패는 관측값
        return ToolResult(tool=name, ok=False, error=f"{type(e).__name__}: {e}"[:400], latency_s=round(time.perf_counter() - t0, 3))


# 후향 검증(app/eval/retro.py) 전용 시점 고정 — 승인 전 정보만 쓰도록 승인 후 자료 경로를 막는다. 평소에는 둘 다 꺼져 있다.
def asof_date() -> str | None:
    """DV_ASOF_DATE(YYYY-MM-DD): CT.gov 검색을 이 날짜 이전 시작 시험으로 제한하고, 승인약 목록(현재 시점 정보)을 쓰지 않는다."""
    return os.getenv("DV_ASOF_DATE") or None


def label_blinded() -> bool:
    """DV_BLIND_LABEL=1: openFDA 라벨(승인 후 문서) 조회를 404와 같게 처리 → 미승인 후보 경로(프로토콜 보고 PK)로 간다."""
    return os.getenv("DV_BLIND_LABEL", "0").lower() in ("1", "true", "on")
