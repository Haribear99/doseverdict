# 평가 축③ — 라벨 PK만으로 용량 최적화 PMR 부과 여부 순위 재현 (n=30, 양성 7)

AUROC 0.658 · PR-AUC 0.477 (무작위 기준선 0.233) · 상위 8 중 양성 2/8 · 계산 모듈 제거(상수 점수) AUROC 0.500

| 순위 | 성분 | 승인 | 점수 | 근거 | PMR 정답 |
|---|---|---|---|---|---|
| 1 | sotorasib | 2021 | 4.5 | E-R unknown, nonlinear/saturable PK, t½≤8h | ✅ 부과 |
| 2 | selpercatinib | 2020 | 4.0 | E-R unknown, nonlinear/saturable PK | — |
| 3 | adagrasib | 2022 | 2.5 | E-R unknown, PB≥97% | ✅ 부과 |
| 4 | pacritinib | 2022 | 2.5 | nonlinear/saturable PK, PB≥97% | — |
| 5 | pralsetinib | 2020 | 2.5 | E-R unknown, PB≥97% | — |
| 6 | tucatinib | 2020 | 2.5 | E-R unknown, PB≥97% | — |
| 7 | vorasidenib | 2024 | 2.5 | E-R unknown, PB≥97% | — |
| 8 | brigatinib | 2017 | 2.0 | E-R unknown | — |
| 9 | ceritinib | 2014 | 2.0 | nonlinear/saturable PK | ✅ 부과 |
| 10 | crizotinib | 2011 | 2.0 | nonlinear/saturable PK | — |
| 11 | everolimus | 2009 | 2.0 | nonlinear/saturable PK | — |
| 12 | idelalisib | 2014 | 2.0 | nonlinear/saturable PK | ✅ 부과 |
| 13 | inavolisib | 2024 | 2.0 | E-R unknown | ✅ 부과 |
| 14 | lazertinib | 2024 | 2.0 | E-R unknown | — |
| 15 | repotrectinib | 2023 | 2.0 | E-R unknown | — |
| 16 | zongertinib | 2025 | 2.0 | E-R unknown | — |
| 17 | ruxolitinib | 2011 | 1.0 | PB≥97%, t½≤8h | — |
| 18 | avapritinib | 2020 | 0.5 | PB≥97% | — |
| 19 | erdafitinib | 2019 | 0.5 | PB≥97% | — |
| 20 | futibatinib | 2022 | 0.5 | t½≤8h | ✅ 부과 |
| 21 | ibrutinib | 2013 | 0.5 | t½≤8h | — |
| 22 | lenvatinib | 2015 | 0.5 | PB≥97% | ✅ 부과 |
| 23 | nilotinib | 2007 | 0.5 | PB≥97% | — |
| 24 | glasdegib | 2018 | 0.0 | - | — |
| 25 | osimertinib | 2015 | 0.0 | - | — |
| 26 | palbociclib | 2015 | 0.0 | - | — |
| 27 | pemigatinib | 2020 | 0.0 | - | — |
| 28 | pirtobrutinib | 2023 | 0.0 | - | — |
| 29 | tovorafenib | 2024 | 0.0 | - | — |
| 30 | vandetanib | 2011 | 0.0 | - | — |

한계: 점수 규칙은 본 프로젝트가 정한 잠정 기준이며 학습하지 않았다(정답을 본 뒤 조정하지 않음). 라벨 PK 정규식 추출 실패 성분은 제외됐고, gefitinib(2003 원문 미확보)·비종양 적응증(remibrutinib, tofacitinib)은 제외했다. 2010년 이전 승인약은 Project Optimus 이전이라 정답 자체의 시대 편향이 있다.
