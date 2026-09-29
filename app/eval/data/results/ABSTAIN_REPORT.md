# 기권 평가 결과 (`python -m app.eval.abstain_eval analyze`)

사전 등록: `docs/abstain_prereg.md`. 항목(약×용량군) 20개, 정답 분포 {'indeterminate': 7, 'covered': 13}. 조건마다 3회 반복의 평균(최소–최대).

| 지표 | 조건 A(시놉시스만) | 조건 B(도구 입력·규칙 제공) | 사후 A′(시놉시스만 + 기억·추정 사용 권장) |
|---|---|---|---|
| A-1 정답이 indeterminate인 용량군에서 확정 판정 비율(1차) | 0.000 (0.000–0.000) | 0.000 (0.000–0.000) | 0.381 (0.143–0.714) |
| A-3 정답이 covered인 용량군에서 기권 비율 | 0.769 (0.769–0.769) | 0.000 (0.000–0.000) | 0.231 (0.077–0.385) |
| B-2 판정 일치율(도구 대비) | 0.250 (0.250–0.250) | 1.000 (1.000–1.000) | 0.717 (0.500–0.850) |
| A-2 입력에 없는 수치 비율 | 0.048 (0.000–0.071) | 0.178 (0.108–0.225) | 0.336 (0.304–0.356) |
| B-1 TCR_avg 상대 오차 중앙값 | 0.004 | 0.003 | 0.51 |
| B-1 TCR_trough 상대 오차 중앙값 | 0.0 | 0.002 | 0.544 |
| 토큰 합계 | 32,567 | 40,043 | 44,240 |

에이전트는 같은 도구 판정을 그대로 내므로 일치율은 정의상 1이다. 이 표는 도구 없이 모델이 무엇을 하는지를 잰다(해석 한계는 사전 등록 참조).
A-2는 시놉시스 본문과만 대조하므로, 조건 B에서는 제공한 pk_inputs 블록의 수치까지 '입력에 없는 수치'로 센다(지표 정의상 부풀림). A-2는 조건 A에서만 해석한다.

## 사후 기술(사전 등록 밖)

- 조건 A: 판정한 용량군 비율 0.250(판정한 약: dv505), 판정 15건 중 도구 판정과 불일치 0건, 반복 3회 판정 일관성 1.000(PK가 라벨에만 있는 약 3종만 1.000)
- 조건 B: 판정한 용량군 비율 1.000(판정한 약: adagrasib, dv505, lorlatinib, sotorasib), 판정 60건 중 도구 판정과 불일치 0건, 반복 3회 판정 일관성 1.000(PK가 라벨에만 있는 약 3종만 1.000)
- 사후 A′(기억·추정 권장): 판정한 용량군 비율 1.000(판정한 약: adagrasib, dv505, lorlatinib, sotorasib), 판정 60건 중 도구 판정과 불일치 17건, 반복 3회 판정 일관성 0.450(PK가 라벨에만 있는 약 3종만 0.267)
- 사후 A′ 도구 판정과 불일치 분해: 정답 covered → 모델 indeterminate 9건, 정답 indeterminate → 모델 covered 6건, 정답 indeterminate → 모델 not_covered 2건
- 사후 A′ 회차별 IC50(모델이 고른 값, 대부분 source=assumption): sotorasib 30 nM / 6 nM / 0.09 µM; adagrasib 10 nM / 50 nM / 25 nM; lorlatinib 30 / 80 nM / 10 — 기억한 라벨 PK(예: 소토라십 Cmax 7.50 µg/mL)는 회차 간 거의 같았고, 판정 흔들림의 주원인은 IC50과 용량 외삽 가정의 재선택이다.
- 반복 일관성 1.000은 조건 A(전부 판단 불가)·B(입력·규칙 제공)에서는 자명한 값이다.
- 벌점 채점(Kalai 등 Nature 2026의 open rubric)은 적용하지 않았다. 그 방식은 벌점을 프롬프트에 고지해야 하는데 이번 프롬프트는 고지하지 않았다.

## 조건 A 예시: 입력에 없는 수치(분자량 등 유도 수치이며 PK 값이 아니다)
- dv505 반복 1: Unbound fraction calculated from binding=0.06 (assumption); Atomic masses used for molecular-mass calculation=C 12.011, H 1.008, F 18.998, N 14.007, O 15.999 g/mol (prior_knowledge)
- dv505 반복 2: Atomic weights used for molecular-weight calculation=C 12.011; H 1.008; F 18.998; N 14.007; O 15.999 g/mol (prior_knowledge); Calculated molecular weight=501.57 g/mol (prior_knowledge)

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
