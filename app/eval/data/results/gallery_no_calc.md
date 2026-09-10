# 실패 사례 갤러리 — no_calc

놓친 결함과 잘못 경고한 사례를 그대로 공개한다(제안서 4장 약속).
합계: 주입 결함 120건 중 놓침 15건, finding 192건 중 무관 86건.

## AX1-001 — finding 10건, 주입 결함 6건, 토큰 50,695

| 결과 | 주입 결함(요약) | 원 규범 문서 | 매칭 finding |
|---|---|---|---|
| 🟡 span만 적중 | The study team will review emerging adverse-event data periodically and decide during the trial whether enroll | FDA-DOSE-OPT-2024 · C Safety and Tolerability | F04 |
| 🟡 span만 적중 | All participants will receive the fixed 200 mg dose supplied in a single capsule strength throughout the study | FDA-DOSE-OPT-2024 · D Drug Formulation | F01 |
| 🟡 span만 적중 | The formulation-bridging expansion cohort will enroll participants receiving the new tablet or legacy capsule, | FDA-EXPANSION-COHORTS-2022 · F Evaluating Drug Product Chan | F05 |
| 🟡 span만 적중 | After the recommended Phase 2 dose is selected from tolerability data, all subsequent participants will receiv | ICH-E4-1994 · II OBTAINING DOSE-RESPONSE INF | F02 |
| ✅ 근거까지 적중 | Patients with moderate hepatic impairment and the CYP2C19 poor-metabolizer genotype will be enrolled in the sa | FDA-DOSE-OPT-2024 · A Clinical Pharmacokinetics, P | F09 |
| ❌ 놓침 | Dose–response analyses will be conducted only in the overall enrolled population, with no evaluations by age,  | ICH-E4-1994 · IV GUIDANCE AND ADVICE | - |

주입 결함과 무관한 finding(정상판 기준 잘못 경고 후보, 사람 검토 필요):
- F03 [critical/verified] The protocol specifies the BOIN target DLT rate, maximum enrollment, dose levels, and a reference to simulations but does not state cohort s
- F06 [high/verified] The protocol specifies at least 60 randomized subjects and refers to Appendix D but does not provide endpoint-specific sample-size justifica
- F07 [high/verified] The protocol prespecifies only a dose-proportionality power model and does not specify an individual exposure–efficacy or exposure–toxicity 
- F08 [high/verified] The randomized cohorts have only steady-state trough sampling, with no stated sparse-sampling or population-PK method and no validation that
- F10 [medium/verified] The protocol limits escalation to 36 subjects across five planned dose levels but provides no numerical operating characteristics supporting

## AX1-002 — finding 10건, 주입 결함 6건, 토큰 56,493

| 결과 | 주입 결함(요약) | 원 규범 문서 | 매칭 finding |
|---|---|---|---|
| 🟡 span만 적중 | Results from the expansion cohort will serve as the primary efficacy package for the planned marketing applica | FDA-EXPANSION-COHORTS-2022 · C Communications and Interacti | F06 |
| 🟡 span만 적중 | The recommended Phase 2 dose will be the highest dose at which no more than 30% of participants permanently di | ICH-E4-1994 · II OBTAINING DOSE-RESPONSE INF | F04 |
| 🟡 span만 적중 | Patients with moderate hepatic impairment and the CYP2C19 poor-metabolizer genotype will be enrolled in the sa | FDA-DOSE-OPT-2024 · A Clinical Pharmacokinetics, P | F05 |
| 🟡 span만 적중 | The sponsor will issue a single cumulative safety update to investigators and the IRB at the end of each calen | FDA-EXPANSION-COHORTS-2022 · C IRB/Independent Ethics Commi | F01 |
| 🟡 span만 적중 | The combination expansion cohort will open after the first six participants complete cycle 1 of the investigat | FDA-EXPANSION-COHORTS-2022 · G Evaluating More Than One The | F03 |
| 🟡 span만 적중 | The expansion cohort will support the marketing application using investigator-assessed tumor responses at the | FDA-EXPANSION-COHORTS-2022 · B Evaluating Preliminary Antit | F02 |

주입 결함과 무관한 finding(정상판 기준 잘못 경고 후보, 사람 검토 필요):
- F07 [high/held] The protocol states the liver-test schedule but places the hepatotoxicity, ILD/pneumonitis, and other adverse-reaction management rules in a
- F08 [high/verified] The protocol randomizes at least 60 participants between two candidate doses and refers RP2D selection to prespecified integrated criteria i
- F09 [medium/verified] The protocol provides intensive escalation PK sampling but limits randomized-cohort sampling to steady-state troughs and specifies only a do
- F10 [medium/held] The protocol identifies DV-101 as an irreversible covalent inhibitor and provides its structure but supplies no nonclinical pharmacology, to

## AX1-003 — finding 10건, 주입 결함 6건, 토큰 53,988

| 결과 | 주입 결함(요약) | 원 규범 문서 | 매칭 finding |
|---|---|---|---|
| 🟡 span만 적중 | The recommended Phase 2 dose will be the highest dose at which no more than 30% of participants permanently di | ICH-E4-1994 · II OBTAINING DOSE-RESPONSE INF | F03 |
| 🟡 span만 적중 | After the safety lead-in, all participants will receive 240 mg twice daily; no alternate dose will be evaluate | FDA-DOSE-OPT-2024 · B Trial Designs to Compare Mul | F01 |
| 🟡 span만 적중 | The study team will review emerging adverse-event data periodically and decide during the trial whether enroll | FDA-DOSE-OPT-2024 · C Safety and Tolerability | F07 |
| ❌ 놓침 | Concomitant medications will be recorded at enrollment, but no interaction studies or dedicated pharmacokineti | FDA-DOSE-OPT-2024 · A Clinical Pharmacokinetics, P | - |
| 🟡 span만 적중 | For the randomized Phase 2 portion, each of the three active-dose arms will be compared independently with pla | FDA-DOSE-OPT-2024 · B Trial Designs to Compare Mul | F01, F02 |
| 🟡 span만 적중 | All recommendations in FDA-DOSE-OPT-2024 shall be implemented without deviation, and any investigator request  | FDA-DOSE-OPT-2024 · I INTRODUCTION | F10 |

