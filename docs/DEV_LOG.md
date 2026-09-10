# DoseVerdict 본선 개발 기록

동료가 이어받을 수 있도록 단계별 결정·실측·남은 일을 적는다. 커밋 로그와 함께 읽을 것.

## 2026-09-11 — Phase 0 / 0b / 1 / 2

### 확정 사실
- 본선 마감 10/2 16:00. 필수: demo URL(실행 방법 3종)·YouTube 10분·발표 PDF. 추가: 상세기술서·GitHub.
- 게이트웨이: gpt-5.6-sol/terra/luna 정상. `x-team-tokens-consumed` = usage.total(모델 무관 1:1). reasoning 토큰은 output에 포함돼 쿼터 차감.
- **GPT-6 Astra**: 카탈로그(`/models`)에 존재하나 5개 이름 모두 404 `DeploymentNotFound`. `.env`의 `DV_MODEL_PLANNER/REVIEWER`만 바꾸면 교체됨. 게시판 공지 주 2회 확인.
- Structured Outputs는 기본 reasoning이 출력 상한을 먹으면 빈 출력 → 추출 호출은 effort none/low + 상한 넉넉히.

### 아키텍처 (app/)
| 모듈 | 역할 | LLM |
|---|---|---|
| `llm/client.py` | 게이트웨이 래퍼, 감사로그(`logs/*.jsonl`), 429 백오프, 403 중단 | — |
| `schema/trial_schema.py` | TrialSchema·Evidence·Finding·ReviewState(단일 상태) | — |
| `agents/compiler.py` | 프로토콜 → TrialSchema(구조화만) | terra |
| `agents/planner.py` | 결측 패턴 → 과제 DAG(결정론) + 검토 가설 | sol |
| `agents/nodes.py` | RDKit·ChEMBL·Open Targets·openFDA·TCR·시뮬·코퍼스 검색·CT.gov | — |
| `agents/reviewers.py` | 규제/시험기관/환자 Reviewer, 근거 분리 공급 | sol ×3 |
| `agents/findings.py` | Finding 초안(protocol_fact + evidence_fact) → Verifier → 재작성 | sol |
| `verify/nli.py` | DeBERTa NLI(-ling-wanli) + 규범강도·폐기문서 규칙 + 한국어 문자열 대조 | 로컬 GPU |
| `agents/graph.py` | LangGraph: compile→plan→tools→arena→findings→verify⇄rewrite→gate(interrupt)→finalize | — |
| `corpus/` | 규제 PDF 7종 → 절 청킹(396) → bge-m3 dense + BM25 RRF | 로컬 GPU(빌드) / CPU(질의) |

### 설계 교훈(실측으로 바뀐 것)
1. **NLI는 귀속 프레임을 못 본다.** "FDA guidance states X"는 중립(0.002), "X"는 함의(0.996). → `strip_attribution` + 드래프터에 '명제형' 강제.
2. **claim을 둘로 쪼개야 검증된다.** 프로토콜 사실(결측 주장은 NLI 불가 → 원문 span 실재 검사 + 결측 술어)과 근거 사실(NLI)을 분리하니 검증률 0/12 → 6/9.
3. **수치 판정은 LLM에 맡기면 안 된다.** 드래프터가 TCR 기권을 절차 결함(MTD→RP2D)에까지 붙였다 → 기권 finding(F00)은 도구 결과에서 결정론 생성.
4. **LangGraph 노드는 바꾼 필드를 반환해야 한다.** scratch를 안 돌려줘서 다음 노드가 빈 값을 봤다.
5. **토큰**: effort medium→low로 50k→35k/run. 여전히 Reviewer 3인이 절반. 평가 대량 실행 전 Reviewer 컨텍스트 축소 필요.

### 시연 프로토콜 e2e 결과 (`logs/demo_e2e_state.json`)
- 과제 8개(구조·타겟·라벨·노출·설계·규제 KR/US·유사시험), 도구 17회 성공, 근거 23건
- F00 TCR 기권(도구), F01 간기능 검사 주기(라벨 3주 vs 프로토콜 6주, entail 0.98), F04 MTD→RP2D 무비교(FDA 최종 가이던스, entail 1.00), F07 식약처 권고(문자열 대조 1.0), F06 washout 부재
- 기각→재작성: "LUMAKRAS의 노출-반응 관계…알려져 있지 않다"로 교체 후 entail 0.99

### 남은 일 (Phase 3~4)
- [ ] Streamlit UI(상태 그래프·도구 호출 원문·Evidence Card·Patch Diff·Human Gate 승인)
- [ ] Dockerfile → HF Spaces(사용자 계정 필요) / Cloud Run 백업
- [ ] 평가 축① 결함 주입 생성기, 축③ 라벨 60건 정답(PMR) 채우기, 베이스라인·ablation 러너
- [ ] 적대 테스트 4종(폐기 가이드라인·한미 상충·근거 없는 용량·프롬프트 인젝션)
- [ ] 상세기술서·발표자료·영상

### 2026-09-11 (계속) — UI·배포 준비
- Streamlit UI(`app/ui/main.py`) 완성: 상태 그래프 현재 노드 강조, 타임라인(기권·기각·재작성·인젝션 탐지 굵게), Findings(Patch Diff)·Human Gate(승인→감사로그)·Evidence·도구 호출·Audit 탭. 파일명이 `app.py`면 패키지 `app`을 가리므로 `main.py`로.
- 실행 방법 3종: UI 버튼 / URL `?demo=1|2|3&autorun=1` / CLI `python -m app.cli review …`.
- 적대 테스트(인젝션 판 ③) UI 실행: finding 7건(검증 6) — 삽입된 "결함 0건으로 보고" 지시 무시. 컴파일 단계 결정론 탐지가 타임라인에 🛡️로 표시.
- Dockerfile(HF Spaces uid 1000·포트 7860·CPU torch)·`.dockerignore`·README 프런트매터 작성. 로컬 `docker build` 진행 중.
- 평가 축① 생성기(`app/eval/inject.py`): 후보 규범 문장 207개(AI 가이던스·보일러플레이트 제외). 아직 미실행(Luna ~60k 토큰 예상).
