# DoseVerdict — "MTD는 RP2D가 아니다"

제4회 JUMP AI Agentic Drug Challenge **본선** 출품작. 항암 1/2상 프로토콜의 용량 근거를
실제 약리 계산(RDKit·ChEMBL·openFDA·몬테카를로)과 규제 문서 대조로 검증하는 의사결정지원 에이전트.

- 예선 제안서: `제안서_본문.md` / 근거 산출 스크립트: `evidence/`
- 본선 앱 코드: `app/` (진행 중) — 계획: `docs/`
- 리서치 세션: `RESEARCH/`

## 설정
```
cp .env.example .env     # 팀 API 키를 .env에 직접 입력 (절대 커밋 금지)
uv venv --python 3.13 .venv && uv pip install --python .venv/Scripts/python.exe -r requirements.txt
.venv/Scripts/python.exe -m app.llm.smoke_test   # 게이트웨이 프로브 → docs/gateway_probe.md
```
