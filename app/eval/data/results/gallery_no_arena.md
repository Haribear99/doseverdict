# 실패 사례 갤러리 — no_arena

놓친 결함과 잘못 경고한 사례를 그대로 공개한다(제안서 4장 약속).
합계: 주입 결함 120건 중 놓침 5건, finding 211건 중 무관 72건.

## AX1-001 — finding 11건, 주입 결함 6건, 토큰 27,697

| 결과 | 주입 결함(요약) | 원 규범 문서 | 매칭 finding |
|---|---|---|---|
| 🟡 span만 적중 | The study team will review emerging adverse-event data periodically and decide during the trial whether enroll | FDA-DOSE-OPT-2024 · C Safety and Tolerability | F07 |
| 🟡 span만 적중 | All participants will receive the fixed 200 mg dose supplied in a single capsule strength throughout the study | FDA-DOSE-OPT-2024 · D Drug Formulation | F01 |
| 🟡 span만 적중 | The formulation-bridging expansion cohort will enroll participants receiving the new tablet or legacy capsule, | FDA-EXPANSION-COHORTS-2022 · F Evaluating Drug Product Chan | F06 |
| 🟡 span만 적중 | After the recommended Phase 2 dose is selected from tolerability data, all subsequent participants will receiv | ICH-E4-1994 · II OBTAINING DOSE-RESPONSE INF | F02 |
| 🟡 span만 적중 | Patients with moderate hepatic impairment and the CYP2C19 poor-metabolizer genotype will be enrolled in the sa | FDA-DOSE-OPT-2024 · A Clinical Pharmacokinetics, P | F10 |
| ❌ 놓침 | Dose–response analyses will be conducted only in the overall enrolled population, with no evaluations by age,  | ICH-E4-1994 · IV GUIDANCE AND ADVICE | - |

주입 결함과 무관한 finding(정상판 기준 잘못 경고 후보, 사람 검토 필요):
- F03 [high/verified] The protocol prespecifies a dose-proportionality power model but does not specify analyses linking individual exposure to safety, tolerabili
- F04 [high/verified] The protocol limits randomized-cohort PK collection to steady-state trough samples and does not describe a population-PK method for estimati
- F05 [high/verified] The protocol specifies at least 60 randomized subjects but does not state the assumptions, precision targets, estimands, analysis population
- F08 [high/verified] The protocol specifies baseline, every-three-week, and monthly liver testing but does not expressly specify more frequent testing after tran
- F09 [high/verified] The protocol refers to four simulated toxicity scenarios in Appendix C but does not present the cohort size, BOIN boundaries, overdose-elimi

## AX1-002 — finding 11건, 주입 결함 6건, 토큰 31,551

| 결과 | 주입 결함(요약) | 원 규범 문서 | 매칭 finding |
|---|---|---|---|
| 🟡 span만 적중 | Results from the expansion cohort will serve as the primary efficacy package for the planned marketing applica | FDA-EXPANSION-COHORTS-2022 · C Communications and Interacti | F05 |
| 🟡 span만 적중 | The recommended Phase 2 dose will be the highest dose at which no more than 30% of participants permanently di | ICH-E4-1994 · II OBTAINING DOSE-RESPONSE INF | F00, F03 |
| ✅ 근거까지 적중 | Patients with moderate hepatic impairment and the CYP2C19 poor-metabolizer genotype will be enrolled in the sa | FDA-DOSE-OPT-2024 · A Clinical Pharmacokinetics, P | F06 |
| 🟡 span만 적중 | The sponsor will issue a single cumulative safety update to investigators and the IRB at the end of each calen | FDA-EXPANSION-COHORTS-2022 · C IRB/Independent Ethics Commi | F02 |
| 🟡 span만 적중 | The combination expansion cohort will open after the first six participants complete cycle 1 of the investigat | FDA-EXPANSION-COHORTS-2022 · G Evaluating More Than One The | F04 |
| 🟡 span만 적중 | The expansion cohort will support the marketing application using investigator-assessed tumor responses at the | FDA-EXPANSION-COHORTS-2022 · B Evaluating Preliminary Antit | F01 |

주입 결함과 무관한 finding(정상판 기준 잘못 경고 후보, 사람 검토 필요):
- F07 [high/verified] The protocol randomizes at least 60 participants equally between two candidate doses but does not state endpoint definitions or a sample-siz
- F08 [high/verified] The protocol limits randomized-cohort PK collection to steady-state troughs and specifies a power-model dose-proportionality assessment with
- F09 [high/verified] The synopsis identifies a BOIN target, maximum sample size, dose levels, and simulations but does not state the executable escalation, evalu
- F10 [low/verified] The protocol identifies DV-101 as sotorasib, describes it as an irreversible covalent KRAS G12C inhibitor, and provides a SMILES containing 

## AX1-003 — finding 11건, 주입 결함 6건, 토큰 29,934

