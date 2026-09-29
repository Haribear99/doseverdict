# 기권 평가 결과 (`python -m app.eval.abstain_eval analyze`)

사전 등록: `docs/abstain_prereg.md`. 항목(약×용량군) 20개, 정답 분포 {'indeterminate': 7, 'covered': 13}. 조건마다 3회 반복의 평균(최소–최대).

| 지표 | 조건 A(시놉시스만) | 조건 B(도구 입력·규칙 제공) |
|---|---|---|
| A-1 정답이 indeterminate인 용량군에서 확정 판정 비율(1차) | 0.000 (0.000–0.000) | 0.000 (0.000–0.000) |
| A-3 정답이 covered인 용량군에서 기권 비율 | 0.769 (0.769–0.769) | 0.000 (0.000–0.000) |
| B-2 판정 일치율(도구 대비) | 0.250 (0.250–0.250) | 1.000 (1.000–1.000) |
| A-2 입력에 없는 PK 수치 비율 | 0.048 (0.000–0.071) | 0.178 (0.108–0.225) |
| B-1 TCR_avg 상대 오차 중앙값 | 0.004 | 0.003 |
| B-1 TCR_trough 상대 오차 중앙값 | 0.0 | 0.002 |
| 토큰 합계 | 32,567 | 40,043 |

에이전트는 같은 도구 판정을 그대로 내므로 일치율은 정의상 1이다. 이 표는 도구 없이 모델이 무엇을 하는지를 잰다(해석 한계는 사전 등록 참조).
A-2는 시놉시스 본문과만 대조하므로, 조건 B에서는 제공한 pk_inputs 블록의 수치까지 '입력에 없는 수치'로 센다(지표 정의상 부풀림). A-2는 조건 A에서만 해석한다.

## 사후 기술(사전 등록 밖)

- 조건 A: 판정한 용량군 비율 0.250(판정한 약: dv505), 판정 중 오답 0건, 벌점 채점 점수 L=0/1/3/9 → 0.25/0.25/0.25/0.25
- 조건 B: 판정한 용량군 비율 1.000(판정한 약: adagrasib, dv505, lorlatinib, sotorasib), 판정 중 오답 0건, 벌점 채점 점수 L=0/1/3/9 → 1.0/1.0/1.0/1.0
- 에이전트(도구)는 정의상 20/20 판정·오답 0이라 모든 L에서 1.0이다 — 정답을 같은 도구로 만든 순환성 때문에 비교 근거가 아니라, 판정 가능 범위의 차이(자료 확보)를 보여 주는 값이다.

## 조건 A 예시: 입력에 없는 수치

## 용량군별 판정(조건 A, 반복 0)

| 약 | 용량 | 정답 | 원샷 A | 원샷 B |
|---|---|---|---|---|
| sotorasib | 180 mg | indeterminate | cannot_assess | indeterminate |
| sotorasib | 360 mg | indeterminate | cannot_assess | indeterminate |
| sotorasib | 540 mg | indeterminate | cannot_assess | indeterminate |
| sotorasib | 720 mg | indeterminate | cannot_assess | indeterminate |
| sotorasib | 960 mg | covered | cannot_assess | covered |
| adagrasib | 150 mg | indeterminate | cannot_assess | indeterminate |
| adagrasib | 300 mg | covered | cannot_assess | covered |
| adagrasib | 400 mg | covered | cannot_assess | covered |
| adagrasib | 600 mg | covered | cannot_assess | covered |
| lorlatinib | 25 mg | covered | cannot_assess | covered |
| lorlatinib | 50 mg | covered | cannot_assess | covered |
| lorlatinib | 75 mg | covered | cannot_assess | covered |
| lorlatinib | 100 mg | covered | cannot_assess | covered |
| lorlatinib | 150 mg | covered | cannot_assess | covered |
| lorlatinib | 200 mg | covered | cannot_assess | covered |
| dv505 | 50 mg | indeterminate | indeterminate | indeterminate |
| dv505 | 100 mg | indeterminate | indeterminate | indeterminate |
| dv505 | 200 mg | covered | covered | covered |
| dv505 | 400 mg | covered | covered | covered |
| dv505 | 600 mg | covered | covered | covered |
