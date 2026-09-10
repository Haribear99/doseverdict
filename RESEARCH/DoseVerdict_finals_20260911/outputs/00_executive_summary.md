# DoseVerdict 본선 착수 리서치 — 의사결정 보고서

세션 `DoseVerdict_finals_20260911` · 작성 2026-09-11 · 조사 에이전트 A~E + 팀장 직접 실행 검증 · 소스 77건(`sources/sources.jsonl`, 참고문헌 `sources/bibliography.md`) · claim ledger 27건(검증 19 / 미확정 8 / 반박 0)

> 본문은 검증 게이트를 통과한 주장만 단정형으로 쓰고 문장 끝에 claim ID를 붙였다. 검증되지 않은 사항은 「미확정 사항과 대응」 절에서만 다룬다.

---

## 1. 결론 — 4개 결정

| 결정 | 최종안 | 검증된 근거 |
|---|---|---|
| **① 스택** | **LangGraph 1.2.11(오케스트레이션·interrupt·SQLite 체크포인터) + LLM 호출은 `openai` SDK 직접(GatewayClient) + Streamlit(st.graphviz_chart) + FastAPI(도구 API)**. `langchain-openai`의 `ChatOpenAI`는 **쓰지 않는다** | Responses 전용 게이트웨이 + `api-key` 헤더 조합에서 `ChatOpenAI`의 성공 사례가 없고 실패 사례만 확인됐다 (clm_010). LangGraph는 LLM 클라이언트에 독립적이며 필요한 HITL·스트리밍·체크포인터를 공식 지원한다 (clm_011). Streamlit 스레드 제약 때문에 동기 `graph.stream()`으로 노드 단위 갱신을 쓴다 (clm_012). |
| **② 배포** | **1순위 허깅페이스 스페이스(컨테이너 SDK, 무료 CPU 티어) / 2순위 Google Cloud Run / 3순위 Cloudflare Tunnel(노트북, 폴백)**. Streamlit Community Cloud·Render는 제외 | Streamlit Cloud(약 1GB)·Render(512MB)는 RDKit·FAISS·임베딩 앱에 메모리가 부족하다 (clm_015). Cloud Run Always Free는 메모리 상한이 넉넉하나 결제 계정 연결이 전제다 (clm_016). HF 무료 티어의 정책 변동 리스크는 「미확정」 절 참조. |
| **③ 모델 티어링** | Planner·Reviewer = **gpt-5.6-sol**, Compiler(구조화 추출) = **gpt-5.6-terra**, 대량 생성·평가 = **gpt-5.6-luna**. 임베딩·리랭커·NLI는 로컬 GPU에서 사전 계산, 배포본은 CPU int8. **Astra는 `.env` 교체 대기** | 게이트웨이는 gpt-5.6 3종만 허용하고 gpt-6.0 지원은 미정이다 (clm_003). 사용자가 말한 Astra는 GPT-6 Astra(2026-09-03/04 출시)이며 Azure Foundry에서는 이미 Responses API 지원 모델이다 (clm_004). 모델 ID·컨텍스트 1M·출력 128k·reasoning effort 6단계는 확인됐다 (clm_005). |
| **④ 토큰 예산** | 3,000만 토큰을 개발 20 / 평가셋 10 / 본평가 40 / 시연 15 / 예비 15%로 배정. **reasoning effort 기본 `medium`, Planner만 `high`**, 스트리밍은 시연 UI에서만, 평가 실행은 비스트리밍 | reasoning 토큰은 output 토큰으로 계량되어 effort를 올리면 쿼터가 직접 줄어든다 (clm_027). 본선 배점에 리소스 활용 효율성 15점이 있으므로 감사로그를 산출물로 낸다 (clm_002). |

### 예선 제안서 대비 정정 사항

1. **식약처 안내서 날짜 — 제안서가 맞았다.** 「항암제 임상시험 중 용량 최적화 전략 가이드라인」은 문서번호 안내서-1443-01, 담당 종양항생약품과, PDF 14쪽이며 본문에 '2025. 8. 29. 제정'이 명시돼 있다. 식약처 웹 등록일은 2025-11-17, KoNECT 미러 게시일은 2025-12-23이다 (clm_019). 기술서에는 "2025-08-29 제정(식약처 웹 등록 2025-11-17)"로 쓴다.
2. **인용 검증기 모델.** 정확한 식별자는 재확인 대상이다. 세부는 「미확정」 절.
3. **규제 문서 원본 확보 경로.** 코퍼스 빌드는 로컬 `app/corpus/raw/`에 보관한 원본을 사용한다. 원격 접근 문제는 「미확정」 절.

