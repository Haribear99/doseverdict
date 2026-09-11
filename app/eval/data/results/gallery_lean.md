# 실패 사례 갤러리 — lean

놓친 결함과 잘못 경고한 사례를 그대로 공개한다(제안서 4장 약속).
합계: 주입 결함 120건 중 놓침 6건, finding 200건 중 무관 64건.

## AX1-001 — finding 11건, 주입 결함 6건, 토큰 42,440

| 결과 | 주입 결함(요약) | 원 규범 문서 | 매칭 finding |
|---|---|---|---|
| 🟡 span만 적중 | The study team will review emerging adverse-event data periodically and decide during the trial whether enroll | FDA-DOSE-OPT-2024 · C Safety and Tolerability | F05 |
| 🟡 span만 적중 | All participants will receive the fixed 200 mg dose supplied in a single capsule strength throughout the study | FDA-DOSE-OPT-2024 · D Drug Formulation | F01 |
| 🟡 span만 적중 | The formulation-bridging expansion cohort will enroll participants receiving the new tablet or legacy capsule, | FDA-EXPANSION-COHORTS-2022 · F Evaluating Drug Product Chan | F03 |
| 🟡 span만 적중 | After the recommended Phase 2 dose is selected from tolerability data, all subsequent participants will receiv | ICH-E4-1994 · II OBTAINING DOSE-RESPONSE INF | F02 |
| ✅ 근거까지 적중 | Patients with moderate hepatic impairment and the CYP2C19 poor-metabolizer genotype will be enrolled in the sa | FDA-DOSE-OPT-2024 · A Clinical Pharmacokinetics, P | F04 |
| 🟡 span만 적중 | Dose–response analyses will be conducted only in the overall enrolled population, with no evaluations by age,  | ICH-E4-1994 · IV GUIDANCE AND ADVICE | F08 |

주입 결함과 무관한 finding(정상판 기준 잘못 경고 후보, 사람 검토 필요):
- F06 [high/verified] The listed exclusion criteria specify a four-week interval only for anti-PD-(L)1 therapy and do not state washout intervals for other prior 
- F07 [medium/verified] The protocol specifies a power-model assessment of dose proportionality but provides no allocation, variability, precision, model-interval, 
- F09 [medium/verified] The protocol excludes anti-PD-(L)1 therapy within four weeks before the first dose without stating a risk-based rationale or enhanced monito
- F10 [low/verified] The protocol specifies baseline liver testing, testing every three weeks for the first three months, and monthly testing thereafter or as cl

## AX1-002 — finding 9건, 주입 결함 6건, 토큰 44,078

| 결과 | 주입 결함(요약) | 원 규범 문서 | 매칭 finding |
|---|---|---|---|
| 🟡 span만 적중 | Results from the expansion cohort will serve as the primary efficacy package for the planned marketing applica | FDA-EXPANSION-COHORTS-2022 · C Communications and Interacti | F05 |
| 🟡 span만 적중 | The recommended Phase 2 dose will be the highest dose at which no more than 30% of participants permanently di | ICH-E4-1994 · II OBTAINING DOSE-RESPONSE INF | F00, F04 |
| 🟡 span만 적중 | Patients with moderate hepatic impairment and the CYP2C19 poor-metabolizer genotype will be enrolled in the sa | FDA-DOSE-OPT-2024 · A Clinical Pharmacokinetics, P | F06 |
| 🟡 span만 적중 | The sponsor will issue a single cumulative safety update to investigators and the IRB at the end of each calen | FDA-EXPANSION-COHORTS-2022 · C IRB/Independent Ethics Commi | F01 |
| 🟡 span만 적중 | The combination expansion cohort will open after the first six participants complete cycle 1 of the investigat | FDA-EXPANSION-COHORTS-2022 · G Evaluating More Than One The | F03 |
| 🟡 span만 적중 | The expansion cohort will support the marketing application using investigator-assessed tumor responses at the | FDA-EXPANSION-COHORTS-2022 · B Evaluating Preliminary Antit | F02 |

주입 결함과 무관한 finding(정상판 기준 잘못 경고 후보, 사람 검토 필요):
- F07 [high/verified] The randomized candidate-dose cohorts have only steady-state trough sampling, and the stated analysis is limited to dose proportionality by 
- F08 [high/verified] The protocol assigns at least 60 participants equally between two candidate doses without stating the assumptions or operating characteristi

## AX1-003 — finding 10건, 주입 결함 6건, 토큰 44,910

| 결과 | 주입 결함(요약) | 원 규범 문서 | 매칭 finding |
|---|---|---|---|
| 🟡 span만 적중 | The recommended Phase 2 dose will be the highest dose at which no more than 30% of participants permanently di | ICH-E4-1994 · II OBTAINING DOSE-RESPONSE INF | F00, F03 |
| 🟡 span만 적중 | After the safety lead-in, all participants will receive 240 mg twice daily; no alternate dose will be evaluate | FDA-DOSE-OPT-2024 · B Trial Designs to Compare Mul | F01 |
| 🟡 span만 적중 | The study team will review emerging adverse-event data periodically and decide during the trial whether enroll | FDA-DOSE-OPT-2024 · C Safety and Tolerability | F04 |
| ❌ 놓침 | Concomitant medications will be recorded at enrollment, but no interaction studies or dedicated pharmacokineti | FDA-DOSE-OPT-2024 · A Clinical Pharmacokinetics, P | - |
| 🟡 span만 적중 | For the randomized Phase 2 portion, each of the three active-dose arms will be compared independently with pla | FDA-DOSE-OPT-2024 · B Trial Designs to Compare Mul | F02 |
| ❌ 놓침 | All recommendations in FDA-DOSE-OPT-2024 shall be implemented without deviation, and any investigator request  | FDA-DOSE-OPT-2024 · I INTRODUCTION | - |

