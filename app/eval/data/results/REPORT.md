# 평가 결과 (축① 규범 유도 결함 주입 Silver Set)

지표 정의: span recall = 주입 문장을 finding이 가리킴(어휘). grounded recall = 그 finding이 정답 규범 문서를 인용했거나 근거 사실이 원문과 겹침. 가중 = critical 4·high 3·medium 2·low 1. precision proxy = 적중 finding / 전체 finding(정상판에 대한 지적은 '무관'으로 세므로 하한). 95% CI는 케이스 단위 부트스트랩(2,000회).

| 설정 | n | span recall [CI] | 가중 span | grounded recall [CI] | 가중 grounded | precision | 검증 통과율 | 토큰/케이스 | 초/케이스 |
|---|---|---|---|---|---|---|---|---|---|
| checklist | 20 | 0.791 [0.69, 0.88] | 0.772 | 0.000 [0.00, 0.00] | 0.000 | 0.747 | 0.000 | 0 | 0 |
| single_rag | 20 | 0.467 [0.38, 0.55] | 0.493 | 0.100 [0.03, 0.17] | 0.108 | 0.658 | 0.000 | 3,300 | 14 |
| full | 20 | 0.925 [0.88, 0.97] | 0.928 | 0.358 [0.27, 0.45] | 0.360 | 0.511 | 0.880 | 57,386 | 199 |
| no_calc | 20 | 0.875 [0.82, 0.93] | 0.879 | 0.425 [0.33, 0.52] | 0.421 | 0.554 | 0.808 | 53,545 | 195 |
| no_arena | 20 | 0.958 [0.93, 0.98] | 0.962 | 0.383 [0.30, 0.47] | 0.386 | 0.550 | 0.883 | 29,799 | 144 |
| no_verifier | 20 | 0.958 [0.92, 0.99] | 0.962 | 0.400 [0.33, 0.48] | 0.402 | 0.525 | 1.000 | 57,791 | 206 |
| lean | 20 | 0.950 [0.91, 0.98] | 0.956 | 0.408 [0.33, 0.47] | 0.414 | 0.577 | 0.925 | 44,291 | 157 |

## 사후 재채점 실험 (저장 상태 + 로컬 NLI 근거 재선택, LLM 재호출 없음 — 채택안은 `_final`; 나머지는 기각·참고)

| 설정 | grounded recall [CI] | 검증 통과율 | 근거 추가 | 비고 |
|---|---|---|---|---|
| full_cocite | 0.383 [0.28, 0.48] | 0.930 | 38 | 사후 재채점: 저장 상태 + reselect_evidence + verify_findings(재작성 없음) |
| full_cocite2 | 0.608 [0.53, 0.70] | 0.963 | 285 | 사후 재채점: 저장 상태 + reselect_evidence + verify_findings(재작성 없음) |
| full_cocite3 | 0.408 [0.32, 0.50] | 0.948 | 50 | 사후 재채점: 저장 상태 + reselect_evidence + verify_findings(재작성 없음) |
| full_final | 0.367 [0.27, 0.47] | 0.898 | 8 | 사후 재채점: 저장 상태 + reselect_evidence + verify_findings(재작성 없음) |
| full_rerank | 0.367 [0.27, 0.47] | 0.930 | 20 | 사후 재채점: 저장 상태 + reselect_evidence + verify_findings(재작성 없음) |
| no_arena_cocite | 0.425 [0.33, 0.52] | 0.928 | 43 | 사후 재채점: 저장 상태 + reselect_evidence + verify_findings(재작성 없음) |
| no_arena_rerank | 0.400 [0.32, 0.48] | 0.928 | 20 | 사후 재채점: 저장 상태 + reselect_evidence + verify_findings(재작성 없음) |

## Ablation 기여도 (full 대비 grounded weighted recall 차이)

| 제거한 구성요소 | 설정 | Δ grounded w-recall | Δ 검증 통과율 | Δ 토큰 |
|---|---|---|---|---|
| 계산 모듈 | no_calc | +0.061 | -0.072 | -3,841 |
| Adversarial Reviewer | no_arena | +0.026 | +0.003 | -27,587 |
| Citation Verifier | no_verifier | +0.042 | +0.120 | +405 |

해석 규칙(제안서 4장): 전체 시스템이 정규식 체크리스트 대비 grounded recall에서 15%p 이상 앞서지 못하면 멀티에이전트가 불필요하다고 보고한다.
→ full − checklist (grounded recall) = +0.358 (기준 충족).
