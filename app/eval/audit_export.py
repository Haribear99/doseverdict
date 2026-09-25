"""
감사로그 공개 집계본 — `logs/`(git·Docker 제외)에서 재현에 필요한 필드만 뽑아 저장소에 둔다.

실행: .venv/Scripts/python.exe -m app.eval.audit_export  →  app/eval/data/audit_usage.jsonl
남기는 필드: ts, role, model, purpose, status, effort, usage. 오류 문자열·쿼터 헤더·프롬프트 해시는 빼서
게이트웨이 주소 등이 섞일 여지를 없앤다. `numbers.py`(누적 토큰)와 `ledger.py`(노드별 원장)는 이 파일만 읽는다.
"""
from __future__ import annotations

import json
from collections.abc import Iterator
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "app" / "eval" / "data" / "audit_usage.jsonl"
KEEP = ("ts", "role", "model", "purpose", "status", "effort", "usage")


def iter_audit() -> Iterator[dict]:
    """공개 집계본의 호출 기록(usage.total_tokens가 있는 것만)."""
    if not OUT.exists():
        return
    for line in OUT.read_text(encoding="utf-8").splitlines():
        if line.strip():
            yield json.loads(line)


def main() -> None:
    rows = []
    for lp in sorted((ROOT / "logs").glob("*.jsonl")):
        for line in lp.read_text(encoding="utf-8").splitlines():
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                continue
            if not (r.get("usage") or {}).get("total_tokens") or "ts" not in r or "model" not in r:
                continue
            rows.append({k: r.get(k) for k in KEEP} | {"source_log": lp.name})
    rows.sort(key=lambda r: r["ts"])
    OUT.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
    print(f"{len(rows)} calls, {sum(r['usage']['total_tokens'] for r in rows):,} tokens → {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