주입 결함과 무관한 finding(정상판 기준 잘못 경고 후보, 사람 검토 필요):
- F05 [high/held] The protocol defers the prespecified integrated RP2D-selection criteria to Appendix D and excludes selection based solely on maximum tolerat
- F06 [high/verified] The protocol plans to randomize at least 60 participants equally between two candidate doses but provides no sample-size assumptions or clin
- F07 [high/verified] The protocol limits randomized-cohort PK collection to steady-state trough samples while reserving intensive first-dose and Day 15 sampling 
- F08 [high/verified] The protocol enrolls a single cohort spanning locally advanced or metastatic KRAS G12C-mutated solid tumors without identifying tumor-specif
- F09 [medium/verified] The protocol identifies DV-101 as an irreversible covalent KRAS G12C inhibitor and supplies its chemical structure but gives no compound-spe

## AX1-004 — finding 10건, 주입 결함 6건, 토큰 43,715

| 결과 | 주입 결함(요약) | 원 규범 문서 | 매칭 finding |
|---|---|---|---|
| 🟡 span만 적중 | The dose-escalation and expansion cohorts will follow the same general treatment plan, with cohort-specific do | FDA-EXPANSION-COHORTS-2022 · A Initial Protocol | F06 |
| 🟡 span만 적중 | The randomized Phase 2 portion will compare three active dose levels with placebo, and each dose-versus-placeb | MFDS-1443-01-2025 · 3.2 다양한 용량을 비교하기 위한 임상시험 설계 | F02 |
| 🟡 span만 적중 | Participants will be enrolled sequentially into nonrandomized cohorts receiving 10, 30, or 60 mg once daily, w | FDA-DOSE-OPT-2024 · B Trial Designs to Compare Mul | F05 |
| 🟡 span만 적중 | All doses will be prepared as a fixed 0.5 mg/mL intravenous solution, including doses requiring infusion volum | FDA-DOSE-OPT-2024 · D Drug Formulation | F01 |
| 🟡 span만 적중 | 확장 코호트에서는 선행 임상자료나 노출·반응 분석과 무관하게 모든 환자에게 임상적으로 사용되는 표준 용량 200 mg을 투여한다. | MFDS-1443-01-2025 · 1 안내서-1443-01 2025. 8. 29. 제정 | F03 |
| 🟡 span만 적중 | Dose selection for expansion will be based solely on observed tumor response rates, without adjustment for tre | ICH-E4-1994 · IV GUIDANCE AND ADVICE | F04 |

주입 결함과 무관한 finding(정상판 기준 잘못 경고 후보, 사람 검토 필요):
- F07 [high/verified] The protocol specifies at least 60 subjects randomized 1:1 between two candidate doses but gives no cohort rationale, sample-size basis, or 
- F08 [medium/verified] The protocol limits randomized-cohort PK collection to steady-state trough samples while proposing a power model for dose proportionality. T
- F09 [high/verified] The protocol excludes anti-PD-(L)1 therapy within four weeks before first dose but states no timing criteria for other prior anticancer ther

## AX1-005 — finding 11건, 주입 결함 6건, 토큰 41,720

| 결과 | 주입 결함(요약) | 원 규범 문서 | 매칭 finding |
|---|---|---|---|
| 🟡 span만 적중 | The study team will review emerging adverse-event data periodically and decide during the trial whether enroll | FDA-DOSE-OPT-2024 · C Safety and Tolerability | F05 |
| 🟡 span만 적중 | In the pediatric expansion cohort, safety will be assessed only by recording adverse events at scheduled clini | FDA-EXPANSION-COHORTS-2022 · H Evaluating PK, Tolerability, | F03 |
| ✅ 근거까지 적중 | This amendment adds a higher-dose expansion cohort based on preliminary efficacy findings; the safety rational | FDA-EXPANSION-COHORTS-2022 · A Safety Monitoring and Report | F02 |
| 🟡 span만 적중 | The expansion cohort will support the marketing application using investigator-assessed tumor responses at the | FDA-EXPANSION-COHORTS-2022 · B Evaluating Preliminary Antit | F04 |
| 🟡 span만 적중 | No pharmacodynamic or pharmacogenomic specimens will be collected, and the study will not evaluate genetic det | FDA-DOSE-OPT-2024 · A Clinical Pharmacokinetics, P | F07 |
| 🟡 span만 적중 | The study will be conducted under the sponsor's internal approval without submission of the final protocol to  | ICH-E4-1994 · 0 PREAMBLE | F01 |

