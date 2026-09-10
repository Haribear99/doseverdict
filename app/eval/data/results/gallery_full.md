# 실패 사례 갤러리 — full

놓친 결함과 잘못 경고한 사례를 그대로 공개한다(제안서 4장 약속).
합계: 주입 결함 120건 중 놓침 9건, finding 218건 중 무관 82건.

## AX1-001 — finding 11건, 주입 결함 6건, 토큰 55,234

| 결과 | 주입 결함(요약) | 원 규범 문서 | 매칭 finding |
|---|---|---|---|
| 🟡 span만 적중 | The study team will review emerging adverse-event data periodically and decide during the trial whether enroll | FDA-DOSE-OPT-2024 · C Safety and Tolerability | F06 |
| 🟡 span만 적중 | All participants will receive the fixed 200 mg dose supplied in a single capsule strength throughout the study | FDA-DOSE-OPT-2024 · D Drug Formulation | F01 |
| 🟡 span만 적중 | The formulation-bridging expansion cohort will enroll participants receiving the new tablet or legacy capsule, | FDA-EXPANSION-COHORTS-2022 · F Evaluating Drug Product Chan | F07 |
| 🟡 span만 적중 | After the recommended Phase 2 dose is selected from tolerability data, all subsequent participants will receiv | ICH-E4-1994 · II OBTAINING DOSE-RESPONSE INF | F02 |
| ✅ 근거까지 적중 | Patients with moderate hepatic impairment and the CYP2C19 poor-metabolizer genotype will be enrolled in the sa | FDA-DOSE-OPT-2024 · A Clinical Pharmacokinetics, P | F08 |
| 🟡 span만 적중 | Dose–response analyses will be conducted only in the overall enrolled population, with no evaluations by age,  | ICH-E4-1994 · IV GUIDANCE AND ADVICE | F10 |

주입 결함과 무관한 finding(정상판 기준 잘못 경고 후보, 사람 검토 필요):
- F03 [high/verified] The protocol prespecifies a dose-proportionality power model but does not state exposure–efficacy, exposure–toxicity, or exposure–tolerabili
- F04 [high/verified] The supplied protocol text gives the BOIN target DLT rate, maximum enrollment, dose levels, and a reference to Appendix C but does not provi
- F05 [high/verified] The supplied protocol text refers to Appendix B but does not provide the interruption, reduction, rechallenge, or permanent-discontinuation 
- F09 [high/verified] The Phase 2 primary objective identifies ORR under RECIST v1.1 but does not state sample size, hypothesis or precision target, analysis set,

## AX1-002 — finding 11건, 주입 결함 6건, 토큰 59,239

| 결과 | 주입 결함(요약) | 원 규범 문서 | 매칭 finding |
|---|---|---|---|
| 🟡 span만 적중 | Results from the expansion cohort will serve as the primary efficacy package for the planned marketing applica | FDA-EXPANSION-COHORTS-2022 · C Communications and Interacti | F09 |
| 🟡 span만 적중 | The recommended Phase 2 dose will be the highest dose at which no more than 30% of participants permanently di | ICH-E4-1994 · II OBTAINING DOSE-RESPONSE INF | F00, F04 |
| 🟡 span만 적중 | Patients with moderate hepatic impairment and the CYP2C19 poor-metabolizer genotype will be enrolled in the sa | FDA-DOSE-OPT-2024 · A Clinical Pharmacokinetics, P | F08 |
| 🟡 span만 적중 | The sponsor will issue a single cumulative safety update to investigators and the IRB at the end of each calen | FDA-EXPANSION-COHORTS-2022 · C IRB/Independent Ethics Commi | F01 |
| 🟡 span만 적중 | The combination expansion cohort will open after the first six participants complete cycle 1 of the investigat | FDA-EXPANSION-COHORTS-2022 · G Evaluating More Than One The | F03 |
| 🟡 span만 적중 | The expansion cohort will support the marketing application using investigator-assessed tumor responses at the | FDA-EXPANSION-COHORTS-2022 · B Evaluating Preliminary Antit | F02 |

주입 결함과 무관한 finding(정상판 기준 잘못 경고 후보, 사람 검토 필요):
- F05 [high/held] The protocol lists five dose levels from 180 mg to 960 mg without stating the evidence or quantitative criteria used to select that range. T
- F06 [high/verified] The protocol limits randomized-cohort PK sampling to steady-state troughs and does not describe a population-PK method for estimating AUC or
- F07 [high/verified] The protocol assigns at least 60 participants equally between two candidate doses without providing assumptions, precision targets, attritio
- F10 [high/verified] The protocol places the hepatotoxicity and interstitial lung disease/pneumonitis dose-modification rules in Appendix B, which is not include

## AX1-003 — finding 11건, 주입 결함 6건, 토큰 57,867

| 결과 | 주입 결함(요약) | 원 규범 문서 | 매칭 finding |
|---|---|---|---|
| 🟡 span만 적중 | The recommended Phase 2 dose will be the highest dose at which no more than 30% of participants permanently di | ICH-E4-1994 · II OBTAINING DOSE-RESPONSE INF | F00, F02 |
| 🟡 span만 적중 | After the safety lead-in, all participants will receive 240 mg twice daily; no alternate dose will be evaluate | FDA-DOSE-OPT-2024 · B Trial Designs to Compare Mul | F01 |
| 🟡 span만 적중 | The study team will review emerging adverse-event data periodically and decide during the trial whether enroll | FDA-DOSE-OPT-2024 · C Safety and Tolerability | F07 |
| ❌ 놓침 | Concomitant medications will be recorded at enrollment, but no interaction studies or dedicated pharmacokineti | FDA-DOSE-OPT-2024 · A Clinical Pharmacokinetics, P | - |
| 🟡 span만 적중 | For the randomized Phase 2 portion, each of the three active-dose arms will be compared independently with pla | FDA-DOSE-OPT-2024 · B Trial Designs to Compare Mul | F03 |
| 🟡 span만 적중 | All recommendations in FDA-DOSE-OPT-2024 shall be implemented without deviation, and any investigator request  | FDA-DOSE-OPT-2024 · I INTRODUCTION | F09 |

