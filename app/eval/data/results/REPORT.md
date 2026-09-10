# 평가 결과 (축① 규범 유도 결함 주입 Silver Set)

지표 정의: span recall = 주입 문장을 finding이 가리킴(어휘). grounded recall = 그 finding이 정답 규범 문서를 인용했거나 근거 사실이 원문과 겹침. 가중 = critical 4·high 3·medium 2·low 1. precision proxy = 적중 finding / 전체 finding(정상판에 대한 지적은 '무관'으로 세므로 하한). 95% CI는 케이스 단위 부트스트랩(2,000회).

| 설정 | n | span recall [CI] | 가중 span | grounded recall [CI] | 가중 grounded | precision | 검증 통과율 | 토큰/케이스 | 초/케이스 |
|---|---|---|---|---|---|---|---|---|---|
| checklist | 20 | 0.791 [0.69, 0.87] | 0.772 | 0.000 [0.00, -0.00] | 0.000 | 0.747 | 0.000 | 0 | 0 |
| full | 3 | 0.889 [0.83, 1.00] | 0.889 | 0.389 [0.17, 0.67] | 0.389 | 0.503 | 0.879 | 64,140 | 204 |

## Ablation 기여도 (full 대비 grounded weighted recall 차이)

| 제거한 구성요소 | 설정 | Δ grounded w-recall | Δ 검증 통과율 | Δ 토큰 |
|---|---|---|---|---|

해석 규칙(제안서 4장): 전체 시스템이 정규식 체크리스트 대비 grounded recall에서 15%p 이상 앞서지 못하면 멀티에이전트가 불필요하다고 보고한다.
→ full − checklist (grounded recall) = +0.389 (기준 충족).