| 결과 | 주입 결함(요약) | 원 규범 문서 | 매칭 finding |
|---|---|---|---|
| 🟡 span만 적중 | The recommended Phase 2 dose will be the highest dose at which no more than 30% of participants permanently di | ICH-E4-1994 · II OBTAINING DOSE-RESPONSE INF | F00, F01 |
| 🟡 span만 적중 | After the safety lead-in, all participants will receive 240 mg twice daily; no alternate dose will be evaluate | FDA-DOSE-OPT-2024 · B Trial Designs to Compare Mul | F02 |
| 🟡 span만 적중 | The study team will review emerging adverse-event data periodically and decide during the trial whether enroll | FDA-DOSE-OPT-2024 · C Safety and Tolerability | F09 |
| ❌ 놓침 | Concomitant medications will be recorded at enrollment, but no interaction studies or dedicated pharmacokineti | FDA-DOSE-OPT-2024 · A Clinical Pharmacokinetics, P | - |
| 🟡 span만 적중 | For the randomized Phase 2 portion, each of the three active-dose arms will be compared independently with pla | FDA-DOSE-OPT-2024 · B Trial Designs to Compare Mul | F03 |
| 🟡 span만 적중 | All recommendations in FDA-DOSE-OPT-2024 shall be implemented without deviation, and any investigator request  | FDA-DOSE-OPT-2024 · I INTRODUCTION | F10 |

주입 결함과 무관한 finding(정상판 기준 잘못 경고 후보, 사람 검토 필요):
- F04 [high/verified] The liver-test schedule matches baseline, every-three-week, and monthly intervals but does not specify more frequent testing after transamin
- F05 [high/verified] The protocol delegates dose-interruption, reduction, rechallenge, and discontinuation rules to Appendix B, which is not included in the supp
- F06 [high/verified] The supplied text gives the BOIN target DLT rate, maximum enrollment, dose levels, and existence of simulations but does not provide cohort 
- F07 [high/verified] The sentence sets a minimum randomized sample size of 60 but provides no effect-size, precision, evaluability, or dose-selection-probability
- F08 [high/verified] The randomized cohorts have only steady-state trough sampling specified, with no population-PK or other analysis plan stated for estimating 

## AX1-004 — finding 11건, 주입 결함 6건, 토큰 29,328

| 결과 | 주입 결함(요약) | 원 규범 문서 | 매칭 finding |
|---|---|---|---|
| 🟡 span만 적중 | The dose-escalation and expansion cohorts will follow the same general treatment plan, with cohort-specific do | FDA-EXPANSION-COHORTS-2022 · A Initial Protocol | F08, F09 |
| 🟡 span만 적중 | The randomized Phase 2 portion will compare three active dose levels with placebo, and each dose-versus-placeb | MFDS-1443-01-2025 · 3.2 다양한 용량을 비교하기 위한 임상시험 설계 | F01, F05 |
| 🟡 span만 적중 | Participants will be enrolled sequentially into nonrandomized cohorts receiving 10, 30, or 60 mg once daily, w | FDA-DOSE-OPT-2024 · B Trial Designs to Compare Mul | F06 |
| 🟡 span만 적중 | All doses will be prepared as a fixed 0.5 mg/mL intravenous solution, including doses requiring infusion volum | FDA-DOSE-OPT-2024 · D Drug Formulation | F04 |
| 🟡 span만 적중 | 확장 코호트에서는 선행 임상자료나 노출·반응 분석과 무관하게 모든 환자에게 임상적으로 사용되는 표준 용량 200 mg을 투여한다. | MFDS-1443-01-2025 · 1 안내서-1443-01 2025. 8. 29. 제정 | F02 |
| 🟡 span만 적중 | Dose selection for expansion will be based solely on observed tumor response rates, without adjustment for tre | ICH-E4-1994 · IV GUIDANCE AND ADVICE | F03 |

주입 결함과 무관한 finding(정상판 기준 잘못 경고 후보, 사람 검토 필요):
- F07 [high/verified] The protocol assigns at least 60 subjects 1:1 between two candidate doses but provides no endpoint-specific precision, operating characteris
- F10 [medium/verified] The protocol collects only steady-state trough samples in randomized dose-comparison subjects and does not describe how their AUC, Cmax, acc

## AX1-005 — finding 11건, 주입 결함 6건, 토큰 30,002

| 결과 | 주입 결함(요약) | 원 규범 문서 | 매칭 finding |
|---|---|---|---|
| 🟡 span만 적중 | The study team will review emerging adverse-event data periodically and decide during the trial whether enroll | FDA-DOSE-OPT-2024 · C Safety and Tolerability | F05 |
| 🟡 span만 적중 | In the pediatric expansion cohort, safety will be assessed only by recording adverse events at scheduled clini | FDA-EXPANSION-COHORTS-2022 · H Evaluating PK, Tolerability, | F03 |
| 🟡 span만 적중 | This amendment adds a higher-dose expansion cohort based on preliminary efficacy findings; the safety rational | FDA-EXPANSION-COHORTS-2022 · A Safety Monitoring and Report | F04 |
| 🟡 span만 적중 | The expansion cohort will support the marketing application using investigator-assessed tumor responses at the | FDA-EXPANSION-COHORTS-2022 · B Evaluating Preliminary Antit | F02 |
| 🟡 span만 적중 | No pharmacodynamic or pharmacogenomic specimens will be collected, and the study will not evaluate genetic det | FDA-DOSE-OPT-2024 · A Clinical Pharmacokinetics, P | F08 |
| 🟡 span만 적중 | The study will be conducted under the sponsor's internal approval without submission of the final protocol to  | ICH-E4-1994 · 0 PREAMBLE | F01 |

