# 반복 일관성 비교 (`python -m app.eval.consistency report`)

사전 등록: `docs/consistency_prereg.md` — 마지막 커밋 232aae6fd40034d858f62a3585ef6ecdd101d75c 2026-10-01T23:59:33+09:00, HEAD 232aae6fd400. 첫 상태 저장 2026-10-02T00:00:02+0900.
약 4종(용량군 20개) × 3회. 차이 = 앞 팔 − 뒤 팔, 약 단위 쌍대.

## 완료 현황

| 상태 디렉터리 | 완료 / 예정 | 인프라 실패로 격리된 시도 | 최종 실패(표본에 실패로 반영) | 환경 조합 수 |
|---|---|---|---|---|
| results/states/consistency_l1_oneshot/ | 12 / 12 | 0 | 0 | 1 |
| results/states/consistency_l1_inputs/ | 12 / 12 | 0 | 0 | 1 |
| results/states/consistency_oneshot/ | 12 / 12 | 0 | 0 | 1 |
| results/states/consistency_agent/ | 12 / 12 | 0 | 0 | 1 |

## 1차: L2 에이전트 − 원샷(지적한 시놉시스 문장 집합의 3회 쌍별 Jaccard)

| 팔 | L2 | 약별 | 빈 집합 쌍 제외 L2(2차) | 빈 집합 쌍 수 | 최종 실패 회차 | 회차별 집합 크기 |
|---|---|---|---|---|---|---|
| 원샷(원 출력) | 0.746 | adagrasib 0.716, dv505 0.644, lorlatinib 0.867, sotorasib 0.758 | 0.746 | 0 | 0 | adagrasib 8/11/11; dv505 7/10/11; lorlatinib 8/8/10; sotorasib 9/10/10 |
| 원샷 + NLI 필터(민감도) | 0.497 | adagrasib 0.719, dv505 0.497, lorlatinib 0.515, sotorasib 0.259 | 0.497 | 0 | 0 | adagrasib 8/7/9; dv505 6/7/11; lorlatinib 4/4/7; sotorasib 4/7/4 |
| 에이전트(lean) | 0.687 | adagrasib 0.686, dv505 0.622, lorlatinib 0.685, sotorasib 0.758 | 0.687 | 0 | 0 | adagrasib 10/11/11; dv505 10/9/11; lorlatinib 14/12/11; sotorasib 11/8/10 |

| 지표 | 비교 | 역할 | 약 | 차이 | 방향(약별) | 정확 부호 뒤집기 p(양측) | 95% CI(정확 열거 부트스트랩, 기술용) | 판정 |
|---|---|---|---|---|---|---|---|---|
| L2 | agent - oneshot | 1차 | 4 | -0.059 | 양수 0·음수 3·0 1 / 약 4종 | 0.250(최소 0.125) | [-0.142, -0.007] | 이 시놉시스 4종에서 차이 확인 안 됨 |
| L2 | agent - oneshot_nli | 민감도(같은 원샷 출력의 부분집합, 독립 비교 아님) | 4 | +0.190 | 양수 3·음수 1·0 0 / 약 4종 | 0.250(최소 0.125) | [+0.018, +0.405] | — |

판정 규칙(사전 고정): 약 단위 정확 부호 뒤집기 검정 p ≤ 0.05이면 방향에 따라 "이 시놉시스 4종에서 에이전트가 같은 입력에 더 일관된 판정(지적 문장 집합)을 낸다" 또는 "이 시놉시스 4종에서 에이전트가 덜 일관된 판정(지적 문장 집합)을 낸다", 그 외 "이 시놉시스 4종에서 차이 확인 안 됨". 약 4종에서는 가능한 최소 양측 p가 0.125라 이 판정은 실행 전부터 "차이 확인 안 됨"으로 정해져 있다. 결과는 방향 일치 수(k/4)와 효과 크기로 읽는다. 부트스트랩 CI는 약 4종의 순서 있는 재표본 256개를 정확 열거한 기술용이며, 어느 약이든 한 약만 4번 뽑히는 재표본이 4/256 = 1.56%라 CI 끝은 가장 극단적인 약 하나에 좌우된다. 민감도 행은 같은 원샷 출력의 부분집합이라 1차와 독립된 증거가 아니다.

