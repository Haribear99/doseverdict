# 수치 원천표 (자동 생성 2026-09-25 18:15, `python -m app.eval.numbers`)

제출물(기술서·발표·영상·README·데모 화면)의 모든 수치는 이 표에서만 가져온다. 점추정 간 차이는 n=20에서 대부분 신뢰구간이 겹친다 — 유의 여부는 `python -m app.eval.compare`로 확인한 것만 주장한다.

## 1. 평가(축① Silver Set, 단일 기준 시놉시스 DV-DEMO-002의 결함 주입 변형)

| 설정 | 설명 | 세트 | n | span recall | grounded (95% CI) | 검증 통과율 | 토큰/케이스 | LLM 실패 | 원천 |
|---|---|---|---|---|---|---|---|---|---|
| full | 09-11 본평가: Reviewer 3인 | 원 20(AX1-001~020) | 20 | 0.925 | 0.358 [0.267, 0.450] | 0.880 | 57,386 | — | `app/eval/data/results/full.json` |
| lean | 09-11 기본: Reviewer 1인 + 재선택 | 원 20(AX1-001~020) | 20 | 0.950 | 0.408 [0.333, 0.483] | 0.925 | 44,291 | — | `app/eval/data/results/lean.json` |
| no_arena | ablation: Reviewer 없음 | 원 20(AX1-001~020) | 20 | 0.958 | 0.383 [0.300, 0.467] | 0.883 | 29,799 | — | `app/eval/data/results/no_arena.json` |
| no_calc | ablation: 계산 도구 없음 | 원 20(AX1-001~020) | 20 | 0.875 | 0.425 [0.333, 0.517] | 0.808 | 53,545 | — | `app/eval/data/results/no_calc.json` |
| no_verifier | ablation: 검증기 없음 | 원 20(AX1-001~020) | 20 | 0.958 | 0.400 [0.325, 0.483] | 1.000 | 57,791 | — | `app/eval/data/results/no_verifier.json` |
| lean_d3 | 09-23 새 코드 기준선(구조화 출력 경화·불변식·범주 필터) | 원 20(AX1-001~020) | 20 | 0.925 | 0.383 [0.308, 0.458] | 0.951 | 48,050 | 0 | `app/eval/data/results/lean_d3.json` |
| lean_cnone | A/B: compile effort none | 원 20(AX1-001~020) | 20 | 0.933 | 0.433 [0.350, 0.517] | 0.922 | 46,877 | 0 | `app/eval/data/results/lean_cnone.json` |
| lean_strict | A/B: reviewers·findings strict | 원 20(AX1-001~020) | 20 | 0.917 | 0.417 [0.350, 0.483] | 0.964 | 45,793 | 0 | `app/eval/data/results/lean_strict.json` |
| lean_q250 | A/B: 근거 인용문 250자 | 원 20(AX1-001~020) | 20 | 0.950 | 0.383 [0.308, 0.458] | 0.954 | 44,197 | 0 | `app/eval/data/results/lean_q250.json` |
| lean_notopic | A/B: 주제 태그 프롬프트 제거 | 원 20(AX1-001~020) | 20 | 0.950 | 0.400 [0.317, 0.483] | 0.911 | 46,419 | 0 | `app/eval/data/results/lean_notopic.json` |
| lean_fmed | A/B: findings effort medium | 원 20(AX1-001~020) | 20 | 0.908 | 0.417 [0.317, 0.508] | 0.950 | 61,754 | 1 | `app/eval/data/results/lean_fmed.json` |
| lean_c6sol | A/B: compile gpt-6-sol | 원 20(AX1-001~020) | 20 | 0.950 | 0.450 [0.367, 0.533] | 0.957 | 47,099 | 0 | `app/eval/data/results/lean_c6sol.json` |
| lean_g6all | A/B: 전 노드 gpt-6-sol | 원 20(AX1-001~020) | 20 | 0.975 | 0.500 [0.417, 0.583] | 0.969 | 43,734 | 0 | `app/eval/data/results/lean_g6all.json` |
| lean_combo | 현재 기본: gpt-6-sol + strict + 인용문 250자 | 원 20(AX1-001~020) | 20 | 0.958 | 0.508 [0.442, 0.575] | 0.975 | 39,262 | 0 | `app/eval/data/results/lean_combo.json` |
| lean_d3ext | 09-23 새 코드, 확장 세트 | 확장 40(AX1-021~060) | 40 | 0.871 | 0.513 [0.462, 0.563] | 0.947 | 47,162 | 0 | `app/eval/data/results/lean_d3ext.json` |
| lean_g6allext | 전 노드 gpt-6-sol, 확장 세트 | 확장 40(AX1-021~060) | 40 | 0.896 | 0.563 [0.500, 0.629] | 0.956 | 44,433 | 0 | `app/eval/data/results/lean_g6allext.json` |
| lean_comboext | 현재 기본, 확장 세트 | 확장 40(AX1-021~060) | 40 | 0.883 | 0.558 [0.492, 0.629] | 0.963 | 38,756 | 0 | `app/eval/data/results/lean_comboext.json` |

## 2. 소토라십 240 mg TCR (`evidence/tcr_240mg.json`)

| 가정 | C_max | C_avg | C_trough | 판정 |
|---|---|---|---|---|
| (가) 선형 CL/F | 8.615 | 2.4964 | 0.3093 | abstain_metric_dependent |
| (나) 노출 유사(라벨 12.3) | 34.4601 | 9.9856 | 1.237 | covered |

종합: **abstain_assumption_dependent** — PK 가정에 따라 판정이 달라짐 — 240 mg 결론을 만들지 않고 용량군별 반복투여 PK를 요청한다

## 3. 게이트웨이 실측 (`docs/gateway_probe.md`)

- 쿼터: 총 6,000만(09-22 공지). 09-23 13:45 헤더 잔여 59,999,986. 과금 = usage.total_tokens 1:1(모델별 가중치 없음, reasoning 포함).
- 캐시: gpt-6-luna 적중 2,780토큰에도 차감 2,788 → 캐시 절감 0(⑩-b).
- 모델: gpt-5.6-sol/terra/luna, gpt-6-sol/luna 200 / gpt-6-astra 404(09-11·09-23). 기본값은 09-24부터 planner·reviewer·extract 모두 gpt-6-sol.
- 토큰 구성: reasoning 비중 gpt-5.6 세대 3.7~4.9%, gpt-6-sol 0.9~1.0%. 입력이 약 70~80%(`docs/token_ledger.md`).

## 4. 누적 사용량 (감사로그 공개 집계본 `app/eval/data/audit_usage.jsonl`의 usage.total_tokens 합)

- 합계 **20,439,005** 토큰(총 쿼터 6,000만의 34.1%), 마지막 호출 2026-09-25T05:04 UTC.
- 일자별(UTC): 2026-09-10 4,824,920, 2026-09-11 1,008,749, 2026-09-23 12,057,935, 2026-09-24 2,439,285, 2026-09-25 108,116
- 모델별: gpt-5.6-sol 12,926,924, gpt-6-sol 5,376,140, gpt-5.6-terra 2,007,168, gpt-5.6-luna 123,172, gpt-6-luna 5,601
- 원본 `logs/`는 git·Docker에서 제외되고, 재현에 필요한 필드(시각·모델·용도·usage)만 공개 집계본으로 커밋한다. 이 절이 제출물의 누적 토큰 단일 출처다.