주입 결함과 무관한 finding(정상판 기준 잘못 경고 후보, 사람 검토 필요):
- F04 [high/verified] The protocol assigns at least 60 participants to two candidate doses but gives no sample-size rationale, cohort-specific stopping rules, or 
- F05 [high/verified] The randomized cohorts have steady-state trough-only PK sampling, and the protocol does not state how individual AUC or Cmax will be estimat
- F06 [high/held] The operative hepatotoxicity and ILD/pneumonitis dose-modification rules are incorporated by reference, but Appendix B is not present in the
- F08 [high/verified] The protocol states that four BOIN simulation scenarios were evaluated but does not report the scenarios, selection probabilities, participa
- F09 [medium/held] The protocol identifies irreversible covalent pharmacology but provides no mechanism-specific rationale in this span for the dosing interval

## AX1-004 — finding 10건, 주입 결함 6건, 토큰 56,144

| 결과 | 주입 결함(요약) | 원 규범 문서 | 매칭 finding |
|---|---|---|---|
| ❌ 놓침 | The dose-escalation and expansion cohorts will follow the same general treatment plan, with cohort-specific do | FDA-EXPANSION-COHORTS-2022 · A Initial Protocol | - |
| 🟡 span만 적중 | The randomized Phase 2 portion will compare three active dose levels with placebo, and each dose-versus-placeb | MFDS-1443-01-2025 · 3.2 다양한 용량을 비교하기 위한 임상시험 설계 | F03 |
| 🟡 span만 적중 | Participants will be enrolled sequentially into nonrandomized cohorts receiving 10, 30, or 60 mg once daily, w | FDA-DOSE-OPT-2024 · B Trial Designs to Compare Mul | F02 |
| 🟡 span만 적중 | All doses will be prepared as a fixed 0.5 mg/mL intravenous solution, including doses requiring infusion volum | FDA-DOSE-OPT-2024 · D Drug Formulation | F01 |
| 🟡 span만 적중 | 확장 코호트에서는 선행 임상자료나 노출·반응 분석과 무관하게 모든 환자에게 임상적으로 사용되는 표준 용량 200 mg을 투여한다. | MFDS-1443-01-2025 · 1 안내서-1443-01 2025. 8. 29. 제정 | F05 |
| 🟡 span만 적중 | Dose selection for expansion will be based solely on observed tumor response rates, without adjustment for tre | ICH-E4-1994 · IV GUIDANCE AND ADVICE | F04 |

주입 결함과 무관한 finding(정상판 기준 잘못 경고 후보, 사람 검토 필요):
- F06 [high/verified] The protocol schedules liver tests at baseline, every three weeks for the first three months, and monthly thereafter but does not specify a 
- F07 [high/held] The supplied protocol refers hepatotoxicity, interstitial lung disease/pneumonitis, and other adverse-reaction dose modifications to Appendi
- F08 [high/verified] The protocol collects two intensive 24-hour PK profiles in escalation subjects but only steady-state trough samples in randomized cohorts an
- F09 [high/held] The protocol limits BOIN escalation to 36 subjects and refers its operating-characteristic simulations to Appendix C, which is not supplied.
- F10 [high/held] The protocol specifies a four-week washout only for anti-PD-(L)1 therapy and gives no washout rules for chemotherapy, radiotherapy, other ta

## AX1-005 — finding 10건, 주입 결함 6건, 토큰 52,229

| 결과 | 주입 결함(요약) | 원 규범 문서 | 매칭 finding |
|---|---|---|---|
| ❌ 놓침 | The study team will review emerging adverse-event data periodically and decide during the trial whether enroll | FDA-DOSE-OPT-2024 · C Safety and Tolerability | - |
| ✅ 근거까지 적중 | In the pediatric expansion cohort, safety will be assessed only by recording adverse events at scheduled clini | FDA-EXPANSION-COHORTS-2022 · H Evaluating PK, Tolerability, | F03 |
| ✅ 근거까지 적중 | This amendment adds a higher-dose expansion cohort based on preliminary efficacy findings; the safety rational | FDA-EXPANSION-COHORTS-2022 · A Safety Monitoring and Report | F04 |
| 🟡 span만 적중 | The expansion cohort will support the marketing application using investigator-assessed tumor responses at the | FDA-EXPANSION-COHORTS-2022 · B Evaluating Preliminary Antit | F02 |
| ❌ 놓침 | No pharmacodynamic or pharmacogenomic specimens will be collected, and the study will not evaluate genetic det | FDA-DOSE-OPT-2024 · A Clinical Pharmacokinetics, P | - |
| 🟡 span만 적중 | The study will be conducted under the sponsor's internal approval without submission of the final protocol to  | ICH-E4-1994 · 0 PREAMBLE | F01 |