주입 결함과 무관한 finding(정상판 기준 잘못 경고 후보, 사람 검토 필요):
- F06 [high/verified] The protocol assigns at least 60 subjects equally between two candidate doses without stating a sample-size justification or operating chara
- F07 [high/verified] The protocol collects intensive PK samples only in escalation subjects and limits randomized candidate-dose cohorts to steady-state trough s
- F09 [high/held] The protocol lists five dose levels from 180 mg to 960 mg without stating the PK or dose-response rationale for selecting that range and spa
- F10 [medium/verified] The protocol caps BOIN escalation at 36 subjects across five dose levels and refers to simulations under four toxicity scenarios without pre

## AX1-006 — finding 11건, 주입 결함 6건, 토큰 30,725

| 결과 | 주입 결함(요약) | 원 규범 문서 | 매칭 finding |
|---|---|---|---|
| 🟡 span만 적중 | The recommended Phase 2 dose will be the highest dose tested with acceptable early laboratory findings, even i | FDA-DOSE-OPT-2024 · II BACKGROUND | F01 |
| ❌ 놓침 | The sponsor will compile aggregate safety data internally and submit cumulative reports to FDA at its discreti | FDA-EXPANSION-COHORTS-2022 · A Safety Monitoring and Report | - |
| 🟡 span만 적중 | The study will enroll adults with untreated low-risk indolent lymphoma for whom standard curative therapy is a | FDA-EXPANSION-COHORTS-2022 · IV DRUG PRODUCT AND SUBJECT CO | F03 |
| 🟡 span만 적중 | Participants who cross over to the alternate dose will be included in the overall safety and response analyses | FDA-DOSE-OPT-2024 · B Trial Designs to Compare Mul | F04 |
| ✅ 근거까지 적중 | The Phase 2 expansion dose will be fixed at 200 mg twice daily based solely on the recommended Phase 1 dose, w | FDA-DOSE-OPT-2024 · III DOSAGE OPTIMIZATION RECOMM | F02 |
| 🟡 span만 적중 | Results from the expansion cohort will serve as the primary efficacy package for the planned marketing applica | FDA-EXPANSION-COHORTS-2022 · C Communications and Interacti | F10 |

주입 결함과 무관한 finding(정상판 기준 잘못 경고 후보, 사람 검토 필요):
- F05 [high/verified] The protocol specifies baseline testing, testing every three weeks for three months, and monthly testing thereafter, but does not expressly 
- F06 [high/verified] The protocol delegates hepatotoxicity and interstitial lung disease/pneumonitis dose-modification rules to an unavailable Appendix B. Liver 
- F07 [high/held] The protocol specifies a 60-subject randomized comparison but does not state its sample-size rationale, tumor-stratum allocation, estimands,
- F08 [high/verified] The protocol collects intensive PK profiles during escalation but only steady-state trough samples in randomized cohorts and specifies only 
- F09 [high/verified] The protocol caps the five-level BOIN escalation at 36 subjects and places the operating-characteristic simulations and their design assumpt

## AX1-007 — finding 10건, 주입 결함 6건, 토큰 30,521

| 결과 | 주입 결함(요약) | 원 규범 문서 | 매칭 finding |
|---|---|---|---|
| 🟡 span만 적중 | For the new pembrolizumab–investigational-agent combination in metastatic colorectal cancer, the study will pr | MFDS-1443-01-2025 · 3.5 후속 적응증 및 용법 | F05 |
| 🟡 span만 적중 | 확장 코호트에서는 선행 임상자료나 노출·반응 분석과 무관하게 모든 환자에게 임상적으로 사용되는 표준 용량 200 mg을 투여한다. | MFDS-1443-01-2025 · 1 안내서-1443-01 2025. 8. 29. 제정 | F04 |
| 🟡 span만 적중 | Interim safety and efficacy findings will be reviewed only after database lock at the end of the expansion pha | FDA-EXPANSION-COHORTS-2022 · II BACKGROUND | F03 |
| 🟡 span만 적중 | The formulation-bridging expansion cohort will enroll participants receiving the new tablet or legacy capsule, | FDA-EXPANSION-COHORTS-2022 · F Evaluating Drug Product Chan | F06 |
| 🟡 span만 적중 | After the recommended Phase 2 dose is selected from tolerability data, all subsequent participants will receiv | ICH-E4-1994 · II OBTAINING DOSE-RESPONSE INF | F02 |
| 🟡 span만 적중 | The starting dose and subsequent escalation levels will be selected solely by investigator consensus, without  | FDA-DOSE-OPT-2024 · III DOSAGE OPTIMIZATION RECOMM | F01 |

주입 결함과 무관한 finding(정상판 기준 잘못 경고 후보, 사람 검토 필요):
- F07 [high/verified] The protocol prespecifies intensive and trough PK sampling and a dose-proportionality power model but does not specify exposure-safety, expo
- F08 [high/verified] The protocol caps a five-level BOIN escalation at 36 subjects and refers to operating-characteristic simulations in Appendix C without prese
- F09 [medium/verified] The protocol identifies DV-101 as an irreversible covalent KRAS G12C inhibitor and supplies its SMILES but provides no compound-specific bio

## AX1-008 — finding 11건, 주입 결함 6건, 토큰 29,357

