---
title: DoseVerdict
emoji: ⚖️
colorFrom: blue
colorTo: gray
sdk: docker
app_port: 7860
pinned: false
---

# DoseVerdict — "MTD는 RP2D가 아니다"

제4회 JUMP AI Agentic Drug Challenge **본선** 출품작 (팀 경기대 지피티 전공). 항암 1/2상 프로토콜의 용량 근거를
실제 약리 계산(RDKit·ChEMBL·openFDA·Open Targets·몬테카를로)과 규제 문서(FDA·ICH·식약처) 대조로 검증하는 의사결정지원 에이전트.

- 판정 권한 분리: 수치 판정은 도구, 규범 판정은 검색+NLI 검증기, 최종 승인은 사람. LLM(gpt-5.6)은 구조화·가설·문장 초안만.
- 근거가 결론을 지탱하지 못하면 결론을 만들지 않는다(기권). 예: TCR이 지표(C_avg/C_trough)에 따라 갈리면 보류하고 PK 자료를 요청.

## 실행 방법 4종

| 방법 | 절차 |
|---|---|
| ① 웹 UI | 배포 URL 접속 → 왼쪽 **예시 프로토콜** 선택 → **검토 실행** (약 3분, 25~45k 토큰; 기본 Reviewer 1인, 체크박스로 3인). Findings·Evidence Card·Patch Diff·Human Gate 탭 확인 |
| ② 원클릭 링크(라이브) | `<배포URL>/?demo=1&autorun=1` (①), `?demo=2` (용량 비교 계획을 갖춘 판), `?demo=3` (프롬프트 인젝션 적대 테스트) |
| ②′ 저장 결과 즉시 보기 | `<배포URL>/?demo=1&cached=1` (또는 사이드바 **⚡ 저장된 결과 즉시 보기**). 같은 예시를 기본 설정으로 실행해 둔 결과(`app/demo/results/`)를 LLM 호출 없이 바로 표시 — CPU 배포본에서 3분을 기다리지 않아도 된다 |
| ③ CLI / 직접 입력 | `python -m app.cli review app/demo/sotorasib_synopsis.md --approve-all --out result.json` 또는 UI에서 **직접 붙여넣기 / 파일 업로드** |

예시 쿼리(프로토콜 문장): *"The MTD will be selected as the RP2D."* → 규제 검색(KR/US 분리)·TCR 3지표·3+3 운영특성 계산 → 기권 1건 + 결함 finding + Patch Diff.

## 로컬 설정
```
cp .env.example .env     # 팀 API 키를 .env에 직접 입력 (절대 커밋 금지)
uv venv --python 3.13 .venv && uv pip install --python .venv/Scripts/python.exe -r requirements.txt
.venv/Scripts/python.exe -m app.llm.smoke_test          # 게이트웨이 프로브 → docs/gateway_probe.md
.venv/Scripts/python.exe -m app.corpus.index build      # (선택) 코퍼스 인덱스 재빌드(GPU 권장)
.venv/Scripts/python.exe -m streamlit run app/ui/main.py
```

## 구조
`app/llm`(게이트웨이·감사로그) · `app/schema`(Trial Schema·상태) · `app/agents`(Compiler·Planner·도구 노드·Reviewer·Findings·Verifier·LangGraph) ·
`app/tools`(RDKit·ChEMBL·openFDA·Open Targets·시뮬·CT.gov) · `app/corpus`(규제 PDF 7종·절 청킹·bge-m3+BM25) · `app/verify`(NLI) · `app/ui`(Streamlit) · `app/eval`(평가셋)
개발 기록: `docs/DEV_LOG.md` · 리서치: `RESEARCH/` · 예선 제안서: `제안서_본문.md`