---

## 2. 본선 요건 (변경 없음)

- 제출 마감 2026-10-02 16:00. 필수: demo URL(실행 방법 3가지 이상)·YouTube 10분·발표 PDF. 추가: 상세기술서 PDF·GitHub (clm_001).
- 배점: 과학적 타당성·혁신성 30 / 자율성·지능 10 / 도구 활용·통합 15 / 리소스 활용 효율성 15 / 시연·완성도 30 (clm_002).

## 3. 게이트웨이·모델 (검증된 사실)

- 데이콘 게이트웨이는 Responses API 경로만 안내하고 `api-key` 헤더로 인증하며, 팀 누적 3,000만 토큰·50만 TPM·300 RPM이다 (clm_003).
- Programmatic Tool Calling은 V8 샌드박스라 네트워크·파일시스템·서브프로세스가 없다. 따라서 RDKit·ChEMBL·openFDA·몬테카를로는 클라이언트 측 function tool로만 구현한다 (clm_009).
- 프롬프트 인젝션 방어는 외부 문서 격리·도구 allowlist·사람 승인이 OWASP·OpenAI 공통 권고다 (clm_013). 제안서 설계와 일치한다.

## 4. 규제 코퍼스 (확보 완료)

| 문서 | 로컬 파일 | 쪽수 | 확보 경로 |
|---|---|---|---|
| FDA 항암제 용량 최적화 가이던스(최종본, 2024년 8월) | `fda_dosing_final_2024.pdf` | 12 | 인터넷 아카이브 사본 |
| FDA AI 신뢰성 초안 가이던스 (2025-01) | `fda_ai_credibility_draft_2025.pdf` | 23 | 인터넷 아카이브 사본 |
| FDA Expansion Cohorts (2022-03) | `fda_expansion_cohorts_2022.pdf` | 19 | 인터넷 아카이브 사본 |
| FDA 방사성의약품 용량 최적화 초안 (2025-08, 신규 발견) | `fda_radiopharm_dose_draft_2025.pdf` | 11 | 인터넷 아카이브 사본 |
| ICH E6(R3) Step 4 (2025-01-06) | `ich_e6r3_step4_2025.pdf` | 86 | 직접 다운로드 (clm_018) |
| ICH E4 (1994) | `ich_e4.pdf` | 14 | 직접 다운로드 (clm_018) |
| 식약처 안내서-1443-01 (2025-08) | `mfds_1443-01_dosing_guide_2025.pdf` | 14 | 식약처 원문 다운로드 (clm_019) |

- 「용량 확장 코호트 설계 시 고려사항」(식약처)은 개별 URL을 못 찾아 미확보. Phase 1에서 식약처 게시판 순회로 재탐색.
- 공개 API 한도: openFDA 키 없이 240/분·1,000/일(키 사용 시 120,000/일)이라 키 발급을 권장한다. ChEMBL·Open Targets는 공식 한도 미공개, CT.gov v2는 약 50 req/min이다 (clm_020).

## 5. 로컬 모델 (검증된 사실)

- bge-m3(0.568B, 8k 토큰, fp16 약 1.06GB)는 8GB VRAM에서 긴 입력 배치가 빠듯하므로 코퍼스 임베딩을 GPU에서 사전 계산하고 배포본은 CPU int8 ONNX(3.23배 가속, 손실 0.5% 미만)로 질의만 인코딩한다 (clm_023).
- 검증기 분리 근거: LLM-judge 자기선호 편향, MiniCheck류 전용 검증기의 효율 (clm_025).
- FlagEmbedding 1.4.2는 transformers `>=4.44.2,<6.0`으로 완화되어 docling/marker와 공존 가능하다 (clm_026).

---

## 6. 다음 행동 (Phase 0 마무리 → Phase 1)

