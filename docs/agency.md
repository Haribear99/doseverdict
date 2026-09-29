# 자율성·도구 활용 집계 (자동 생성 2026-09-29 11:21, `python -m app.eval.agency`)

원천: `app/eval/data/results/states/{lean_v3,lean_v3b,lean_mdrug3}/*.json` (70케이스, 최종 코드 c7dc0be — 원 20 2회 반복 + 다약물 30) · 데모: `app/demo/results/demo*.json`. 단위 규칙은 스크립트 머리말 참조.

## 1. 재계획 이벤트 — 평가 세트

| 트리거 | 의미 | 이벤트 | 케이스(/70) | finding |
|---|---|---|---|---|
| `citation_held` | 인용 근거 불충분 → finding 보류(held) | 24 | 17 | 21 |
| `citation_rejected` | 인용 기각 → 문장 재작성(재계획①) | 0 | 0 | — |
| `evidence_reselected` | 근거 재선택(로컬 NLI, GPU 있을 때만) | 29 | 26 | — |
| `invariant_tcr_claim` | LLM finding이 TCR 판정을 담음 → 보류(held), 수치 판정은 도구 finding만 | 0 | 0 | — |
| `invariant_conflict_abstain` | Reviewer 간 상충 미해소 → 기권(Reviewer 3인 옵션에서만 동작) | 0 | 0 | — |
| `prompt_injection_detected` | 문서 내 지시문 탐지 → 데이터로만 처리 | 0 | 0 | — |
| `source_version_conflict` | 폐기된 초안 인용 → 최신 최종본 기준 | 0 | 0 | — |
| `tool_failure` | 도구 실패 → 근거 미확보 표기 | 0 | 0 | — |
| `held_research` | 보류 finding 표적 재검색(로컬 NLI, 가드 선행) | 22 | 16 | 19 |
| `budget_guard` | 호출 전 예산 가드 → 강등·결론 없음 | 0 | 0 | — |
| `tool_fallback` | 매핑 표 밖 약물 → ChEMBL 이름 검색·openFDA 성분명 검색으로 대체 조회 | 20 | 10 | — |
| `llm_output_failure` | LLM 구조화 출력 실패 → 결론 없음 | 0 | 0 | — |

- 재작성 없음.
- 보류 재검색 22건 중 검증 전환 1건, 보류 유지 21건(NLI 판정 27쌍 — 가드가 대부분을 걸렀다).
- `evidence_reselected`는 CUDA가 있을 때만 켜진다(`DV_EVIDENCE_RERANK=auto`). 평가는 GPU PC에서 돌았고 배포본(CPU)에서는 꺼진다.
- 평가 세트에는 인젝션·폐기 초안이 없어 해당 트리거가 0이다. 이 경로는 아래 데모·적대 테스트로 보인다.
- 도구 실패 중 openFDA 404는 대부분 미승인 가상 후보 DV-505의 라벨 없음(정상)이다. 이는 `tool_failure`가 아니라 `no_label`로 처리한다.

## 2. 재계획 이벤트 — 시연 데모 5종

| 트리거 | 의미 | 이벤트 | 케이스(/5) | finding |
|---|---|---|---|---|
| `citation_held` | 인용 근거 불충분 → finding 보류(held) | 2 | 2 | 2 |
| `citation_rejected` | 인용 기각 → 문장 재작성(재계획①) | 0 | 0 | — |
| `evidence_reselected` | 근거 재선택(로컬 NLI, GPU 있을 때만) | 2 | 2 | — |
| `invariant_tcr_claim` | LLM finding이 TCR 판정을 담음 → 보류(held), 수치 판정은 도구 finding만 | 0 | 0 | — |
| `invariant_conflict_abstain` | Reviewer 간 상충 미해소 → 기권(Reviewer 3인 옵션에서만 동작) | 0 | 0 | — |
| `prompt_injection_detected` | 문서 내 지시문 탐지 → 데이터로만 처리 | 1 | 1 | — |
| `source_version_conflict` | 폐기된 초안 인용 → 최신 최종본 기준 | 0 | 0 | — |
| `tool_failure` | 도구 실패 → 근거 미확보 표기 | 0 | 0 | — |
| `held_research` | 보류 finding 표적 재검색(로컬 NLI, 가드 선행) | 2 | 2 | 2 |
| `budget_guard` | 호출 전 예산 가드 → 강등·결론 없음 | 0 | 0 | — |
| `tool_fallback` | 매핑 표 밖 약물 → ChEMBL 이름 검색·openFDA 성분명 검색으로 대체 조회 | 2 | 1 | — |
| `llm_output_failure` | LLM 구조화 출력 실패 → 결론 없음 | 0 | 0 | — |

## 3. finding 판정·검증 — 평가 세트

| 항목 | 값 |
|---|---|
| finding 총수 | 666 (케이스당 9.5) |
| 판정(verdict) | defect 606, abstain 60 |
| 검증 상태 | verified 643, held 23 |
| 비기권 finding 검증 통과율 | 583/606 = 0.962 |

## 4. 도구 호출 — 평가 세트

| 도구 | 호출 | 케이스당 | 성공률 | 지연 중앙값(s) | 지연 최대(s) | 실패 유형 |
|---|---|---|---|---|---|---|
| `pharm.tcr_three_metrics` | 367 | 5.2 | 1.000 | 0.000 | 0.000 | — |
| `openfda.label` | 167 | 2.4 | 0.940 | 1.364 | 6.343 | HTTP 404 10 |
| `corpus.search` | 140 | 2.0 | 1.000 | 2.314 | 81.861 | — |
| `rdkit.structure_profile` | 70 | 1.0 | 1.000 | 0.105 | 1.400 | — |
| `opentargets.target_evidence` | 70 | 1.0 | 1.000 | 0.945 | 1.331 | — |
| `pharm.exposure_power` | 70 | 1.0 | 1.000 | 0.000 | 0.000 | — |
| `design.compare_sample_matched` | 70 | 1.0 | 1.000 | 3.616 | 5.261 | — |
| `design.required_sample_for_pcs` | 70 | 1.0 | 1.000 | 9.450 | 12.734 | — |
| `ctgov.search_analog_trials` | 70 | 1.0 | 1.000 | 0.352 | 1.181 | — |
| `chembl.potency` | 60 | 0.9 | 1.000 | 2.632 | 27.785 | — |
| `chembl.lookup` | 20 | 0.3 | 1.000 | 0.781 | 2.540 | — |
| **합계** | 1174 | 16.8 | 0.991 | | | 도구 종류 11개 |
| 예상된 라벨 없음(openFDA 404) 10건 제외 | 1164 | | 1.000 | | | |

성공률은 `ok` 필드 기준이다. 실패도 관측값으로 저장·표시한다(UI 도구 호출 탭).