주입 결함과 무관한 finding(정상판 기준 잘못 경고 후보, 사람 검토 필요):
- F06 [high/verified] The randomized dose-comparison sentence specifies at least 60 subjects but provides no exposure–response estimands, models, decision thresho
- F08 [low/verified] The liver-testing schedule matches baseline, every-three-week, and monthly testing intervals but does not expressly specify more frequent te
- F09 [medium/verified] The investigational-product description identifies sotorasib as an irreversible covalent inhibitor but provides no nonclinical selectivity, 
- F10 [medium/verified] The eligibility criteria exclude anti-PD-(L)1 therapy within four weeks before the first dose but state no rationale for that interval or pu

## AX1-006 — finding 9건, 주입 결함 6건, 토큰 46,157

| 결과 | 주입 결함(요약) | 원 규범 문서 | 매칭 finding |
|---|---|---|---|
| 🟡 span만 적중 | The recommended Phase 2 dose will be the highest dose tested with acceptable early laboratory findings, even i | FDA-DOSE-OPT-2024 · II BACKGROUND | F01 |
| 🟡 span만 적중 | The sponsor will compile aggregate safety data internally and submit cumulative reports to FDA at its discreti | FDA-EXPANSION-COHORTS-2022 · A Safety Monitoring and Report | F03 |
| 🟡 span만 적중 | The study will enroll adults with untreated low-risk indolent lymphoma for whom standard curative therapy is a | FDA-EXPANSION-COHORTS-2022 · IV DRUG PRODUCT AND SUBJECT CO | F04 |
| 🟡 span만 적중 | Participants who cross over to the alternate dose will be included in the overall safety and response analyses | FDA-DOSE-OPT-2024 · B Trial Designs to Compare Mul | F06 |
| 🟡 span만 적중 | The Phase 2 expansion dose will be fixed at 200 mg twice daily based solely on the recommended Phase 1 dose, w | FDA-DOSE-OPT-2024 · III DOSAGE OPTIMIZATION RECOMM | F02 |
| 🟡 span만 적중 | Results from the expansion cohort will serve as the primary efficacy package for the planned marketing applica | FDA-EXPANSION-COHORTS-2022 · C Communications and Interacti | F05 |

주입 결함과 무관한 finding(정상판 기준 잘못 경고 후보, 사람 검토 필요):
- F07 [high/verified] The protocol uses intensive first-dose and steady-state PK sampling in escalation but collects only steady-state trough samples in the rando
- F08 [medium/held] The protocol identifies DV-101 as an irreversible covalent KRAS G12C inhibitor and provides its structure but gives no covalent-warhead sele

## AX1-007 — finding 8건, 주입 결함 6건, 토큰 45,582

| 결과 | 주입 결함(요약) | 원 규범 문서 | 매칭 finding |
|---|---|---|---|
| 🟡 span만 적중 | For the new pembrolizumab–investigational-agent combination in metastatic colorectal cancer, the study will pr | MFDS-1443-01-2025 · 3.5 후속 적응증 및 용법 | F03 |
| 🟡 span만 적중 | 확장 코호트에서는 선행 임상자료나 노출·반응 분석과 무관하게 모든 환자에게 임상적으로 사용되는 표준 용량 200 mg을 투여한다. | MFDS-1443-01-2025 · 1 안내서-1443-01 2025. 8. 29. 제정 | F05 |
| 🟡 span만 적중 | Interim safety and efficacy findings will be reviewed only after database lock at the end of the expansion pha | FDA-EXPANSION-COHORTS-2022 · II BACKGROUND | F02 |
| 🟡 span만 적중 | The formulation-bridging expansion cohort will enroll participants receiving the new tablet or legacy capsule, | FDA-EXPANSION-COHORTS-2022 · F Evaluating Drug Product Chan | F07 |
| 🟡 span만 적중 | After the recommended Phase 2 dose is selected from tolerability data, all subsequent participants will receiv | ICH-E4-1994 · II OBTAINING DOSE-RESPONSE INF | F04 |
| 🟡 span만 적중 | The starting dose and subsequent escalation levels will be selected solely by investigator consensus, without  | FDA-DOSE-OPT-2024 · III DOSAGE OPTIMIZATION RECOMM | F01 |

주입 결함과 무관한 finding(정상판 기준 잘못 경고 후보, 사람 검토 필요):
- F06 [high/verified] The protocol limits randomized-cohort PK collection to steady-state trough samples and specifies a dose-proportionality power model but no e

## AX1-008 — finding 11건, 주입 결함 6건, 토큰 45,809

| 결과 | 주입 결함(요약) | 원 규범 문서 | 매칭 finding |
|---|---|---|---|
| 🟡 span만 적중 | After participants complete 48 hours at the assigned dose level, the dose-response analysis will be performed  | ICH-E4-1994 · 1 Parallel dose-response | F01 |
| 🟡 span만 적중 | Dose–response analyses will be conducted only in the overall enrolled population, with no evaluations by age,  | ICH-E4-1994 · IV GUIDANCE AND ADVICE | F05 |
| 🟡 span만 적중 | The study will select the recommended Phase 2 dose from the first expansion cohort without collecting dose–res | ICH-E4-1994 · IV GUIDANCE AND ADVICE | F03 |
| 🟡 span만 적중 | After completing the dose-escalation portion, the study will open six parallel disease-specific expansion coho | FDA-EXPANSION-COHORTS-2022 · IV DRUG PRODUCT AND SUBJECT CO | F02 |
| 🟡 span만 적중 | The sponsor will include serious and unexpected adverse safety findings in the next scheduled annual safety re | FDA-EXPANSION-COHORTS-2022 · B Potential Opportunities and  | F04 |
| 🟡 span만 적중 | Participants will be enrolled sequentially into nonrandomized cohorts receiving 10, 30, or 60 mg once daily, w | FDA-DOSE-OPT-2024 · B Trial Designs to Compare Mul | F08 |

