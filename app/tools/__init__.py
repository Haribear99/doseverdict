"""
도구 계층 — 예선 `evidence/` 스크립트를 수정하지 않고 import 가능한 함수로 감싼다.

규칙(제안서 2장): 도구 실패는 예외가 아니라 관측값이다. 모든 도구는 ToolResult를 돌려주고,
Orchestrator가 실패를 보고 대체 소스로 재계획한다.
"""
from __future__ import annotations

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