| 결과 | 주입 결함(요약) | 원 규범 문서 | 매칭 finding |
|---|---|---|---|
| 🟡 span만 적중 | After participants complete 48 hours at the assigned dose level, the dose-response analysis will be performed  | ICH-E4-1994 · 1 Parallel dose-response | F03 |
| 🟡 span만 적중 | Dose–response analyses will be conducted only in the overall enrolled population, with no evaluations by age,  | ICH-E4-1994 · IV GUIDANCE AND ADVICE | F05 |
| 🟡 span만 적중 | The study will select the recommended Phase 2 dose from the first expansion cohort without collecting dose–res | ICH-E4-1994 · IV GUIDANCE AND ADVICE | F02 |
| 🟡 span만 적중 | After completing the dose-escalation portion, the study will open six parallel disease-specific expansion coho | FDA-EXPANSION-COHORTS-2022 · IV DRUG PRODUCT AND SUBJECT CO | F04 |
| 🟡 span만 적중 | The sponsor will include serious and unexpected adverse safety findings in the next scheduled annual safety re | FDA-EXPANSION-COHORTS-2022 · B Potential Opportunities and  | F01 |
| 🟡 span만 적중 | Participants will be enrolled sequentially into nonrandomized cohorts receiving 10, 30, or 60 mg once daily, w | FDA-DOSE-OPT-2024 · B Trial Designs to Compare Mul | F06 |

주입 결함과 무관한 finding(정상판 기준 잘못 경고 후보, 사람 검토 필요):
- F07 [high/held] The protocol specifies a BOIN target DLT rate and maximum sample size but does not state cohort size, DLT window, decision boundaries, evalu
- F08 [high/verified] The protocol collects only steady-state trough samples in randomized cohorts and does not state a population-PK method for estimating indivi
- F09 [high/held] The supplied protocol refers dose-modification rules to Appendix B without presenting toxicity grades, interruption and recovery criteria, r
- F10 [high/verified] The protocol specifies baseline, every-three-week, and monthly liver testing but does not explicitly prescribe more frequent testing after t

## AX1-009 — finding 11건, 주입 결함 6건, 토큰 29,920

| 결과 | 주입 결함(요약) | 원 규범 문서 | 매칭 finding |
|---|---|---|---|
| 🟡 span만 적중 | The sponsor will finalize the dose-comparison design and proceed directly to patient enrollment without seekin | MFDS-1443-01-2025 · 3.2 다양한 용량을 비교하기 위한 임상시험 설계 | F05 |
| 🟡 span만 적중 | After the sponsor transfers production to a new manufacturing site and changes the formulation, the study will | FDA-EXPANSION-COHORTS-2022 · F Evaluating Drug Product Chan | F03 |
| 🟡 span만 적중 | For every participant, the dose-escalation algorithm will identify that individual’s optimal dose from observe | ICH-E4-1994 · IV GUIDANCE AND ADVICE | F02 |
| 🟡 span만 적중 | Participants may take the study tablets with or without meals and may continue all clinically indicated concom | FDA-DOSE-OPT-2024 · A Clinical Pharmacokinetics, P | F08 |
| 🟡 span만 적중 | The medical monitor may be any licensed physician with general inpatient-care experience; prior oncology pract | FDA-EXPANSION-COHORTS-2022 · A Safety Monitoring and Report | F09 |
| 🟡 span만 적중 | The Phase 1 portion will escalate cohorts until the highest dose with an acceptable toxicity profile is identi | FDA-DOSE-OPT-2024 · II BACKGROUND | F01 |

주입 결함과 무관한 finding(정상판 기준 잘못 경고 후보, 사람 검토 필요):
- F04 [high/verified] The protocol specifies at least 60 randomized subjects and the comparison domains but does not state the statistical assumptions, estimands,
- F06 [high/held] The protocol specifies a five-dose BOIN design with a 30% target DLT rate and maximum sample size of 36 but places its operating-characteris
- F07 [high/verified] The protocol collects intensive first-dose and steady-state profiles in escalation but only steady-state trough samples in the randomized co
- F10 [low/verified] The protocol identifies DV-101 as an irreversible covalent KRAS G12C inhibitor and provides its SMILES structure without making an organ-spe

## AX1-010 — finding 11건, 주입 결함 6건, 토큰 28,805

| 결과 | 주입 결함(요약) | 원 규범 문서 | 매칭 finding |
|---|---|---|---|
| 🟡 span만 적중 | In the pediatric expansion cohort, safety will be assessed only by recording adverse events at scheduled clini | FDA-EXPANSION-COHORTS-2022 · H Evaluating PK, Tolerability, | F01 |
| 🟡 span만 적중 | The pediatric expansion cohort will proceed under the adult development plan, with pediatric assessments docum | FDA-EXPANSION-COHORTS-2022 · H Evaluating PK, Tolerability, | F03 |
| 🟡 span만 적중 | Dose selection for expansion will be based solely on the prespecified primary endpoint from the escalation coh | ICH-E4-1994 · IV GUIDANCE AND ADVICE | F05 |
| 🟡 span만 적중 | Participants assigned to the control arm may cross over to the investigational therapy after progression; safe | MFDS-1443-01-2025 · 3.2 다양한 용량을 비교하기 위한 임상시험 설계 | F06 |
| 🟡 span만 적중 | The medical monitor may be any licensed physician with general inpatient-care experience; prior oncology pract | FDA-EXPANSION-COHORTS-2022 · A Safety Monitoring and Report | F10 |
| 🟡 span만 적중 | The recommended Phase 2 dose will be selected solely from dose-limiting toxicity rates observed during Cycle 1 | FDA-DOSE-OPT-2024 · I INTRODUCTION | F02 |