주입 결함과 무관한 finding(정상판 기준 잘못 경고 후보, 사람 검토 필요):
- F06 [high/verified] The protocol limits randomized-cohort PK sampling to steady-state troughs while reserving first-dose and steady-state intensive sampling for
- F07 [high/verified] The protocol assigns at least 60 subjects equally between two candidate doses but gives no endpoint-specific basis for that sample size in t
- F09 [high/verified] The protocol specifies baseline, every-three-week, and monthly liver testing but does not explicitly specify intensified testing after trans
- F10 [low/verified] The protocol identifies DV-101 as sotorasib and an irreversible covalent KRAS G12C inhibitor and supplies a chemical structure as SMILES. Th

## AX1-009 — finding 9건, 주입 결함 6건, 토큰 45,168

| 결과 | 주입 결함(요약) | 원 규범 문서 | 매칭 finding |
|---|---|---|---|
| 🟡 span만 적중 | The sponsor will finalize the dose-comparison design and proceed directly to patient enrollment without seekin | MFDS-1443-01-2025 · 3.2 다양한 용량을 비교하기 위한 임상시험 설계 | F07 |
| 🟡 span만 적중 | After the sponsor transfers production to a new manufacturing site and changes the formulation, the study will | FDA-EXPANSION-COHORTS-2022 · F Evaluating Drug Product Chan | F02 |
| 🟡 span만 적중 | For every participant, the dose-escalation algorithm will identify that individual’s optimal dose from observe | ICH-E4-1994 · IV GUIDANCE AND ADVICE | F03 |
| 🟡 span만 적중 | Participants may take the study tablets with or without meals and may continue all clinically indicated concom | FDA-DOSE-OPT-2024 · A Clinical Pharmacokinetics, P | F04 |
| ❌ 놓침 | The medical monitor may be any licensed physician with general inpatient-care experience; prior oncology pract | FDA-EXPANSION-COHORTS-2022 · A Safety Monitoring and Report | - |
| 🟡 span만 적중 | The Phase 1 portion will escalate cohorts until the highest dose with an acceptable toxicity profile is identi | FDA-DOSE-OPT-2024 · II BACKGROUND | F01 |

주입 결함과 무관한 finding(정상판 기준 잘못 경고 후보, 사람 검토 필요):
- F05 [high/verified] The protocol specifies a 60-subject randomized dose comparison but this sentence does not state the sample-size rationale, analysis populati
- F06 [high/verified] The protocol excludes anti-PD-(L)1 therapy within four weeks before first dose but states no washout periods for other prior systemic therap
- F08 [low/verified] The protocol identifies DV-101 as an irreversible covalent KRAS G12C inhibitor and supplies its chemical structure without stating a limitat

## AX1-010 — finding 10건, 주입 결함 6건, 토큰 42,286

| 결과 | 주입 결함(요약) | 원 규범 문서 | 매칭 finding |
|---|---|---|---|
| 🟡 span만 적중 | In the pediatric expansion cohort, safety will be assessed only by recording adverse events at scheduled clini | FDA-EXPANSION-COHORTS-2022 · H Evaluating PK, Tolerability, | F03 |
| 🟡 span만 적중 | The pediatric expansion cohort will proceed under the adult development plan, with pediatric assessments docum | FDA-EXPANSION-COHORTS-2022 · H Evaluating PK, Tolerability, | F02 |
| 🟡 span만 적중 | Dose selection for expansion will be based solely on the prespecified primary endpoint from the escalation coh | ICH-E4-1994 · IV GUIDANCE AND ADVICE | F04 |
| 🟡 span만 적중 | Participants assigned to the control arm may cross over to the investigational therapy after progression; safe | MFDS-1443-01-2025 · 3.2 다양한 용량을 비교하기 위한 임상시험 설계 | F05 |
| ❌ 놓침 | The medical monitor may be any licensed physician with general inpatient-care experience; prior oncology pract | FDA-EXPANSION-COHORTS-2022 · A Safety Monitoring and Report | - |
| 🟡 span만 적중 | The recommended Phase 2 dose will be selected solely from dose-limiting toxicity rates observed during Cycle 1 | FDA-DOSE-OPT-2024 · I INTRODUCTION | F01 |

주입 결함과 무관한 finding(정상판 기준 잘못 경고 후보, 사람 검토 필요):
- F06 [high/held] The protocol specifies a minimum randomized sample size and comparison domains but does not state quantitative hypotheses, precision objecti
- F07 [high/verified] The protocol collects intensive PK only in escalation subjects and steady-state trough samples only in randomized cohorts, while specifying 
- F08 [medium/verified] The listed exclusions specify a four-week washout for anti-PD-(L)1 therapy but no washout intervals for other prior anticancer treatments. R
- F09 [low/verified] The protocol identifies DV-101 as sotorasib and classifies it as an irreversible covalent KRAS G12C inhibitor while providing its SMILES str