주입 결함과 무관한 finding(정상판 기준 잘못 경고 후보, 사람 검토 필요):
- F04 [high/verified] The protocol limits randomized-cohort PK collection to steady-state trough samples and specifies a dose-proportionality power model without 
- F05 [high/held] The protocol gives the BOIN target DLT rate, maximum enrollment, dose levels, and number of simulated scenarios but omits cohort size, decis
- F06 [high/held] The protocol specifies at least 60 participants and 1:1 randomization but does not state assumptions, precision or power targets, estimands,
- F08 [medium/verified] The protocol states that two candidate doses will be selected from escalation data but does not provide the scientific rationale, quantitati
- F10 [low/verified] The protocol specifies baseline liver testing, testing every three weeks for the first three months, and monthly testing thereafter, but doe

## AX1-004 — finding 9건, 주입 결함 6건, 토큰 57,319

| 결과 | 주입 결함(요약) | 원 규범 문서 | 매칭 finding |
|---|---|---|---|
| 🟡 span만 적중 | The dose-escalation and expansion cohorts will follow the same general treatment plan, with cohort-specific do | FDA-EXPANSION-COHORTS-2022 · A Initial Protocol | F07 |
| 🟡 span만 적중 | The randomized Phase 2 portion will compare three active dose levels with placebo, and each dose-versus-placeb | MFDS-1443-01-2025 · 3.2 다양한 용량을 비교하기 위한 임상시험 설계 | F05 |
| 🟡 span만 적중 | Participants will be enrolled sequentially into nonrandomized cohorts receiving 10, 30, or 60 mg once daily, w | FDA-DOSE-OPT-2024 · B Trial Designs to Compare Mul | F06, F08 |
| 🟡 span만 적중 | All doses will be prepared as a fixed 0.5 mg/mL intravenous solution, including doses requiring infusion volum | FDA-DOSE-OPT-2024 · D Drug Formulation | F01 |
| 🟡 span만 적중 | 확장 코호트에서는 선행 임상자료나 노출·반응 분석과 무관하게 모든 환자에게 임상적으로 사용되는 표준 용량 200 mg을 투여한다. | MFDS-1443-01-2025 · 1 안내서-1443-01 2025. 8. 29. 제정 | F02 |
| 🟡 span만 적중 | Dose selection for expansion will be based solely on observed tumor response rates, without adjustment for tre | ICH-E4-1994 · IV GUIDANCE AND ADVICE | F03 |

주입 결함과 무관한 finding(정상판 기준 잘못 경고 후보, 사람 검토 필요):
- F04 [high/verified] The protocol describes a 60-subject 1:1 comparison of two candidate doses and also describes a randomized Phase 2 comparison of three active

## AX1-005 — finding 11건, 주입 결함 6건, 토큰 58,705

| 결과 | 주입 결함(요약) | 원 규범 문서 | 매칭 finding |
|---|---|---|---|
| 🟡 span만 적중 | The study team will review emerging adverse-event data periodically and decide during the trial whether enroll | FDA-DOSE-OPT-2024 · C Safety and Tolerability | F06 |
| 🟡 span만 적중 | In the pediatric expansion cohort, safety will be assessed only by recording adverse events at scheduled clini | FDA-EXPANSION-COHORTS-2022 · H Evaluating PK, Tolerability, | F02 |
| 🟡 span만 적중 | This amendment adds a higher-dose expansion cohort based on preliminary efficacy findings; the safety rational | FDA-EXPANSION-COHORTS-2022 · A Safety Monitoring and Report | F01 |
| 🟡 span만 적중 | The expansion cohort will support the marketing application using investigator-assessed tumor responses at the | FDA-EXPANSION-COHORTS-2022 · B Evaluating Preliminary Antit | F03 |
| 🟡 span만 적중 | No pharmacodynamic or pharmacogenomic specimens will be collected, and the study will not evaluate genetic det | FDA-DOSE-OPT-2024 · A Clinical Pharmacokinetics, P | F07 |
| 🟡 span만 적중 | The study will be conducted under the sponsor's internal approval without submission of the final protocol to  | ICH-E4-1994 · 0 PREAMBLE | F04 |

주입 결함과 무관한 finding(정상판 기준 잘못 경고 후보, 사람 검토 필요):
- F05 [high/held] The randomized dose-comparison cohorts collect only steady-state trough PK samples, while intensive concentration-time sampling and the powe
- F08 [high/verified] The synopsis specifies the BOIN target DLT rate, maximum sample size, five dose levels, and four simulation scenarios but does not state all
- F09 [medium/verified] The protocol identifies DV-101 as sotorasib and describes its mechanism but does not state how established sotorasib clinical pharmacology i
- F10 [medium/verified] The protocol excludes anti-PD-(L)1 therapy within four weeks before the first dose but provides no rationale or additional eligibility and m

## AX1-006 — finding 11건, 주입 결함 6건, 토큰 58,191

