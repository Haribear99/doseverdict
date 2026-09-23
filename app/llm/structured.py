"""
구조화 출력 공통 호출 — 스키마는 Pydantic 모델에서 만들고, 응답은 같은 모델로 재검증한다.

- strict=True면 openai의 to_strict_json_schema로 변환(모든 필드 required, additionalProperties false). 게이트웨이 실측 docs/gateway_probe.md ⑪.
- 응답이 status="incomplete"(max_output_tokens 소진 등)면 파싱 전에 실패로 본다 — .parse()는 이 경우 LengthFinishReasonError를
  일관되게 내지 않는다(2026-09-23 게이트웨이 실측, interim-report-responses-parse-migration-on-azure-backed-gateway).
- 실패하면 오류 메시지를 붙여 1회 재시도한다. 그래도 실패하면 None과 오류를 돌려주고, 호출부는 빈 결과로 조용히 넘어가지 말고 실패를 기록한다.
- 반환 usage는 모든 시도의 합이다(토큰 원장이 실측값만 쓰도록).
"""
from __future__ import annotations

import json
from typing import Any, TypeVar

from openai.lib._pydantic import to_strict_json_schema
from pydantic import BaseModel, ValidationError

from app.llm.client import GatewayClient

M = TypeVar("M", bound=BaseModel)
_USAGE_KEYS = ("input_tokens", "output_tokens", "total_tokens", "reasoning_tokens", "cached_tokens")


def text_format(name: str, model: type[BaseModel], strict: bool) -> dict[str, Any]:
    schema = to_strict_json_schema(model) if strict else model.model_json_schema()
    return {"type": "json_schema", "name": name, "strict": strict, "schema": schema}


def _add_usage(acc: dict[str, int], u: dict[str, Any]) -> None:
    for k in _USAGE_KEYS:
        acc[k] = acc.get(k, 0) + int(u.get(k) or 0)


def call_structured(gc: GatewayClient, role: str, user_input: str, *, model: type[M], name: str, strict: bool,
                    instructions: str | None = None, reasoning_effort: str | None = None,
                    max_output_tokens: int | None = None, purpose: str = "", retries: int = 1) -> tuple[M | None, dict[str, Any]]:
    """반환: (검증된 모델 또는 None, meta{usage 합, model, prompt_sha256, attempts, error})."""
    fmt = text_format(name, model, strict)
    usage: dict[str, int] = {}
    meta: dict[str, Any] = {"usage": usage, "attempts": 0, "error": None}
    err = None
    for attempt in range(retries + 1):
        inp = user_input if not err else f"{user_input}\n\nYour previous output was rejected: {err}. Return valid JSON only."
        resp, rec = gc.respond(role, inp, instructions=instructions, text_format=fmt, reasoning_effort=reasoning_effort,
                               max_output_tokens=max_output_tokens, purpose=purpose)
        _add_usage(usage, rec.usage)
        meta.update(model=rec.model, prompt_sha256=rec.prompt_sha256, attempts=attempt + 1)
        status = getattr(resp, "status", None)
        if status == "incomplete":
            reason = getattr(getattr(resp, "incomplete_details", None), "reason", None)
            err = f"response incomplete ({reason})"
            continue
        try:
            obj = model.model_validate(json.loads(resp.output_text))
            meta["error"] = None
            return obj, meta
        except (json.JSONDecodeError, ValidationError) as e:
            err = f"{type(e).__name__}: {str(e)[:400]}"
    meta["error"] = err
    return None, meta


def record_failure(scratch: dict[str, Any], node: str, meta: dict[str, Any]) -> None:
    """실패를 상태에 남긴다 — 평가·UI가 '결함 없음'과 '생성 실패'를 구분할 수 있게."""
    scratch.setdefault("llm_failures", []).append({"node": node, "error": meta.get("error"), "attempts": meta.get("attempts")})