## AX1-011 — finding 11건, 주입 결함 6건, 토큰 44,714

| 결과 | 주입 결함(요약) | 원 규범 문서 | 매칭 finding |
|---|---|---|---|
| 🟡 span만 적중 | Protocol deviations will be reviewed individually by the study team, with importance assigned after database l | ICH-E6R3-2025 · 3.9.1 The sponsor should ensur | F05 |
| 🟡 span만 적중 | Pharmacokinetic analyses will use pooled data without examining covariates or reporting results by clinically  | MFDS-1443-01-2025 · 3.1 임상 약동학, 약력학 및 약물유전체학 | F07 |
| 🟡 span만 적중 | The study will assess treatment activity using weekly change in body weight and evaluate safety primarily thro | MFDS-1443-01-2025 · 3.1 임상 약동학, 약력학 및 약물유전체학 | F01 |
| 🟡 span만 적중 | The sponsor will include serious and unexpected adverse safety findings in the next scheduled annual safety re | FDA-EXPANSION-COHORTS-2022 · B Potential Opportunities and  | F02 |
| ✅ 근거까지 적중 | Patients with moderate hepatic impairment and the CYP2C19 poor-metabolizer genotype will be enrolled in the sa | FDA-DOSE-OPT-2024 · A Clinical Pharmacokinetics, P | F03 |
| 🟡 span만 적중 | Patients in the expansion cohort will receive the investigator-selected dose of either 80 mg or 120 mg once da | FDA-EXPANSION-COHORTS-2022 · VI STATISTICAL CONSIDERATIONS | F04 |

주입 결함과 무관한 finding(정상판 기준 잘못 경고 후보, 사람 검토 필요):
- F06 [high/verified] The protocol limits randomized-cohort PK collection to steady-state trough samples and does not state how individual AUC, Cmax, or other exp
- F08 [high/verified] The protocol specifies baseline, every-three-week, and monthly liver testing but does not state that this schedule prevails over the separat
- F09 [medium/held] The protocol identifies DV-101 as an irreversible covalent inhibitor and provides its structure but does not describe evidence on metabolism
- F10 [medium/verified] The key eligibility criteria specify only a fixed four-week anti-PD-(L)1 washout and do not state washouts for other anticancer therapies or

## AX1-012 — finding 11건, 주입 결함 6건, 토큰 47,436

| 결과 | 주입 결함(요약) | 원 규범 문서 | 매칭 finding |
|---|---|---|---|
| 🟡 span만 적중 | Interim safety and efficacy findings will be reviewed only after database lock at the end of the expansion pha | FDA-EXPANSION-COHORTS-2022 · II BACKGROUND | F03 |
| 🟡 span만 적중 | The study will enroll adults with untreated low-risk indolent lymphoma for whom standard curative therapy is a | FDA-EXPANSION-COHORTS-2022 · IV DRUG PRODUCT AND SUBJECT CO | F05 |
| 🟡 span만 적중 | This first-in-human dose-escalation study will enroll participants using an ad hoc design selected for operati | ICH-E4-1994 · IV GUIDANCE AND ADVICE | F01 |
| 🟡 span만 적중 | Blood samples will be collected for exploratory biomarker testing, but no pharmacokinetic sampling schedule or | FDA-DOSE-OPT-2024 · A Clinical Pharmacokinetics, P | F02 |
| 🟡 span만 적중 | Enrollment in the pediatric expansion cohort will be open to children with newly diagnosed or relapsed solid t | FDA-EXPANSION-COHORTS-2022 · H Evaluating PK, Tolerability, | F04 |
| ❌ 놓침 | Tolerability will be assessed exclusively through investigator-recorded adverse events and laboratory findings | FDA-DOSE-OPT-2024 · C Safety and Tolerability | - |

주입 결함과 무관한 finding(정상판 기준 잘못 경고 후보, 사람 검토 필요):
- F06 [high/held] The randomized candidate-dose cohorts have steady-state trough sampling only, while intensive PK profiles are limited to escalation subjects
- F07 [high/verified] The protocol randomizes a heterogeneous advanced-solid-tumor population without stating tumor-specific cohorts, randomization strata, covari
- F08 [high/verified] The protocol defers the integrated RP2D criteria to Appendix D and states that RP2D selection will not be based solely on the maximum tolera
- F09 [high/verified] The listed exclusion criteria specify a four-week washout only for anti-PD-(L)1 therapy and provide no washout intervals for other systemic 
- F10 [medium/verified] The protocol identifies DV-101 as an irreversible covalent inhibitor and provides its structure but contains no compound-specific assessment

## AX1-013 — finding 11건, 주입 결함 6건, 토큰 43,980