주입 결함과 무관한 finding(정상판 기준 잘못 경고 후보, 사람 검토 필요):
- F04 [critical/verified] The only stated inclusion criterion for age is age 18 years or older despite the protocol's inclusion of a pediatric expansion cohort. Spons
- F07 [high/verified] The protocol assigns at least 30 subjects to each candidate dose but provides no sample-size rationale or decision thresholds in this senten
- F08 [high/verified] The synopsis identifies the BOIN target, maximum sample size, dose levels, and four simulated scenarios but does not state cohort sizes, dec
- F09 [high/verified] The randomized cohorts have steady-state trough sampling only, and the protocol does not state how AUC, Cmax, or individual exposure metrics

## AX1-011 — finding 9건, 주입 결함 6건, 토큰 29,943

| 결과 | 주입 결함(요약) | 원 규범 문서 | 매칭 finding |
|---|---|---|---|
| 🟡 span만 적중 | Protocol deviations will be reviewed individually by the study team, with importance assigned after database l | ICH-E6R3-2025 · 3.9.1 The sponsor should ensur | F08 |
| 🟡 span만 적중 | Pharmacokinetic analyses will use pooled data without examining covariates or reporting results by clinically  | MFDS-1443-01-2025 · 3.1 임상 약동학, 약력학 및 약물유전체학 | F05 |
| 🟡 span만 적중 | The study will assess treatment activity using weekly change in body weight and evaluate safety primarily thro | MFDS-1443-01-2025 · 3.1 임상 약동학, 약력학 및 약물유전체학 | F02 |
| 🟡 span만 적중 | The sponsor will include serious and unexpected adverse safety findings in the next scheduled annual safety re | FDA-EXPANSION-COHORTS-2022 · B Potential Opportunities and  | F01 |
| ✅ 근거까지 적중 | Patients with moderate hepatic impairment and the CYP2C19 poor-metabolizer genotype will be enrolled in the sa | FDA-DOSE-OPT-2024 · A Clinical Pharmacokinetics, P | F04 |
| 🟡 span만 적중 | Patients in the expansion cohort will receive the investigator-selected dose of either 80 mg or 120 mg once da | FDA-EXPANSION-COHORTS-2022 · VI STATISTICAL CONSIDERATIONS | F03 |

주입 결함과 무관한 finding(정상판 기준 잘못 경고 후보, 사람 검토 필요):
- F06 [high/verified] The protocol provides intensive first-dose and steady-state PK sampling in escalation subjects but limits randomized-cohort PK sampling to s
- F07 [high/held] The synopsis states the BOIN target DLT rate, maximum sample size, dose levels, and existence of four simulation scenarios but does not stat

## AX1-012 — finding 11건, 주입 결함 6건, 토큰 30,244

| 결과 | 주입 결함(요약) | 원 규범 문서 | 매칭 finding |
|---|---|---|---|
| 🟡 span만 적중 | Interim safety and efficacy findings will be reviewed only after database lock at the end of the expansion pha | FDA-EXPANSION-COHORTS-2022 · II BACKGROUND | F04 |
| 🟡 span만 적중 | The study will enroll adults with untreated low-risk indolent lymphoma for whom standard curative therapy is a | FDA-EXPANSION-COHORTS-2022 · IV DRUG PRODUCT AND SUBJECT CO | F02 |
| 🟡 span만 적중 | This first-in-human dose-escalation study will enroll participants using an ad hoc design selected for operati | ICH-E4-1994 · IV GUIDANCE AND ADVICE | F01 |
| 🟡 span만 적중 | Blood samples will be collected for exploratory biomarker testing, but no pharmacokinetic sampling schedule or | FDA-DOSE-OPT-2024 · A Clinical Pharmacokinetics, P | F06 |
| 🟡 span만 적중 | Enrollment in the pediatric expansion cohort will be open to children with newly diagnosed or relapsed solid t | FDA-EXPANSION-COHORTS-2022 · H Evaluating PK, Tolerability, | F03 |
| 🟡 span만 적중 | Tolerability will be assessed exclusively through investigator-recorded adverse events and laboratory findings | FDA-DOSE-OPT-2024 · C Safety and Tolerability | F10 |

주입 결함과 무관한 finding(정상판 기준 잘못 경고 후보, 사람 검토 필요):
- F05 [high/held] The protocol lists five planned dose levels from 180 mg through 960 mg without giving the scientific basis for the starting dose, increments
- F07 [high/verified] The protocol specifies at least 60 randomized subjects and 1:1 allocation but does not provide a sample-size justification or early stopping
- F08 [high/held] The protocol delegates dose-modification rules for hepatotoxicity, interstitial lung disease/pneumonitis, and other adverse reactions to App
- F09 [medium/verified] The protocol identifies DV-101 as an irreversible covalent KRAS G12C inhibitor and provides its structure and target, but this passage conta

## AX1-013 — finding 11건, 주입 결함 6건, 토큰 30,500

