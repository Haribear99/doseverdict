"""구조화 출력 경화 테스트 — 게이트웨이 없이 가짜 클라이언트로 검증."""
from types import SimpleNamespace

from openai.lib._pydantic import to_strict_json_schema

from app.agents.findings import _FindingOut, _FindingsOut, _RewriteOut
from app.agents.planner import _Questions
from app.agents.reviewers import _Position, _Positions
from app.llm.structured import call_structured, record_failure
from app.schema.trial_schema import TrialSchema


class FakeGateway:
    """respond()가 미리 정한 (status, output_text)를 차례로 돌려준다."""

    def __init__(self, outputs):
        self.outputs = list(outputs)
        self.inputs = []

    def respond(self, role, inp, **kw):
        self.inputs.append(inp)
        status, text = self.outputs.pop(0)
        resp = SimpleNamespace(status=status, output_text=text, incomplete_details=SimpleNamespace(reason="max_output_tokens"))
        rec = SimpleNamespace(usage={"input_tokens": 10, "output_tokens": 5, "total_tokens": 15}, model="m", prompt_sha256="h")
        return resp, rec


def test_strict_schema_builds_for_every_llm_output_model():
    # strict 변환이 예외 없이 되는지(임의 키 맵 dict[str, …]이 남아 있으면 게이트웨이가 400을 낸다 — gateway_probe ⑪)
    def walk(o):
        if isinstance(o, dict):
            ap = o.get("additionalProperties")
            assert ap in (None, False), f"map-typed field left in strict schema: {ap}"
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)

    for m in (TrialSchema, _Questions, _Positions, _FindingsOut, _RewriteOut):
        s = to_strict_json_schema(m)
        assert s["type"] == "object"
        walk(s)


def test_source_spans_accepts_legacy_dict():
    ts = TrialSchema.model_validate({"source_spans": {"design.dose_strategy.rp2d_rule_text": {"section": "5.2", "text": "RP2D = MTD"}}})
    assert ts.source_spans[0].field == "design.dose_strategy.rp2d_rule_text"
    assert ts.source_spans[0].text == "RP2D = MTD"


def test_field_order_rationale_before_verdict():
    assert list(_Position.model_fields).index("position") < list(_Position.model_fields).index("severity")
    names = list(_FindingOut.model_fields)
    assert names.index("protocol_fact") < names.index("category") and names.index("evidence_fact") < names.index("severity")


def test_incomplete_then_valid_retries_and_sums_usage():
    gc = FakeGateway([("incomplete", '{"evidence_fact": "tru'), ("completed", '{"evidence_fact": "ok"}')])
    out, meta = call_structured(gc, "planner", "x", model=_RewriteOut, name="rewrite", strict=True)
    assert out.evidence_fact == "ok"
    assert meta["attempts"] == 2 and meta["usage"]["total_tokens"] == 30
    assert "incomplete" in gc.inputs[1]          # 두 번째 요청에 실패 사유를 피드백했다


def test_persistent_failure_returns_none_and_is_recorded():
    gc = FakeGateway([("completed", "not json"), ("completed", '{"wrong": 1}')])
    out, meta = call_structured(gc, "planner", "x", model=_RewriteOut, name="rewrite", strict=True)
    assert out is None and meta["error"]
    scratch = {}
    record_failure(scratch, "rewrite", meta)
    assert scratch["llm_failures"][0]["node"] == "rewrite"
