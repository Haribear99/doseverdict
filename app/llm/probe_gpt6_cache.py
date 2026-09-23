"""
게이트웨이 추가 프로브(2026-09-23) — 토큰 소량(목표 1만 이내)으로
⑨ GPT-6 세대 Sol/Luna 배포 여부(09-22 Azure GA)  ⑩ 프롬프트 캐시 적중 시 팀 쿼터 차감 방식
을 실측해 docs/gateway_probe.md 끝에 절로 덧붙인다.

실행:  .venv/Scripts/python.exe -m app.llm.probe_gpt6_cache
"""
from __future__ import annotations

import json
import time
from datetime import datetime
from pathlib import Path

from openai import APIStatusError

from app.llm.client import GatewayClient

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs" / "gateway_probe.md"
GPT6_PROBES = ["gpt-6-sol", "gpt-6-luna", "gpt-6-sol-2026-09-22", "gpt-6-luna-2026-09-22"]


def row(*cells) -> str:
    return "| " + " | ".join(str(c) for c in cells) + " |"


def _consumed(rec) -> int | None:
    v = (rec.quota or {}).get("x-team-tokens-consumed")
    return int(v) if v not in (None, "") else None


def main() -> int:
    gc = GatewayClient(audit_path=ROOT / "logs" / "smoke_test.jsonl")
    lines = ["", "---", "", f"## ⑨ GPT-6 세대 Sol/Luna 프로브 ({datetime.now():%Y-%m-%d %H:%M})", "",
             row("model name", "status", "message"), row("---", "---", "---")]
    for m in GPT6_PROBES:
        try:
            resp, rec = gc.respond("bulk", "Reply only OK", model=m, purpose="gpt6_probe", max_output_tokens=16)
            lines.append(row(m, rec.status, f"**응답 성공** output={resp.output_text!r} model={getattr(resp, 'model', '?')}"))
        except APIStatusError as e:
            try:
                body = json.dumps(e.body, ensure_ascii=False)[:160]
            except Exception:  # noqa: BLE001
                body = str(e)[:160]
            lines.append(row(m, e.status_code, body.replace("|", "\\|")))
        time.sleep(0.5)

    # ⑩ 캐시: 1,024토큰 이상 동일 접두부로 같은 모델을 연속 3회 호출
    prefix = "You are a clinical pharmacology assistant. Reference context follows.\n" + \
             "\n".join(f"Rule {i}: dose rationale must cite exposure metric C_max, C_avg, C_trough and label section." for i in range(120))
    lines += ["", f"## ⑩ 프롬프트 캐시와 쿼터 차감 (gpt-5.6-luna, 공통 접두부 약 {len(prefix)//4} 토큰 추정)", "",
              row("call", "in", "cached", "out", "total", "consumed(hdr)", "quota_remaining(hdr)"), row(*["---"] * 7)]
    for i in range(3):
        resp, rec = gc.respond("bulk", prefix + f"\nQuestion {i}: reply only OK", model="gpt-5.6-luna",
                               purpose="cache_probe", max_output_tokens=16, reasoning_effort="none",
                               prompt_cache_key="dv-cache-probe")
        u = rec.usage
        lines.append(row(i + 1, u.get("input_tokens"), u.get("cached_tokens"), u.get("output_tokens"), u.get("total_tokens"),
                         _consumed(rec), (rec.quota or {}).get("x-team-remaining-quota-tokens")))
        time.sleep(1.0)

    with OUT.open("a", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