| 결과 | 주입 결함(요약) | 원 규범 문서 | 매칭 finding |
|---|---|---|---|
| 🟡 span만 적중 | Enrollment in the pediatric expansion cohort will be open to children with newly diagnosed or relapsed solid t | FDA-EXPANSION-COHORTS-2022 · H Evaluating PK, Tolerability, | F02 |
| 🟡 span만 적중 | The sponsor will finalize the dose-comparison design and proceed directly to patient enrollment without seekin | MFDS-1443-01-2025 · 3.2 다양한 용량을 비교하기 위한 임상시험 설계 | F05 |
| 🟡 span만 적중 | During this first-in-human study, safety will be assessed only by participant-reported symptoms, and treatment | FDA-DOSE-OPT-2024 · A Clinical Pharmacokinetics, P | F03 |
| 🟡 span만 적중 | The study will enroll adults with untreated low-risk indolent lymphoma for whom standard curative therapy is a | FDA-EXPANSION-COHORTS-2022 · IV DRUG PRODUCT AND SUBJECT CO | F04 |
| 🟡 span만 적중 | Patients with moderate hepatic impairment and carriers of the ABCB1 variant will be enrolled only in the expan | FDA-DOSE-OPT-2024 · A Clinical Pharmacokinetics, P | F08 |
| 🟡 span만 적중 | After enrolling the initial three participants at 10 mg, the study will proceed directly to a fixed 10 mg expa | MFDS-1443-01-2025 · 1 안내서-1443-01 2025. 8. 29. 제정 | F01 |

주입 결함과 무관한 finding(정상판 기준 잘못 경고 후보, 사람 검토 필요):
- F06 [high/verified] The protocol provides intensive first-dose and steady-state PK sampling in escalation but limits randomized-cohort PK collection to steady-s
- F07 [high/held] The protocol specifies a 60-subject randomized comparison but does not state the dose-selection estimand, precision target, sample-size assu
- F09 [high/verified] The BOIN design uses a 30% target DLT rate, five planned dose levels, and a maximum of 36 subjects, with operating characteristics delegated
- F10 [medium/verified] The protocol identifies DV-101 as an irreversible covalent inhibitor and provides its structure and target but provides no compound-specific

## AX1-014 — finding 9건, 주입 결함 6건, 토큰 29,405

| 결과 | 주입 결함(요약) | 원 규범 문서 | 매칭 finding |
|---|---|---|---|
| 🟡 span만 적중 | For every participant, the dose-escalation algorithm will identify that individual’s optimal dose from observe | ICH-E4-1994 · IV GUIDANCE AND ADVICE | F05 |
| 🟡 span만 적중 | Pharmacokinetic blood samples will be collected only before dosing and at 1 hour after the first administratio | MFDS-1443-01-2025 · 3.1 임상 약동학, 약력학 및 약물유전체학 | F04, F07 |
| 🟡 span만 적중 | After completing the dose-escalation study, participants will enroll into the expansion cohorts under the same | FDA-EXPANSION-COHORTS-2022 · A Initial Protocol | F06 |
| 🟡 span만 적중 | After identification of a potentially fatal dose-limiting toxicity during escalation, the study will open all  | FDA-EXPANSION-COHORTS-2022 · A Assessing Safety of Recommen | F01 |
| 🟡 span만 적중 | The sponsor will issue a single cumulative safety update to investigators and the IRB at the end of each calen | FDA-EXPANSION-COHORTS-2022 · C IRB/Independent Ethics Commi | F03 |
| 🟡 span만 적중 | The recommended Phase 2 dose will be selected using tumor response and exposure data only; treatment discontin | FDA-DOSE-OPT-2024 · C Safety and Tolerability | F02 |

주입 결함과 무관한 finding(정상판 기준 잘못 경고 후보, 사람 검토 필요):
- F08 [medium/verified] The protocol assigns at least 60 participants equally between two candidate doses but provides no statistical assumptions, precision targets

## AX1-015 — finding 11건, 주입 결함 6건, 토큰 29,508

| 결과 | 주입 결함(요약) | 원 규범 문서 | 매칭 finding |
|---|---|---|---|
| 🟡 span만 적중 | The recommended Phase 2 dose will be selected solely from dose-limiting toxicity rates observed during Cycle 1 | FDA-DOSE-OPT-2024 · I INTRODUCTION | F03 |
| 🟡 span만 적중 | Dose selection for expansion will be based solely on observed tumor response rates, without adjustment for tre | ICH-E4-1994 · IV GUIDANCE AND ADVICE | F06 |
| 🟡 span만 적중 | The biomarker-selected expansion cohort will enroll 30 participants, with no assumptions, precision targets, h | FDA-EXPANSION-COHORTS-2022 · VI STATISTICAL CONSIDERATIONS | F04 |
| 🟡 span만 적중 | After the recommended starting dose is established, all subsequent participants will receive the same fixed do | ICH-E4-1994 · II OBTAINING DOSE-RESPONSE INF | F01 |
| 🟡 span만 적중 | This first-in-human dose-escalation study will enroll participants using an ad hoc design selected for operati | ICH-E4-1994 · IV GUIDANCE AND ADVICE | F02 |
| 🟡 span만 적중 | The combination expansion cohort will open after the first six participants complete cycle 1 of the investigat | FDA-EXPANSION-COHORTS-2022 · G Evaluating More Than One The | F05 |

주입 결함과 무관한 finding(정상판 기준 잘못 경고 후보, 사람 검토 필요):
- F07 [high/verified] The protocol provides intensive first-dose and steady-state sampling in escalation subjects but limits randomized-cohort PK collection to st
- F08 [high/verified] The synopsis identifies the BOIN target, maximum sample size, dose levels, and four simulated toxicity scenarios but does not state cohort s
- F09 [high/verified] The protocol schedules liver tests before treatment, every three weeks for the first three months, and monthly thereafter or as clinically i
- F10 [high/verified] The synopsis only cross-references Appendix B for dose-modification rules and does not itself provide interruption, reduction, discontinuati