1. 사용자: `.env`에 키 입력 → `python -m app.llm.smoke_test` (3모델·Astra 프로브·Structured Outputs·tool·stream·effort별 토큰).
2. 코퍼스 청킹·임베딩 사전 계산(GPU) → `app/corpus/index/`.
3. NLI 모델 다운로드 실행 검증, bge-m3 fp16 VRAM 실측(512 토큰 배치).
4. 허깅페이스 스페이스에 빈 컨테이너 스페이스 생성 테스트 — 실패 시 Cloud Run 카드 등록 여부를 사용자에게 확인.

---

## 미확정 사항과 대응 (Unresolved)

아래는 검증 게이트를 통과하지 못한 주장이다. 본문에서는 단정하지 않았고, 각 항목을 실측으로 닫는다.

| ID | 내용(요지) | 미확정 사유 | 현재 대응 | 닫는 방법 |
|---|---|---|---|---|
| clm_006 | GPT-5.6 인하 후 공개 가격(Sol $4/$20, Terra $2/$12, Luna $0.20/$1.20) | 출시가와 상충, 공식 페이지 자동 조회 403 | 게이트웨이는 토큰 수 기준 쿼터라 설계 무관 | 필요 시 OpenAI 대시보드 확인 |
| clm_007 | APIM 토큰 정책이 usage 기준으로 계량하고 스트리밍 시 추정치 처리 | 소스 type 1종 | 평가 실행은 비스트리밍으로 usage 기록 | 스모크 ①·⑤ 헤더 비교 |
| clm_008 | APIM SSE에 buffer-response=false·4분 유휴 타임아웃 | 조직 1개(Microsoft) | 장기 추론은 분할 또는 스트리밍 | 스모크 ⑤ 실측 |
| clm_014 | HF Spaces 무료 CPU Basic(2 vCPU·16GB·48h sleep), 2026-07 Docker 유료화 변동 후 롤백 정황 | 공식 문서 경고문 vs 포럼 상충 | 1순위로 두되 Cloud Run 백업 준비 | 빈 Docker Space 생성 실측 |
| clm_017 | fda.gov 직링크가 자동화 클라이언트(curl/httpx)에 404, 브라우저형에는 정상 | 클라이언트별 결과 상이(partial) | Wayback 스냅샷(digest 동일)으로 확보 완료 | 코퍼스 빌드 스크립트에 Wayback 경로 고정 |
| clm_021 | AACT 월간 스냅샷(20260619, 2.3GB) 2026년에도 발행 | 조직 1개(CTTI) | 후향 검증 축②는 축소 후보 1순위 | 다운로드 시 확인 |
| clm_022 | 제안서의 `MoritzLaurer/DeBERTa-v3-large-mnli-fever-anli`는 HF 404, 실사용은 `-ling-wanli` 버전(0.4B, MIT) | 동일 조직 2표면 | 코드에서는 `-ling-wanli` ID를 기본값으로 둔다 | Phase 1 모델 다운로드 |
| clm_024 | 규제 조항 검색에서 cross-encoder 리랭킹 효과가 문헌상 엇갈림 | 피어리뷰 vs 업체 블로그 상충 | 리랭커는 옵션 플래그로 구현 | Gold Set ablation |

추가 미검증 메모(ledger 미등록): file_search 도구는 `/files`·`/vector_stores` 엔드포인트가 필요해 이 게이트웨이에서는 쓸 수 없다는 A 에이전트 판단(설계상 사용 안 함). FDA E6(R3) 준수 시행일 미지정·Annex 2 2027-01-15 발효 예정은 2차 소스.

## 반박 (Refuted)

없음. 리서치 에이전트 D가 제기한 "식약처 안내서 번호·날짜 불일치"는 팀장이 식약처 원문 게시물과 PDF 표지를 직접 확인해 번호·제정일(2025-08-29)이 정확함을 확인했다(clm_019). 에이전트 D의 "FDA 404 미재현"은 클라이언트 종류 차이로 설명된다(clm_017).

## Confidence

- 검증 19 / 미확정 8 / 반박 0. 미확정 비율 30%(임계 50% 이하).
- 실행 검증(confirmed) 3건: ICH PDF 다운로드, 식약처 PDF 번호·발행월, FlagEmbedding 1.4.2 의존성. partial 1건: FDA 직링크.
- 게이트웨이 관련 주장은 API 키 입력 후 스모크 테스트로 재판정한다.
