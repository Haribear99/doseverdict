"""GatewayClient 단위 테스트 — 실제 API 호출 없이 헤더 파싱·감사로그·모델 라우팅만 검증."""
import json
import os

import pytest

from app.llm import client as c


def test_model_for_reads_env(monkeypatch):
    monkeypatch.setenv("DV_MODEL_PLANNER", "gpt-6-astra")
    assert c.model_for("planner") == "gpt-6-astra"
    monkeypatch.delenv("DV_MODEL_PLANNER")
    assert c.model_for("planner") == "gpt-5.6-sol"
    assert c.model_for("bulk") == "gpt-5.6-luna"


def test_quota_header_parse():
    hdrs = {"x-team-remaining-quota-tokens": "29999000", "x-team-tokens-consumed": "12"}
    q = c._quota(hdrs)
    assert q["x-team-remaining-quota-tokens"] == "29999000"
    assert q["x-team-remaining-requests"] is None


def test_client_requires_key(monkeypatch, tmp_path):
    monkeypatch.setenv("OPENAI_API_KEY", "API_KEY_PLACEHOLDER")
    monkeypatch.setenv("OPENAI_BASE_URL", "https://example.invalid/v1")
    with pytest.raises(RuntimeError):
        c.GatewayClient(audit_path=tmp_path / "a.jsonl")


def test_audit_totals(monkeypatch, tmp_path):
    monkeypatch.setenv("OPENAI_API_KEY", "dummy-key-for-unit-test")
    monkeypatch.setenv("OPENAI_BASE_URL", "https://example.invalid/v1")
    gc = c.GatewayClient(audit_path=tmp_path / "a.jsonl")
    rec = c.CallRecord(ts="t", role="bulk", model="gpt-5.6-luna", purpose="p", prompt_sha256="h", status=200, latency_s=0.1,
                       usage={"input_tokens": 10, "output_tokens": 5, "total_tokens": 15},
                       quota={"x-team-remaining-quota-tokens": "100"})
    gc._log(rec); gc._log(rec)
    t = gc.audit_totals()
    assert t["calls"] == 2 and t["by_model"]["gpt-5.6-luna"]["total"] == 30 and t["last_quota"] == "100"
