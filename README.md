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

- 판정 권한 분리: 수치 판정은 도구, 규범 판정은 검색+NLI 검증기, 최종 승인은 사람. LLM(gpt-6-sol)은 구조화·가설·문장 초안만.
- 근거가 결론을 지탱하지 못하면 결론을 만들지 않는다(기권). 예: TCR이 지표(C_avg/C_trough)에 따라 갈리면 보류하고 PK 자료를 요청.

## 실행 방법 4종

배포 URL: `https://huggingface.co/spaces/Haribear99/doseverdict` (앱 직접 주소 `https://haribear99-doseverdict.hf.space`). 제출 전 공개 전환 예정.

| 방법 | 절차 |
|---|---|
| ① 웹 UI | 배포 URL 접속 → 왼쪽 **예시 프로토콜** 선택 → **검토 실행** (배포본 CPU 웜 상태 약 1.5분, 3~4만 토큰; 기본 Reviewer 1인, 체크박스로 3인). Findings(Patch Diff)·Human Gate·근거·도구 호출·Audit·후향 검증 탭 확인 |
| ② 원클릭 링크(라이브) | `<배포URL>/?demo=1&autorun=1` (①), `?demo=2` (용량 비교 계획을 갖춘 판), `?demo=3` (프롬프트 인젝션 적대 테스트) |
| ②′ 저장 결과 즉시 보기 | `<배포URL>/?demo=1&cached=1` (또는 사이드바 **⚡ 저장된 결과 즉시 보기**). 같은 예시를 기본 설정으로 실행해 둔 결과(`app/demo/results/`)를 LLM 호출 없이 바로 표시 — 라이브 검토를 기다리지 않아도 된다(권장 동선) |
| ③ CLI / 직접 입력 | `python -m app.cli review app/demo/sotorasib_synopsis.md --approve-all --out result.json` 또는 UI에서 **직접 붙여넣기 / 파일 업로드** |
| ④ 로컬 Docker | `docker build -t doseverdict . && docker run -p 7860:7860 -e OPENAI_API_KEY=... -e OPENAI_BASE_URL=... doseverdict` → `http://localhost:7860` |

예시 쿼리(프로토콜 문장): *"The MTD will be selected as the RP2D."* → 규제 검색(KR/US 분리)·TCR 3지표·3+3 운영특성 계산 → 기권 1건 + 결함 finding + Patch Diff.
예시 ④ 로를라티닙(매핑 표 밖 약물, `?demo=4`), ⑤ 미승인 가상 후보 DV-505(프로토콜 보고 PK, `?demo=5`)도 같은 방식으로 열 수 있다. 첫 화면의 **후향 검증** 절과 마지막 탭에서 실사례 검증 결과를 볼 수 있다.

## 평가 결과 요약 (모든 수치의 원천: `docs/numbers.md`)

| 무엇을 물었나 | 결과 | 판정 |
|---|---|---|
| 합성 결함(Silver Set 원 20)을 찾고 올바른 규범으로 근거를 대나 | span 0.950/0.975, grounded 0.450/0.517(같은 설정 2회), 비기권 검증 통과율 0.962, 케이스당 약 4만 토큰 | 09-11 배포 기본 대비 토큰 −10.4%, 검증 통과율 +0.044 [+0.012, +0.071] |
| 다른 약에서도 도나(다약물 30) | span 0.933, grounded 0.450, 약리 축 30/30 완주 | 같은 결함 문장을 비슷한 수준으로 찾음 |
| 실제 약 43건의 승인 전 1상 초록에서 FDA가 용량최적화 PMR을 부과한 14건을 가려내나(사전 등록) | AUROC 0.440 [0.270, 0.621]. 43건 모두에서 용량 근거 결함을 지적(지적 정확성 미평가, 21/161건은 입력 템플릿 문장이 유발) | **null** — 판별력 없음과 구별되지 않음. 초록은 모델이 42~43/43 재식별, 파이프라인이 11/43에서 약 이름을 스스로 복원 |
| 같은 모델을 도구 없이 한 번 부르면(원샷, 사전 등록) | grounded 에이전트 0.483 대 원샷 0.392, 차이 −0.092 [−0.208, +0.021]. 토큰 8분의 1 | **차이 확인 안 됨**. 사후: 같은 판정기로 근거 문장을 원문과 대조하면 에이전트 94~98%, 원샷 55~77% 확인(판정기가 에이전트 검증기와 같은 모델이라 에이전트에 유리) |