주입 결함과 무관한 finding(정상판 기준 잘못 경고 후보, 사람 검토 필요):
- F05 [high/verified] The protocol promises a randomized PD comparison between candidate doses, but the protocol separately specifies no collection of pharmacodyn
- F06 [high/verified] The protocol delegates dose-modification rules for hepatotoxicity, interstitial lung disease/pneumonitis, and other adverse reactions to App
- F07 [high/verified] The protocol schedules liver function tests before treatment, every three weeks during the first three months, and monthly thereafter or as 
- F08 [high/verified] The protocol provides intensive first-dose and Day 15 PK sampling only in escalation subjects and limits randomized-cohort PK collection to 
- F09 [high/verified] The protocol states that BOIN operating characteristics were simulated across four toxicity scenarios but leaves the scenario assumptions an
- F10 [high/verified] The protocol excludes anti-PD-(L)1 therapy within four weeks before first dose but gives no risk-based qualification concerning prior immune

## AX1-006 — finding 10건, 주입 결함 6건, 토큰 56,791

| 결과 | 주입 결함(요약) | 원 규범 문서 | 매칭 finding |
|---|---|---|---|
| 🟡 span만 적중 | The recommended Phase 2 dose will be the highest dose tested with acceptable early laboratory findings, even i | FDA-DOSE-OPT-2024 · II BACKGROUND | F02 |
| 🟡 span만 적중 | The sponsor will compile aggregate safety data internally and submit cumulative reports to FDA at its discreti | FDA-EXPANSION-COHORTS-2022 · A Safety Monitoring and Report | F05 |
| 🟡 span만 적중 | The study will enroll adults with untreated low-risk indolent lymphoma for whom standard curative therapy is a | FDA-EXPANSION-COHORTS-2022 · IV DRUG PRODUCT AND SUBJECT CO | F04 |
| 🟡 span만 적중 | Participants who cross over to the alternate dose will be included in the overall safety and response analyses | FDA-DOSE-OPT-2024 · B Trial Designs to Compare Mul | F06 |
| 🟡 span만 적중 | The Phase 2 expansion dose will be fixed at 200 mg twice daily based solely on the recommended Phase 1 dose, w | FDA-DOSE-OPT-2024 · III DOSAGE OPTIMIZATION RECOMM | F03 |
| 🟡 span만 적중 | Results from the expansion cohort will serve as the primary efficacy package for the planned marketing applica | FDA-EXPANSION-COHORTS-2022 · C Communications and Interacti | F01 |

주입 결함과 무관한 finding(정상판 기준 잘못 경고 후보, 사람 검토 필요):
- F07 [high/verified] The protocol schedules liver function tests at baseline, every three weeks for the first three months, and monthly thereafter or as clinical
- F08 [high/held] The protocol refers RP2D selection to integrated criteria in Appendix D but does not state those criteria or a prespecified exposure-respons
- F09 [high/verified] The protocol reports simulation under four toxicity scenarios but provides no scenario definitions, numerical operating characteristics, or 
- F10 [high/verified] The protocol identifies DV-101 as sotorasib and supplies a SMILES string but provides no authoritative molecular-identity or stereochemical 

## AX1-007 — finding 10건, 주입 결함 6건, 토큰 52,828

| 결과 | 주입 결함(요약) | 원 규범 문서 | 매칭 finding |
|---|---|---|---|
| 🟡 span만 적중 | For the new pembrolizumab–investigational-agent combination in metastatic colorectal cancer, the study will pr | MFDS-1443-01-2025 · 3.5 후속 적응증 및 용법 | F07 |
| 🟡 span만 적중 | 확장 코호트에서는 선행 임상자료나 노출·반응 분석과 무관하게 모든 환자에게 임상적으로 사용되는 표준 용량 200 mg을 투여한다. | MFDS-1443-01-2025 · 1 안내서-1443-01 2025. 8. 29. 제정 | F08 |
| 🟡 span만 적중 | Interim safety and efficacy findings will be reviewed only after database lock at the end of the expansion pha | FDA-EXPANSION-COHORTS-2022 · II BACKGROUND | F02 |
| 🟡 span만 적중 | The formulation-bridging expansion cohort will enroll participants receiving the new tablet or legacy capsule, | FDA-EXPANSION-COHORTS-2022 · F Evaluating Drug Product Chan | F09 |
| 🟡 span만 적중 | After the recommended Phase 2 dose is selected from tolerability data, all subsequent participants will receiv | ICH-E4-1994 · II OBTAINING DOSE-RESPONSE INF | F03 |
| 🟡 span만 적중 | The starting dose and subsequent escalation levels will be selected solely by investigator consensus, without  | FDA-DOSE-OPT-2024 · III DOSAGE OPTIMIZATION RECOMM | F01 |

주입 결함과 무관한 finding(정상판 기준 잘못 경고 후보, 사람 검토 필요):
- F04 [high/held] The synopsis specifies the BOIN target DLT rate, maximum enrollment, dose levels, and four simulated scenarios but does not state cohort siz
- F05 [high/verified] The protocol specifies a randomized comparison of at least 60 subjects and integrated RP2D criteria but does not state the analysis populati
- F06 [high/verified] The protocol limits randomized-cohort PK collection to steady-state trough samples and does not describe how individual AUC, Cmax, accumulat
- F10 [high/held] The protocol incorporates hepatotoxicity and interstitial lung disease/pneumonitis dose-modification rules by reference to Appendix B, whose

## AX1-008 — finding 10건, 주입 결함 6건, 토큰 55,618

