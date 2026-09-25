# 자율성·도구 활용 집계 (자동 생성 2026-09-25 18:15, `python -m app.eval.agency`)

원천: `app/eval/data/results/states/{lean_combo,lean_comboext}/*.json` (60케이스, 현재 기본 설정) · 데모: `app/demo/results/demo*.json`. 단위 규칙은 스크립트 머리말 참조.

## 1. 재계획 이벤트 — 평가 세트

| 트리거 | 의미 | 이벤트 | 케이스(/60) | finding |
|---|---|---|---|---|
| `citation_held` | 인용 근거 불충분 → finding 보류(held) | 21 | 16 | 19 |
| `citation_rejected` | 인용 기각 → 문장 재작성(재계획①) | 6 | 2 | 2 |
| `evidence_reselected` | 근거 재선택(로컬 NLI, GPU 있을 때만) | 20 | 20 | — |
| `invariant_tcr_claim` | LLM finding이 TCR 판정을 담음 → 보류(held), 수치 판정은 도구 finding만 | 0 | 0 | — |
| `invariant_conflict_abstain` | Reviewer 간 상충 미해소 → 기권(Reviewer 3인 옵션에서만 동작) | 0 | 0 | — |
| `prompt_injection_detected` | 문서 내 지시문 탐지 → 데이터로만 처리 | 0 | 0 | — |
| `source_version_conflict` | 폐기된 초안 인용 → 최신 최종본 기준 | 0 | 0 | — |
| `tool_failure` | 도구 실패 → 근거 미확보 표기 | 0 | 0 | — |
| `llm_output_failure` | LLM 구조화 출력 실패 → 결론 없음 | 0 | 0 | — |

- 재작성 2건 중 최종 검증 통과 2건.
- `evidence_reselected`는 CUDA가 있을 때만 켜진다(`DV_EVIDENCE_RERANK=auto`). 평가는 GPU PC에서 돌았고 배포본(CPU)에서는 꺼진다.
- 평가 세트에는 인젝션·폐기 초안이 없어 해당 트리거가 0이다. 이 경로는 아래 데모·적대 테스트로 보인다.
- 도구 실패 5건(4절)은 평가 당시 `tool_failure`로 기록되지 않았다. 과제가 다른 도구 결과로 `done` 처리됐기 때문이다(09-25 수정 전 코드). openFDA 실패 1건(AX1-046)에서는 라벨 PK 미확보로 240 mg 기권 finding이 빠졌다(기권 59/60의 이유).

## 2. 재계획 이벤트 — 시연 데모 3종

| 트리거 | 의미 | 이벤트 | 케이스(/3) | finding |
|---|---|---|---|---|
| `citation_held` | 인용 근거 불충분 → finding 보류(held) | 2 | 2 | 2 |
| `citation_rejected` | 인용 기각 → 문장 재작성(재계획①) | 2 | 1 | 1 |
| `evidence_reselected` | 근거 재선택(로컬 NLI, GPU 있을 때만) | 0 | 0 | — |
| `invariant_tcr_claim` | LLM finding이 TCR 판정을 담음 → 보류(held), 수치 판정은 도구 finding만 | 0 | 0 | — |
| `invariant_conflict_abstain` | Reviewer 간 상충 미해소 → 기권(Reviewer 3인 옵션에서만 동작) | 0 | 0 | — |
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

| 도구 | 호출 | 케이스당 | 성공률 | 지연 중앙값(s) | 지연 최대(s) | 실패 유형 |
|---|---|---|---|---|---|---|
| `pharm.tcr_three_metrics` | 307 | 5.1 | 1.000 | 0.000 | 0.000 | — |
| `openfda.label` | 120 | 2.0 | 0.992 | 1.582 | 6.720 | HTTP 500 1 |
| `corpus.search` | 120 | 2.0 | 1.000 | 2.292 | 80.469 | — |
| `rdkit.structure_profile` | 60 | 1.0 | 1.000 | 0.090 | 1.320 | — |
| `chembl.potency` | 60 | 1.0 | 0.933 | 2.644 | 41.204 | HTTP 500 3, 타임아웃 1 |
| `opentargets.target_evidence` | 60 | 1.0 | 1.000 | 0.929 | 1.341 | — |
| `design.compare_sample_matched` | 60 | 1.0 | 1.000 | 3.609 | 6.107 | — |
| `design.required_sample_for_pcs` | 60 | 1.0 | 1.000 | 9.306 | 15.481 | — |
| `ctgov.search_analog_trials` | 60 | 1.0 | 1.000 | 0.444 | 0.752 | — |
| `pharm.exposure_power` | 59 | 1.0 | 1.000 | 0.000 | 0.000 | — |
| **합계** | 966 | 16.1 | 0.995 | | | 도구 종류 10개 |

성공률은 `ok` 필드 기준이다. 실패도 관측값으로 저장·표시한다(UI 도구 호출 탭).