| 결과 | 주입 결함(요약) | 원 규범 문서 | 매칭 finding |
|---|---|---|---|
| 🟡 span만 적중 | The recommended Phase 2 dose will be the highest dose tested with acceptable early laboratory findings, even i | FDA-DOSE-OPT-2024 · II BACKGROUND | F02 |
| 🟡 span만 적중 | The sponsor will compile aggregate safety data internally and submit cumulative reports to FDA at its discreti | FDA-EXPANSION-COHORTS-2022 · A Safety Monitoring and Report | F04 |
| 🟡 span만 적중 | The study will enroll adults with untreated low-risk indolent lymphoma for whom standard curative therapy is a | FDA-EXPANSION-COHORTS-2022 · IV DRUG PRODUCT AND SUBJECT CO | F03 |
| 🟡 span만 적중 | Participants who cross over to the alternate dose will be included in the overall safety and response analyses | FDA-DOSE-OPT-2024 · B Trial Designs to Compare Mul | F05 |
| 🟡 span만 적중 | The Phase 2 expansion dose will be fixed at 200 mg twice daily based solely on the recommended Phase 1 dose, w | FDA-DOSE-OPT-2024 · III DOSAGE OPTIMIZATION RECOMM | F01 |
| 🟡 span만 적중 | Results from the expansion cohort will serve as the primary efficacy package for the planned marketing applica | FDA-EXPANSION-COHORTS-2022 · C Communications and Interacti | F09 |

주입 결함과 무관한 finding(정상판 기준 잘못 경고 후보, 사람 검토 필요):
- F06 [high/verified] The protocol specifies at least 60 randomized participants and the comparison domains but does not state sample-size assumptions, precision 
- F07 [high/verified] The protocol limits the five-level BOIN escalation to 36 participants and refers to four simulated toxicity scenarios without reporting thei
- F08 [high/verified] The protocol refers hepatotoxicity and ILD/pneumonitis dose-modification rules to Appendix B but provides no grading, detection, interruptio
- F10 [medium/verified] The protocol uses intensive first-dose and steady-state PK sampling in escalation participants but collects only steady-state trough samples

## AX1-007 — finding 11건, 주입 결함 6건, 토큰 55,757

| 결과 | 주입 결함(요약) | 원 규범 문서 | 매칭 finding |
|---|---|---|---|
| 🟡 span만 적중 | For the new pembrolizumab–investigational-agent combination in metastatic colorectal cancer, the study will pr | MFDS-1443-01-2025 · 3.5 후속 적응증 및 용법 | F06 |
| 🟡 span만 적중 | 확장 코호트에서는 선행 임상자료나 노출·반응 분석과 무관하게 모든 환자에게 임상적으로 사용되는 표준 용량 200 mg을 투여한다. | MFDS-1443-01-2025 · 1 안내서-1443-01 2025. 8. 29. 제정 | F07 |
| 🟡 span만 적중 | Interim safety and efficacy findings will be reviewed only after database lock at the end of the expansion pha | FDA-EXPANSION-COHORTS-2022 · II BACKGROUND | F03 |
| 🟡 span만 적중 | The formulation-bridging expansion cohort will enroll participants receiving the new tablet or legacy capsule, | FDA-EXPANSION-COHORTS-2022 · F Evaluating Drug Product Chan | F08 |
| 🟡 span만 적중 | After the recommended Phase 2 dose is selected from tolerability data, all subsequent participants will receiv | ICH-E4-1994 · II OBTAINING DOSE-RESPONSE INF | F02 |
| 🟡 span만 적중 | The starting dose and subsequent escalation levels will be selected solely by investigator consensus, without  | FDA-DOSE-OPT-2024 · III DOSAGE OPTIMIZATION RECOMM | F01 |

주입 결함과 무관한 finding(정상판 기준 잘못 경고 후보, 사람 검토 필요):
- F04 [high/verified] The protocol refers to integrated RP2D-selection criteria in Appendix D but does not present the analyses, thresholds, covariates, or uncert
- F05 [high/verified] The protocol specifies at least 60 randomized subjects but does not state the sample-size assumptions, precision targets, multiplicity appro
- F09 [high/verified] The protocol specifies five dose levels, a 30% DLT target, a 36-subject maximum, and four simulated toxicity scenarios but does not provide 
- F10 [high/verified] The protocol provides baseline, every-three-week, and monthly liver testing but does not specify intensified testing triggers for participan

## AX1-008 — finding 11건, 주입 결함 6건, 토큰 59,054

| 결과 | 주입 결함(요약) | 원 규범 문서 | 매칭 finding |
|---|---|---|---|
| 🟡 span만 적중 | After participants complete 48 hours at the assigned dose level, the dose-response analysis will be performed  | ICH-E4-1994 · 1 Parallel dose-response | F03 |
| 🟡 span만 적중 | Dose–response analyses will be conducted only in the overall enrolled population, with no evaluations by age,  | ICH-E4-1994 · IV GUIDANCE AND ADVICE | F05 |
| 🟡 span만 적중 | The study will select the recommended Phase 2 dose from the first expansion cohort without collecting dose–res | ICH-E4-1994 · IV GUIDANCE AND ADVICE | F02 |
| 🟡 span만 적중 | After completing the dose-escalation portion, the study will open six parallel disease-specific expansion coho | FDA-EXPANSION-COHORTS-2022 · IV DRUG PRODUCT AND SUBJECT CO | F04 |
| 🟡 span만 적중 | The sponsor will include serious and unexpected adverse safety findings in the next scheduled annual safety re | FDA-EXPANSION-COHORTS-2022 · B Potential Opportunities and  | F01 |
| 🟡 span만 적중 | Participants will be enrolled sequentially into nonrandomized cohorts receiving 10, 30, or 60 mg once daily, w | FDA-DOSE-OPT-2024 · B Trial Designs to Compare Mul | F07 |

