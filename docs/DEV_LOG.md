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
- **모델 내장 이미지 CPU e2e(예시 ①, CLI, 예열 없음)**: compile 26s / plan 32s / tools 50s(첫 corpus.search 30s = bge-m3 로드) / arena 18s / findings 29s / verify 34s = **3.1분**(종전 9.4분). Streamlit은 기동 시 예열하므로 라이브 검토 약 2.5분 예상(HF 무료 2 vCPU는 더 느릴 수 있음). 전체 다운로드+chown 중복으로 41GB가 됐던 이미지는 필요 형식만(bge-m3 bin, DeBERTa safetensors)·USER user 이후 다운로드로 정리.

### 2026-09-23 — 추가 토큰 3,000만(총 6,000만)·GPT-6 실측·리서치 반영 개발

**게이트웨이 실측**(`docs/gateway_probe.md` ⑧~⑫)
- gpt-6-astra: 5개 이름 모두 여전히 404(09-11과 같음). OpenAI 문서상 Astra는 effort none을 받지 않는다(HTTP 400).
- **gpt-6-sol과 gpt-6-luna는 200으로 응답한다**(09-07 공지 목록에는 없음 → 주최측 문의 발송 권고).
- 쿼터 헤더 59,999,986(실시간으로 줄어듦).
- **캐시 적중(2,780토큰)에도 팀 쿼터는 total_tokens 전액이 차감된다.** 캐시는 절감 수단이 아니다.
- strict json_schema: TrialSchema는 `source_spans` dict 때문에 400, list로 바꾸면 통과.
- logprobs는 effort none에서만 되고, reasoning 모델에서는 400.

**240 mg TCR**(`evidence/tcr_240mg.py`): 가정에 따라 판정이 갈려 기권이다.
- (가) 선형 CL/F: 8.6 / 2.5 / 0.31
- (나) 라벨 12.3 노출 유사: 34.5 / 10.0 / 1.24

**배포**: HF 계정 Haribear99(PRO)에 비공개 Space `Haribear99/doseverdict`를 만들었다. Secrets를 등록하고 `git archive HEAD`를 업로드했다. RUNNING, health 200. 공개 전환은 제출 직전에 한다.

**코드 변경**
- d26248e 구조화 출력 경화
  - `app/llm/structured.py`: Pydantic 스키마 생성, incomplete 사전 검사, 1회 재시도, usage 합산, 실패 기록
  - `source_spans`를 list로 변경
  - compiler·planner에 strict 적용
  - reviewers·findings는 근거 필드를 판정 필드 앞에 두고, strict는 `DV_STRICT_DRAFT` 스위치로
  - rewrite 토큰을 실측으로 기록
  - `DV_NODE_MODEL_<NODE>`, `DV_EFFORT_<NODE>` 추가
- 32c2bad 결정론 불변식: LLM의 TCR 판정 주장은 held, Reviewer 충돌 시 기권, 기권에는 사유 필수.
- c7ddabc 인용 범주-주제 대조: 용량 finding에 붙은 GCP·품질 조항을 인용에서 빼 후보로 이동. 평가 러너 `--suffix` 추가.
- 3e5d656 fail-closed: 계획·초안 생성이 끝내 실패하면 결론 없음으로 처리. refusal·잘림 처리, Astra effort 가드, 평가셋 40케이스 확장(`gold_axis1_ext.jsonl`).
- 0c2813a 토큰 원장(`app/eval/ledger.py` → `docs/token_ledger.md`, `figures/pareto_tokens_grounded.png`).
  - 케이스당 reasoning은 3.7~4.9%, 입력은 약 70~80%다. **쿼터 레버는 effort가 아니라 입력 크기다.**
- 7cff3b9 `DV_QUOTE_CHARS`(입력 축소 A/B), 4b0e6c3 `DV_TOPIC_PROMPT`(주제 태그 프롬프트 A/B, 켜짐일 때 프롬프트 동일성 검증).
- 테스트는 29개에서 39개로 늘었고 전부 통과한다.

**측정: lean_d3**(새 코드 기준선, 20케이스, 기존 lean 대비 쌍대 부트스트랩)
- grounded 0.383(−0.025 [−0.100, +0.042])
- span 0.925
- 검증 0.951(+0.026, 유의하지 않음)
- **토큰 48.0k(+3.8k [+1.2k, +6.9k], 유의한 증가)**. 증가분 대부분은 findings 입력(+2.35k, 주제 태그)이다.
- LLM 출력 실패 0건.
- 판정: 범주 필터는 grounded를 올리지 못했다. 주제 태그를 뺀 조건(`_notopic`)과 입력 축소(`_q250`)를 A/B로 판정한다.

