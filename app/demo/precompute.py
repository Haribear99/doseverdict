"""
예시 프로토콜 3종을 기본(lean) 설정으로 실행해 상태를 저장한다 → UI '저장된 결과 즉시 보기'와 URL `?demo=N&cached=1`이 이 파일을 읽는다.
배포본(CPU)에서 심사위원이 3분을 기다리지 않게 하려는 것이며, 라이브 실행 버튼은 그대로 남는다.

실행: .venv/Scripts/python.exe -m app.demo.precompute            (약 3 × 30k 토큰)
산출: app/demo/results/demo1.json … demo3.json (ReviewState 전량, 감사 메타 포함)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from app.agents.graph import run_until_gate

ROOT = Path(__file__).resolve().parents[2]
DEMO_FILES = ["sotorasib_synopsis.md", "sotorasib_synopsis_fixed.md", "sotorasib_synopsis_injection.md"]
OUT = ROOT / "app" / "demo" / "results"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    only = {int(a) for a in sys.argv[1:]} if len(sys.argv) > 1 else set(range(1, len(DEMO_FILES) + 1))
    for i, name in enumerate(DEMO_FILES, 1):
        if i not in only:
            continue
        text = (ROOT / "app" / "demo" / name).read_text(encoding="utf-8")
        _, _, st = run_until_gate(text, run_id=f"demo{i}-precomputed", reviewers=["regulatory"])
        (OUT / f"demo{i}.json").write_text(st.model_dump_json(indent=1), encoding="utf-8")
        print(json.dumps({"demo": i, "file": name, "tokens": st.budget.used_tokens, "tools": st.budget.used_tool_calls, "findings": len(st.findings),
                          "verified": sum(1 for f in st.findings if f.verifier_status == "verified")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