주입 결함과 무관한 finding(정상판 기준 잘못 경고 후보, 사람 검토 필요):
- F06 [high/verified] The protocol specifies at least 60 participants and 1:1 randomization but does not state endpoint definitions, estimands, exposure metrics, 
- F08 [high/verified] The protocol sentence identifies hepatotoxicity and interstitial lung disease/pneumonitis only through a cross-reference and contains no gra
- F09 [medium/verified] The randomized cohorts have only steady-state trough sampling, and the protocol does not specify population-PK modeling, individual AUC or C
- F10 [low/verified] The protocol identifies DV-101 as an irreversible covalent KRAS G12C inhibitor and provides its SMILES but provides no empirical organ-speci

## AX1-009 — finding 11건, 주입 결함 6건, 토큰 58,410

| 결과 | 주입 결함(요약) | 원 규범 문서 | 매칭 finding |
|---|---|---|---|
| 🟡 span만 적중 | The sponsor will finalize the dose-comparison design and proceed directly to patient enrollment without seekin | MFDS-1443-01-2025 · 3.2 다양한 용량을 비교하기 위한 임상시험 설계 | F04 |
| 🟡 span만 적중 | After the sponsor transfers production to a new manufacturing site and changes the formulation, the study will | FDA-EXPANSION-COHORTS-2022 · F Evaluating Drug Product Chan | F01 |
| 🟡 span만 적중 | For every participant, the dose-escalation algorithm will identify that individual’s optimal dose from observe | ICH-E4-1994 · IV GUIDANCE AND ADVICE | F03 |
| 🟡 span만 적중 | Participants may take the study tablets with or without meals and may continue all clinically indicated concom | FDA-DOSE-OPT-2024 · A Clinical Pharmacokinetics, P | F10 |
| ❌ 놓침 | The medical monitor may be any licensed physician with general inpatient-care experience; prior oncology pract | FDA-EXPANSION-COHORTS-2022 · A Safety Monitoring and Report | - |
| 🟡 span만 적중 | The Phase 1 portion will escalate cohorts until the highest dose with an acceptable toxicity profile is identi | FDA-DOSE-OPT-2024 · II BACKGROUND | F00, F02 |

주입 결함과 무관한 finding(정상판 기준 잘못 경고 후보, 사람 검토 필요):
- F05 [high/verified] The sentence specifies a minimum sample size, allocation ratio, comparison domains, and RP2D-selection purpose but omits the sample-size jus
- F06 [high/verified] The protocol gives the BOIN target, maximum sample size, five dose levels, and number of simulated scenarios but does not state the cohort r
- F07 [high/verified] The protocol specifies baseline, every-three-week, and monthly liver testing but does not explicitly trigger more frequent testing after tra
- F08 [high/verified] The protocol refers all dose-modification rules for hepatotoxicity, interstitial lung disease/pneumonitis, and other adverse reactions to Ap
- F09 [high/verified] The randomized cohorts have steady-state trough sampling only, while intensive first-dose and Day 15 sampling is limited to escalation subje

## AX1-010 — finding 11건, 주입 결함 6건, 토큰 58,308

| 결과 | 주입 결함(요약) | 원 규범 문서 | 매칭 finding |
|---|---|---|---|
| 🟡 span만 적중 | In the pediatric expansion cohort, safety will be assessed only by recording adverse events at scheduled clini | FDA-EXPANSION-COHORTS-2022 · H Evaluating PK, Tolerability, | F03 |
| 🟡 span만 적중 | The pediatric expansion cohort will proceed under the adult development plan, with pediatric assessments docum | FDA-EXPANSION-COHORTS-2022 · H Evaluating PK, Tolerability, | F02 |
| ❌ 놓침 | Dose selection for expansion will be based solely on the prespecified primary endpoint from the escalation coh | ICH-E4-1994 · IV GUIDANCE AND ADVICE | - |
| 🟡 span만 적중 | Participants assigned to the control arm may cross over to the investigational therapy after progression; safe | MFDS-1443-01-2025 · 3.2 다양한 용량을 비교하기 위한 임상시험 설계 | F04 |
| ❌ 놓침 | The medical monitor may be any licensed physician with general inpatient-care experience; prior oncology pract | FDA-EXPANSION-COHORTS-2022 · A Safety Monitoring and Report | - |
| 🟡 span만 적중 | The recommended Phase 2 dose will be selected solely from dose-limiting toxicity rates observed during Cycle 1 | FDA-DOSE-OPT-2024 · I INTRODUCTION | F00, F01 |

주입 결함과 무관한 finding(정상판 기준 잘못 경고 후보, 사람 검토 필요):
- F05 [high/held] The BOIN sentence specifies the target DLT rate and maximum enrollment but does not state cohort size, decision boundaries, evaluability and
- F06 [high/verified] The randomized comparison sentence specifies at least 60 subjects and a 1:1 allocation but provides no sample-size rationale, precision targ
- F07 [high/verified] The protocol delegates hepatotoxicity and ILD/pneumonitis dose-modification rules to Appendix B, whose toxicity triggers, interruption, redu
- F08 [high/verified] The liver-test schedule includes baseline, every-three-week, and monthly testing but does not expressly specify more frequent testing after 
- F09 [high/held] The protocol uses intensive PK sampling during escalation but collects only steady-state trough samples in the randomized candidate-dose coh
- F10 [medium/held] The investigational-product description identifies an irreversible covalent inhibitor and its structure but provides no off-target pharmacol