| 결과 | 주입 결함(요약) | 원 규범 문서 | 매칭 finding |
|---|---|---|---|
| 🟡 span만 적중 | After participants complete 48 hours at the assigned dose level, the dose-response analysis will be performed  | ICH-E4-1994 · 1 Parallel dose-response | F05 |
| 🟡 span만 적중 | Dose–response analyses will be conducted only in the overall enrolled population, with no evaluations by age,  | ICH-E4-1994 · IV GUIDANCE AND ADVICE | F06 |
| ❌ 놓침 | The study will select the recommended Phase 2 dose from the first expansion cohort without collecting dose–res | ICH-E4-1994 · IV GUIDANCE AND ADVICE | - |
| 🟡 span만 적중 | After completing the dose-escalation portion, the study will open six parallel disease-specific expansion coho | FDA-EXPANSION-COHORTS-2022 · IV DRUG PRODUCT AND SUBJECT CO | F04 |
| 🟡 span만 적중 | The sponsor will include serious and unexpected adverse safety findings in the next scheduled annual safety re | FDA-EXPANSION-COHORTS-2022 · B Potential Opportunities and  | F01 |
| 🟡 span만 적중 | Participants will be enrolled sequentially into nonrandomized cohorts receiving 10, 30, or 60 mg once daily, w | FDA-DOSE-OPT-2024 · B Trial Designs to Compare Mul | F03 |

주입 결함과 무관한 finding(정상판 기준 잘못 경고 후보, 사람 검토 필요):
- F02 [critical/verified] The protocol places the dose-modification rules for hepatotoxicity and interstitial lung disease/pneumonitis in Appendix B, which was not su
- F07 [high/held] The protocol names safety, tolerability, PK, PD, and preliminary antitumor activity for the randomized comparison but does not specify an in
- F08 [high/verified] The protocol limits randomized-cohort PK collection to steady-state trough samples and does not describe how individual AUC, Cmax, accumulat
- F09 [high/verified] The protocol applies an every-three-week liver-test schedule for the first three months and does not specify a more frequent pathway for par
- F10 [high/verified] The protocol excludes anti-PD-(L)1 therapy within four weeks before the first dose but does not state the rationale for that fixed interval 

## AX1-009 — finding 10건, 주입 결함 6건, 토큰 54,071

| 결과 | 주입 결함(요약) | 원 규범 문서 | 매칭 finding |
|---|---|---|---|
| 🟡 span만 적중 | The sponsor will finalize the dose-comparison design and proceed directly to patient enrollment without seekin | MFDS-1443-01-2025 · 3.2 다양한 용량을 비교하기 위한 임상시험 설계 | F09 |
| 🟡 span만 적중 | After the sponsor transfers production to a new manufacturing site and changes the formulation, the study will | FDA-EXPANSION-COHORTS-2022 · F Evaluating Drug Product Chan | F02 |
| 🟡 span만 적중 | For every participant, the dose-escalation algorithm will identify that individual’s optimal dose from observe | ICH-E4-1994 · IV GUIDANCE AND ADVICE | F03 |
| 🟡 span만 적중 | Participants may take the study tablets with or without meals and may continue all clinically indicated concom | FDA-DOSE-OPT-2024 · A Clinical Pharmacokinetics, P | F07 |
| 🟡 span만 적중 | The medical monitor may be any licensed physician with general inpatient-care experience; prior oncology pract | FDA-EXPANSION-COHORTS-2022 · A Safety Monitoring and Report | F10 |
| 🟡 span만 적중 | The Phase 1 portion will escalate cohorts until the highest dose with an acceptable toxicity profile is identi | FDA-DOSE-OPT-2024 · II BACKGROUND | F01 |

주입 결함과 무관한 finding(정상판 기준 잘못 경고 후보, 사람 검토 필요):
- F04 [high/held] The protocol specifies five BOIN dose levels, a 30% target DLT rate, a maximum of 36 subjects, and four simulated scenarios but does not pro
- F05 [high/verified] The protocol randomizes at least 60 subjects between two candidate doses but gives no sample-size rationale, precision target, decision thre
- F06 [high/verified] The protocol limits randomized-cohort PK collection to steady-state trough samples while intensive first-dose and steady-state sampling is c
- F08 [high/verified] The protocol places hepatotoxicity and interstitial lung disease/pneumonitis dose-modification rules in Appendix B, which is not included in

## AX1-010 — finding 10건, 주입 결함 6건, 토큰 51,805

| 결과 | 주입 결함(요약) | 원 규범 문서 | 매칭 finding |
|---|---|---|---|
| 🟡 span만 적중 | In the pediatric expansion cohort, safety will be assessed only by recording adverse events at scheduled clini | FDA-EXPANSION-COHORTS-2022 · H Evaluating PK, Tolerability, | F02 |
| 🟡 span만 적중 | The pediatric expansion cohort will proceed under the adult development plan, with pediatric assessments docum | FDA-EXPANSION-COHORTS-2022 · H Evaluating PK, Tolerability, | F03 |
| 🟡 span만 적중 | Dose selection for expansion will be based solely on the prespecified primary endpoint from the escalation coh | ICH-E4-1994 · IV GUIDANCE AND ADVICE | F04 |
| ❌ 놓침 | Participants assigned to the control arm may cross over to the investigational therapy after progression; safe | MFDS-1443-01-2025 · 3.2 다양한 용량을 비교하기 위한 임상시험 설계 | - |
| ❌ 놓침 | The medical monitor may be any licensed physician with general inpatient-care experience; prior oncology pract | FDA-EXPANSION-COHORTS-2022 · A Safety Monitoring and Report | - |
| 🟡 span만 적중 | The recommended Phase 2 dose will be selected solely from dose-limiting toxicity rates observed during Cycle 1 | FDA-DOSE-OPT-2024 · I INTRODUCTION | F01 |