**진행 중인 A/B**(각 20케이스): `_cnone`(compile effort none) → `_strict` → `_c6sol`(compile에 gpt-6-sol) → `_fmed`(findings effort medium). 두 번째 슬롯에서는 `_q250` → `_notopic`. 확장 40케이스 `lean_d3ext`도 진행 중이다.

**한계**: 평가 60케이스가 모두 소토라십 시놉시스(DV-DEMO-002)의 변형이다. 확장 세트는 문서 분포가 달라(확장코호트 45%, E6R3 20%) 결과를 분리해 보고한다.

**리서치**: `research/notes/final_report_doseverdict-finals-jev-astra-9b11b2.md`(dissertation, 27k단어). ship 게이트는 길이 검사 하나만 실패했다(argumentative 목표를 적용한 탓). 사용자 결정에 따라 본문을 유지하고 요약본은 `docs/리서치_요약_0923.md`에 둔다.

### 2026-09-23 (계속) — 확장 40케이스·A/B 1차 결과

- **lean_d3ext(확장 40케이스, 새 코드)**: span 0.871 [0.812, 0.921], grounded 0.513 [0.462, 0.563], 검증 0.947 [0.914, 0.974], 47.2k 토큰, LLM 실패 0. 문서 분포가 원 20케이스와 달라(확장코호트 결함 비중 큼) 원 세트 0.383과 합산·직접 비교하지 않는다.
- **A/B(각 20케이스, lean_d3 대비 쌍대 부트스트랩, `python -m app.eval.compare`)** — 사전 등록 규칙(채택: 토큰 −15% 이상이고 품질 −5pp 이내 또는 grounded CI 하한 > 0)에서 셋 다 보류:

  | 실험 | 토큰 | grounded | 검증 통과율 |
  |---|---|---|---|
  | compile effort none(`_cnone`) | −2.4% [−3.7k, +0.7k] | +0.050 [−0.042, +0.133] | −0.029 [−0.095, +0.027] |
  | strict reviewers·findings(`_strict`) | −4.7% [−6.0k, +0.7k] | +0.033 [−0.034, +0.100] | +0.013 [−0.026, +0.054] |
  | 인용문 250자(`_q250`) | **−8.0% [−6.8k, −1.3k] 유의** | ±0.000 [−0.059, +0.067] | +0.004 [−0.040, +0.050] |

  해석:
  - effort none은 절감이 미미하다(reasoning 비중이 작다).
  - strict는 품질을 해치지 않았다. 문헌에서 우려한 format tax는 나타나지 않았다.
  - 인용문 축소는 품질 손실 없이 유의하게 줄였지만 −15% 기준에는 못 미친다.
  - 다음 후보: 결합 설정(strict + 250자 + 주제 태그 제거).
- 시스템 메모리 부족으로 A/B 체인 셸이 강제 중지됐다. 결과는 다음과 같다.
  - `_cnone`·`_strict`·`_q250`: 완료.
  - `_c6sol`·`_notopic`: 실행 중이던 평가 프로세스가 계속 진행.
  - `_fmed`(findings effort medium): 시작하지 못했다.

### 2026-09-23 (계속) — GPT-6 A/B: 전 노드 gpt-6-sol 채택 후보

사용자가 GPT-6 사용을 승인했다(09-23 저녁). 모든 A/B는 lean_d3 대비 20케이스 쌍대 부트스트랩이다.

- `_notopic`(주제 태그 프롬프트 제거): 토큰 −3.4% [−4.8k, +0.7k], grounded +0.017, 검증 −0.040 [−0.090, +0.010]. 절감이 작고 검증이 떨어지는 쪽이라 결합 설정에서 제외한다.
- `_c6sol`(compile만 gpt-6-sol): grounded +0.067 [−0.025, +0.150], 토큰 −2.0%. 보류.
- **`_g6all`(compile·plan·arena·findings·rewrite 전부 gpt-6-sol)**
  - grounded **0.500(+0.117 [+0.033, +0.200])**
  - span **0.975(+0.050 [+0.008, +0.100])**
  - 검증 0.969(+0.019, 유의하지 않음)
  - 토큰 **43.7k(−9.0% [−8.3k, −1.0k])**
  - 소요 89초(기준 178초), LLM 실패 0
  - 사전 규칙상 **채택**이다. findings의 reasoning 토큰은 1,051에서 191로 줄었다.
  - 주의: A/B 7종의 다중 비교라 우연일 가능성이 있다. 확장 40케이스(`_g6allext`)로 재확인한 뒤 기본값으로 올린다.