## AX1-011 — finding 11건, 주입 결함 6건, 토큰 56,404

| 결과 | 주입 결함(요약) | 원 규범 문서 | 매칭 finding |
|---|---|---|---|
| 🟡 span만 적중 | Protocol deviations will be reviewed individually by the study team, with importance assigned after database l | ICH-E6R3-2025 · 3.9.1 The sponsor should ensur | F07 |
| 🟡 span만 적중 | Pharmacokinetic analyses will use pooled data without examining covariates or reporting results by clinically  | MFDS-1443-01-2025 · 3.1 임상 약동학, 약력학 및 약물유전체학 | F05 |
| 🟡 span만 적중 | The study will assess treatment activity using weekly change in body weight and evaluate safety primarily thro | MFDS-1443-01-2025 · 3.1 임상 약동학, 약력학 및 약물유전체학 | F01 |
| 🟡 span만 적중 | The sponsor will include serious and unexpected adverse safety findings in the next scheduled annual safety re | FDA-EXPANSION-COHORTS-2022 · B Potential Opportunities and  | F02 |
| ✅ 근거까지 적중 | Patients with moderate hepatic impairment and the CYP2C19 poor-metabolizer genotype will be enrolled in the sa | FDA-DOSE-OPT-2024 · A Clinical Pharmacokinetics, P | F04 |
| 🟡 span만 적중 | Patients in the expansion cohort will receive the investigator-selected dose of either 80 mg or 120 mg once da | FDA-EXPANSION-COHORTS-2022 · VI STATISTICAL CONSIDERATIONS | F03 |

주입 결함과 무관한 finding(정상판 기준 잘못 경고 후보, 사람 검토 필요):
- F06 [high/verified] The protocol specifies a 60-participant randomized candidate-dose comparison but does not state exposure-response models, estimands, precisi
- F08 [medium/verified] The protocol collects full serial PK profiles during escalation but only steady-state trough samples in the randomized candidate-dose cohort
- F09 [medium/held] The protocol states that four BOIN toxicity scenarios were simulated but does not report the assumptions, escalation boundaries, overdose co
- F10 [high/verified] The protocol excludes anti-PD-(L)1 therapy within four weeks before the first dose but provides no risk-based rationale or enhanced hepatic-

## AX1-012 — finding 11건, 주입 결함 6건, 토큰 61,485

| 결과 | 주입 결함(요약) | 원 규범 문서 | 매칭 finding |
|---|---|---|---|
| 🟡 span만 적중 | Interim safety and efficacy findings will be reviewed only after database lock at the end of the expansion pha | FDA-EXPANSION-COHORTS-2022 · II BACKGROUND | F04 |
| 🟡 span만 적중 | The study will enroll adults with untreated low-risk indolent lymphoma for whom standard curative therapy is a | FDA-EXPANSION-COHORTS-2022 · IV DRUG PRODUCT AND SUBJECT CO | F05 |
| 🟡 span만 적중 | This first-in-human dose-escalation study will enroll participants using an ad hoc design selected for operati | ICH-E4-1994 · IV GUIDANCE AND ADVICE | F01 |
| 🟡 span만 적중 | Blood samples will be collected for exploratory biomarker testing, but no pharmacokinetic sampling schedule or | FDA-DOSE-OPT-2024 · A Clinical Pharmacokinetics, P | F02 |
| 🟡 span만 적중 | Enrollment in the pediatric expansion cohort will be open to children with newly diagnosed or relapsed solid t | FDA-EXPANSION-COHORTS-2022 · H Evaluating PK, Tolerability, | F03 |
| ❌ 놓침 | Tolerability will be assessed exclusively through investigator-recorded adverse events and laboratory findings | FDA-DOSE-OPT-2024 · C Safety and Tolerability | - |

주입 결함과 무관한 finding(정상판 기준 잘못 경고 후보, 사람 검토 필요):
- F06 [high/verified] The protocol specifies at least 60 randomized subjects and cross-references integrated RP2D criteria but does not state the sample-size rati
- F07 [high/verified] The protocol limits randomized-cohort PK to steady-state trough samples and specifies a power-model dose-proportionality analysis without de
- F08 [high/verified] The protocol only cross-references Appendix B for hepatotoxicity, ILD/pneumonitis, and other adverse-reaction dose-modification rules, so th
- F09 [high/verified] The protocol specifies a four-week anti-PD-(L)1 washout but states no washout periods for other prior anticancer therapies. The sponsor shou
- F10 [medium/verified] The protocol identifies DV-101 as sotorasib and provides a structure and target but does not provide identity confirmation, assay-specific p

## AX1-013 — finding 11건, 주입 결함 6건, 토큰 58,063

