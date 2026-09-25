# 자율성·도구 활용 집계 (자동 생성 2026-09-25 13:57, `python -m app.eval.agency`)

원천: `app/eval/data/results/states/{lean_combo,lean_comboext}/*.json` (60케이스, 현재 기본 설정) · 데모: `app/demo/results/demo*.json`. 단위 규칙은 스크립트 머리말 참조.

## 1. 재계획 이벤트 — 평가 세트

| 트리거 | 의미 | 이벤트 | 케이스(/60) | finding |
|---|---|---|---|---|
| `citation_held` | 인용 근거 불충분 → finding 보류(held) | 21 | 16 | 19 |
| `citation_rejected` | 인용 기각 → 문장 재작성(재계획①) | 6 | 2 | 2 |
| `evidence_reselected` | 근거 재선택(로컬 NLI, GPU 있을 때만) | 20 | 20 | — |
| `invariant_tcr_claim` | LLM의 TCR 주장 → 도구 판정으로 교체(held) | 0 | 0 | — |
| `invariant_conflict_abstain` | Reviewer 충돌 미해소 → 기권 | 0 | 0 | — |
| `prompt_injection_detected` | 문서 내 지시문 탐지 → 데이터로만 처리 | 0 | 0 | — |
| `source_version_conflict` | 폐기된 초안 인용 → 최신 최종본 기준 | 0 | 0 | — |
| `tool_failure` | 도구 실패 → 근거 미확보 표기 | 0 | 0 | — |
| `llm_output_failure` | LLM 구조화 출력 실패 → 결론 없음 | 0 | 0 | — |

- 재작성 2건 중 최종 검증 통과 2건.
- `evidence_reselected`는 CUDA가 있을 때만 켜진다(`DV_EVIDENCE_RERANK=auto`). 평가는 GPU PC에서 돌았고 배포본(CPU)에서는 꺼진다.
- 평가 세트에는 주입·폐기 초안·도구 실패가 없어 해당 트리거가 0이다. 이 경로는 아래 데모·적대 테스트로 보인다.

## 2. 재계획 이벤트 — 시연 데모 3종

| 트리거 | 의미 | 이벤트 | 케이스(/3) | finding |
|---|---|---|---|---|
| `citation_held` | 인용 근거 불충분 → finding 보류(held) | 2 | 2 | 2 |
| `citation_rejected` | 인용 기각 → 문장 재작성(재계획①) | 2 | 1 | 1 |
| `evidence_reselected` | 근거 재선택(로컬 NLI, GPU 있을 때만) | 0 | 0 | — |
| `invariant_tcr_claim` | LLM의 TCR 주장 → 도구 판정으로 교체(held) | 0 | 0 | — |
| `invariant_conflict_abstain` | Reviewer 충돌 미해소 → 기권 | 0 | 0 | — |
| `prompt_injection_detected` | 문서 내 지시문 탐지 → 데이터로만 처리 | 1 | 1 | — |
| `source_version_conflict` | 폐기된 초안 인용 → 최신 최종본 기준 | 0 | 0 | — |
| `tool_failure` | 도구 실패 → 근거 미확보 표기 | 0 | 0 | — |
| `llm_output_failure` | LLM 구조화 출력 실패 → 결론 없음 | 0 | 0 | — |

## 3. finding 판정·검증 — 평가 세트

| 항목 | 값 |
|---|---|
| finding 총수 | 561 (케이스당 9.3) |
| 판정(verdict) | defect 502, abstain 59 |
| 검증 상태 | verified 542, held 19 |
| 비기권 finding 검증 통과율 | 483/502 = 0.962 |

## 4. 도구 호출 — 평가 세트

| 도구 | 호출 | 케이스당 | 성공률 | 지연 중앙값(s) | 지연 최대(s) | 대표 오류 |
|---|---|---|---|---|---|---|
| `pharm.tcr_three_metrics` | 307 | 5.1 | 1.000 | 0.000 | 0.000 | — |
| `openfda.label` | 120 | 2.0 | 0.992 | 1.582 | 6.720 | HTTPError: HTTP Error 500: Internal Server Error |
| `corpus.search` | 120 | 2.0 | 1.000 | 2.292 | 80.469 | — |
| `rdkit.structure_profile` | 60 | 1.0 | 1.000 | 0.090 | 1.320 | — |
| `chembl.potency` | 60 | 1.0 | 0.933 | 2.644 | 41.204 | HTTPError: HTTP Error 500: Internal Server Error |
| `opentargets.target_evidence` | 60 | 1.0 | 1.000 | 0.929 | 1.341 | — |
| `design.compare_sample_matched` | 60 | 1.0 | 1.000 | 3.609 | 6.107 | — |
| `design.required_sample_for_pcs` | 60 | 1.0 | 1.000 | 9.306 | 15.481 | — |
| `ctgov.search_analog_trials` | 60 | 1.0 | 1.000 | 0.444 | 0.752 | — |
| `pharm.exposure_power` | 59 | 1.0 | 1.000 | 0.000 | 0.000 | — |
| **합계** | 966 | 16.1 | 0.995 | | | 도구 종류 10개 |

성공률은 `ok` 필드 기준이다. 실패도 관측값으로 저장·표시한다(UI 도구 호출 탭).