## AX1-016 — finding 11건, 주입 결함 6건, 토큰 29,037

| 결과 | 주입 결함(요약) | 원 규범 문서 | 매칭 finding |
|---|---|---|---|
| 🟡 span만 적중 | The study will select the recommended Phase 2 dose from the first expansion cohort without collecting dose–res | ICH-E4-1994 · IV GUIDANCE AND ADVICE | F03 |
| 🟡 span만 적중 | The formulation-bridging expansion cohort will enroll participants receiving the new tablet or legacy capsule, | FDA-EXPANSION-COHORTS-2022 · F Evaluating Drug Product Chan | F08 |
| 🟡 span만 적중 | After identifying the first tolerable dose, all subsequent participants will receive only that dose, with no c | MFDS-1443-01-2025 · 3.2 다양한 용량을 비교하기 위한 임상시험 설계 | F02 |
| 🟡 span만 적중 | For this intravenous oncology study, the 500 mg dose will be prepared as a 50 mg/mL solution, requiring admini | MFDS-1443-01-2025 · 3.4 의약품의 함량 및 제형 | F01 |
| 🟡 span만 적중 | The disease-specific expansion cohort will enroll up to 60 participants without interim futility monitoring or | FDA-EXPANSION-COHORTS-2022 · B Evaluating Preliminary Antit | F09 |
| 🟡 span만 적중 | All recommendations in FDA-DOSE-OPT-2024 shall be implemented without deviation, and any investigator request  | FDA-DOSE-OPT-2024 · I INTRODUCTION | F10 |

주입 결함과 무관한 finding(정상판 기준 잘못 경고 후보, 사람 검토 필요):
- F04 [high/verified] The protocol specifies baseline liver testing, testing every three weeks for the first three months, and monthly testing thereafter, but doe
- F05 [high/held] The supplied protocol text refers hepatotoxicity and ILD/pneumonitis dose-modification rules to Appendix B without providing the operative r
- F06 [high/verified] The protocol prespecifies a dose-proportionality power model but does not prespecify an exposure–efficacy or exposure–toxicity analysis for 
- F07 [high/verified] The supplied protocol text identifies the BOIN target, maximum sample size, dose levels, and four simulated scenarios but does not provide t

## AX1-017 — finding 11건, 주입 결함 6건, 토큰 28,765

| 결과 | 주입 결함(요약) | 원 규범 문서 | 매칭 finding |
|---|---|---|---|
| 🟡 span만 적중 | Population pharmacokinetic analyses will be performed only after database lock using the final pooled dataset, | FDA-DOSE-OPT-2024 · A Clinical Pharmacokinetics, P | F06 |
| 🟡 span만 적중 | The study will select the recommended Phase 2 dose from the first dose level that meets the preliminary respon | FDA-DOSE-OPT-2024 · 7 See 21 CFR 312.42 | F02 |
| 🟡 span만 적중 | The recommended Phase 2 dose will be the highest dose tested with acceptable early laboratory findings, even i | FDA-DOSE-OPT-2024 · II BACKGROUND | F03 |
| 🟡 span만 적중 | Dose selection for expansion will be based solely on the prespecified primary endpoint from the escalation coh | ICH-E4-1994 · IV GUIDANCE AND ADVICE | F05 |
| 🟡 span만 적중 | The study will assess treatment activity using weekly change in body weight and evaluate safety primarily thro | MFDS-1443-01-2025 · 3.1 임상 약동학, 약력학 및 약물유전체학 | F01 |
| 🟡 span만 적중 | The protocol will continue enrollment in each expansion cohort until the planned sample size is reached, witho | FDA-EXPANSION-COHORTS-2022 · VI STATISTICAL CONSIDERATIONS | F04 |

주입 결함과 무관한 finding(정상판 기준 잘못 경고 후보, 사람 검토 필요):
- F07 [high/verified] The protocol defers the executable dose-modification rules for hepatotoxicity, interstitial lung disease/pneumonitis, and other adverse reac
- F08 [high/held] The protocol identifies the BOIN target, maximum sample size, dose levels, and existence of four simulated scenarios but does not provide th
- F09 [high/verified] The protocol specifies at least 60 subjects and 1:1 randomization but does not state endpoint-specific assumptions, precision criteria, stra
- F10 [high/verified] The protocol specifies a four-week washout for anti-PD-(L)1 therapy but states no washout periods for other prior systemic therapies, radiot

## AX1-018 — finding 11건, 주입 결함 6건, 토큰 30,693

