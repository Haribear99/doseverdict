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
- Dockerfile(HF Spaces uid 1000·포트 7860·CPU torch)·`.dockerignore`·README 프런트매터 작성. 로컬 `docker build` 완료(3.1GB) → 컨테이너 기동 5초 만에 health 200, 인덱스(396×1024) 로드 확인. HF Spaces 계정만 있으면 배포 가능.
- 평가 축① 생성기(`app/eval/inject.py`): 후보 규범 문장 207개(AI 가이던스·보일러플레이트 제외). 아직 미실행(Luna ~60k 토큰 예상).
- 적대 테스트 ①(폐기 가이던스 인용, `app/demo/adversarial_superseded_guidance.md`) CLI 실행: `source_version_conflict` 이벤트 + V01 finding(현행 2024-08 최종본 기준으로 검토) 생성, finding 8건 전부 검증, 25.7k 토큰(미국 단일국·SMILES 없음 → 구조 축 '근거 미확보' 표기 확인).

### 2026-09-11 (계속) — 평가 착수
- 축① gold set: 규범 문장 140개 → Luna 합성 결함 140건(64.8k 토큰) → 범위 내 문서(FDA 용량최적화·확장코호트·식약처·ICH E4·E6R3 설계/품질)로 100건 선별 → 20케이스 × 6결함.
- 파일럿(3케이스): 원문을 플래너·Reviewer·Findings에 전달하고 플래너 생성 검색 질의를 추가하기 전 span 0.33 → 후 0.89. grounded(정답 규범 문서 인용) 0.39. 정규식 체크리스트는 결측 술어 표면형으로 span 0.78을 내지만 grounded 0 — 그래서 grounded recall을 주 지표로 둔다.
- 토큰: run당 64k(원문 전달로 41k→64k) → 인용 450자·원문 4,500자로 축소 후 본평가 진행. 본평가 20케이스 × (checklist·single_rag·full·no_calc·no_arena·no_verifier) 병렬 2프로세스 실행 중(`app/eval/data/results/`, 상태 전량 보존).
- 축③ 정답(PMR 부과 여부) 31개 성분을 웹 조사 에이전트 2개에 위임(승인서한·PMR DB 기준, unknown 허용).
- 축③ 정답 확보: 조사 에이전트 2개가 31개 성분(+소토라십·아다그라십)의 FDA 승인서한 원문을 대조 → 용량 최적화 PMR 양성 7건(ceritinib·futibatinib·idelalisib·inavolisib·lenvatinib·sotorasib·adagrasib), unknown 1(gefitinib 2003), 비종양 제외 2. `app/eval/data/pmr_ground_truth.jsonl`.
- 축③ 평가(`app/eval/axis3.py`, LLM 없음): 라벨 PK 진술(E-R 미상·비선형 PK·단백결합·반감기)만으로 위험 순위 → n=30, AUROC 0.658, PR-AUC 0.477(무작위 0.233), 상위 8 중 양성 2. 점수 규칙은 정답 확인 전 고정(사후 조정 없음). 계산 모듈 제거 시 0.5.

