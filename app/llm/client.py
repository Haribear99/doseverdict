"""
DoseVerdict — 데이콘 OpenAI 호환 게이트웨이 클라이언트.

- Base URL / api-key 헤더 / 역할별 모델명은 전부 환경변수에서 읽는다 (Astra 개방 시 .env만 수정).
- 모든 호출의 팀 쿼터 헤더(x-team-*)를 파싱해 JSONL 감사로그에 남긴다 (리소스 효율성 평가 근거).
- 429는 지수 백오프로 재시도, 403(팀 쿼터 소진)은 즉시 예외로 올린다.
"""
from __future__ import annotations

import hashlib
import json
import os
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from openai import APIStatusError, OpenAI, RateLimitError

load_dotenv()

ROLE_ENV = {
    "planner": "DV_MODEL_PLANNER",
    "reviewer": "DV_MODEL_REVIEWER",
    "extract": "DV_MODEL_EXTRACT",
    "bulk": "DV_MODEL_BULK",
}
DEFAULT_MODELS = {
    "planner": "gpt-5.6-sol",
    "reviewer": "gpt-5.6-sol",
    "extract": "gpt-5.6-terra",
    "bulk": "gpt-5.6-luna",
}
QUOTA_HEADERS = (
    "x-team-remaining-quota-tokens",
    "x-team-tokens-consumed",
    "x-team-remaining-tokens",
    "x-team-remaining-requests",
)


class QuotaExhausted(RuntimeError):
    """403 — 팀 전체 토큰 한도 소진."""


@dataclass
class CallRecord:
    ts: str
    role: str
    model: str
    purpose: str
    prompt_sha256: str
    status: int
    latency_s: float
    usage: dict[str, Any] = field(default_factory=dict)
    quota: dict[str, str | None] = field(default_factory=dict)
    error: str | None = None


def model_for(role: str) -> str:
    return os.getenv(ROLE_ENV[role], DEFAULT_MODELS[role])


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


class GatewayClient:
    def __init__(self, audit_path: str | os.PathLike | None = None, max_retries: int = 4):
        api_key = os.getenv("OPENAI_API_KEY")
        base_url = os.getenv("OPENAI_BASE_URL")
        if not api_key or api_key == "API_KEY_PLACEHOLDER":
            raise RuntimeError("OPENAI_API_KEY가 .env에 없습니다. .env.example을 복사해 키를 직접 입력하세요.")
        if not base_url:
            raise RuntimeError("OPENAI_BASE_URL이 .env에 없습니다.")
        self.client = OpenAI(
            base_url=base_url,
            api_key=api_key,
            default_headers={"api-key": api_key},  # 게이트웨이는 api-key 헤더로 인증한다
            max_retries=0,  # 재시도는 여기서 직접 제어(403은 재시도 금지)
        )
        self.audit_path = Path(audit_path or os.getenv("DV_AUDIT_LOG", "logs/llm_calls.jsonl"))
        self.audit_path.parent.mkdir(parents=True, exist_ok=True)
        self.max_retries = max_retries

    # ------------------------------------------------------------------ core
    def respond(
        self,
        role: str,
        input: str | list[dict[str, Any]],
        *,
        purpose: str = "",
        instructions: str | None = None,
        tools: list[dict[str, Any]] | None = None,
        text_format: dict[str, Any] | None = None,
        reasoning_effort: str | None = None,
        max_output_tokens: int | None = None,
        model: str | None = None,
        **extra: Any,
    ):
        """Responses API 1회 호출. 반환: (response, CallRecord)."""
        model = model or model_for(role)
        body: dict[str, Any] = {"model": model, "input": input}
        if instructions:
            body["instructions"] = instructions
        if tools:
            body["tools"] = tools
        if text_format:
            body["text"] = {"format": text_format}
        if reasoning_effort:
            body["reasoning"] = {"effort": reasoning_effort}
        if max_output_tokens:
            body["max_output_tokens"] = max_output_tokens
        body.update(extra)

        prompt_hash = _sha(json.dumps(body, ensure_ascii=False, sort_keys=True, default=str))
        delay = 2.0
        for attempt in range(self.max_retries + 1):
            t0 = time.perf_counter()
            try:
                raw = self.client.responses.with_raw_response.create(**body)
                resp = raw.parse()
                rec = CallRecord(
                    ts=datetime.now(timezone.utc).isoformat(),
                    role=role, model=model, purpose=purpose, prompt_sha256=prompt_hash,
                    status=raw.status_code, latency_s=round(time.perf_counter() - t0, 3),
                    usage=_usage_dict(resp), quota=_quota(raw.headers),
                )
                self._log(rec)
                return resp, rec
            except RateLimitError as e:  # 429
                self._log(self._err_rec(role, model, purpose, prompt_hash, 429, t0, str(e)))
                if attempt == self.max_retries:
                    raise
                time.sleep(delay)
                delay *= 2
            except APIStatusError as e:
                self._log(self._err_rec(role, model, purpose, prompt_hash, e.status_code, t0, str(e)))
                if e.status_code == 403:
                    raise QuotaExhausted("팀 토큰 한도 소진(403). 운영진 문의 필요.") from e
                raise

    # ------------------------------------------------------------------ util
    def _err_rec(self, role, model, purpose, h, status, t0, msg) -> CallRecord:
        return CallRecord(
            ts=datetime.now(timezone.utc).isoformat(), role=role, model=model, purpose=purpose,
            prompt_sha256=h, status=status, latency_s=round(time.perf_counter() - t0, 3), error=msg[:300],
        )

    def _log(self, rec: CallRecord) -> None:
        with self.audit_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(rec.__dict__, ensure_ascii=False) + "\n")

    def audit_totals(self) -> dict[str, Any]:
        """감사로그 집계: 호출 수, 모델별 토큰, 마지막 잔여 쿼터."""
        totals: dict[str, Any] = {"calls": 0, "by_model": {}, "last_quota": None}
        if not self.audit_path.exists():
            return totals
        for line in self.audit_path.read_text(encoding="utf-8").splitlines():
            r = json.loads(line)
            totals["calls"] += 1
            m = totals["by_model"].setdefault(r["model"], {"calls": 0, "input": 0, "output": 0, "total": 0})
            m["calls"] += 1
            u = r.get("usage") or {}
            m["input"] += u.get("input_tokens") or 0
            m["output"] += u.get("output_tokens") or 0
            m["total"] += u.get("total_tokens") or 0
            if (r.get("quota") or {}).get("x-team-remaining-quota-tokens"):
                totals["last_quota"] = r["quota"]["x-team-remaining-quota-tokens"]
        return totals


def _usage_dict(resp) -> dict[str, Any]:
    u = getattr(resp, "usage", None)
    if u is None:
        return {}
    d = u.model_dump() if hasattr(u, "model_dump") else dict(u)
    return {k: d.get(k) for k in ("input_tokens", "output_tokens", "total_tokens")} | {
        "reasoning_tokens": (d.get("output_tokens_details") or {}).get("reasoning_tokens"),
        "cached_tokens": (d.get("input_tokens_details") or {}).get("cached_tokens"),
    }


def _quota(headers) -> dict[str, str | None]:
    return {h: headers.get(h) for h in QUOTA_HEADERS}