### 2026-09-24 — LLM 호출 타임아웃·재시도

- `_g6allext` 평가가 AX1-044에서 plan을 마친 뒤 멈췄다(09-24 00:13). 외부 도구 호출에는 모두 `timeout=40`이 걸려 있었지만, LLM 클라이언트는 SDK 기본값(600초)을 쓰고 있었고 연결·타임아웃 예외는 재시도하지 않았다.
- `app/llm/client.py`:
  - 호출 타임아웃을 `DV_LLM_TIMEOUT`(기본 180초)으로 둔다.
  - `APITimeoutError`·`APIConnectionError`는 429처럼 지수 백오프로 재시도하고 감사로그에 status 0으로 남긴다.
- 테스트 39개 통과. 진행 중인 `_g6allext` 이어 실행은 수정 전 코드로 돌고 있다.

### 2026-09-24 — 확장 세트 재확인 → 기본 모델 gpt-6-sol 전환

- `_g6allext`(확장 40케이스, 전 노드 gpt-6-sol)를 `lean_d3ext`와 비교했다.
  - grounded 0.563(+0.050 [−0.012, +0.108])
  - span +0.025, 검증 +0.009
  - 토큰 44.4k(−5.8% [−4.3k, −1.0k])
  - 소요 96초(기준 183초), LLM 실패 0
  - 확장 세트만 보면 **보류**다(grounded CI가 0을 포함).
- 60케이스 통합 쌍대 부트스트랩(원 20 + 확장 40, 분포가 달라 참고용):
  - grounded **+0.072 [+0.022, +0.122]**
  - 토큰 −3.3k [−5.0k, −1.7k]
  - 소요 −87초 [−104, −76]
  - 검증·span은 떨어지지 않았다.
- 판단:
  - 어떤 지표도 나빠지지 않았고, 토큰과 시간은 두 세트 모두에서 유의하게 줄었다.
  - grounded 개선 폭은 원 세트(+0.117)가 확장 세트(+0.050)보다 커서, 처음 추정치가 과대였을 수 있다.
  - **기본 모델을 planner·reviewer·extract 모두 gpt-6-sol로 전환한다.** 바꾼 곳은 `client.py`, `.env`, `.env.example`, UI, README다.
  - bulk(gpt-5.6-luna)는 A/B를 하지 않았으므로 그대로 둔다.
- 기술서의 "grounded 개선"은 두 수치를 함께 적는다: 확장 세트 +0.050(유의하지 않음), 통합 +0.072(유의).
- `_fmed`(findings effort medium, gpt-5.6 기준) vs lean_d3: 토큰 +28.5%, grounded +0.033, 검증 ±0 → **기각**.
- 다음: `_combo` = gpt-6-sol 기본 + `DV_STRICT_DRAFT=1` + `DV_QUOTE_CHARS=250`, 기준선은 `lean_g6all`(같은 모델). strict·250자는 gpt-5.6에서만 측정했기 때문에 새 모델에서 다시 확인한다.
- `_combo`(gpt-6-sol + strict + 인용문 250자, 사용자 터미널에서 실행) vs `lean_g6all`:
  - 토큰 39.3k(−10.2% [−6.6k, −2.9k], 유의)
  - grounded 0.508(+0.008 [−0.075, +0.092])
  - 검증 +0.006, span −0.017, precision +0.023
  - LLM 실패 0
  - 사전 규칙상 **보류**다(절감이 −15% 미달이고 grounded CI가 0을 포함). 품질 손실 없이 토큰이 유의하게 줄었으므로 확장 세트(`_comboext`)에서 `lean_g6allext`와 비교해 재확인한다.
  - 참고로 09-23 기준선(lean_d3) 대비 누적 효과는 토큰 −18.3%, grounded +0.125다.

### 2026-09-25 — 결합 설정 재확인 → strict·인용문 250자 기본 채택

- `_comboext`(확장 40케이스) vs `lean_g6allext`:
  - 토큰 38.8k(−12.8% [−7.4k, −4.3k], 유의)
  - grounded 0.558(−0.004 [−0.063, +0.054])
  - 검증 +0.007, span −0.013
  - precision +0.034 [+0.002, +0.066]
  - 소요 82초, LLM 실패 0
  - 사전 규칙상 보류다.