### 2026-09-11 (계속) — 본평가 중간 결과(full 20케이스)
- 병렬 2프로세스가 메모리 부족으로 죽어 단일 프로세스·`--resume`으로 재실행(full 완료, ablation 진행 중).
- single_rag 베이스라인은 인용 문서·인용문 필드가 없어 grounded가 구조적으로 0이었다 → 스키마에 `cited_doc_id`·`guidance_quote`를 넣고 재실행(span 0.467, grounded 0.100, 3.3k 토큰/케이스).
- full: span 0.925 [0.88, 0.97], grounded 0.358 [0.27, 0.45], precision proxy 0.511, 검증 통과율 0.880, 57.4k 토큰/케이스, 167초. checklist는 span 0.791이지만 grounded 0 → full − checklist = +0.358(15%p 기준 충족).
- 갤러리(`gallery_full.md`): 결함 120건 중 놓침 9, finding 218건 중 주입 결함과 무관 82(정상판에 대한 지적이라 '잘못 경고 후보'로 사람 검토 필요 — precision proxy는 하한).
- grounded 실패 원인(`app/eval/diagnose.py`): span 적중 111건 중 정답 문서 미인용 67건은 **전부 다른 규제 문서를 인용한 경우**(근거 없음 0, 비규제만 0). 가장 흔한 쌍은 ICH E4 → FDA 용량최적화 2024(15건), FDA 확장코호트 → ICH E6(R3)(10건). 출처 절은 hold-out으로 검색에서 빠지므로 같은 규범을 말하는 자매 문서를 찾은 경우가 많다. 지표는 사전 정의대로 엄격하게 유지하고, 이 분류를 보고서에 그대로 싣는다(지표 완화 없음).
- 평가 중단 1회: 게이트웨이 500 `model_error`(findings 호출)로 프로세스 종료 → 클라이언트에 5xx 지수 백오프 재시도 추가, `--resume` 재개. 재개 케이스의 소요시간이 0으로 잡히던 문제는 감사로그(첫 호출 시작~마지막 호출 응답) 기준으로 통일(full 199초/케이스, 벽시계보다 로컬 NLI 검증 시간만큼 짧음).
- no_calc 20케이스: span 0.875 [0.82, 0.93], grounded 0.425 [0.33, 0.52], 검증 0.808, 53.5k 토큰. **축①(규범 유도 결함)에서는 계산 모듈 제거가 grounded recall을 낮추지 않는다**(+0.061, CI 겹침). 계산 모듈의 기여는 축③(AUROC 0.658 vs 0.5)과 TCR 기권(F00)에 있고, 축①은 규제 문서 근거만 묻는 셋이므로 예상된 결과 — 그대로 보고.
- no_arena 20케이스: span 0.958 [0.93, 0.98], grounded 0.383 [0.30, 0.47], 검증 0.883, **29.8k 토큰(full의 52%)**, 144초. **축①에서 Adversarial Reviewer 3인은 측정 가능한 기여가 없고 토큰만 2배**다(Δ grounded +0.026, CI 완전 겹침). 축① Silver Set은 규제 문서 근거만 묻고 시험기관 실행 가능성·환자 부담 관점은 결함으로 주입하지 않으므로 Arena의 설계 목적(관점 분리·상충 의견)이 이 셋으로는 측정되지 않는다는 한계와 함께 그대로 보고. 리소스 효율 배점(15)을 고려해 기본 설정을 lean(Arena 제거 또는 Reviewer 1인)으로 바꿀지는 사용자 결정 사항 — 제안서 축소 규칙 ②(Reviewer 3→2)에 해당.
- Arena 실행 확인: full 상태에 케이스당 Reviewer 포지션 23.7개, finding 218건 중 200건에 포지션 연결, `conflict_unresolved` 13건. full에만 있는 finding 56건 중 주입 결함 적중은 16건이고 나머지는 no_arena와 같은 "~를 명시하지 않음" 유형 — Arena가 관점(실행 가능성·환자 부담)이 다른 finding을 체계적으로 추가하지는 않았다.

### 2026-09-11 (계속) — 본평가 완료·적대 테스트 ②③
- no_verifier 20케이스: span 0.958, grounded 0.400, 57.8k 토큰. **ablation 3종 모두 grounded recall 하락 없음**(CI 겹침) — 상세기술서 6절에 부정적 결과 그대로 기록. Verifier 변별력은 별도 산출: verified finding의 결함 적중 0.62 vs held 0.38(`diagnose.py`에 추가).
- 누적 토큰 4,747,255(15.8%). 용도별 findings 34% / Arena 34% / plan 14% / compile 13%. 쿼터 헤더는 09-10 이후 미갱신.
- 적대 ② 한미 상충(`adversarial_kr_us_conflict.md`): F08이 식약처 문서를 민원인 안내서로 식별해 "구속 규정" 주장을 결함 판정. 10건 전부 검증, 44.6k.
- 적대 ③ 근거 없는 용량(`adversarial_unsupported_dose.md`): 4개 축 근거 미확보 표기·도구 미호출, F01이 무근거 RP2D 확정을 식약처 조항으로 지적. 7건 전부 검증, 33.1k.
- 상세기술서 4~8·11절, 발표자료 7·10·11장, 영상 스크립트 수치 반영 완료(TODO 0건). 남은 것: HF Spaces 배포(계정 필요), lean 기본 설정 결정(사용자), 영상 촬영, PDF 변환.

### 2026-09-11 (계속) — 결정 반영: 토큰 절감 기본 설정 + 근거 재선택 실험
- 사용자 결정: 토큰 최소화, Reviewer는 권고안(규제 1인 기본, 3인은 옵션), HF 계정 있음, 남은 기간 성능 실험 계속.
- 용도별 토큰(케이스당, full): findings 19.6k / 규제 Reviewer 11.7k / plan 7.6k / compile 7.0k / 시험기관·환자 Reviewer 각 5.7k. lean(규제 1인)은 약 40k, no_arena는 30k로 추정.
- `DV_REVIEWERS`(기본 regulatory) + UI 체크박스 "Reviewer 3인". 평가 설정 `lean`(규제 1인 + 재선택) 추가, 기존 full·ablation은 3인 조건 보존.
- **근거 재선택 실험(사후 재채점, 토큰 0, `app/eval/rescore.py`)** — full 상태 20케이스 기준 grounded recall:
  | 규칙 | grounded | 검증 통과율 | 추가 인용 | 판정 |
  |---|---|---|---|---|
  | 기준(full) | 0.358 | 0.880 | — | — |
  | 교체만(현 근거 함의 < 0.9일 때 전체 상위 6) | 0.367 | 0.930 | 20 | 효과 미미 |
  | + 다른 문서 공동 인용(함의 ≥ 0.9, 전체 상위 6) | 0.383 | 0.930 | 38 | 미미 |
  | + 문서별 상위 3 후보, 검증기 임계값 0.7 | **0.608** | 0.963 | 285 | **기각** — 표본 12건 중 절반 이상이 오인용(일반 서술 조항→구체 규범 NLI 거짓 양성, 영↔한 교차, 표지 청크) |
  | + 가드(같은 언어·내용어 50% 실재·함의 ≥ 0.9) | 0.408 | 0.948 | 50 | 표본 14건에서 여전히 오인용 4~6건 → 자동 인용 부적합 |
  상한 진단: grounded 실패 67건 중 정답 문서에 검증기 통과 조항이 있는 경우 약 40건. 그러나 그것을 자동으로 붙이면 오인용이 섞인다.