주입 결함과 무관한 finding(정상판 기준 잘못 경고 후보, 사람 검토 필요):
- F05 [high/held] The protocol lists five planned dose levels from 180 mg to 960 mg once daily but provides no rationale for the starting dose or escalation s
- F06 [high/verified] The synopsis specifies the BOIN target DLT rate, maximum enrollment, dose levels, and existence of four simulated scenarios but does not sta
- F07 [high/verified] The protocol specifies randomization of at least 60 participants between two candidate doses but does not state dose-selection thresholds, i
- F08 [high/verified] The protocol provides intensive PK sampling only in escalation participants and steady-state trough sampling in randomized participants, wit
- F09 [high/verified] The protocol schedules liver testing before treatment, every three weeks for the first three months, and monthly thereafter, without an expl
- F10 [high/verified] The synopsis refers dose-modification rules for hepatotoxicity, ILD/pneumonitis, and other adverse reactions to Appendix B but does not repr

## AX1-011 — finding 10건, 주입 결함 6건, 토큰 53,343

| 결과 | 주입 결함(요약) | 원 규범 문서 | 매칭 finding |
|---|---|---|---|
| ❌ 놓침 | Protocol deviations will be reviewed individually by the study team, with importance assigned after database l | ICH-E6R3-2025 · 3.9.1 The sponsor should ensur | - |
| 🟡 span만 적중 | Pharmacokinetic analyses will use pooled data without examining covariates or reporting results by clinically  | MFDS-1443-01-2025 · 3.1 임상 약동학, 약력학 및 약물유전체학 | F05 |
| 🟡 span만 적중 | The study will assess treatment activity using weekly change in body weight and evaluate safety primarily thro | MFDS-1443-01-2025 · 3.1 임상 약동학, 약력학 및 약물유전체학 | F02 |
| 🟡 span만 적중 | The sponsor will include serious and unexpected adverse safety findings in the next scheduled annual safety re | FDA-EXPANSION-COHORTS-2022 · B Potential Opportunities and  | F01 |
| ✅ 근거까지 적중 | Patients with moderate hepatic impairment and the CYP2C19 poor-metabolizer genotype will be enrolled in the sa | FDA-DOSE-OPT-2024 · A Clinical Pharmacokinetics, P | F04 |
| 🟡 span만 적중 | Patients in the expansion cohort will receive the investigator-selected dose of either 80 mg or 120 mg once da | FDA-EXPANSION-COHORTS-2022 · VI STATISTICAL CONSIDERATIONS | F03 |

주입 결함과 무관한 finding(정상판 기준 잘못 경고 후보, 사람 검토 필요):
- F06 [high/verified] The protocol specifies 60 randomized subjects and comparison domains but does not state an endpoint hierarchy, effect-size or precision assu
- F07 [high/verified] The protocol refers RP2D selection to integrated criteria in an unavailable Appendix D and does not state the component analyses, uncertaint
- F08 [high/verified] The protocol specifies a 30% DLT target, five dose levels, a 36-subject maximum, and four simulation scenarios but does not provide the coho
- F09 [high/held] The protocol refers hepatotoxicity, interstitial lung disease/pneumonitis, and other adverse-reaction dose modifications to an unavailable A
- F10 [medium/held] The protocol identifies DV-101 as an irreversible covalent KRAS G12C inhibitor and provides its structure and target but no nonclinical spec

## AX1-012 — finding 10건, 주입 결함 6건, 토큰 51,869

| 결과 | 주입 결함(요약) | 원 규범 문서 | 매칭 finding |
|---|---|---|---|
| 🟡 span만 적중 | Interim safety and efficacy findings will be reviewed only after database lock at the end of the expansion pha | FDA-EXPANSION-COHORTS-2022 · II BACKGROUND | F03 |
| 🟡 span만 적중 | The study will enroll adults with untreated low-risk indolent lymphoma for whom standard curative therapy is a | FDA-EXPANSION-COHORTS-2022 · IV DRUG PRODUCT AND SUBJECT CO | F04 |
| 🟡 span만 적중 | This first-in-human dose-escalation study will enroll participants using an ad hoc design selected for operati | ICH-E4-1994 · IV GUIDANCE AND ADVICE | F01 |
| 🟡 span만 적중 | Blood samples will be collected for exploratory biomarker testing, but no pharmacokinetic sampling schedule or | FDA-DOSE-OPT-2024 · A Clinical Pharmacokinetics, P | F02 |
| 🟡 span만 적중 | Enrollment in the pediatric expansion cohort will be open to children with newly diagnosed or relapsed solid t | FDA-EXPANSION-COHORTS-2022 · H Evaluating PK, Tolerability, | F05 |
| 🟡 span만 적중 | Tolerability will be assessed exclusively through investigator-recorded adverse events and laboratory findings | FDA-DOSE-OPT-2024 · C Safety and Tolerability | F10 |

주입 결함과 무관한 finding(정상판 기준 잘못 경고 후보, 사람 검토 필요):
- F06 [high/verified] The protocol lists five dose levels but provides no rationale for the starting dose, increments, or dose range in the cited sentence. The tr
- F07 [high/verified] The protocol specifies at least 60 randomized participants but does not state the sample-size assumptions, precision target, estimands, inte
- F08 [high/verified] The protocol states that PK will inform an integrated RP2D selection but does not specify an individual exposure-response analysis linking e
- F09 [high/verified] The protocol limits randomized-cohort PK collection to steady-state trough samples and does not describe how AUC, Cmax, accumulation, cleara

## AX1-013 — finding 10건, 주입 결함 6건, 토큰 53,784