| 결과 | 주입 결함(요약) | 원 규범 문서 | 매칭 finding |
|---|---|---|---|
| 🟡 span만 적중 | Enrollment in the pediatric expansion cohort will be open to children with newly diagnosed or relapsed solid t | FDA-EXPANSION-COHORTS-2022 · H Evaluating PK, Tolerability, | F03 |
| ❌ 놓침 | The sponsor will finalize the dose-comparison design and proceed directly to patient enrollment without seekin | MFDS-1443-01-2025 · 3.2 다양한 용량을 비교하기 위한 임상시험 설계 | - |
| 🟡 span만 적중 | During this first-in-human study, safety will be assessed only by participant-reported symptoms, and treatment | FDA-DOSE-OPT-2024 · A Clinical Pharmacokinetics, P | F02 |
| 🟡 span만 적중 | The study will enroll adults with untreated low-risk indolent lymphoma for whom standard curative therapy is a | FDA-EXPANSION-COHORTS-2022 · IV DRUG PRODUCT AND SUBJECT CO | F04 |
| 🟡 span만 적중 | Patients with moderate hepatic impairment and carriers of the ABCB1 variant will be enrolled only in the expan | FDA-DOSE-OPT-2024 · A Clinical Pharmacokinetics, P | F05 |
| 🟡 span만 적중 | After enrolling the initial three participants at 10 mg, the study will proceed directly to a fixed 10 mg expa | MFDS-1443-01-2025 · 1 안내서-1443-01 2025. 8. 29. 제정 | F01 |

주입 결함과 무관한 finding(정상판 기준 잘못 경고 후보, 사람 검토 필요):
- F06 [high/verified] The protocol places the operative hepatotoxicity and ILD/pneumonitis dose-modification rules in Appendix B, whose criteria are not present i
- F07 [high/verified] The protocol states that BOIN operating characteristics were evaluated under four toxicity scenarios but does not provide those scenarios, d
- F08 [high/verified] The protocol assigns RP2D selection to integrated criteria in Appendix D but does not show the quantitative exposure-response methods, estim
- F09 [high/verified] The protocol uses intensive first-dose and Day 15 sampling in escalation but collects only steady-state trough samples in the randomized can
- F10 [high/verified] The protocol specifies baseline, every-three-week, and monthly liver testing but does not define more frequent testing after transaminase or

## AX1-014 — finding 11건, 주입 결함 6건, 토큰 55,264

| 결과 | 주입 결함(요약) | 원 규범 문서 | 매칭 finding |
|---|---|---|---|
| 🟡 span만 적중 | For every participant, the dose-escalation algorithm will identify that individual’s optimal dose from observe | ICH-E4-1994 · IV GUIDANCE AND ADVICE | F05 |
| 🟡 span만 적중 | Pharmacokinetic blood samples will be collected only before dosing and at 1 hour after the first administratio | MFDS-1443-01-2025 · 3.1 임상 약동학, 약력학 및 약물유전체학 | F03 |
| 🟡 span만 적중 | After completing the dose-escalation study, participants will enroll into the expansion cohorts under the same | FDA-EXPANSION-COHORTS-2022 · A Initial Protocol | F07 |
| 🟡 span만 적중 | After identification of a potentially fatal dose-limiting toxicity during escalation, the study will open all  | FDA-EXPANSION-COHORTS-2022 · A Assessing Safety of Recommen | F01 |
| 🟡 span만 적중 | The sponsor will issue a single cumulative safety update to investigators and the IRB at the end of each calen | FDA-EXPANSION-COHORTS-2022 · C IRB/Independent Ethics Commi | F02 |
| 🟡 span만 적중 | The recommended Phase 2 dose will be selected using tumor response and exposure data only; treatment discontin | FDA-DOSE-OPT-2024 · C Safety and Tolerability | F00, F04 |

주입 결함과 무관한 finding(정상판 기준 잘못 경고 후보, 사람 검토 필요):
- F06 [high/verified] The protocol specifies at least 60 randomized subjects and comparison domains but does not state sample-size assumptions, estimands, stratif
- F08 [high/verified] The protocol states the BOIN target DLT rate, dose levels, maximum enrollment, and number of simulated scenarios but does not state cohort s
- F09 [high/held] The protocol lists five dose levels from 180 mg to 960 mg without stating the rationale for the starting dose, escalation increments, or ove
- F10 [high/verified] The protocol states routine baseline, every-three-week, and monthly liver testing but does not explicitly specify more frequent testing afte

## AX1-015 — finding 11건, 주입 결함 6건, 토큰 54,844

| 결과 | 주입 결함(요약) | 원 규범 문서 | 매칭 finding |
|---|---|---|---|
| 🟡 span만 적중 | The recommended Phase 2 dose will be selected solely from dose-limiting toxicity rates observed during Cycle 1 | FDA-DOSE-OPT-2024 · I INTRODUCTION | F03 |
| 🟡 span만 적중 | Dose selection for expansion will be based solely on observed tumor response rates, without adjustment for tre | ICH-E4-1994 · IV GUIDANCE AND ADVICE | F05 |
| 🟡 span만 적중 | The biomarker-selected expansion cohort will enroll 30 participants, with no assumptions, precision targets, h | FDA-EXPANSION-COHORTS-2022 · VI STATISTICAL CONSIDERATIONS | F07 |
| 🟡 span만 적중 | After the recommended starting dose is established, all subsequent participants will receive the same fixed do | ICH-E4-1994 · II OBTAINING DOSE-RESPONSE INF | F01 |
| 🟡 span만 적중 | This first-in-human dose-escalation study will enroll participants using an ad hoc design selected for operati | ICH-E4-1994 · IV GUIDANCE AND ADVICE | F02 |
| 🟡 span만 적중 | The combination expansion cohort will open after the first six participants complete cycle 1 of the investigat | FDA-EXPANSION-COHORTS-2022 · G Evaluating More Than One The | F04 |