- **최종 채택**: 자동 공동 인용은 인용(`evidence_ids`)에 넣지 않고 `related_evidence_ids`(사람 검토용 후보, UI에 "관련 조항 후보"로 표시)로만 제안. 교체 규칙은 가드 통과 + 함의 ≥ 0.9일 때만. 지표는 인용만으로 계산하므로 grounded는 거의 그대로다 — "검증된 인용"이라는 약속을 지키는 쪽을 택했다.
- 배포본(CPU)에서는 NLI 1쌍 ~수 초라 재선택을 `DV_EVIDENCE_RERANK=auto`(GPU에서만)로 둔다. 심사위원용으로 예시 3종의 저장 결과를 즉시 보여주는 버튼·URL(`?demo=N&cached=1`) 추가(`app/demo/precompute.py`).
- **lean 20케이스(규제 1인 + 재선택 채택안 + 범위 규칙, 새 실행)**: span 0.950 [0.91, 0.98], grounded 0.408 [0.33, 0.47], precision 0.577, 검증 0.925, 44.3k 토큰, 157초. full 대비 토큰 −23%에 전 지표 동등 이상. 놓침 6/120, 무관 finding 64/200(full 82/218). → 배포 기본값 확정.
- Docker(CPU) e2e: 컨테이너에서 예시 ① 완주 9.5분(평가와 CPU 공유 조건) — 라이브 시연에는 길어 저장 결과 즉시 보기(`?demo=N&cached=1`)를 기본 동선으로. 배포 requirements에 `langgraph-checkpoint-sqlite` 누락 발견·수정.
- **CPU 배포 병목 진단(Docker, 노드별)**: compile 25s / plan 43s / tools 190s / arena 26s / findings 43s / **verify 229s** = 9.4분. 질의 임베딩은 원래 CPU(0.22초/건)라 tools의 대부분은 bge-m3·인덱스 로드와 시뮬 16초. verify는 transformers 5가 CPU에서 NLI 대형 모델을 bf16으로 자동 로드해 **20초/쌍**이 나온 것이 원인 → `dtype=float32` 강제 시 **1.8초/쌍(4스레드)·2.6초(2스레드), GPU 판정과 12/12 일치**. int8 동적 양자화(대형 0.64초, base 0.22초)는 판정 일치율 4/40·3/40으로 사용 불가, base fp32도 24/40 → 대형 fp32 유지. Streamlit 기동 시 인덱스·NLI 예열(`_warm_models`) 추가.
- Docker 재측정(float32 NLI·검증 순서 수정 후): compile 26s / plan 54s / tools 182s(첫 corpus.search 164s = bge-m3 로드+임베딩, 컨테이너가 로컬 CPU보다 ~5배 느림) / arena 18s / findings 43s / verify 176s = 8.4분. 컨테이너 CPU 경로가 로컬 벤치보다 훨씬 느려 HF 무료 CPU에서는 라이브 10분 이상 예상 → 저장 결과 즉시 보기를 기본 동선으로 README에 명시. dense 검색 제거 가능성은 오프라인 검색 벤치로 판단.
- 오프라인 검색 벤치(결함 문장 100건 → 출처 청크): BM25만 recall@1/3/5 = 0.24/0.37/0.42(3 ms), 하이브리드 0.22/0.39/0.46(505 ms, CPU), dense만 0.22/0.34/0.37. dense 이득은 recall@5 +4%p. 예열 후 질의당 0.5초라 하이브리드 유지, 로드 비용만 예열로 제거.
- **컨테이너 느림의 진짜 원인**: 이미지에 모델이 없어 `docker run`마다 bge-m3(2.2GB)·DeBERTa(1.7GB)·mDeBERTa를 HF Hub에서 내려받고 있었다(첫 corpus.search 164초, verify 176초의 대부분). Dockerfile에 빌드 시 `snapshot_download` 3종 추가.
- 검증기 전제 창 선택(`focus_window`): 인용문이 600자를 넘으면 주장과 어휘가 가장 겹치는 문장 창만 NLI 전제로 쓰고, 함의가 안 나오면 전문으로 재판정. lean 사후 재채점: grounded 0.408 동일, 검증 통과율 0.925→0.954(전제가 짧고 초점이 맞아 함의가 안정). CPU에서는 전제 길이 제곱에 비례하는 NLI 비용도 준다.