| 결과 | 주입 결함(요약) | 원 규범 문서 | 매칭 finding |
|---|---|---|---|
| 🟡 span만 적중 | Enrollment in the pediatric expansion cohort will be open to children with newly diagnosed or relapsed solid t | FDA-EXPANSION-COHORTS-2022 · H Evaluating PK, Tolerability, | F03 |
| 🟡 span만 적중 | The sponsor will finalize the dose-comparison design and proceed directly to patient enrollment without seekin | MFDS-1443-01-2025 · 3.2 다양한 용량을 비교하기 위한 임상시험 설계 | F09 |
| 🟡 span만 적중 | During this first-in-human study, safety will be assessed only by participant-reported symptoms, and treatment | FDA-DOSE-OPT-2024 · A Clinical Pharmacokinetics, P | F02 |
| 🟡 span만 적중 | The study will enroll adults with untreated low-risk indolent lymphoma for whom standard curative therapy is a | FDA-EXPANSION-COHORTS-2022 · IV DRUG PRODUCT AND SUBJECT CO | F04 |
| ❌ 놓침 | Patients with moderate hepatic impairment and carriers of the ABCB1 variant will be enrolled only in the expan | FDA-DOSE-OPT-2024 · A Clinical Pharmacokinetics, P | - |
| 🟡 span만 적중 | After enrolling the initial three participants at 10 mg, the study will proceed directly to a fixed 10 mg expa | MFDS-1443-01-2025 · 1 안내서-1443-01 2025. 8. 29. 제정 | F01 |

주입 결함과 무관한 finding(정상판 기준 잘못 경고 후보, 사람 검토 필요):
- F05 [high/verified] The protocol identifies the BOIN target DLT rate, maximum sample size, five planned dose levels, and four simulated toxicity scenarios but d
- F06 [high/verified] The protocol refers to prespecified integrated RP2D criteria in Appendix D but does not state the criteria, quantitative thresholds, weighti
- F07 [high/verified] The protocol randomizes at least 60 participants 1:1 between two candidate doses but does not state effect-size assumptions, variability ass
- F08 [high/verified] The protocol provides intensive PK sampling only during escalation and limits randomized-cohort PK collection to steady-state trough samples
- F10 [medium/held] The protocol applies a fixed four-week anti-PD-(L)1 washout without stating criteria based on agent half-life, unresolved immune-mediated to

## AX1-014 — finding 10건, 주입 결함 6건, 토큰 51,618

| 결과 | 주입 결함(요약) | 원 규범 문서 | 매칭 finding |
|---|---|---|---|
| 🟡 span만 적중 | For every participant, the dose-escalation algorithm will identify that individual’s optimal dose from observe | ICH-E4-1994 · IV GUIDANCE AND ADVICE | F05 |
| 🟡 span만 적중 | Pharmacokinetic blood samples will be collected only before dosing and at 1 hour after the first administratio | MFDS-1443-01-2025 · 3.1 임상 약동학, 약력학 및 약물유전체학 | F01 |
| 🟡 span만 적중 | After completing the dose-escalation study, participants will enroll into the expansion cohorts under the same | FDA-EXPANSION-COHORTS-2022 · A Initial Protocol | F08 |
| 🟡 span만 적중 | After identification of a potentially fatal dose-limiting toxicity during escalation, the study will open all  | FDA-EXPANSION-COHORTS-2022 · A Assessing Safety of Recommen | F02 |
| 🟡 span만 적중 | The sponsor will issue a single cumulative safety update to investigators and the IRB at the end of each calen | FDA-EXPANSION-COHORTS-2022 · C IRB/Independent Ethics Commi | F04 |
| 🟡 span만 적중 | The recommended Phase 2 dose will be selected using tumor response and exposure data only; treatment discontin | FDA-DOSE-OPT-2024 · C Safety and Tolerability | F03 |

주입 결함과 무관한 finding(정상판 기준 잘못 경고 후보, 사람 검토 필요):
- F06 [high/verified] The synopsis gives the BOIN target, maximum enrollment, dose levels, and number of simulated scenarios but omits cohort size, decision bound
- F07 [high/verified] The protocol specifies a 60-subject randomized comparison but does not state the sample-size assumptions, clinically important differences, 
- F09 [high/held] The protocol identifies 180 mg as the lowest planned dose but provides no starting-dose rationale or supporting nonclinical, clinical, expos
- F10 [high/verified] The protocol refers to integrated RP2D criteria in Appendix D but does not state in the synopsis whether a population exposure–response anal

## AX1-015 — finding 9건, 주입 결함 6건, 토큰 54,212

| 결과 | 주입 결함(요약) | 원 규범 문서 | 매칭 finding |
|---|---|---|---|
| 🟡 span만 적중 | The recommended Phase 2 dose will be selected solely from dose-limiting toxicity rates observed during Cycle 1 | FDA-DOSE-OPT-2024 · I INTRODUCTION | F03 |
| 🟡 span만 적중 | Dose selection for expansion will be based solely on observed tumor response rates, without adjustment for tre | ICH-E4-1994 · IV GUIDANCE AND ADVICE | F05 |
| 🟡 span만 적중 | The biomarker-selected expansion cohort will enroll 30 participants, with no assumptions, precision targets, h | FDA-EXPANSION-COHORTS-2022 · VI STATISTICAL CONSIDERATIONS | F06 |
| 🟡 span만 적중 | After the recommended starting dose is established, all subsequent participants will receive the same fixed do | ICH-E4-1994 · II OBTAINING DOSE-RESPONSE INF | F01 |
| 🟡 span만 적중 | This first-in-human dose-escalation study will enroll participants using an ad hoc design selected for operati | ICH-E4-1994 · IV GUIDANCE AND ADVICE | F02 |
| 🟡 span만 적중 | The combination expansion cohort will open after the first six participants complete cycle 1 of the investigat | FDA-EXPANSION-COHORTS-2022 · G Evaluating More Than One The | F04 |

