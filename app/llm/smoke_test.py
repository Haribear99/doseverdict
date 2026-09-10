"""
게이트웨이 스모크 테스트 — 총 토큰 사용을 최소화(목표 1만 토큰 이내)하면서
① 3개 모델 응답 + 쿼터 헤더  ② GPT-6 Astra 프로브(400/404 예상)
③ Structured Outputs  ④ function tool 호출  ⑤ 스트리밍  ⑥ reasoning effort별 토큰 소비
를 실측해 docs/gateway_probe.md 에 표로 기록한다.

실행:  .venv/Scripts/python.exe -m app.llm.smoke_test
"""
from __future__ import annotations

import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

from openai import APIStatusError

from app.llm.client import GatewayClient, QuotaExhausted

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs" / "gateway_probe.md"
MODELS = ["gpt-5.6-luna", "gpt-5.6-terra", "gpt-5.6-sol"]
ASTRA_PROBES = ["gpt-6-astra", "gpt-6.0", "gpt-6", "gpt-6.0-astra", "gpt-6-astra-2026-09-03"]


def row(*cells) -> str:
    return "| " + " | ".join(str(c) for c in cells) + " |"


def main() -> int:
    gc = GatewayClient(audit_path=ROOT / "logs" / "smoke_test.jsonl")
    lines = [f"# 게이트웨이 프로브 결과 ({datetime.now():%Y-%m-%d %H:%M})", ""]

    # ① 모델별 최소 호출 + 헤더
    lines += ["## ① 모델별 최소 호출 (input: 'Reply only OK')", "",
              row("model", "status", "output", "in", "out", "reasoning", "total", "consumed(hdr)", "quota_remaining(hdr)", "tpm_left", "rpm_left", "latency_s"),
              row(*["---"] * 12)]
    for m in MODELS:
        try:
            resp, rec = gc.respond("bulk", "Reply only OK", model=m, purpose="smoke_min", max_output_tokens=16)
            q = rec.quota
            lines.append(row(m, rec.status, repr(resp.output_text)[:20], rec.usage.get("input_tokens"), rec.usage.get("output_tokens"),
                             rec.usage.get("reasoning_tokens"), rec.usage.get("total_tokens"), q.get("x-team-tokens-consumed"),
                             q.get("x-team-remaining-quota-tokens"), q.get("x-team-remaining-tokens"), q.get("x-team-remaining-requests"), rec.latency_s))
        except QuotaExhausted as e:
            lines.append(row(m, 403, str(e), *[""] * 9)); break
        except APIStatusError as e:
            lines.append(row(m, e.status_code, str(e)[:80], *[""] * 9))
        time.sleep(0.5)

    # ② Astra 프로브
    lines += ["", "## ② GPT-6 Astra 프로브 (허용 목록 밖 → 400/404 예상)", "", row("model name", "status", "message"), row("---", "---", "---")]
    for m in ASTRA_PROBES:
        try:
            resp, rec = gc.respond("bulk", "Reply only OK", model=m, purpose="astra_probe", max_output_tokens=16)
            lines.append(row(m, rec.status, f"**응답 성공** output={resp.output_text!r} model={getattr(resp, 'model', '?')}"))
        except APIStatusError as e:
            body = ""
            try:
                body = json.dumps(e.body, ensure_ascii=False)[:160]
            except Exception:
                body = str(e)[:160]
            lines.append(row(m, e.status_code, body.replace("|", "\\|")))
        except Exception as e:  # noqa: BLE001
            lines.append(row(m, "ERR", str(e)[:120]))
        time.sleep(0.5)

    # ③ Structured Outputs (json_schema strict)
    lines += ["", "## ③ Structured Outputs (text.format=json_schema, strict)", ""]
    schema = {
        "type": "json_schema", "name": "dose_check", "strict": True,
        "schema": {"type": "object", "additionalProperties": False,
                   "properties": {"drug": {"type": "string"}, "dose_mg": {"type": "integer"}, "verdict": {"type": "string", "enum": ["covered", "not_covered", "abstain"]}},
                   "required": ["drug", "dose_mg", "verdict"]},
    }
    try:
        # 기본 reasoning(medium)이 출력 상한을 먼저 소진하면 output_text가 비어 파싱이 실패한다 → 추출 호출은 effort none + 넉넉한 상한
        resp, rec = gc.respond("extract", "Sotorasib 960 mg once daily. Return the fields. If evidence is insufficient, verdict must be 'abstain'.",
                               text_format=schema, purpose="smoke_structured", reasoning_effort="none", max_output_tokens=300)
        parsed = json.loads(resp.output_text)
        lines.append(f"- status {rec.status}, parsed={parsed}, usage={rec.usage}")
    except Exception as e:  # noqa: BLE001
        lines.append(f"- **실패**: {str(e)[:200]}")

    # ④ function tool 호출
    lines += ["", "## ④ Function tool 호출", ""]
    tools = [{"type": "function", "name": "get_label_pk", "strict": True,
              "description": "Fetch FDA label PK parameters for a drug",
              "parameters": {"type": "object", "additionalProperties": False, "properties": {"brand_name": {"type": "string"}}, "required": ["brand_name"]}}]
    try:
        resp, rec = gc.respond("planner", "Look up the label PK for LUMAKRAS using the tool. Do not answer from memory.",
                               tools=tools, purpose="smoke_tool", max_output_tokens=128, model="gpt-5.6-terra")
        calls = [o for o in resp.output if getattr(o, "type", "") == "function_call"]
        lines.append(f"- status {rec.status}, function_calls={[(c.name, c.arguments) for c in calls]}, usage={rec.usage}")
    except Exception as e:  # noqa: BLE001
        lines.append(f"- **실패**: {str(e)[:200]}")

    # ⑤ 스트리밍 (SDK stream=True 이벤트 수신)
    lines += ["", "## ⑤ 스트리밍", ""]
    try:
        t0 = time.perf_counter()
        n_events, text = 0, ""
        with gc.client.responses.stream(model="gpt-5.6-luna", input="Count from 1 to 5, comma separated.", max_output_tokens=32) as s:
            for ev in s:
                n_events += 1
                if ev.type == "response.output_text.delta":
                    text += ev.delta
            final = s.get_final_response()
        lines.append(f"- events={n_events}, text={text!r}, usage={getattr(final, 'usage', None)}, latency={time.perf_counter() - t0:.2f}s")
    except Exception as e:  # noqa: BLE001
        lines.append(f"- **실패**: {str(e)[:200]}")

    # ⑥ reasoning effort별 토큰 (Luna, 동일 프롬프트)
    lines += ["", "## ⑥ reasoning effort별 토큰 소비 (gpt-5.6-luna, 동일 프롬프트)", "",
              row("effort", "status", "in", "out", "reasoning", "total", "consumed(hdr)", "latency_s"), row(*["---"] * 8)]
    prompt = "A drug has half-life 5 h and is dosed once daily. Roughly what fraction of Cmax remains at 24 h? One number."
    for eff in ["none", "low", "medium"]:
        try:
            resp, rec = gc.respond("bulk", prompt, model="gpt-5.6-luna", reasoning_effort=eff, purpose=f"smoke_effort_{eff}", max_output_tokens=200)
            lines.append(row(eff, rec.status, rec.usage.get("input_tokens"), rec.usage.get("output_tokens"), rec.usage.get("reasoning_tokens"),
                             rec.usage.get("total_tokens"), rec.quota.get("x-team-tokens-consumed"), rec.latency_s))
        except Exception as e:  # noqa: BLE001
            lines.append(row(eff, "ERR", str(e)[:100].replace("|", "\\|"), *[""] * 5))
        time.sleep(0.5)

    totals = gc.audit_totals()
    lines += ["", "## 합계", "", f"```json\n{json.dumps(totals, ensure_ascii=False, indent=2)}\n```"]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    print(f"\n→ {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