## L1(용량군 3회 판정 일치) — 기술 통계

에이전트 L1은 기존 실행에서 이미 관측됐고 입력 확보가 결정론적이라 사전 등록에서 1차 판정에서 뺐다(사전 등록 '이미 본 것'). 판정 문구를 만들지 않는다.

| 팔 | L1(합산) | 약별 평균(2차) | missing 제외(2차) | 약별(일치/용량군) | 판정값 분포 | 3회 모두 missing·cannot_assess 용량군 |
|---|---|---|---|---|---|---|
| 원샷(도구 없음) | 0.650 | 0.642 | 0.650 | adagrasib 2/4, dv505 5/5, lorlatinib 4/6, sotorasib 2/5 | covered 35, not_covered 4, indeterminate 21 | 0 |
| 원샷 입력 + 결정론 계산기 | 0.700 | 0.688 | 0.700 | adagrasib 3/4, dv505 5/5, lorlatinib 6/6, sotorasib 0/5 | covered 48, indeterminate 12 | 0 |
| 에이전트(lean) | 1.000 | 1.000 | 1.000 | adagrasib 4/4, dv505 5/5, lorlatinib 6/6, sotorasib 5/5 | covered 39, indeterminate 21 | 0 |

| 지표 | 비교 | 역할 | 약 | 차이 | 방향(약별) | 정확 부호 뒤집기 p(양측) | 95% CI(정확 열거 부트스트랩) | 판정 |
|---|---|---|---|---|---|---|---|---|
| L1 | agent - oneshot | 기술(판정 문구 없음) | 4 | +0.350 | 양수 3·음수 0·0 1 / 약 4종 | 0.250(최소 0.125) | [+0.105, +0.556] | — |
| L1 | agent - oneshot_tool | 기술(판정 문구 없음) | 4 | +0.300 | 양수 2·음수 0·0 2 / 약 4종 | 0.500(최소 0.125) | [+0.000, +0.750] | — |
| L1 | oneshot_tool - oneshot | 기술(판정 문구 없음) | 4 | +0.050 | 양수 2·음수 1·0 1 / 약 4종 | 1.000(최소 0.125) | [-0.263, +0.300] | — |

에이전트가 포함된 L1 비교는 한계 3(에이전트 L1은 도구 정답과 같은 계산 경로) 단서와 함께만 인용한다. "원샷 입력 + 계산기 − 원샷"이 유의하지 않아도 동등성 근거가 아니다(동등성 마진을 사전에 정하지 않았으므로 동등성 주장 금지).

### 입력 재현(정보가 있는 L1 지표, 기술용)

| 약 | 원샷 입력 6개 3회 동일 | 에이전트 입력 6개 3회 동일 | 에이전트 계산 용량 집합 3회 동일 |
|---|---|---|---|
| sotorasib | 아니오 | 예 | 예 |
| adagrasib | 아니오 | 예 | 예 |
| lorlatinib | 아니오 | 예 | 예 |
| dv505 | 아니오 | 예 | 예 |

