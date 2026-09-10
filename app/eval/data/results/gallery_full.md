# 실패 사례 갤러리 — full

놓친 결함과 잘못 경고한 사례를 그대로 공개한다(제안서 4장 약속).
합계: 주입 결함 18건 중 놓침 2건, finding 32건 중 무관 13건.

## AX1-001 — finding 11건, 주입 결함 6건, 토큰 62,710

| 결과 | 주입 결함(요약) | 원 규범 문서 | 매칭 finding |
|---|---|---|---|
| ❌ 놓침 | The study team will review emerging adverse-event data periodically and decide during the trial whether enroll | FDA-DOSE-OPT-2024 · C Safety and Tolerability | - |
| 🟡 span만 적중 | All participants will receive the fixed 200 mg dose supplied in a single capsule strength throughout the study | FDA-DOSE-OPT-2024 · D Drug Formulation | F01 |
| 🟡 span만 적중 | The formulation-bridging expansion cohort will enroll participants receiving the new tablet or legacy capsule, | FDA-EXPANSION-COHORTS-2022 · F Evaluating Drug Product Chan | F03 |
| 🟡 span만 적중 | After the recommended Phase 2 dose is selected from tolerability data, all subsequent participants will receiv | ICH-E4-1994 · II OBTAINING DOSE-RESPONSE INF | F02 |
| ✅ 근거까지 적중 | Patients with moderate hepatic impairment and the CYP2C19 poor-metabolizer genotype will be enrolled in the sa | FDA-DOSE-OPT-2024 · A Clinical Pharmacokinetics, P | F04 |
| 🟡 span만 적중 | Dose–response analyses will be conducted only in the overall enrolled population, with no evaluations by age,  | ICH-E4-1994 · IV GUIDANCE AND ADVICE | F05 |

주입 결함과 무관한 finding(정상판 기준 잘못 경고 후보, 사람 검토 필요):
- F06 [high/held] The dose-escalation description gives the BOIN target, maximum enrollment, dose levels, and a reference to simulations but does not state co
- F07 [high/verified] The protocol specifies at least 60 randomized participants but provides no sample-size justification or prespecified endpoint and analysis c
- F08 [medium/held] The protocol identifies DV-101 as an irreversible covalent KRAS G12C inhibitor and supplies a structure but gives no biochemical or cellular
- F09 [medium/verified] The protocol refers to integrated RP2D criteria in Appendix D but does not state those criteria in the provided text. 임상시험 용량 선정 시 약동학, 약력학,
- F10 [medium/verified] The protocol specifies baseline, every-three-week, and monthly liver testing but does not expressly state that testing will become more freq

## AX1-002 — finding 10건, 주입 결함 6건, 토큰 66,509

| 결과 | 주입 결함(요약) | 원 규범 문서 | 매칭 finding |
|---|---|---|---|
| 🟡 span만 적중 | Results from the expansion cohort will serve as the primary efficacy package for the planned marketing applica | FDA-EXPANSION-COHORTS-2022 · C Communications and Interacti | F07 |
| 🟡 span만 적중 | The recommended Phase 2 dose will be the highest dose at which no more than 30% of participants permanently di | ICH-E4-1994 · II OBTAINING DOSE-RESPONSE INF | F00, F04 |
| ✅ 근거까지 적중 | Patients with moderate hepatic impairment and the CYP2C19 poor-metabolizer genotype will be enrolled in the sa | FDA-DOSE-OPT-2024 · A Clinical Pharmacokinetics, P | F05 |
| 🟡 span만 적중 | The sponsor will issue a single cumulative safety update to investigators and the IRB at the end of each calen | FDA-EXPANSION-COHORTS-2022 · C IRB/Independent Ethics Commi | F01 |
| 🟡 span만 적중 | The combination expansion cohort will open after the first six participants complete cycle 1 of the investigat | FDA-EXPANSION-COHORTS-2022 · G Evaluating More Than One The | F03 |
| 🟡 span만 적중 | The expansion cohort will support the marketing application using investigator-assessed tumor responses at the | FDA-EXPANSION-COHORTS-2022 · B Evaluating Preliminary Antit | F02 |

주입 결함과 무관한 finding(정상판 기준 잘못 경고 후보, 사람 검토 필요):
- F06 [high/verified] The protocol limits randomized-cohort PK collection to steady-state trough samples obtained once per cycle. LUMAKRAS has non-linear, time-de
- F08 [high/verified] The protocol specifies baseline, every-three-week, and monthly liver testing but does not specify more frequent testing after transaminase o
- F09 [medium/verified] The exclusion criteria specify a four-week washout for anti-PD-(L)1 therapy but state no washout periods for other systemic anticancer thera

## AX1-003 — finding 11건, 주입 결함 6건, 토큰 63,201

| 결과 | 주입 결함(요약) | 원 규범 문서 | 매칭 finding |
|---|---|---|---|
| 🟡 span만 적중 | The recommended Phase 2 dose will be the highest dose at which no more than 30% of participants permanently di | ICH-E4-1994 · II OBTAINING DOSE-RESPONSE INF | F00, F03 |
| 🟡 span만 적중 | After the safety lead-in, all participants will receive 240 mg twice daily; no alternate dose will be evaluate | FDA-DOSE-OPT-2024 · B Trial Designs to Compare Mul | F01 |
| 🟡 span만 적중 | The study team will review emerging adverse-event data periodically and decide during the trial whether enroll | FDA-DOSE-OPT-2024 · C Safety and Tolerability | F04 |
| 🟡 span만 적중 | Concomitant medications will be recorded at enrollment, but no interaction studies or dedicated pharmacokineti | FDA-DOSE-OPT-2024 · A Clinical Pharmacokinetics, P | F07 |
| 🟡 span만 적중 | For the randomized Phase 2 portion, each of the three active-dose arms will be compared independently with pla | FDA-DOSE-OPT-2024 · B Trial Designs to Compare Mul | F02 |
| ❌ 놓침 | All recommendations in FDA-DOSE-OPT-2024 shall be implemented without deviation, and any investigator request  | FDA-DOSE-OPT-2024 · I INTRODUCTION | - |

주입 결함과 무관한 finding(정상판 기준 잘못 경고 후보, 사람 검토 필요):
- F05 [high/verified] The protocol limits randomized-cohort PK sampling to steady-state troughs and specifies dose-proportionality analysis but no population-PK o
- F06 [high/verified] The protocol assigns at least 60 participants equally to two candidate doses but does not provide a sample-size rationale, evaluability rule
- F08 [high/verified] The protocol refers hepatotoxicity, interstitial lung disease/pneumonitis, and other adverse-reaction management to Appendix B, whose rules 
- F09 [medium/verified] The protocol excludes anti-PD-(L)1 therapy within four weeks before the first dose but provides no risk-stratified liver-monitoring or other
- F10 [medium/verified] The protocol identifies DV-101 as sotorasib and supplies a SMILES and target statement but cites no authoritative identity record or compoun