| 결과 | 주입 결함(요약) | 원 규범 문서 | 매칭 finding |
|---|---|---|---|
| 🟡 span만 적중 | Enrollment in the pediatric expansion cohort will be open to children with newly diagnosed or relapsed solid t | FDA-EXPANSION-COHORTS-2022 · H Evaluating PK, Tolerability, | F03 |
| 🟡 span만 적중 | The sponsor will finalize the dose-comparison design and proceed directly to patient enrollment without seekin | MFDS-1443-01-2025 · 3.2 다양한 용량을 비교하기 위한 임상시험 설계 | F08, F09 |
| 🟡 span만 적중 | During this first-in-human study, safety will be assessed only by participant-reported symptoms, and treatment | FDA-DOSE-OPT-2024 · A Clinical Pharmacokinetics, P | F02 |
| 🟡 span만 적중 | The study will enroll adults with untreated low-risk indolent lymphoma for whom standard curative therapy is a | FDA-EXPANSION-COHORTS-2022 · IV DRUG PRODUCT AND SUBJECT CO | F04 |
| 🟡 span만 적중 | Patients with moderate hepatic impairment and carriers of the ABCB1 variant will be enrolled only in the expan | FDA-DOSE-OPT-2024 · A Clinical Pharmacokinetics, P | F07 |
| 🟡 span만 적중 | After enrolling the initial three participants at 10 mg, the study will proceed directly to a fixed 10 mg expa | MFDS-1443-01-2025 · 1 안내서-1443-01 2025. 8. 29. 제정 | F01 |

주입 결함과 무관한 finding(정상판 기준 잘못 경고 후보, 사람 검토 필요):
- F05 [high/verified] The protocol specifies a minimum randomized sample of 60 subjects but does not state cohort-specific hypotheses, precision or sample-size as
- F06 [high/verified] The protocol states that PK and PD will be compared between candidate doses but does not define dose-specific exposure assumptions, an expos
- F10 [low/verified] The protocol identifies DV-101 as sotorasib, describes it as an irreversible covalent KRAS G12C inhibitor, and provides a SMILES containing 

## AX1-014 — finding 10건, 주입 결함 6건, 토큰 43,996

| 결과 | 주입 결함(요약) | 원 규범 문서 | 매칭 finding |
|---|---|---|---|
| 🟡 span만 적중 | For every participant, the dose-escalation algorithm will identify that individual’s optimal dose from observe | ICH-E4-1994 · IV GUIDANCE AND ADVICE | F05 |
| 🟡 span만 적중 | Pharmacokinetic blood samples will be collected only before dosing and at 1 hour after the first administratio | MFDS-1443-01-2025 · 3.1 임상 약동학, 약력학 및 약물유전체학 | F04 |
| 🟡 span만 적중 | After completing the dose-escalation study, participants will enroll into the expansion cohorts under the same | FDA-EXPANSION-COHORTS-2022 · A Initial Protocol | F06 |
| 🟡 span만 적중 | After identification of a potentially fatal dose-limiting toxicity during escalation, the study will open all  | FDA-EXPANSION-COHORTS-2022 · A Assessing Safety of Recommen | F02 |
| 🟡 span만 적중 | The sponsor will issue a single cumulative safety update to investigators and the IRB at the end of each calen | FDA-EXPANSION-COHORTS-2022 · C IRB/Independent Ethics Commi | F01 |
| 🟡 span만 적중 | The recommended Phase 2 dose will be selected using tumor response and exposure data only; treatment discontin | FDA-DOSE-OPT-2024 · C Safety and Tolerability | F00, F03 |

주입 결함과 무관한 finding(정상판 기준 잘못 경고 후보, 사람 검토 필요):
- F07 [high/verified] The protocol specifies at least 60 randomized subjects but provides no quantitative sample-size justification or evaluability assumptions in
- F08 [high/verified] The randomized comparison lists safety, tolerability, PK, PD, and preliminary antitumor activity but does not state how these measures and d
- F09 [low/held] The protocol identifies DV-101 as sotorasib, provides a SMILES string containing a C=CC(=O)N moiety, and assigns KRAS G12C as its target. 구조

## AX1-015 — finding 11건, 주입 결함 6건, 토큰 43,415

| 결과 | 주입 결함(요약) | 원 규범 문서 | 매칭 finding |
|---|---|---|---|
| 🟡 span만 적중 | The recommended Phase 2 dose will be selected solely from dose-limiting toxicity rates observed during Cycle 1 | FDA-DOSE-OPT-2024 · I INTRODUCTION | F03 |
| 🟡 span만 적중 | Dose selection for expansion will be based solely on observed tumor response rates, without adjustment for tre | ICH-E4-1994 · IV GUIDANCE AND ADVICE | F04 |
| 🟡 span만 적중 | The biomarker-selected expansion cohort will enroll 30 participants, with no assumptions, precision targets, h | FDA-EXPANSION-COHORTS-2022 · VI STATISTICAL CONSIDERATIONS | F06 |
| 🟡 span만 적중 | After the recommended starting dose is established, all subsequent participants will receive the same fixed do | ICH-E4-1994 · II OBTAINING DOSE-RESPONSE INF | F01 |
| 🟡 span만 적중 | This first-in-human dose-escalation study will enroll participants using an ad hoc design selected for operati | ICH-E4-1994 · IV GUIDANCE AND ADVICE | F02 |
| 🟡 span만 적중 | The combination expansion cohort will open after the first six participants complete cycle 1 of the investigat | FDA-EXPANSION-COHORTS-2022 · G Evaluating More Than One The | F05 |