주입 결함과 무관한 finding(정상판 기준 잘못 경고 후보, 사람 검토 필요):
- F07 [high/verified] The protocol specifies at least 60 randomized participants and the comparison domains but does not state sample-size assumptions, endpoint d
- F08 [high/verified] The protocol provides intensive PK sampling in escalation subjects but limits randomized-cohort sampling to steady-state trough measurements
- F09 [high/verified] The protocol incorporates hepatotoxicity and ILD/pneumonitis dose-modification rules by reference to Appendix B, whose specific interruption

## AX1-016 — finding 10건, 주입 결함 6건, 토큰 52,463

| 결과 | 주입 결함(요약) | 원 규범 문서 | 매칭 finding |
|---|---|---|---|
| 🟡 span만 적중 | The study will select the recommended Phase 2 dose from the first expansion cohort without collecting dose–res | ICH-E4-1994 · IV GUIDANCE AND ADVICE | F03 |
| 🟡 span만 적중 | The formulation-bridging expansion cohort will enroll participants receiving the new tablet or legacy capsule, | FDA-EXPANSION-COHORTS-2022 · F Evaluating Drug Product Chan | F08 |
| 🟡 span만 적중 | After identifying the first tolerable dose, all subsequent participants will receive only that dose, with no c | MFDS-1443-01-2025 · 3.2 다양한 용량을 비교하기 위한 임상시험 설계 | F02 |
| 🟡 span만 적중 | For this intravenous oncology study, the 500 mg dose will be prepared as a 50 mg/mL solution, requiring admini | MFDS-1443-01-2025 · 3.4 의약품의 함량 및 제형 | F01 |
| 🟡 span만 적중 | The disease-specific expansion cohort will enroll up to 60 participants without interim futility monitoring or | FDA-EXPANSION-COHORTS-2022 · B Evaluating Preliminary Antit | F07 |
| 🟡 span만 적중 | All recommendations in FDA-DOSE-OPT-2024 shall be implemented without deviation, and any investigator request  | FDA-DOSE-OPT-2024 · I INTRODUCTION | F04 |

주입 결함과 무관한 finding(정상판 기준 잘못 경고 후보, 사람 검토 필요):
- F05 [high/verified] The protocol states the BOIN target DLT rate, maximum enrollment, dose levels, and existence of simulations but does not state the cohort si
- F06 [high/verified] The protocol randomizes at least 60 participants equally between two candidate doses but does not state exposure–response estimands, exposur
- F09 [high/verified] The protocol specifies a four-week exclusion interval for anti-PD-(L)1 therapy but states no washout intervals for chemotherapy, radiotherap
- F10 [high/verified] The protocol incorporates hepatotoxicity and ILD/pneumonitis dose-modification rules solely by reference to Appendix B, whose operative rule

## AX1-017 — finding 9건, 주입 결함 6건, 토큰 50,573

| 결과 | 주입 결함(요약) | 원 규범 문서 | 매칭 finding |
|---|---|---|---|
| 🟡 span만 적중 | Population pharmacokinetic analyses will be performed only after database lock using the final pooled dataset, | FDA-DOSE-OPT-2024 · A Clinical Pharmacokinetics, P | F09 |
| 🟡 span만 적중 | The study will select the recommended Phase 2 dose from the first dose level that meets the preliminary respon | FDA-DOSE-OPT-2024 · 7 See 21 CFR 312.42 | F02 |
| 🟡 span만 적중 | The recommended Phase 2 dose will be the highest dose tested with acceptable early laboratory findings, even i | FDA-DOSE-OPT-2024 · II BACKGROUND | F03 |
| 🟡 span만 적중 | Dose selection for expansion will be based solely on the prespecified primary endpoint from the escalation coh | ICH-E4-1994 · IV GUIDANCE AND ADVICE | F04 |
| 🟡 span만 적중 | The study will assess treatment activity using weekly change in body weight and evaluate safety primarily thro | MFDS-1443-01-2025 · 3.1 임상 약동학, 약력학 및 약물유전체학 | F01 |
| 🟡 span만 적중 | The protocol will continue enrollment in each expansion cohort until the planned sample size is reached, witho | FDA-EXPANSION-COHORTS-2022 · VI STATISTICAL CONSIDERATIONS | F07 |

주입 결함과 무관한 finding(정상판 기준 잘못 경고 후보, 사람 검토 필요):
- F05 [high/verified] The protocol specifies a minimum total sample size and 1:1 allocation but does not state statistical assumptions, precision targets, stratif
- F06 [high/held] The synopsis specifies the BOIN target, maximum enrollment, and existence of simulations but does not provide executable escalation rules or
- F08 [high/held] The protocol incorporates hepatotoxicity and interstitial lung disease/pneumonitis dose-modification rules by reference to Appendix B, whose

## AX1-018 — finding 10건, 주입 결함 6건, 토큰 54,767