- 원샷 입력 + 계산기가 고른 입력(회차별, 이 팔 판정의 변동은 여기서만 온다):
  - adagrasib 회차 0: cl_f_L_per_hr=37, t_half_hr=23, tau_hr=12, fu=0.016, ic50_nM=10, mw=604.12
  - adagrasib 회차 1: cl_f_L_per_hr=25.8, t_half_hr=23, tau_hr=12, fu=0.017, ic50_nM=10, mw=604.11
  - adagrasib 회차 2: cl_f_L_per_hr=37, t_half_hr=23, tau_hr=12, fu=0.016, ic50_nM=5, mw=604.13
  - dv505 회차 0: cl_f_L_per_hr=18, t_half_hr=9, tau_hr=24, fu=0.06, ic50_nM=12, mw=501.56
  - dv505 회차 1: cl_f_L_per_hr=18, t_half_hr=9, tau_hr=24, fu=0.06, ic50_nM=12, mw=501.56
  - dv505 회차 2: cl_f_L_per_hr=18, t_half_hr=9, tau_hr=24, fu=0.06, ic50_nM=12, mw=473.34
  - lorlatinib 회차 0: cl_f_L_per_hr=18, t_half_hr=24, tau_hr=24, fu=0.34, ic50_nM=10, mw=406.41
  - lorlatinib 회차 1: cl_f_L_per_hr=18, t_half_hr=24, tau_hr=24, fu=0.34, ic50_nM=1.3, mw=406.41
  - lorlatinib 회차 2: cl_f_L_per_hr=18, t_half_hr=14, tau_hr=24, fu=0.34, ic50_nM=1.3, mw=406.41
  - sotorasib 회차 0: cl_f_L_per_hr=26.2, t_half_hr=5, tau_hr=24, fu=0.11, ic50_nM=90, mw=560.6
  - sotorasib 회차 1: cl_f_L_per_hr=26.2, t_half_hr=5, tau_hr=24, fu=0.11, ic50_nM=6, mw=560.6
  - sotorasib 회차 2: cl_f_L_per_hr=26.2, t_half_hr=5, tau_hr=24, fu=0.11, ic50_nM=6, mw=560.6
- 에이전트가 확보한 입력(회차별):
  - adagrasib 회차 0: cl_f=37.0, t_half=23.0, tau=12.0, fu=0.02, ic50=10.0, mw=604.13, pk_src=FDA 라벨 12.3(KRAZATI), ic50_src=ChEMBL 세포 기반 중앙값, 용량 [150.0, 300.0, 400.0, 600.0]
  - adagrasib 회차 1: cl_f=37.0, t_half=23.0, tau=12.0, fu=0.02, ic50=10.0, mw=604.13, pk_src=FDA 라벨 12.3(KRAZATI), ic50_src=ChEMBL 세포 기반 중앙값, 용량 [150.0, 300.0, 400.0, 600.0]
  - adagrasib 회차 2: cl_f=37.0, t_half=23.0, tau=12.0, fu=0.02, ic50=10.0, mw=604.13, pk_src=FDA 라벨 12.3(KRAZATI), ic50_src=ChEMBL 세포 기반 중앙값, 용량 [150.0, 300.0, 400.0, 600.0]
  - dv505 회차 0: cl_f=18.0, t_half=9.0, tau=24.0, fu=0.06, ic50=12.0, mw=501.566, pk_src=프로토콜 보고 PK, ic50_src=프로토콜 보고 IC50, 용량 [50.0, 100.0, 200.0, 400.0, 600.0]
  - dv505 회차 1: cl_f=18.0, t_half=9.0, tau=24.0, fu=0.06, ic50=12.0, mw=501.566, pk_src=프로토콜 보고 PK, ic50_src=프로토콜 보고 IC50, 용량 [50.0, 100.0, 200.0, 400.0, 600.0]
  - dv505 회차 2: cl_f=18.0, t_half=9.0, tau=24.0, fu=0.06, ic50=12.0, mw=501.566, pk_src=프로토콜 보고 PK, ic50_src=프로토콜 보고 IC50, 용량 [50.0, 100.0, 200.0, 400.0, 600.0]
  - lorlatinib 회차 0: cl_f=18.0, t_half=24.0, tau=24.0, fu=0.34, ic50=9.0, mw=406.421, pk_src=FDA 라벨 12.3(Lorbrena), ic50_src=ChEMBL 세포 기반 중앙값, 용량 [25.0, 50.0, 75.0, 100.0, 150.0, 200.0]
  - lorlatinib 회차 1: cl_f=18.0, t_half=24.0, tau=24.0, fu=0.34, ic50=9.0, mw=406.421, pk_src=FDA 라벨 12.3(Lorbrena), ic50_src=ChEMBL 세포 기반 중앙값, 용량 [25.0, 50.0, 75.0, 100.0, 150.0, 200.0]
  - lorlatinib 회차 2: cl_f=18.0, t_half=24.0, tau=24.0, fu=0.34, ic50=9.0, mw=406.421, pk_src=FDA 라벨 12.3(Lorbrena), ic50_src=ChEMBL 세포 기반 중앙값, 용량 [25.0, 50.0, 75.0, 100.0, 150.0, 200.0]
  - sotorasib 회차 0: cl_f=26.2, t_half=5.0, tau=24.0, fu=0.11, ic50=30.0, mw=560.605, pk_src=FDA 라벨 12.3(LUMAKRAS), ic50_src=ChEMBL 세포 기반 중앙값, 용량 [180.0, 360.0, 540.0, 720.0, 960.0]
  - sotorasib 회차 1: cl_f=26.2, t_half=5.0, tau=24.0, fu=0.11, ic50=30.0, mw=560.605, pk_src=FDA 라벨 12.3(LUMAKRAS), ic50_src=ChEMBL 세포 기반 중앙값, 용량 [180.0, 360.0, 540.0, 720.0, 960.0]
  - sotorasib 회차 2: cl_f=26.2, t_half=5.0, tau=24.0, fu=0.11, ic50=30.0, mw=560.605, pk_src=FDA 라벨 12.3(LUMAKRAS), ic50_src=ChEMBL 세포 기반 중앙값, 용량 [180.0, 360.0, 540.0, 720.0, 960.0]