| 결과 | 주입 결함(요약) | 원 규범 문서 | 매칭 finding |
|---|---|---|---|
| 🟡 span만 적중 | All participants will receive 80 mg orally twice daily from Cycle 1 Day 1, with no intra-patient dose escalati | ICH-E4-1994 · I INTRODUCTION | F03 |
| 🟡 span만 적중 | After the recommended Phase 2 dose is selected, no additional dose-optimization or comparative dose evaluation | FDA-DOSE-OPT-2024 · II BACKGROUND | F05 |
| 🟡 span만 적중 | The recommended Phase 2 dose will be selected solely from dose-limiting toxicity rates observed during Cycle 1 | FDA-DOSE-OPT-2024 · I INTRODUCTION | F01 |
| 🟡 span만 적중 | After the safety lead-in, all participants will receive 240 mg twice daily; no alternate dose will be evaluate | FDA-DOSE-OPT-2024 · B Trial Designs to Compare Mul | F02 |
| 🟡 span만 적중 | The recommended Phase 2 dose will be the highest dose tested with acceptable early laboratory findings, even i | FDA-DOSE-OPT-2024 · II BACKGROUND | F04 |
| 🟡 span만 적중 | Participants who cross over to the alternate dose will be included in the overall safety and response analyses | FDA-DOSE-OPT-2024 · B Trial Designs to Compare Mul | F07 |

주입 결함과 무관한 finding(정상판 기준 잘못 경고 후보, 사람 검토 필요):
- F06 [high/verified] The protocol specifies at least 60 randomized participants but does not state a sample-size justification, decision thresholds, analysis pop
- F08 [high/verified] The protocol identifies the BOIN method, a 30% target DLT rate, and a 36-subject maximum but does not state cohort size, decision boundaries
- F09 [medium/held] The protocol caps BOIN escalation at 36 participants for a design intended to evaluate five dose levels. 정확 MTD 선택률 50%를 목표로 하면 BOIN 기준 필요 n
- F10 [medium/verified] The protocol uses intensive first-dose and steady-state sampling during escalation but collects only steady-state trough samples in the rand

## AX1-019 — finding 11건, 주입 결함 6건, 토큰 30,147

| 결과 | 주입 결함(요약) | 원 규범 문서 | 매칭 finding |
|---|---|---|---|
| 🟡 span만 적중 | After the recommended Phase 2 dose is selected from tolerability data, all subsequent participants will receiv | ICH-E4-1994 · II OBTAINING DOSE-RESPONSE INF | F03 |
| 🟡 span만 적중 | In this open-label, single-arm Phase 1/2 study, treatment activity will be assessed against historical respons | ICH-E4-1994 · IV GUIDANCE AND ADVICE | F05 |
| ❌ 놓침 | Dose-response analyses will be limited to the randomized expansion cohort, and data from dose-escalation parti | ICH-E4-1994 · II OBTAINING DOSE-RESPONSE INF | - |
| 🟡 span만 적중 | After enrolling the initial three participants at 10 mg, the study will proceed directly to a fixed 10 mg expa | MFDS-1443-01-2025 · 1 안내서-1443-01 2025. 8. 29. 제정 | F02, F07 |
| 🟡 span만 적중 | All participants will receive the fixed 200 mg dose supplied in a single capsule strength throughout the study | FDA-DOSE-OPT-2024 · D Drug Formulation | F01 |
| 🟡 span만 적중 | Results from the expansion cohort will serve as the primary efficacy package for the planned marketing applica | FDA-EXPANSION-COHORTS-2022 · C Communications and Interacti | F04 |

주입 결함과 무관한 finding(정상판 기준 잘못 경고 후보, 사람 검토 필요):
- F06 [high/held] The protocol identifies a BOIN target DLT rate and maximum sample size but does not state the decision boundaries, cohort rules, evaluabilit
- F08 [high/verified] The protocol plans at least 60 randomized participants but provides no sample-size assumptions, precision target, estimand, multiplicity app
- F09 [high/verified] The protocol limits randomized-cohort PK sampling to steady-state troughs and proposes a power model for dose proportionality without descri
- F10 [high/verified] The protocol specifies baseline, every-three-week, and monthly liver testing but does not state that testing will become more frequent after

## AX1-020 — finding 7건, 주입 결함 6건, 토큰 29,902

| 결과 | 주입 결함(요약) | 원 규범 문서 | 매칭 finding |
|---|---|---|---|
| 🟡 span만 적중 | The study team will review emerging adverse-event data periodically and decide during the trial whether enroll | FDA-DOSE-OPT-2024 · C Safety and Tolerability | F04 |
| 🟡 span만 적중 | Patients with moderate hepatic impairment and the CYP2C19 poor-metabolizer genotype will be enrolled in the sa | FDA-DOSE-OPT-2024 · A Clinical Pharmacokinetics, P | F05 |
| ❌ 놓침 | Results from the expansion cohort will serve as the primary efficacy package for the planned marketing applica | FDA-EXPANSION-COHORTS-2022 · C Communications and Interacti | - |
| 🟡 span만 적중 | The expansion cohort will enroll 80 patients at 200 mg twice daily immediately after the first three participa | FDA-DOSE-OPT-2024 · III DOSAGE OPTIMIZATION RECOMM | F02 |
| 🟡 span만 적중 | Blood samples will be collected for exploratory biomarker testing, but no pharmacokinetic sampling schedule or | FDA-DOSE-OPT-2024 · A Clinical Pharmacokinetics, P | F06 |
| 🟡 span만 적중 | The recommended Phase 2 dose will be selected solely from the highest tolerated dose in the escalation cohort, | FDA-DOSE-OPT-2024 · A Clinical Pharmacokinetics, P | F00, F01 |

주입 결함과 무관한 finding(정상판 기준 잘못 경고 후보, 사람 검토 필요):
- F03 [high/verified] The protocol assigns at least 60 subjects equally between two doses but provides no effect-size assumptions, precision targets, decision thr

