"""
수정안 적용 — 검토 결과의 수정안(suggested_patch)을 원문 span에 치환해 '수정판'을 만든다(결정론, LLM 0).

용도: UI "수정안 적용 후 재검토"(에이전트가 자기 수정안을 적용한 판을 다시 검토해 남은 문제만 보고)와
특이도 평가 C(`app/eval/specificity.py`). 원문에 span이 그대로 없거나 수정안이 비어 있으면 건너뛴다.
"""
from __future__ import annotations

from typing import Any


def apply_patches(text: str, findings: list[Any]) -> tuple[str, list[dict]]:
    """findings: Finding 모델 또는 dict. 반환: (수정판, 적용 목록[{finding_id, span, patch}])."""
    applied = []
    for f in findings:
        g = f if isinstance(f, dict) else f.model_dump()
        span = (g.get("protocol_span") or {}).get("text") or ""
        patch = g.get("suggested_patch")
        if g.get("verdict") == "defect" and patch and span and span in text:
            text = text.replace(span, patch, 1)
            applied.append({"finding_id": g.get("finding_id"), "span": span, "patch": patch})
    return text, applied


def still_flagged(patches: list[dict], findings: list[Any]) -> list[bool]:
    """재검토 결과에서 수정된 문장이 다시 지적됐는가(채점과 같은 겹침 규칙)."""
    from app.eval.run_eval import matches
    spans = []
    for f in findings:
        g = f if isinstance(f, dict) else f.model_dump()
        if g.get("verdict") == "defect" and g.get("finding_id") != "F00":
            spans.append((g.get("protocol_span") or {}).get("text") or "")
    return [any(matches(p["patch"], [s]) for s in spans) for p in patches]