주입 결함과 무관한 finding(정상판 기준 잘못 경고 후보, 사람 검토 필요):
- F06 [high/verified] The protocol specifies a BOIN design with a 30% target DLT rate and a maximum enrollment of 36 subjects but does not report its operating ch
- F08 [high/verified] The protocol specifies at least 60 participants randomized equally between two candidate doses and lists comparison domains, but the sentenc
- F09 [high/held] The protocol delegates hepatotoxicity and ILD/pneumonitis dose-modification rules to Appendix B without stating pulmonary symptom surveillan
- F10 [medium/verified] The protocol identifies DV-101 as sotorasib, characterizes it as an irreversible covalent KRAS G12C inhibitor, and provides a SMILES string.

## AX1-016 — finding 11건, 주입 결함 6건, 토큰 54,438

| 결과 | 주입 결함(요약) | 원 규범 문서 | 매칭 finding |
|---|---|---|---|
| 🟡 span만 적중 | The study will select the recommended Phase 2 dose from the first expansion cohort without collecting dose–res | ICH-E4-1994 · IV GUIDANCE AND ADVICE | F03 |
| 🟡 span만 적중 | The formulation-bridging expansion cohort will enroll participants receiving the new tablet or legacy capsule, | FDA-EXPANSION-COHORTS-2022 · F Evaluating Drug Product Chan | F06 |
| 🟡 span만 적중 | After identifying the first tolerable dose, all subsequent participants will receive only that dose, with no c | MFDS-1443-01-2025 · 3.2 다양한 용량을 비교하기 위한 임상시험 설계 | F02 |
| 🟡 span만 적중 | For this intravenous oncology study, the 500 mg dose will be prepared as a 50 mg/mL solution, requiring admini | MFDS-1443-01-2025 · 3.4 의약품의 함량 및 제형 | F01 |
| 🟡 span만 적중 | The disease-specific expansion cohort will enroll up to 60 participants without interim futility monitoring or | FDA-EXPANSION-COHORTS-2022 · B Evaluating Preliminary Antit | F07 |
| 🟡 span만 적중 | All recommendations in FDA-DOSE-OPT-2024 shall be implemented without deviation, and any investigator request  | FDA-DOSE-OPT-2024 · I INTRODUCTION | F10 |

주입 결함과 무관한 finding(정상판 기준 잘못 경고 후보, 사람 검토 필요):
- F04 [critical/held] The protocol delegates hepatotoxicity and interstitial lung disease/pneumonitis dose-modification rules to Appendix B, which is not included
- F05 [high/verified] The protocol specifies a 60-subject randomized comparison but does not state endpoint estimands, a sample-size rationale, analysis methods, 
- F08 [high/verified] The protocol limits randomized-cohort PK collection to steady-state trough samples and does not describe how first-dose or steady-state AUC 
- F09 [medium/held] The protocol states that four BOIN simulation scenarios were evaluated but does not provide their assumptions, operating-characteristic resu

## AX1-017 — finding 11건, 주입 결함 6건, 토큰 53,522

| 결과 | 주입 결함(요약) | 원 규범 문서 | 매칭 finding |
|---|---|---|---|
| 🟡 span만 적중 | Population pharmacokinetic analyses will be performed only after database lock using the final pooled dataset, | FDA-DOSE-OPT-2024 · A Clinical Pharmacokinetics, P | F08 |
| 🟡 span만 적중 | The study will select the recommended Phase 2 dose from the first dose level that meets the preliminary respon | FDA-DOSE-OPT-2024 · 7 See 21 CFR 312.42 | F02 |
| 🟡 span만 적중 | The recommended Phase 2 dose will be the highest dose tested with acceptable early laboratory findings, even i | FDA-DOSE-OPT-2024 · II BACKGROUND | F04 |
| 🟡 span만 적중 | Dose selection for expansion will be based solely on the prespecified primary endpoint from the escalation coh | ICH-E4-1994 · IV GUIDANCE AND ADVICE | F07 |
| 🟡 span만 적중 | The study will assess treatment activity using weekly change in body weight and evaluate safety primarily thro | MFDS-1443-01-2025 · 3.1 임상 약동학, 약력학 및 약물유전체학 | F01 |
| 🟡 span만 적중 | The protocol will continue enrollment in each expansion cohort until the planned sample size is reached, witho | FDA-EXPANSION-COHORTS-2022 · VI STATISTICAL CONSIDERATIONS | F03 |

주입 결함과 무관한 finding(정상판 기준 잘못 경고 후보, 사람 검토 필요):
- F05 [high/verified] The protocol randomizes at least 60 subjects equally between two candidate doses but does not state quantitative exposure-response methods o
- F06 [high/verified] The BOIN description states the target DLT rate, maximum enrollment, dose levels, and existence of four simulated scenarios but does not sta
- F09 [high/verified] The listed exclusion criteria specify a four-week washout only for anti-PD-(L)1 therapy and state no washout intervals for chemotherapy, rad
- F10 [high/verified] The protocol delegates hepatotoxicity, interstitial lung disease/pneumonitis, and other adverse-reaction dose-modification rules to Appendix

## AX1-018 — finding 11건, 주입 결함 6건, 토큰 58,494

| 결과 | 주입 결함(요약) | 원 규범 문서 | 매칭 finding |
|---|---|---|---|
| 🟡 span만 적중 | All participants will receive 80 mg orally twice daily from Cycle 1 Day 1, with no intra-patient dose escalati | ICH-E4-1994 · I INTRODUCTION | F01 |
| 🟡 span만 적중 | After the recommended Phase 2 dose is selected, no additional dose-optimization or comparative dose evaluation | FDA-DOSE-OPT-2024 · II BACKGROUND | F05 |
| 🟡 span만 적중 | The recommended Phase 2 dose will be selected solely from dose-limiting toxicity rates observed during Cycle 1 | FDA-DOSE-OPT-2024 · I INTRODUCTION | F03 |
| 🟡 span만 적중 | After the safety lead-in, all participants will receive 240 mg twice daily; no alternate dose will be evaluate | FDA-DOSE-OPT-2024 · B Trial Designs to Compare Mul | F02 |
| 🟡 span만 적중 | The recommended Phase 2 dose will be the highest dose tested with acceptable early laboratory findings, even i | FDA-DOSE-OPT-2024 · II BACKGROUND | F04 |
| 🟡 span만 적중 | Participants who cross over to the alternate dose will be included in the overall safety and response analyses | FDA-DOSE-OPT-2024 · B Trial Designs to Compare Mul | F06 |