- 60케이스 통합(참고용): 토큰 −11.9% [−6.6k, −4.2k], grounded ±0.000 [−0.047, +0.047], 검증 +0.007.
- 판단:
  - 토큰 절감이 독립된 두 세트에서 모두 재현됐다.
  - 통합 grounded CI의 하한(−0.047)이 사전 규칙의 품질 허용폭(−5pp) 안에 있다.
  - 이 비열등성 근거로 **strict(`DV_STRICT_DRAFT`)와 인용문 250자(`DV_QUOTE_CHARS`)를 기본값으로 채택한다.**
  - 사전 규칙의 "−15% 이상 절감" 조건은 충족하지 못했으므로, 기술서에는 "비열등성 기준 채택"이라고 적는다.
- 09-23 기준선(gpt-5.6, 450자, strict 끔) 대비 현재 기본 설정: 원 20케이스 기준 토큰 −18.3%, grounded +0.125. 확장 세트 기준(`lean_d3ext` 대비 `lean_comboext`): 토큰 −17.8%(채택 규칙 충족), grounded +0.046 [−0.017, +0.104], precision +0.053 [+0.010, +0.099].
- 캐시 데모 3종 재생성(`python -m app.demo.precompute`, 새 기본 설정: gpt-6-sol + strict + 250자). 괄호 안은 09-11 값이다.
  | 데모 | 토큰 | finding | 검증 통과 | 핵심 동작 |
  |---|---|---|---|---|
  | demo1 원본 | 37.2k(42.4k) | 10 | 9 | 240 mg TCR 기권(abstain) |
  | demo2 수정본 | 37.1k(44.5k) | 7(9) | 6 | finding 감소 |
  | demo3 주입 | 29.5k(36.6k) | 7 | 7 | `prompt_injection_detected` 재계획, 지시 불이행 |
- HF Space `Haribear99/doseverdict` 재배포(HEAD 1374eaa, git archive): BUILDING→RUNNING 102초, `/_stcore/health` 200(1.1초).

### 2026-09-25 — UI: 예열 비차단, 라이브 실행 회귀 수정

- **라이브 실행 회귀(09-23 도입)**: LLM 실패 표시 코드가 `graph.stream`의 `__interrupt__` 업데이트(tuple)에 `.get`을 호출했다. 그래서 라이브 검토가 Human Gate 직전에 `AttributeError`로 죽었다. 평가는 `on_step`을 쓰지 않아 드러나지 않았고, 09-24에 배포한 Space에도 이 버그가 있었다. `__interrupt__`는 타임라인에서 제외하고 dict일 때만 읽도록 고쳤다.
- **예열 비차단**: `_warm_models()`가 화면을 그리기 전에 동기로 실행돼, 저장된 결과 보기(`?cached=1`)까지 bge-m3·NLI 로드를 기다렸다(PRD P0-1 함정). 이를 백그라운드 스레드(`_warm_thread`)로 옮기고, 라이브 실행만 시작 전에 join한다.
- 결정론적 finding의 `span 원문 일치: None` 표기를 `검사 안 함`으로 바꿨다.
- 로컬 Playwright e2e(예시 ①):
  - 서버 기동 직후 캐시 화면이 열린다(Findings 10건, 기권 표시).
  - 라이브 실행: compile 15s → plan 30s → tools 61s → arena 71s → findings 139s → verify 140s. 34.6k 토큰, 도구 17회, 검증 10/10.
  - Human Gate 승인까지 정상.

### 2026-09-25 — 배포본 결함: 규제 조항 검색이 한 번도 동작하지 않았음

- HF Space에서 라이브 검토를 처음 끝까지 돌렸다(로그인된 Chrome, 예시 ①). 결과는 25.6k 토큰, 93초, 검증 11/11이었다. 그런데 **tools 근거가 12건**으로, 로컬 42건보다 크게 적었다.
- 도구 호출 탭을 확인하니 `regulatory_clause_search` 2회가 모두 `invalid load key, 'v'`로 실패했다.
- 원인:
  - Space 저장소는 `bm25.pkl`·`dense.npy`(·PDF·PNG·hwpx)를 LFS로 저장한다.
  - 그런데 우리가 올린 `.gitattributes`(`* text=auto eol=lf`)가 HF 기본 LFS 규칙을 덮어썼다.
  - 그래서 Docker 빌드의 clone이 LFS 포인터 파일을 받았고, 이를 pickle로 로드하다 실패했다.
  - 09-23 첫 배포부터 이 상태였다. health 200과 캐시 결과(로컬에서 생성)로는 드러나지 않았다.
