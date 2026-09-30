# 특이도 평가 결과 (`python -m app.eval.specificity report`)

사전 등록: `docs/specificity_prereg.md`. 기준 문장 = 결함 없음으로 가정(특이도는 하한).

## A. 문장 단위 민감도·특이도(기존 저장 상태)

| 실행 | n | 민감도 [95% CI] | 특이도 [95% CI] | Youden J [95% CI] | 판정 |
|---|---|---|---|---|---|
| lean_v3 | 20 | 0.950 [0.908, 0.983] | 0.812 [0.779, 0.845] | 0.762 [0.704, 0.815] | 주입 문장을 골라 짚는다 |
| lean_v3b | 20 | 0.975 [0.95, 1.0] | 0.786 [0.714, 0.85] | 0.761 [0.675, 0.836] | 주입 문장을 골라 짚는다 |
| lean_mdrug3 | 30 | 0.933 [0.889, 0.972] | 0.737 [0.704, 0.77] | 0.670 [0.609, 0.727] | 주입 문장을 골라 짚는다 |

여러 케이스에서 반복 지적된 기준 문장(실제 결함 후보이거나 체계적 오경보 — 사람 확인용):

- [sotorasib_synopsis_fixed.md] 33케이스: "Intensive PK sampling on Cycle 1 Day 1 and Day 15 (pre-dose, 0.5, 1, 2, 4, 6, 8 and 24 h post-dose) in all escalation subjects; steady-state trough sampling every cycle in the randomized cohorts."
- [sotorasib_synopsis_fixed.md] 27케이스: "At least 60 subjects will be randomized 1:1 to the two candidate dose levels to compare safety, tolerability, PK, PD and preliminary antitumor activity before selecting the RP2D."
- [sotorasib_synopsis_fixed.md] 17케이스: "Dose proportionality will be assessed by a power model."
- [sotorasib_synopsis_fixed.md] 17케이스: "Exclusion: active brain metastases; prior treatment with a KRAS G12C inhibitor;"
- [sotorasib_synopsis_fixed.md] 17케이스: "QTcF >470 ms; anti-PD-(L)1 therapy within 4 weeks prior to the first dose."
- [adagrasib_synopsis_fixed.md] 10케이스: "Liver function tests (ALT, AST, total bilirubin) will be assessed before the first dose and monthly for 3 months and as clinically indicated thereafter."
- [adagrasib_synopsis_fixed.md] 9케이스: "Intensive PK sampling on Cycle 1 Day 1 and Day 8 (pre-dose, 1, 2, 4, 6, 8 and 12 h post-dose) in all escalation subjects; steady-state trough sampling every cycle in the randomized cohorts."
- [lorlatinib_synopsis_fixed.md] 9케이스: "Serum cholesterol and triglycerides will be assessed before the first dose, at 1, 2, 4 and 8 weeks, and periodically thereafter."
- [dv505_synopsis_fixed.md] 9케이스: "At least 60 subjects will be randomized 1:1 to the two candidate dose levels to compare safety, tolerability, PK, PD and preliminary antitumor activity before selecting the RP2D."
- [sotorasib_synopsis_fixed.md] 8케이스: "DV-101 (sotorasib) is an oral, irreversible, covalent KRAS G12C inhibitor."
- [sotorasib_synopsis_fixed.md] 8케이스: "SMILES: C=CC(=O)N1CCN(c2nc(=O)n(-c3c(C)ccnc3C(C)C)c3nc(-c4c(O)cccc4F)c(F)cc23)[C@@H](C)C1."
- [lorlatinib_synopsis_fixed.md] 8케이스: "Central nervous system effects (cognitive, mood, speech and psychotic effects) will be assessed at each visit."

## B. 결함 없는 기준 시놉시스 실행(음성 대조)

12회 중 12회 완료. 특이도 0.64, 실행당 지적된 기준 문장 8.0, defect finding 6.42, 토큰 466,603.

| 실행 | 기준 문장 | 지적된 기준 문장 | defect finding |
|---|---|---|---|
| adagrasib_synopsis_fixed_0 | 22 | 7 | 6 |
| adagrasib_synopsis_fixed_1 | 22 | 6 | 6 |
| adagrasib_synopsis_fixed_2 | 22 | 11 | 8 |
| dv505_synopsis_fixed_0 | 23 | 6 | 5 |
| dv505_synopsis_fixed_1 | 23 | 11 | 8 |
| dv505_synopsis_fixed_2 | 23 | 5 | 4 |
| lorlatinib_synopsis_fixed_0 | 23 | 10 | 8 |
| lorlatinib_synopsis_fixed_1 | 23 | 6 | 6 |
| lorlatinib_synopsis_fixed_2 | 23 | 11 | 8 |
| sotorasib_synopsis_fixed_0 | 21 | 6 | 5 |
| sotorasib_synopsis_fixed_1 | 21 | 11 | 8 |
| sotorasib_synopsis_fixed_2 | 21 | 6 | 5 |

## C. 수정안 적용 후 재검토

14케이스, 수정안 30건. 수정된 문장 재지적률 0.2(1차). defect finding 8.36 → 7.14(케이스 평균). 수정하지 않은 주입 문장의 지적 49 → 53건. 토큰 551,572.