정리하면, 이 에이전트에 기대할 수 있는 것은 "더 많이 찾는다"가 아니라 **찾은 것마다 원문 조항·도구 계산값·기권 사유가 붙어 사람이 확인할 수 있다**는 점이고, 그 차이도 사후 분석으로만 확인됐다. 부정적 결과(ablation 기여 미측정, 후향 검증 null, 원샷 대비 탐지 우위 없음)와 누설 차단의 빈틈도 모두 공개한다. 상세: `docs/상세기술서.md` 6절.

## 로컬 설정
```
cp .env.example .env     # 팀 API 키를 .env에 직접 입력 (절대 커밋 금지)
uv venv --python 3.13 .venv && uv pip install --python .venv/Scripts/python.exe -r requirements.txt
.venv/Scripts/python.exe -m app.llm.smoke_test          # 게이트웨이 프로브 → docs/gateway_probe.md
.venv/Scripts/python.exe -m app.corpus.index build      # (선택) 코퍼스 인덱스 재빌드(GPU 권장)
.venv/Scripts/python.exe -m streamlit run app/ui/main.py
```

## 배포 (Hugging Face Spaces, Docker SDK)

1. Space 생성: **Docker** SDK, CPU basic. 배포는 `python -m app.deploy_space`로만 한다(커밋된 파일을 git archive로 올리고, Space용 `.gitattributes`에 LFS 규칙을 넣는다 — 이 규칙이 없으면 코퍼스 인덱스가 LFS 포인터로 들어가 규제 검색이 실패한다). 포트 7860, 이 README 프런트매터가 Space 설정.
2. **Settings → Variables and secrets**에 `OPENAI_API_KEY`(팀 키, Secret)와 `OPENAI_BASE_URL`(데이콘 게이트웨이, Variable)을 넣는다. 키는 저장소 어디에도 두지 않는다.
3. 선택 변수: `DV_REVIEWERS`(기본 `regulatory`), `DV_EVIDENCE_RERANK`(기본 `auto` = GPU에서만), `DV_RUN_TOKEN_BUDGET`(기본 150000), `OPENFDA_API_KEY`.
4. 실측(2026-09-25, HF cpu-basic): 라이브 검토 웜 상태 83초(검색 결함 수정 후 1회, 수정 전 93초). 재빌드·재기동 직후 첫 접속은 모듈 로드와 모델 예열로 약 1분. 모델 예열은 백그라운드 스레드라 **저장 결과 즉시 보기**(`?demo=N&cached=1`)는 예열을 기다리지 않는다.
5. 배포 확인은 health가 아니라 라이브 1회 실행 후 **도구 호출 탭의 실패 여부와 근거 건수**(예시 ① 약 50건)로 한다.

## 구조
`app/llm`(게이트웨이·감사로그) · `app/schema`(Trial Schema·상태) · `app/agents`(Compiler·Planner·도구 노드·Reviewer·Findings·Verifier·LangGraph) ·
`app/tools`(RDKit·ChEMBL·openFDA·Open Targets·시뮬·CT.gov) · `app/corpus`(규제 PDF 7종·절 청킹·bge-m3+BM25) · `app/verify`(NLI) · `app/ui`(Streamlit) · `app/eval`(평가셋)
개발 기록: `docs/DEV_LOG.md` · 상세기술서: `docs/상세기술서.md` · 수치 원천: `docs/numbers.md`(평가·TCR·누적 토큰), `docs/agency.md`(재계획·도구), `docs/token_ledger.md` · 리서치: `RESEARCH/` · 예선 제안서: `제안서_본문.md`