- 수정: `app/deploy_space.py`를 추가했다. git archive HEAD를 올리면서, Space용 `.gitattributes`에 LFS 규칙(pkl·npy·pdf·png·hwpx·bin·safetensors)을 더한다. **앞으로 배포는 이 스크립트로만 한다.**
- 재배포 후 같은 조건의 결과: compile 15s → plan 31s → tools 53s(**근거 52건**, 도구 17회) → arena 64s → findings 76s → verify 83s. 36.5k 토큰, finding 9건, 검증 9/9, 240 mg 기권 유지.
- HF cpu-basic 웜 실행 약 83~93초로, 로컬(140초)보다 빠르다. 로컬 findings 단계는 68초였는데, 로컬 PC의 NLI 재선택(CUDA 감지 시 `DV_EVIDENCE_RERANK=auto`가 켬) 때문으로 추정한다. 재빌드 시 BUILDING→RUNNING은 83~102초.
- 교훈: 배포 검증은 health가 아니라 **도구 호출 성공률**로 한다. 실패한 도구 호출도 UI에 관측값으로 남긴 설계 덕분에 발견할 수 있었다.

### 2026-09-25 — 자율성·도구 집계(P1-2·P1-3), 외부 API 재시도, IC50 대체 표기

- `app/eval/agency.py` → `docs/agency.md`: 현재 기본 설정 60케이스(combo·comboext)의 저장 상태만 읽는다(토큰 0). 단위 규칙(이벤트·케이스·finding·도구 호출)은 스크립트 머리말에 고정했다.
  - 재계획 이벤트:
    - citation_held 21이벤트(16케이스·19 finding)
    - evidence_reselected 20(GPU에서만 켜짐)
    - citation_rejected 6(2케이스, 재작성 2건 모두 최종 검증 통과)
    - 데모에서는 prompt_injection_detected 1
  - finding: 561건(케이스당 9.3), defect 502·abstain 59, 비기권 검증 통과율 483/502 = **0.962**
  - 도구: 966회(케이스당 16.1), 10종, 성공률 **0.995**. 실패 5건은 chembl.potency 500 4건과 openfda.label 500 1건이다.
- 집계 중 발견한 결함:
  - ChEMBL 실패 시 과제가 `done`으로 남고, TCR이 IC50 기본값 30 nM을 조용히 쓰면서 근거 문장에는 "세포 기반"이라고 적었다. 기본값이 ChEMBL 중앙값과 같아 이번 수치에는 영향이 없었다.
    - 수정: 대체 시 `tool_failure` 재계획 이벤트를 남기고, 근거 문장에 "ChEMBL 미확보 → 기본값"이라고 출처를 명시한다.
  - chembl.potency 호출 로그의 `chembl_id`가 해석 전 값(None)이었다. 실제로 호출한 ID를 기록하도록 고쳤다.
  - 외부 API(`fetch_json`: ChEMBL·openFDA)가 재시도 없이 실패했다. 5xx·연결·타임아웃은 2초·4초 백오프로 2회 재시도하도록 했다(`tests/test_fetch_retry.py` 3건).
- 토큰 원장·파레토 그림에 09-23 이후 설정 6개를 추가했다. 확장 세트는 속 빈 사각형으로 구분한다. 감사로그 합계와 평가 결과의 토큰은 모든 설정에서 일치했다.
- LangGraph 체크포인트 직렬화 허용 목록: `trial_schema`의 BaseModel·Enum 타입만 등록했다(`graph._serde()`, MemorySaver·SqliteSaver 공통). 적용 전에는 "미등록 타입 역직렬화" 경고가 났고, 차기 버전에서는 차단 예정이었다. `LANGGRAPH_STRICT_MSGPACK=true`에서 예시 ① 실행 → Human Gate(37.9k 토큰, finding 11) → 승인 재개 → `completed`까지 확인했다.
- 배포본 재확인(HEAD 0de00a7), 예시 ③ 인젝션, autorun 링크 사용:
  - 인젝션 탐지 표시, 33.3k 토큰, 도구 17회, finding 7건, 검증 7/7, 240 mg 기권
  - 재빌드 직후 첫 접속에서 화면이 뜨기까지 약 50~60초가 걸렸다(모듈 import와 예열). 이후 compile 11s, plan 27s.
  - 콜드 경로(재빌드·재기동 직후 첫 접속) 약 1분을 영상과 README 실행 방법에 적고, 심사위원용 기본 경로는 "저장된 결과 즉시 보기"로 안내한다.