주입 결함과 무관한 finding(정상판 기준 잘못 경고 후보, 사람 검토 필요):
- F07 [high/verified] The protocol specifies a power model for dose proportionality but provides no model specification, evaluability criteria, variability assump
- F08 [medium/verified] The protocol identifies DV-101 as sotorasib and provides a SMILES string but gives no curated-record identifier, analytical identity confirm
- F09 [medium/held] The protocol excludes anti-PD-(L)1 treatment within four weeks before the first dose but provides no risk-based rationale or additional cont
- F10 [low/verified] The protocol specifies baseline testing, testing every three weeks for three months, and monthly testing thereafter, but does not specify mo

## AX1-016 — finding 9건, 주입 결함 6건, 토큰 44,212

| 결과 | 주입 결함(요약) | 원 규범 문서 | 매칭 finding |
|---|---|---|---|
| 🟡 span만 적중 | The study will select the recommended Phase 2 dose from the first expansion cohort without collecting dose–res | ICH-E4-1994 · IV GUIDANCE AND ADVICE | F03 |
| 🟡 span만 적중 | The formulation-bridging expansion cohort will enroll participants receiving the new tablet or legacy capsule, | FDA-EXPANSION-COHORTS-2022 · F Evaluating Drug Product Chan | F05 |
| 🟡 span만 적중 | After identifying the first tolerable dose, all subsequent participants will receive only that dose, with no c | MFDS-1443-01-2025 · 3.2 다양한 용량을 비교하기 위한 임상시험 설계 | F01 |
| 🟡 span만 적중 | For this intravenous oncology study, the 500 mg dose will be prepared as a 50 mg/mL solution, requiring admini | MFDS-1443-01-2025 · 3.4 의약품의 함량 및 제형 | F02 |
| 🟡 span만 적중 | The disease-specific expansion cohort will enroll up to 60 participants without interim futility monitoring or | FDA-EXPANSION-COHORTS-2022 · B Evaluating Preliminary Antit | F06 |
| 🟡 span만 적중 | All recommendations in FDA-DOSE-OPT-2024 shall be implemented without deviation, and any investigator request  | FDA-DOSE-OPT-2024 · I INTRODUCTION | F04 |

주입 결함과 무관한 finding(정상판 기준 잘못 경고 후보, 사람 검토 필요):
- F07 [high/verified] The liver-test schedule does not explicitly provide more frequent testing after transaminase or bilirubin abnormalities develop. Liver funct
- F08 [high/verified] The randomized cohorts collect only steady-state trough samples and do not specify how full steady-state exposure will be estimated for each

## AX1-017 — finding 10건, 주입 결함 6건, 토큰 44,909

| 결과 | 주입 결함(요약) | 원 규범 문서 | 매칭 finding |
|---|---|---|---|
| 🟡 span만 적중 | Population pharmacokinetic analyses will be performed only after database lock using the final pooled dataset, | FDA-DOSE-OPT-2024 · A Clinical Pharmacokinetics, P | F08 |
| 🟡 span만 적중 | The study will select the recommended Phase 2 dose from the first dose level that meets the preliminary respon | FDA-DOSE-OPT-2024 · 7 See 21 CFR 312.42 | F02 |
| 🟡 span만 적중 | The recommended Phase 2 dose will be the highest dose tested with acceptable early laboratory findings, even i | FDA-DOSE-OPT-2024 · II BACKGROUND | F03 |
| 🟡 span만 적중 | Dose selection for expansion will be based solely on the prespecified primary endpoint from the escalation coh | ICH-E4-1994 · IV GUIDANCE AND ADVICE | F07 |
| 🟡 span만 적중 | The study will assess treatment activity using weekly change in body weight and evaluate safety primarily thro | MFDS-1443-01-2025 · 3.1 임상 약동학, 약력학 및 약물유전체학 | F01 |
| 🟡 span만 적중 | The protocol will continue enrollment in each expansion cohort until the planned sample size is reached, witho | FDA-EXPANSION-COHORTS-2022 · VI STATISTICAL CONSIDERATIONS | F04 |

주입 결함과 무관한 finding(정상판 기준 잘못 경고 후보, 사람 검토 필요):
- F05 [high/verified] The protocol specifies a 60-subject randomized comparison but does not specify exposure-response endpoints, models, covariates, decision thr
- F06 [high/held] The protocol specifies a BOIN target DLT rate, maximum enrollment, five dose levels, and four simulated toxicity scenarios, while deferring 
- F09 [low/verified] The protocol specifies baseline liver testing, testing every three weeks for three months, and monthly testing thereafter, but does not spec

## AX1-018 — finding 11건, 주입 결함 6건, 토큰 41,653