## 실행별 상태

| kind | 실행 | 시도 번호 | 최종 인프라 실패 | 비고 |
|---|---|---|---|---|
| l1_oneshot | adagrasib_0 | 0 | False | parse_ok True |
| l1_oneshot | adagrasib_1 | 0 | False | parse_ok True |
| l1_oneshot | adagrasib_2 | 0 | False | parse_ok True |
| l1_oneshot | dv505_0 | 0 | False | parse_ok True |
| l1_oneshot | dv505_1 | 0 | False | parse_ok True |
| l1_oneshot | dv505_2 | 0 | False | parse_ok True |
| l1_oneshot | lorlatinib_0 | 0 | False | parse_ok True |
| l1_oneshot | lorlatinib_1 | 0 | False | parse_ok True |
| l1_oneshot | lorlatinib_2 | 0 | False | parse_ok True |
| l1_oneshot | sotorasib_0 | 0 | False | parse_ok True |
| l1_oneshot | sotorasib_1 | 0 | False | parse_ok True |
| l1_oneshot | sotorasib_2 | 0 | False | parse_ok True |
| l1_inputs | adagrasib_0 | 0 | False | parse_ok True |
| l1_inputs | adagrasib_1 | 0 | False | parse_ok True |
| l1_inputs | adagrasib_2 | 0 | False | parse_ok True |
| l1_inputs | dv505_0 | 0 | False | parse_ok True |
| l1_inputs | dv505_1 | 0 | False | parse_ok True |
| l1_inputs | dv505_2 | 0 | False | parse_ok True |
| l1_inputs | lorlatinib_0 | 0 | False | parse_ok True |
| l1_inputs | lorlatinib_1 | 0 | False | parse_ok True |
| l1_inputs | lorlatinib_2 | 0 | False | parse_ok True |
| l1_inputs | sotorasib_0 | 0 | False | parse_ok True |
| l1_inputs | sotorasib_1 | 0 | False | parse_ok True |
| l1_inputs | sotorasib_2 | 0 | False | parse_ok True |
| oneshot | adagrasib_0 | 0 | False | parse_ok True |
| oneshot | adagrasib_1 | 0 | False | parse_ok True |
| oneshot | adagrasib_2 | 0 | False | parse_ok True |
| oneshot | dv505_0 | 0 | False | parse_ok True |
| oneshot | dv505_1 | 0 | False | parse_ok True |
| oneshot | dv505_2 | 0 | False | parse_ok True |
| oneshot | lorlatinib_0 | 0 | False | parse_ok True |
| oneshot | lorlatinib_1 | 0 | False | parse_ok True |
| oneshot | lorlatinib_2 | 0 | False | parse_ok True |
| oneshot | sotorasib_0 | 0 | False | parse_ok True |
| oneshot | sotorasib_1 | 0 | False | parse_ok True |
| oneshot | sotorasib_2 | 0 | False | parse_ok True |
| agent | adagrasib_0 | 0 | False | terminal_status running, llm_failures 0 |
| agent | adagrasib_1 | 0 | False | terminal_status running, llm_failures 0 |
| agent | adagrasib_2 | 0 | False | terminal_status running, llm_failures 0 |
| agent | dv505_0 | 0 | False | terminal_status running, llm_failures 0 |
| agent | dv505_1 | 0 | False | terminal_status running, llm_failures 0 |
| agent | dv505_2 | 0 | False | terminal_status running, llm_failures 0 |
| agent | lorlatinib_0 | 0 | False | terminal_status running, llm_failures 0 |
| agent | lorlatinib_1 | 0 | False | terminal_status running, llm_failures 0 |
| agent | lorlatinib_2 | 0 | False | terminal_status running, llm_failures 0 |
| agent | sotorasib_0 | 0 | False | terminal_status running, llm_failures 0 |
| agent | sotorasib_1 | 0 | False | terminal_status running, llm_failures 0 |
| agent | sotorasib_2 | 0 | False | terminal_status running, llm_failures 0 |