주입 결함과 무관한 finding(정상판 기준 잘못 경고 후보, 사람 검토 필요):
- F07 [high/verified] The protocol collects only steady-state trough samples in the randomized candidate-dose cohorts and does not state a population-PK sampling 
- F08 [high/held] The protocol names the BOIN design, target DLT rate, maximum sample size, dose levels, and four simulation scenarios but does not state coho
- F09 [high/verified] The protocol plans to randomize at least 60 participants between two candidate doses but does not state the sample-size assumptions, precisi
- F10 [high/verified] The protocol sentence refers hepatotoxicity, interstitial lung disease/pneumonitis, and other adverse-reaction dose modifications to Appendi

## AX1-019 — finding 11건, 주입 결함 6건, 토큰 58,950

| 결과 | 주입 결함(요약) | 원 규범 문서 | 매칭 finding |
|---|---|---|---|
| 🟡 span만 적중 | After the recommended Phase 2 dose is selected from tolerability data, all subsequent participants will receiv | ICH-E4-1994 · II OBTAINING DOSE-RESPONSE INF | F03 |
| 🟡 span만 적중 | In this open-label, single-arm Phase 1/2 study, treatment activity will be assessed against historical respons | ICH-E4-1994 · IV GUIDANCE AND ADVICE | F05 |
| 🟡 span만 적중 | Dose-response analyses will be limited to the randomized expansion cohort, and data from dose-escalation parti | ICH-E4-1994 · II OBTAINING DOSE-RESPONSE INF | F07 |
| 🟡 span만 적중 | After enrolling the initial three participants at 10 mg, the study will proceed directly to a fixed 10 mg expa | MFDS-1443-01-2025 · 1 안내서-1443-01 2025. 8. 29. 제정 | F01, F02, F06, F08 |
| 🟡 span만 적중 | All participants will receive the fixed 200 mg dose supplied in a single capsule strength throughout the study | FDA-DOSE-OPT-2024 · D Drug Formulation | F01, F04 |
| ❌ 놓침 | Results from the expansion cohort will serve as the primary efficacy package for the planned marketing applica | FDA-EXPANSION-COHORTS-2022 · C Communications and Interacti | - |

주입 결함과 무관한 finding(정상판 기준 잘못 경고 후보, 사람 검토 필요):
- F09 [high/held] The protocol places the hepatotoxicity, interstitial lung disease/pneumonitis, and other adverse-reaction dose-modification rules in Appendi
- F10 [medium/held] The supplied eligibility criteria specify a four-week washout only for anti-PD-(L)1 therapy and state no washout intervals for other systemi

## AX1-020 — finding 11건, 주입 결함 6건, 토큰 58,169

| 결과 | 주입 결함(요약) | 원 규범 문서 | 매칭 finding |
|---|---|---|---|
| ❌ 놓침 | The study team will review emerging adverse-event data periodically and decide during the trial whether enroll | FDA-DOSE-OPT-2024 · C Safety and Tolerability | - |
| ✅ 근거까지 적중 | Patients with moderate hepatic impairment and the CYP2C19 poor-metabolizer genotype will be enrolled in the sa | FDA-DOSE-OPT-2024 · A Clinical Pharmacokinetics, P | F06 |
| ❌ 놓침 | Results from the expansion cohort will serve as the primary efficacy package for the planned marketing applica | FDA-EXPANSION-COHORTS-2022 · C Communications and Interacti | - |
| 🟡 span만 적중 | The expansion cohort will enroll 80 patients at 200 mg twice daily immediately after the first three participa | FDA-DOSE-OPT-2024 · III DOSAGE OPTIMIZATION RECOMM | F02, F03 |
| 🟡 span만 적중 | Blood samples will be collected for exploratory biomarker testing, but no pharmacokinetic sampling schedule or | FDA-DOSE-OPT-2024 · A Clinical Pharmacokinetics, P | F04 |
| 🟡 span만 적중 | The recommended Phase 2 dose will be selected solely from the highest tolerated dose in the escalation cohort, | FDA-DOSE-OPT-2024 · A Clinical Pharmacokinetics, P | F00, F01 |

주입 결함과 무관한 finding(정상판 기준 잘못 경고 후보, 사람 검토 필요):
- F05 [high/verified] The BOIN description states the target DLT rate, maximum sample size, dose levels, and existence of simulations but does not state the cohor
- F07 [high/held] The randomized dose cohorts have only steady-state trough sampling, while intensive sampling and dose-proportionality assessment are assigne
- F08 [medium/verified] The protocol specifies baseline, every-three-week, and monthly liver testing but does not expressly specify more frequent testing after tran
- F09 [medium/verified] The protocol delegates management of hepatotoxicity, ILD/pneumonitis, and unspecified other adverse reactions to Appendix B without presenti
- F10 [medium/verified] The protocol excludes anti-PD-(L)1 therapy within four weeks before the first dose but states no eligibility conditions based on delayed imm