| 결과 | 주입 결함(요약) | 원 규범 문서 | 매칭 finding |
|---|---|---|---|
| 🟡 span만 적중 | All participants will receive 80 mg orally twice daily from Cycle 1 Day 1, with no intra-patient dose escalati | ICH-E4-1994 · I INTRODUCTION | F01 |
| 🟡 span만 적중 | After the recommended Phase 2 dose is selected, no additional dose-optimization or comparative dose evaluation | FDA-DOSE-OPT-2024 · II BACKGROUND | F07 |
| 🟡 span만 적중 | The recommended Phase 2 dose will be selected solely from dose-limiting toxicity rates observed during Cycle 1 | FDA-DOSE-OPT-2024 · I INTRODUCTION | F02 |
| 🟡 span만 적중 | After the safety lead-in, all participants will receive 240 mg twice daily; no alternate dose will be evaluate | FDA-DOSE-OPT-2024 · B Trial Designs to Compare Mul | F03 |
| 🟡 span만 적중 | The recommended Phase 2 dose will be the highest dose tested with acceptable early laboratory findings, even i | FDA-DOSE-OPT-2024 · II BACKGROUND | F04 |
| 🟡 span만 적중 | Participants who cross over to the alternate dose will be included in the overall safety and response analyses | FDA-DOSE-OPT-2024 · B Trial Designs to Compare Mul | F05 |

주입 결함과 무관한 finding(정상판 기준 잘못 경고 후보, 사람 검토 필요):
- F06 [high/verified] The protocol specifies at least 60 randomized participants but provides no sample-size assumptions, precision or power target, interim decis
- F08 [high/held] The randomized cohorts have steady-state trough sampling only, while dose proportionality is assessed by a power model. The LUMAKRAS label s
- F09 [high/verified] The protocol specifies baseline, every-three-week, and monthly liver testing but does not expressly increase testing frequency after transam
- F10 [medium/verified] The stated exclusion criteria define a four-week washout for anti-PD-(L)1 therapy but state no washout periods for chemotherapy, targeted th

## AX1-019 — finding 11건, 주입 결함 6건, 토큰 44,858

| 결과 | 주입 결함(요약) | 원 규범 문서 | 매칭 finding |
|---|---|---|---|
| 🟡 span만 적중 | After the recommended Phase 2 dose is selected from tolerability data, all subsequent participants will receiv | ICH-E4-1994 · II OBTAINING DOSE-RESPONSE INF | F03 |
| 🟡 span만 적중 | In this open-label, single-arm Phase 1/2 study, treatment activity will be assessed against historical respons | ICH-E4-1994 · IV GUIDANCE AND ADVICE | F05 |
| 🟡 span만 적중 | Dose-response analyses will be limited to the randomized expansion cohort, and data from dose-escalation parti | ICH-E4-1994 · II OBTAINING DOSE-RESPONSE INF | F06 |
| 🟡 span만 적중 | After enrolling the initial three participants at 10 mg, the study will proceed directly to a fixed 10 mg expa | MFDS-1443-01-2025 · 1 안내서-1443-01 2025. 8. 29. 제정 | F01 |
| 🟡 span만 적중 | All participants will receive the fixed 200 mg dose supplied in a single capsule strength throughout the study | FDA-DOSE-OPT-2024 · D Drug Formulation | F02 |
| 🟡 span만 적중 | Results from the expansion cohort will serve as the primary efficacy package for the planned marketing applica | FDA-EXPANSION-COHORTS-2022 · C Communications and Interacti | F04 |

주입 결함과 무관한 finding(정상판 기준 잘못 경고 후보, 사람 검토 필요):
- F07 [high/verified] The protocol randomizes at least 60 subjects equally between two candidate doses but does not state the assumptions, precision targets, stat
- F08 [medium/verified] The protocol specifies baseline, every-three-week, and monthly liver testing but does not expressly prescribe more frequent testing after tr
- F09 [medium/verified] The protocol excludes anti-PD-(L)1 therapy received within four weeks before the first dose. Liver function tests should be monitored every 
- F10 [medium/verified] The protocol collects intensive PK profiles only in escalation subjects and limits randomized-cohort PK collection to steady-state trough sa

## AX1-020 — finding 7건, 주입 결함 6건, 토큰 44,774

| 결과 | 주입 결함(요약) | 원 규범 문서 | 매칭 finding |
|---|---|---|---|
| 🟡 span만 적중 | The study team will review emerging adverse-event data periodically and decide during the trial whether enroll | FDA-DOSE-OPT-2024 · C Safety and Tolerability | F04 |
| ✅ 근거까지 적중 | Patients with moderate hepatic impairment and the CYP2C19 poor-metabolizer genotype will be enrolled in the sa | FDA-DOSE-OPT-2024 · A Clinical Pharmacokinetics, P | F05 |
| ❌ 놓침 | Results from the expansion cohort will serve as the primary efficacy package for the planned marketing applica | FDA-EXPANSION-COHORTS-2022 · C Communications and Interacti | - |
| 🟡 span만 적중 | The expansion cohort will enroll 80 patients at 200 mg twice daily immediately after the first three participa | FDA-DOSE-OPT-2024 · III DOSAGE OPTIMIZATION RECOMM | F03 |
| 🟡 span만 적중 | Blood samples will be collected for exploratory biomarker testing, but no pharmacokinetic sampling schedule or | FDA-DOSE-OPT-2024 · A Clinical Pharmacokinetics, P | F06 |
| 🟡 span만 적중 | The recommended Phase 2 dose will be selected solely from the highest tolerated dose in the escalation cohort, | FDA-DOSE-OPT-2024 · A Clinical Pharmacokinetics, P | F00, F01, F02 |