## 비용(토큰)

| 팔 | 토큰 | 내역 |
|---|---|---|
| 원샷(L1·L2) | 104,928 | L1 원샷 42,945(+격리 0) + L2 원샷 61,983(+격리 0) |
| 원샷 입력 + 계산기(L1) | 28,800 | 입력 추출(+격리 0). L2 NLI 필터는 원샷 L2 출력 61,983을 공유(로컬 NLI, 토큰 0) |
| 에이전트 | 481,530(감사로그, 1차) | 상태 합 481,530 |

감사로그 교차 확인(저장소 `logs/*.jsonl`): L1 원샷 12건 42,945, 입력 추출 12건 28,800, 에이전트 48건 481,530(모델 gpt-6-sol). 원샷 모델 {'l1_oneshot': ['gpt-6-sol'], 'l1_inputs': ['gpt-6-sol'], 'oneshot': ['gpt-6-sol']}. L2 원샷은 run_eval.run_oneshot의 고정 purpose(`eval_oneshot`)라 감사로그에서 따로 가려낼 수 없어 상태 기록값만 쓴다.

## 해석 한계(사전 등록 요약)

- 일관성은 정확성이 아니다. 매번 같은 틀린 판정도 1.000이다.
- 계산기가 결정론적이라 '원샷 입력 + 계산기'와 에이전트의 L1 변동은 입력 선택에서만 온다. 가르는 것은 '입력을 어떤 규약으로 확보하는가'다.
- 에이전트 L1은 이미 관측됐고 도구 정답과 같은 계산 경로라 순환적이다. 시놉시스는 팀이 이미 본 문서다(블라인드 아님).
- 약 4종이라 어떤 비교도 α 0.05에 도달할 수 없다. 방향 일치 수와 효과 크기만 읽는다.
- 원샷 팔(planner 역할 모델, effort medium)과 에이전트(노드별 모델)는 모델·샘플링이 다르다. 차이에는 모델 차이가 섞인다.
- '원샷 입력 + 계산기'의 지시문은 기억·추정을 권장한다(사후 A′과 같은 취지). '프로토콜 값만, 없으면 null'로 지시하면 결과가 뒤집힐 수 있다.