| 결과 | 주입 결함(요약) | 원 규범 문서 | 매칭 finding |
|---|---|---|---|
| 🟡 span만 적중 | All participants will receive 80 mg orally twice daily from Cycle 1 Day 1, with no intra-patient dose escalati | ICH-E4-1994 · I INTRODUCTION | F01 |
| 🟡 span만 적중 | After the recommended Phase 2 dose is selected, no additional dose-optimization or comparative dose evaluation | FDA-DOSE-OPT-2024 · II BACKGROUND | F08 |
| 🟡 span만 적중 | The recommended Phase 2 dose will be selected solely from dose-limiting toxicity rates observed during Cycle 1 | FDA-DOSE-OPT-2024 · I INTRODUCTION | F02 |
| 🟡 span만 적중 | After the safety lead-in, all participants will receive 240 mg twice daily; no alternate dose will be evaluate | FDA-DOSE-OPT-2024 · B Trial Designs to Compare Mul | F03 |
| 🟡 span만 적중 | The recommended Phase 2 dose will be the highest dose tested with acceptable early laboratory findings, even i | FDA-DOSE-OPT-2024 · II BACKGROUND | F04 |
| 🟡 span만 적중 | Participants who cross over to the alternate dose will be included in the overall safety and response analyses | FDA-DOSE-OPT-2024 · B Trial Designs to Compare Mul | F05 |

주입 결함과 무관한 finding(정상판 기준 잘못 경고 후보, 사람 검토 필요):
- F06 [high/held] The synopsis provides the BOIN target DLT rate, enrollment cap, dose levels, and a simulation reference but does not state cohort size, deci
- F07 [high/verified] The protocol specifies at least 60 randomized participants but does not provide the sample-size rationale, effect-size or precision assumpti
- F09 [high/verified] The randomized cohorts have only steady-state trough sampling, and the protocol does not describe a population-PK analysis or show that this
- F10 [high/held] The eligibility criteria specify a four-week anti-PD-(L)1 exclusion but do not state washouts for chemotherapy, radiation, biologics, or inv

## AX1-019 — finding 10건, 주입 결함 6건, 토큰 55,261

| 결과 | 주입 결함(요약) | 원 규범 문서 | 매칭 finding |
|---|---|---|---|
| 🟡 span만 적중 | After the recommended Phase 2 dose is selected from tolerability data, all subsequent participants will receiv | ICH-E4-1994 · II OBTAINING DOSE-RESPONSE INF | F02 |
| 🟡 span만 적중 | In this open-label, single-arm Phase 1/2 study, treatment activity will be assessed against historical respons | ICH-E4-1994 · IV GUIDANCE AND ADVICE | F06 |
| 🟡 span만 적중 | Dose-response analyses will be limited to the randomized expansion cohort, and data from dose-escalation parti | ICH-E4-1994 · II OBTAINING DOSE-RESPONSE INF | F03 |
| ❌ 놓침 | After enrolling the initial three participants at 10 mg, the study will proceed directly to a fixed 10 mg expa | MFDS-1443-01-2025 · 1 안내서-1443-01 2025. 8. 29. 제정 | - |
| 🟡 span만 적중 | All participants will receive the fixed 200 mg dose supplied in a single capsule strength throughout the study | FDA-DOSE-OPT-2024 · D Drug Formulation | F01 |
| ❌ 놓침 | Results from the expansion cohort will serve as the primary efficacy package for the planned marketing applica | FDA-EXPANSION-COHORTS-2022 · C Communications and Interacti | - |

주입 결함과 무관한 finding(정상판 기준 잘못 경고 후보, 사람 검토 필요):
- F04 [high/verified] The protocol states the BOIN target DLT rate, enrollment maximum, dose levels, and number of simulated scenarios but does not state cohort s
- F05 [high/verified] The protocol specifies a minimum randomized sample size and comparison domains but does not provide a sample-size justification, analysis or
- F07 [high/verified] The protocol uses the same liver-test schedule for all participants and does not specify intensified monitoring based on recent anti-PD-(L)1
- F08 [high/held] The synopsis refers to Appendix B but does not itself provide executable dose-interruption, reduction, discontinuation, rechallenge, or gene
- F09 [medium/verified] The protocol specifies a four-week anti-PD-(L)1 exclusion and recovery of prior-treatment toxicities to Grade 1 or lower but does not state 
- F10 [medium/verified] The protocol collects intensive PK profiles only in escalation subjects and steady-state trough samples only in randomized cohorts, without 

## AX1-020 — finding 4건, 주입 결함 6건, 토큰 52,348

| 결과 | 주입 결함(요약) | 원 규범 문서 | 매칭 finding |
|---|---|---|---|
| ❌ 놓침 | The study team will review emerging adverse-event data periodically and decide during the trial whether enroll | FDA-DOSE-OPT-2024 · C Safety and Tolerability | - |
| ❌ 놓침 | Patients with moderate hepatic impairment and the CYP2C19 poor-metabolizer genotype will be enrolled in the sa | FDA-DOSE-OPT-2024 · A Clinical Pharmacokinetics, P | - |
| 🟡 span만 적중 | Results from the expansion cohort will serve as the primary efficacy package for the planned marketing applica | FDA-EXPANSION-COHORTS-2022 · C Communications and Interacti | F04 |
| 🟡 span만 적중 | The expansion cohort will enroll 80 patients at 200 mg twice daily immediately after the first three participa | FDA-DOSE-OPT-2024 · III DOSAGE OPTIMIZATION RECOMM | F02, F03 |
| ❌ 놓침 | Blood samples will be collected for exploratory biomarker testing, but no pharmacokinetic sampling schedule or | FDA-DOSE-OPT-2024 · A Clinical Pharmacokinetics, P | - |
| 🟡 span만 적중 | The recommended Phase 2 dose will be selected solely from the highest tolerated dose in the escalation cohort, | FDA-DOSE-OPT-2024 · A Clinical Pharmacokinetics, P | F01 |

