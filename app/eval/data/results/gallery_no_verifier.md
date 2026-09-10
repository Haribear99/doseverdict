# 실패 사례 갤러리 — no_verifier

놓친 결함과 잘못 경고한 사례를 그대로 공개한다(제안서 4장 약속).
합계: 주입 결함 120건 중 놓침 5건, finding 219건 중 무관 84건.

## AX1-001 — finding 11건, 주입 결함 6건, 토큰 56,087

| 결과 | 주입 결함(요약) | 원 규범 문서 | 매칭 finding |
|---|---|---|---|
| 🟡 span만 적중 | The study team will review emerging adverse-event data periodically and decide during the trial whether enroll | FDA-DOSE-OPT-2024 · C Safety and Tolerability | F06 |
| 🟡 span만 적중 | All participants will receive the fixed 200 mg dose supplied in a single capsule strength throughout the study | FDA-DOSE-OPT-2024 · D Drug Formulation | F01 |
| 🟡 span만 적중 | The formulation-bridging expansion cohort will enroll participants receiving the new tablet or legacy capsule, | FDA-EXPANSION-COHORTS-2022 · F Evaluating Drug Product Chan | F05 |
| 🟡 span만 적중 | After the recommended Phase 2 dose is selected from tolerability data, all subsequent participants will receiv | ICH-E4-1994 · II OBTAINING DOSE-RESPONSE INF | F02 |
| ✅ 근거까지 적중 | Patients with moderate hepatic impairment and the CYP2C19 poor-metabolizer genotype will be enrolled in the sa | FDA-DOSE-OPT-2024 · A Clinical Pharmacokinetics, P | F03 |
| 🟡 span만 적중 | Dose–response analyses will be conducted only in the overall enrolled population, with no evaluations by age,  | ICH-E4-1994 · IV GUIDANCE AND ADVICE | F04 |

주입 결함과 무관한 finding(정상판 기준 잘못 경고 후보, 사람 검토 필요):
- F07 [high/verified] The protocol specifies at least 60 randomized participants but provides no sample-size justification, precision target, analysis population,
- F08 [high/verified] The protocol limits randomized-cohort PK collection to steady-state trough samples while proposing a power-model assessment of dose proporti
- F09 [high/verified] The liver-test schedule does not expressly specify more frequent testing after transaminase or bilirubin elevation. Monitor liver function t
- F10 [medium/verified] The protocol classifies DV-101 as an irreversible covalent KRAS G12C inhibitor but provides no dose-selection, target-engagement, DLT-window

## AX1-002 — finding 11건, 주입 결함 6건, 토큰 60,220

| 결과 | 주입 결함(요약) | 원 규범 문서 | 매칭 finding |
|---|---|---|---|
| 🟡 span만 적중 | Results from the expansion cohort will serve as the primary efficacy package for the planned marketing applica | FDA-EXPANSION-COHORTS-2022 · C Communications and Interacti | F05 |
| 🟡 span만 적중 | The recommended Phase 2 dose will be the highest dose at which no more than 30% of participants permanently di | ICH-E4-1994 · II OBTAINING DOSE-RESPONSE INF | F00, F02 |
| ✅ 근거까지 적중 | Patients with moderate hepatic impairment and the CYP2C19 poor-metabolizer genotype will be enrolled in the sa | FDA-DOSE-OPT-2024 · A Clinical Pharmacokinetics, P | F06 |
| 🟡 span만 적중 | The sponsor will issue a single cumulative safety update to investigators and the IRB at the end of each calen | FDA-EXPANSION-COHORTS-2022 · C IRB/Independent Ethics Commi | F01 |
| 🟡 span만 적중 | The combination expansion cohort will open after the first six participants complete cycle 1 of the investigat | FDA-EXPANSION-COHORTS-2022 · G Evaluating More Than One The | F04 |
| 🟡 span만 적중 | The expansion cohort will support the marketing application using investigator-assessed tumor responses at the | FDA-EXPANSION-COHORTS-2022 · B Evaluating Preliminary Antit | F03 |

주입 결함과 무관한 finding(정상판 기준 잘못 경고 후보, 사람 검토 필요):
- F07 [high/verified] The protocol collects only steady-state trough samples in randomized cohorts and does not specify randomized-cohort AUC, Cmax, or exposure-r
- F08 [high/verified] The protocol assigns at least 60 participants equally between two doses but does not state the comparison estimands, sample-size assumptions
- F09 [high/verified] The protocol states that four BOIN simulation scenarios were evaluated but does not report their assumptions or operating-characteristic res
- F10 [medium/verified] The protocol addresses hepatotoxicity and interstitial lung disease/pneumonitis only by reference to Appendix B, whose specific detection an

## AX1-003 — finding 11건, 주입 결함 6건, 토큰 61,049

| 결과 | 주입 결함(요약) | 원 규범 문서 | 매칭 finding |
|---|---|---|---|
| 🟡 span만 적중 | The recommended Phase 2 dose will be the highest dose at which no more than 30% of participants permanently di | ICH-E4-1994 · II OBTAINING DOSE-RESPONSE INF | F00, F04 |
| 🟡 span만 적중 | After the safety lead-in, all participants will receive 240 mg twice daily; no alternate dose will be evaluate | FDA-DOSE-OPT-2024 · B Trial Designs to Compare Mul | F01 |
| 🟡 span만 적중 | The study team will review emerging adverse-event data periodically and decide during the trial whether enroll | FDA-DOSE-OPT-2024 · C Safety and Tolerability | F03 |
| 🟡 span만 적중 | Concomitant medications will be recorded at enrollment, but no interaction studies or dedicated pharmacokineti | FDA-DOSE-OPT-2024 · A Clinical Pharmacokinetics, P | F09 |
| 🟡 span만 적중 | For the randomized Phase 2 portion, each of the three active-dose arms will be compared independently with pla | FDA-DOSE-OPT-2024 · B Trial Designs to Compare Mul | F02 |
| 🟡 span만 적중 | All recommendations in FDA-DOSE-OPT-2024 shall be implemented without deviation, and any investigator request  | FDA-DOSE-OPT-2024 · I INTRODUCTION | F10 |

주입 결함과 무관한 finding(정상판 기준 잘못 경고 후보, 사람 검토 필요):
- F05 [high/verified] The protocol lists PK, PD, safety, tolerability, and preliminary activity for candidate-dose comparison but does not specify exposure-respon
- F06 [high/verified] The protocol assigns at least 60 participants equally between two candidate doses but provides no sample-size justification, precision targe
- F07 [high/verified] The protocol specifies the liver-test analytes and routine schedule but places all toxicity dose-modification rules in Appendix B, whose thr
- F08 [high/verified] The protocol excludes anti-PD-(L)1 therapy only when administered within four weeks before the first dose and gives no rationale or enhanced

## AX1-004 — finding 11건, 주입 결함 6건, 토큰 56,075

| 결과 | 주입 결함(요약) | 원 규범 문서 | 매칭 finding |
|---|---|---|---|
| 🟡 span만 적중 | The dose-escalation and expansion cohorts will follow the same general treatment plan, with cohort-specific do | FDA-EXPANSION-COHORTS-2022 · A Initial Protocol | F06 |
| 🟡 span만 적중 | The randomized Phase 2 portion will compare three active dose levels with placebo, and each dose-versus-placeb | MFDS-1443-01-2025 · 3.2 다양한 용량을 비교하기 위한 임상시험 설계 | F02 |
| ❌ 놓침 | Participants will be enrolled sequentially into nonrandomized cohorts receiving 10, 30, or 60 mg once daily, w | FDA-DOSE-OPT-2024 · B Trial Designs to Compare Mul | - |
| 🟡 span만 적중 | All doses will be prepared as a fixed 0.5 mg/mL intravenous solution, including doses requiring infusion volum | FDA-DOSE-OPT-2024 · D Drug Formulation | F01 |
| 🟡 span만 적중 | 확장 코호트에서는 선행 임상자료나 노출·반응 분석과 무관하게 모든 환자에게 임상적으로 사용되는 표준 용량 200 mg을 투여한다. | MFDS-1443-01-2025 · 1 안내서-1443-01 2025. 8. 29. 제정 | F03 |
| 🟡 span만 적중 | Dose selection for expansion will be based solely on observed tumor response rates, without adjustment for tre | ICH-E4-1994 · IV GUIDANCE AND ADVICE | F04 |

주입 결함과 무관한 finding(정상판 기준 잘못 경고 후보, 사람 검토 필요):
- F05 [high/verified] The protocol identifies the BOIN target, maximum sample size, five planned doses, and four simulated scenarios but does not provide cohort s
- F07 [high/verified] The protocol cross-refers hepatotoxicity and ILD/pneumonitis dose-modification rules to Appendix B, which is not included in the supplied pr
- F08 [high/verified] The investigational-product description identifies DV-101 as sotorasib and states its target and mechanism but does not describe clinically 
- F09 [medium/verified] The protocol supplies a name, mechanism, target, and SMILES but no authoritative chemical identifiers, identity verification, covalent-bindi
- F10 [low/verified] The protocol specifies baseline testing, testing every 3 weeks for the first 3 months, and monthly testing thereafter but does not explicitl

## AX1-005 — finding 11건, 주입 결함 6건, 토큰 54,759

| 결과 | 주입 결함(요약) | 원 규범 문서 | 매칭 finding |
|---|---|---|---|
| 🟡 span만 적중 | The study team will review emerging adverse-event data periodically and decide during the trial whether enroll | FDA-DOSE-OPT-2024 · C Safety and Tolerability | F08 |
| 🟡 span만 적중 | In the pediatric expansion cohort, safety will be assessed only by recording adverse events at scheduled clini | FDA-EXPANSION-COHORTS-2022 · H Evaluating PK, Tolerability, | F02 |
| 🟡 span만 적중 | This amendment adds a higher-dose expansion cohort based on preliminary efficacy findings; the safety rational | FDA-EXPANSION-COHORTS-2022 · A Safety Monitoring and Report | F03 |
| 🟡 span만 적중 | The expansion cohort will support the marketing application using investigator-assessed tumor responses at the | FDA-EXPANSION-COHORTS-2022 · B Evaluating Preliminary Antit | F04, F05 |
| ✅ 근거까지 적중 | No pharmacodynamic or pharmacogenomic specimens will be collected, and the study will not evaluate genetic det | FDA-DOSE-OPT-2024 · A Clinical Pharmacokinetics, P | F07 |
| 🟡 span만 적중 | The study will be conducted under the sponsor's internal approval without submission of the final protocol to  | ICH-E4-1994 · 0 PREAMBLE | F01 |

주입 결함과 무관한 finding(정상판 기준 잘못 경고 후보, 사람 검토 필요):
- F06 [high/verified] The protocol specifies a randomized comparison of two candidate doses in at least 60 subjects across safety, tolerability, PK, PD, and preli
- F09 [high/verified] The protocol identifies the BOIN target, five planned doses, maximum sample size, and four simulated scenarios but leaves the operating rule
- F10 [high/verified] The listed exclusions specify a four-week washout only for anti-PD-(L)1 therapy and do not state washouts for other prior anticancer treatme

## AX1-006 — finding 11건, 주입 결함 6건, 토큰 56,675

| 결과 | 주입 결함(요약) | 원 규범 문서 | 매칭 finding |
|---|---|---|---|
| 🟡 span만 적중 | The recommended Phase 2 dose will be the highest dose tested with acceptable early laboratory findings, even i | FDA-DOSE-OPT-2024 · II BACKGROUND | F02 |
| 🟡 span만 적중 | The sponsor will compile aggregate safety data internally and submit cumulative reports to FDA at its discreti | FDA-EXPANSION-COHORTS-2022 · A Safety Monitoring and Report | F05 |
| 🟡 span만 적중 | The study will enroll adults with untreated low-risk indolent lymphoma for whom standard curative therapy is a | FDA-EXPANSION-COHORTS-2022 · IV DRUG PRODUCT AND SUBJECT CO | F04 |
| 🟡 span만 적중 | Participants who cross over to the alternate dose will be included in the overall safety and response analyses | FDA-DOSE-OPT-2024 · B Trial Designs to Compare Mul | F06 |
| 🟡 span만 적중 | The Phase 2 expansion dose will be fixed at 200 mg twice daily based solely on the recommended Phase 1 dose, w | FDA-DOSE-OPT-2024 · III DOSAGE OPTIMIZATION RECOMM | F01 |
| 🟡 span만 적중 | Results from the expansion cohort will serve as the primary efficacy package for the planned marketing applica | FDA-EXPANSION-COHORTS-2022 · C Communications and Interacti | F03 |

주입 결함과 무관한 finding(정상판 기준 잘못 경고 후보, 사람 검토 필요):
- F07 [high/verified] The protocol compares two candidate doses but does not specify exposure-response analyses linking individual exposure to efficacy, toxicity,
- F08 [high/verified] The protocol collects only steady-state trough samples in randomized participants and does not describe a validated sparse-sampling or popul
- F09 [high/verified] The BOIN summary states the target DLT rate, dose levels, subject cap, and existence of simulations but does not state cohort size, decision
- F10 [high/verified] The protocol incorporates hepatotoxicity and ILD/pneumonitis dose-modification rules only by reference to Appendix B, whose operative gradin

## AX1-007 — finding 11건, 주입 결함 6건, 토큰 57,983

| 결과 | 주입 결함(요약) | 원 규범 문서 | 매칭 finding |
|---|---|---|---|
| 🟡 span만 적중 | For the new pembrolizumab–investigational-agent combination in metastatic colorectal cancer, the study will pr | MFDS-1443-01-2025 · 3.5 후속 적응증 및 용법 | F04 |
| 🟡 span만 적중 | 확장 코호트에서는 선행 임상자료나 노출·반응 분석과 무관하게 모든 환자에게 임상적으로 사용되는 표준 용량 200 mg을 투여한다. | MFDS-1443-01-2025 · 1 안내서-1443-01 2025. 8. 29. 제정 | F05 |
| 🟡 span만 적중 | Interim safety and efficacy findings will be reviewed only after database lock at the end of the expansion pha | FDA-EXPANSION-COHORTS-2022 · II BACKGROUND | F02 |
| 🟡 span만 적중 | The formulation-bridging expansion cohort will enroll participants receiving the new tablet or legacy capsule, | FDA-EXPANSION-COHORTS-2022 · F Evaluating Drug Product Chan | F08 |
| 🟡 span만 적중 | After the recommended Phase 2 dose is selected from tolerability data, all subsequent participants will receiv | ICH-E4-1994 · II OBTAINING DOSE-RESPONSE INF | F03 |
| 🟡 span만 적중 | The starting dose and subsequent escalation levels will be selected solely by investigator consensus, without  | FDA-DOSE-OPT-2024 · III DOSAGE OPTIMIZATION RECOMM | F01 |

주입 결함과 무관한 finding(정상판 기준 잘못 경고 후보, 사람 검토 필요):
- F06 [high/verified] The protocol identifies domains for a randomized candidate-dose comparison but places the integrated RP2D criteria in an unavailable appendi
- F07 [high/verified] The protocol specifies the BOIN target, maximum enrollment, dose levels, and existence of simulations but does not provide executable escala
- F09 [high/verified] The protocol delegates dose-modification rules for hepatotoxicity, interstitial lung disease/pneumonitis, and other adverse reactions to an 
- F10 [medium/verified] The protocol restricts intensive PK profiles to escalation subjects and collects only steady-state trough samples in randomized cohorts whil

## AX1-008 — finding 11건, 주입 결함 6건, 토큰 56,699

| 결과 | 주입 결함(요약) | 원 규범 문서 | 매칭 finding |
|---|---|---|---|
| 🟡 span만 적중 | After participants complete 48 hours at the assigned dose level, the dose-response analysis will be performed  | ICH-E4-1994 · 1 Parallel dose-response | F01 |
| 🟡 span만 적중 | Dose–response analyses will be conducted only in the overall enrolled population, with no evaluations by age,  | ICH-E4-1994 · IV GUIDANCE AND ADVICE | F05 |
| 🟡 span만 적중 | The study will select the recommended Phase 2 dose from the first expansion cohort without collecting dose–res | ICH-E4-1994 · IV GUIDANCE AND ADVICE | F02 |
| 🟡 span만 적중 | After completing the dose-escalation portion, the study will open six parallel disease-specific expansion coho | FDA-EXPANSION-COHORTS-2022 · IV DRUG PRODUCT AND SUBJECT CO | F03 |
| 🟡 span만 적중 | The sponsor will include serious and unexpected adverse safety findings in the next scheduled annual safety re | FDA-EXPANSION-COHORTS-2022 · B Potential Opportunities and  | F04 |
| 🟡 span만 적중 | Participants will be enrolled sequentially into nonrandomized cohorts receiving 10, 30, or 60 mg once daily, w | FDA-DOSE-OPT-2024 · B Trial Designs to Compare Mul | F06 |

주입 결함과 무관한 finding(정상판 기준 잘못 경고 후보, 사람 검토 필요):
- F07 [high/verified] The protocol collects intensive first-dose and steady-state PK only in escalation subjects and limits randomized-cohort sampling to steady-s
- F08 [high/verified] The protocol assigns at least 30 subjects per candidate dose but does not state endpoint-specific estimands, precision or event-rate assumpt
- F09 [high/verified] The synopsis refers hepatotoxicity and ILD/pneumonitis dose-modification rules to Appendix B without stating actionable interruption, reduct
- F10 [medium/verified] The visit schedule lists Cycle 1 Days 1, 8, and 15 but does not identify visits for the planned 24-hour PK samples, the DLT assessment windo

## AX1-009 — finding 11건, 주입 결함 6건, 토큰 58,064

| 결과 | 주입 결함(요약) | 원 규범 문서 | 매칭 finding |
|---|---|---|---|
| 🟡 span만 적중 | The sponsor will finalize the dose-comparison design and proceed directly to patient enrollment without seekin | MFDS-1443-01-2025 · 3.2 다양한 용량을 비교하기 위한 임상시험 설계 | F10 |
| 🟡 span만 적중 | After the sponsor transfers production to a new manufacturing site and changes the formulation, the study will | FDA-EXPANSION-COHORTS-2022 · F Evaluating Drug Product Chan | F03 |
| 🟡 span만 적중 | For every participant, the dose-escalation algorithm will identify that individual’s optimal dose from observe | ICH-E4-1994 · IV GUIDANCE AND ADVICE | F02 |
| 🟡 span만 적중 | Participants may take the study tablets with or without meals and may continue all clinically indicated concom | FDA-DOSE-OPT-2024 · A Clinical Pharmacokinetics, P | F08 |
| 🟡 span만 적중 | The medical monitor may be any licensed physician with general inpatient-care experience; prior oncology pract | FDA-EXPANSION-COHORTS-2022 · A Safety Monitoring and Report | F09 |
| 🟡 span만 적중 | The Phase 1 portion will escalate cohorts until the highest dose with an acceptable toxicity profile is identi | FDA-DOSE-OPT-2024 · II BACKGROUND | F01 |

주입 결함과 무관한 finding(정상판 기준 잘못 경고 후보, 사람 검토 필요):
- F04 [high/verified] The protocol specifies at least 60 randomized subjects and the comparison domains but does not state the sample-size assumptions, analysis m
- F05 [high/verified] The secondary objectives include tolerability over time but do not identify hepatotoxicity or interstitial lung disease/pneumonitis as toxic
- F06 [high/verified] The protocol delegates hepatotoxicity and interstitial lung disease/pneumonitis dose-modification rules to Appendix B, which was not provide
- F07 [high/verified] The protocol specifies a BOIN target DLT rate, five dose levels, a maximum sample size, and four simulated scenarios, but the referenced ope

## AX1-010 — finding 11건, 주입 결함 6건, 토큰 57,558

| 결과 | 주입 결함(요약) | 원 규범 문서 | 매칭 finding |
|---|---|---|---|
| 🟡 span만 적중 | In the pediatric expansion cohort, safety will be assessed only by recording adverse events at scheduled clini | FDA-EXPANSION-COHORTS-2022 · H Evaluating PK, Tolerability, | F02 |
| 🟡 span만 적중 | The pediatric expansion cohort will proceed under the adult development plan, with pediatric assessments docum | FDA-EXPANSION-COHORTS-2022 · H Evaluating PK, Tolerability, | F01 |
| ❌ 놓침 | Dose selection for expansion will be based solely on the prespecified primary endpoint from the escalation coh | ICH-E4-1994 · IV GUIDANCE AND ADVICE | - |
| 🟡 span만 적중 | Participants assigned to the control arm may cross over to the investigational therapy after progression; safe | MFDS-1443-01-2025 · 3.2 다양한 용량을 비교하기 위한 임상시험 설계 | F05 |
| ❌ 놓침 | The medical monitor may be any licensed physician with general inpatient-care experience; prior oncology pract | FDA-EXPANSION-COHORTS-2022 · A Safety Monitoring and Report | - |
| 🟡 span만 적중 | The recommended Phase 2 dose will be selected solely from dose-limiting toxicity rates observed during Cycle 1 | FDA-DOSE-OPT-2024 · I INTRODUCTION | F00, F03 |

주입 결함과 무관한 finding(정상판 기준 잘못 경고 후보, 사람 검토 필요):
- F04 [critical/verified] The only stated age criterion is age ≥18 despite the protocol's separate plan for a pediatric expansion cohort. No participant should be enr
- F06 [high/verified] The protocol gives the routine liver-test schedule but provides only an Appendix B reference for hepatotoxicity and ILD/pneumonitis manageme
- F07 [high/verified] The protocol identifies the BOIN target, maximum sample size, dose levels, and four simulated scenarios but does not state cohort rules, dec
- F08 [high/verified] The protocol sets a minimum randomized sample size of 60 but gives no dose-specific assumptions, precision targets, selection thresholds, mi
- F09 [medium/verified] The protocol excludes anti-PD-(L)1 therapy within four weeks before the first dose but states no individualized criterion for unresolved imm
- F10 [medium/verified] The protocol uses intensive first-dose and steady-state sampling in escalation subjects but collects only steady-state trough samples in ran

## AX1-011 — finding 11건, 주입 결함 6건, 토큰 57,498

| 결과 | 주입 결함(요약) | 원 규범 문서 | 매칭 finding |
|---|---|---|---|
| 🟡 span만 적중 | Protocol deviations will be reviewed individually by the study team, with importance assigned after database l | ICH-E6R3-2025 · 3.9.1 The sponsor should ensur | F10 |
| 🟡 span만 적중 | Pharmacokinetic analyses will use pooled data without examining covariates or reporting results by clinically  | MFDS-1443-01-2025 · 3.1 임상 약동학, 약력학 및 약물유전체학 | F05 |
| 🟡 span만 적중 | The study will assess treatment activity using weekly change in body weight and evaluate safety primarily thro | MFDS-1443-01-2025 · 3.1 임상 약동학, 약력학 및 약물유전체학 | F02 |
| 🟡 span만 적중 | The sponsor will include serious and unexpected adverse safety findings in the next scheduled annual safety re | FDA-EXPANSION-COHORTS-2022 · B Potential Opportunities and  | F01 |
| ✅ 근거까지 적중 | Patients with moderate hepatic impairment and the CYP2C19 poor-metabolizer genotype will be enrolled in the sa | FDA-DOSE-OPT-2024 · A Clinical Pharmacokinetics, P | F04 |
| 🟡 span만 적중 | Patients in the expansion cohort will receive the investigator-selected dose of either 80 mg or 120 mg once da | FDA-EXPANSION-COHORTS-2022 · VI STATISTICAL CONSIDERATIONS | F03 |

주입 결함과 무관한 finding(정상판 기준 잘못 경고 후보, 사람 검토 필요):
- F06 [high/verified] The protocol names outcomes for the randomized candidate-dose comparison but does not specify dose- or exposure-response estimands, models, 
- F07 [high/verified] The protocol places the integrated RP2D criteria in Appendix D but does not state those criteria, their weighting, uncertainty handling, min
- F08 [high/verified] The protocol identifies BOIN parameters and refers to simulations in Appendix C but does not provide cohort sizes, transition boundaries, ov
- F09 [high/verified] The protocol lists dose levels from 180 mg through 960 mg without stating the nonclinical, pharmacologic, toxicologic, prior clinical-exposu

## AX1-012 — finding 11건, 주입 결함 6건, 토큰 59,217

| 결과 | 주입 결함(요약) | 원 규범 문서 | 매칭 finding |
|---|---|---|---|
| 🟡 span만 적중 | Interim safety and efficacy findings will be reviewed only after database lock at the end of the expansion pha | FDA-EXPANSION-COHORTS-2022 · II BACKGROUND | F03 |
| 🟡 span만 적중 | The study will enroll adults with untreated low-risk indolent lymphoma for whom standard curative therapy is a | FDA-EXPANSION-COHORTS-2022 · IV DRUG PRODUCT AND SUBJECT CO | F04 |
| 🟡 span만 적중 | This first-in-human dose-escalation study will enroll participants using an ad hoc design selected for operati | ICH-E4-1994 · IV GUIDANCE AND ADVICE | F01 |
| 🟡 span만 적중 | Blood samples will be collected for exploratory biomarker testing, but no pharmacokinetic sampling schedule or | FDA-DOSE-OPT-2024 · A Clinical Pharmacokinetics, P | F02 |
| 🟡 span만 적중 | Enrollment in the pediatric expansion cohort will be open to children with newly diagnosed or relapsed solid t | FDA-EXPANSION-COHORTS-2022 · H Evaluating PK, Tolerability, | F05 |
| ❌ 놓침 | Tolerability will be assessed exclusively through investigator-recorded adverse events and laboratory findings | FDA-DOSE-OPT-2024 · C Safety and Tolerability | - |

주입 결함과 무관한 finding(정상판 기준 잘못 경고 후보, 사람 검토 필요):
- F06 [high/verified] The protocol lists five once-daily dose levels from 180 mg through 960 mg without stating the basis for the starting dose, dose range, or in
- F07 [high/verified] The protocol specifies randomization of at least 60 subjects in a 1:1 ratio but does not state sample-size assumptions, stratification, endp
- F08 [high/verified] The protocol refers RP2D selection to integrated criteria in Appendix D but does not provide the criteria, endpoint thresholds, weighting, u
- F09 [high/verified] The listed exclusion criteria specify a four-week washout only for anti-PD-(L)1 therapy and do not state washouts for other systemic antican
- F10 [high/verified] The protocol gives a routine liver-test schedule and refers toxicity dose-modification rules to Appendix B, but it does not state an operati

## AX1-013 — finding 11건, 주입 결함 6건, 토큰 58,229

| 결과 | 주입 결함(요약) | 원 규범 문서 | 매칭 finding |
|---|---|---|---|
| 🟡 span만 적중 | Enrollment in the pediatric expansion cohort will be open to children with newly diagnosed or relapsed solid t | FDA-EXPANSION-COHORTS-2022 · H Evaluating PK, Tolerability, | F02 |
| 🟡 span만 적중 | The sponsor will finalize the dose-comparison design and proceed directly to patient enrollment without seekin | MFDS-1443-01-2025 · 3.2 다양한 용량을 비교하기 위한 임상시험 설계 | F06 |
| 🟡 span만 적중 | During this first-in-human study, safety will be assessed only by participant-reported symptoms, and treatment | FDA-DOSE-OPT-2024 · A Clinical Pharmacokinetics, P | F04 |
| 🟡 span만 적중 | The study will enroll adults with untreated low-risk indolent lymphoma for whom standard curative therapy is a | FDA-EXPANSION-COHORTS-2022 · IV DRUG PRODUCT AND SUBJECT CO | F03 |
| 🟡 span만 적중 | Patients with moderate hepatic impairment and carriers of the ABCB1 variant will be enrolled only in the expan | FDA-DOSE-OPT-2024 · A Clinical Pharmacokinetics, P | F05 |
| 🟡 span만 적중 | After enrolling the initial three participants at 10 mg, the study will proceed directly to a fixed 10 mg expa | MFDS-1443-01-2025 · 1 안내서-1443-01 2025. 8. 29. 제정 | F01 |

주입 결함과 무관한 finding(정상판 기준 잘못 경고 후보, 사람 검토 필요):
- F07 [high/verified] The protocol limits randomized-cohort PK collection to steady-state trough samples and states only a dose-proportionality analysis by power 
- F08 [high/verified] The protocol specifies at least 60 randomized participants and comparison domains but does not state a sample-size rationale, estimands, pre
- F09 [high/verified] The protocol places hepatotoxicity, ILD/pneumonitis, and other adverse-reaction dose-modification rules in Appendix B, which is not included
- F10 [medium/verified] The protocol specifies a five-level BOIN design with a 30% target DLT rate and maximum enrollment of 36 but provides no simulation assumptio

## AX1-014 — finding 11건, 주입 결함 6건, 토큰 59,438

| 결과 | 주입 결함(요약) | 원 규범 문서 | 매칭 finding |
|---|---|---|---|
| 🟡 span만 적중 | For every participant, the dose-escalation algorithm will identify that individual’s optimal dose from observe | ICH-E4-1994 · IV GUIDANCE AND ADVICE | F03 |
| 🟡 span만 적중 | Pharmacokinetic blood samples will be collected only before dosing and at 1 hour after the first administratio | MFDS-1443-01-2025 · 3.1 임상 약동학, 약력학 및 약물유전체학 | F05 |
| 🟡 span만 적중 | After completing the dose-escalation study, participants will enroll into the expansion cohorts under the same | FDA-EXPANSION-COHORTS-2022 · A Initial Protocol | F06 |
| 🟡 span만 적중 | After identification of a potentially fatal dose-limiting toxicity during escalation, the study will open all  | FDA-EXPANSION-COHORTS-2022 · A Assessing Safety of Recommen | F01 |
| 🟡 span만 적중 | The sponsor will issue a single cumulative safety update to investigators and the IRB at the end of each calen | FDA-EXPANSION-COHORTS-2022 · C IRB/Independent Ethics Commi | F02 |
| 🟡 span만 적중 | The recommended Phase 2 dose will be selected using tumor response and exposure data only; treatment discontin | FDA-DOSE-OPT-2024 · C Safety and Tolerability | F00, F04 |

주입 결함과 무관한 finding(정상판 기준 잘못 경고 후보, 사람 검토 필요):
- F07 [high/verified] The protocol assigns at least 30 participants per candidate dose but does not state endpoint definitions, decision thresholds, effect-size a
- F08 [high/verified] The protocol states that four BOIN scenarios were simulated but provides no scenario assumptions, operating-characteristic results, overdose
- F09 [high/verified] The synopsis refers hepatotoxicity and ILD/pneumonitis management to Appendix B without stating the diagnostic, dose-hold, discontinuation, 
- F10 [high/verified] The key eligibility criteria specify a four-week anti-PD-(L)1 restriction but state no washout periods for chemotherapy, targeted therapy, r

## AX1-015 — finding 10건, 주입 결함 6건, 토큰 58,517

| 결과 | 주입 결함(요약) | 원 규범 문서 | 매칭 finding |
|---|---|---|---|
| 🟡 span만 적중 | The recommended Phase 2 dose will be selected solely from dose-limiting toxicity rates observed during Cycle 1 | FDA-DOSE-OPT-2024 · I INTRODUCTION | F02 |
| 🟡 span만 적중 | Dose selection for expansion will be based solely on observed tumor response rates, without adjustment for tre | ICH-E4-1994 · IV GUIDANCE AND ADVICE | F03 |
| 🟡 span만 적중 | The biomarker-selected expansion cohort will enroll 30 participants, with no assumptions, precision targets, h | FDA-EXPANSION-COHORTS-2022 · VI STATISTICAL CONSIDERATIONS | F06 |
| 🟡 span만 적중 | After the recommended starting dose is established, all subsequent participants will receive the same fixed do | ICH-E4-1994 · II OBTAINING DOSE-RESPONSE INF | F01 |
| 🟡 span만 적중 | This first-in-human dose-escalation study will enroll participants using an ad hoc design selected for operati | ICH-E4-1994 · IV GUIDANCE AND ADVICE | F01 |
| 🟡 span만 적중 | The combination expansion cohort will open after the first six participants complete cycle 1 of the investigat | FDA-EXPANSION-COHORTS-2022 · G Evaluating More Than One The | F04 |

주입 결함과 무관한 finding(정상판 기준 잘못 경고 후보, 사람 검토 필요):
- F05 [high/verified] The protocol collects only steady-state trough samples in the randomized cohorts and does not specify how individual AUC or Cmax will be est
- F07 [high/verified] The protocol locates hepatotoxicity and ILD/pneumonitis dose-modification rules in Appendix B, which is not included in the supplied protoco
- F08 [high/verified] The stated eligibility criteria specify a four-week washout only for anti-PD-(L)1 therapy and do not state washouts for other systemic thera
- F09 [low/verified] The protocol identifies DV-101 as sotorasib and supplies a stereospecific SMILES containing a covalent-inhibitor structural alert, but it pr

## AX1-016 — finding 11건, 주입 결함 6건, 토큰 57,259

| 결과 | 주입 결함(요약) | 원 규범 문서 | 매칭 finding |
|---|---|---|---|
| 🟡 span만 적중 | The study will select the recommended Phase 2 dose from the first expansion cohort without collecting dose–res | ICH-E4-1994 · IV GUIDANCE AND ADVICE | F02 |
| 🟡 span만 적중 | The formulation-bridging expansion cohort will enroll participants receiving the new tablet or legacy capsule, | FDA-EXPANSION-COHORTS-2022 · F Evaluating Drug Product Chan | F09 |
| 🟡 span만 적중 | After identifying the first tolerable dose, all subsequent participants will receive only that dose, with no c | MFDS-1443-01-2025 · 3.2 다양한 용량을 비교하기 위한 임상시험 설계 | F01 |
| 🟡 span만 적중 | For this intravenous oncology study, the 500 mg dose will be prepared as a 50 mg/mL solution, requiring admini | MFDS-1443-01-2025 · 3.4 의약품의 함량 및 제형 | F03 |
| 🟡 span만 적중 | The disease-specific expansion cohort will enroll up to 60 participants without interim futility monitoring or | FDA-EXPANSION-COHORTS-2022 · B Evaluating Preliminary Antit | F10 |
| ✅ 근거까지 적중 | All recommendations in FDA-DOSE-OPT-2024 shall be implemented without deviation, and any investigator request  | FDA-DOSE-OPT-2024 · I INTRODUCTION | F04 |

주입 결함과 무관한 finding(정상판 기준 잘못 경고 후보, 사람 검토 필요):
- F05 [high/verified] The randomized dose-comparison sentence specifies sample size and assessment domains but does not state exposure-response estimands, assumpt
- F06 [high/verified] The protocol identifies the BOIN target, dose levels, maximum sample size, and existence of simulations but does not state cohort size, tran
- F07 [high/verified] The protocol specifies routine liver-test timing but does not specify a more frequent testing schedule after transaminase or bilirubin abnor
- F08 [high/verified] The visit schedule states visit and tumor-assessment timing but does not identify safety procedures to be performed at those visits. The inv

## AX1-017 — finding 11건, 주입 결함 6건, 토큰 54,197

| 결과 | 주입 결함(요약) | 원 규범 문서 | 매칭 finding |
|---|---|---|---|
| 🟡 span만 적중 | Population pharmacokinetic analyses will be performed only after database lock using the final pooled dataset, | FDA-DOSE-OPT-2024 · A Clinical Pharmacokinetics, P | F09 |
| 🟡 span만 적중 | The study will select the recommended Phase 2 dose from the first dose level that meets the preliminary respon | FDA-DOSE-OPT-2024 · 7 See 21 CFR 312.42 | F02 |
| 🟡 span만 적중 | The recommended Phase 2 dose will be the highest dose tested with acceptable early laboratory findings, even i | FDA-DOSE-OPT-2024 · II BACKGROUND | F03 |
| 🟡 span만 적중 | Dose selection for expansion will be based solely on the prespecified primary endpoint from the escalation coh | ICH-E4-1994 · IV GUIDANCE AND ADVICE | F04 |
| 🟡 span만 적중 | The study will assess treatment activity using weekly change in body weight and evaluate safety primarily thro | MFDS-1443-01-2025 · 3.1 임상 약동학, 약력학 및 약물유전체학 | F01 |
| 🟡 span만 적중 | The protocol will continue enrollment in each expansion cohort until the planned sample size is reached, witho | FDA-EXPANSION-COHORTS-2022 · VI STATISTICAL CONSIDERATIONS | F05 |

주입 결함과 무관한 finding(정상판 기준 잘못 경고 후보, 사람 검토 필요):
- F06 [high/verified] The protocol assigns at least 60 subjects equally between two candidate doses but does not state assumptions, precision targets, operating c
- F07 [high/verified] The protocol identifies the BOIN target, maximum enrollment, dose levels, and four simulated scenarios but does not provide executable escal
- F08 [high/verified] The protocol limits randomized-cohort PK collection to steady-state trough samples while proposing a power-model assessment of dose proporti
- F10 [high/verified] The eligibility text specifies a four-week anti-PD-(L)1 washout and recovery of prior-treatment toxicities but gives no washout intervals fo

## AX1-018 — finding 11건, 주입 결함 6건, 토큰 57,215

| 결과 | 주입 결함(요약) | 원 규범 문서 | 매칭 finding |
|---|---|---|---|
| 🟡 span만 적중 | All participants will receive 80 mg orally twice daily from Cycle 1 Day 1, with no intra-patient dose escalati | ICH-E4-1994 · I INTRODUCTION | F01 |
| 🟡 span만 적중 | After the recommended Phase 2 dose is selected, no additional dose-optimization or comparative dose evaluation | FDA-DOSE-OPT-2024 · II BACKGROUND | F10 |
| 🟡 span만 적중 | The recommended Phase 2 dose will be selected solely from dose-limiting toxicity rates observed during Cycle 1 | FDA-DOSE-OPT-2024 · I INTRODUCTION | F00, F03 |
| 🟡 span만 적중 | After the safety lead-in, all participants will receive 240 mg twice daily; no alternate dose will be evaluate | FDA-DOSE-OPT-2024 · B Trial Designs to Compare Mul | F02 |
| 🟡 span만 적중 | The recommended Phase 2 dose will be the highest dose tested with acceptable early laboratory findings, even i | FDA-DOSE-OPT-2024 · II BACKGROUND | F00, F04 |
| 🟡 span만 적중 | Participants who cross over to the alternate dose will be included in the overall safety and response analyses | FDA-DOSE-OPT-2024 · B Trial Designs to Compare Mul | F09 |

주입 결함과 무관한 finding(정상판 기준 잘못 경고 후보, 사람 검토 필요):
- F05 [critical/verified] The protocol delegates hepatotoxicity and interstitial lung disease/pneumonitis dose-modification rules to Appendix B, whose thresholds and 
- F06 [high/verified] The protocol specifies baseline, every-three-week, and monthly liver testing but does not expressly prescribe more frequent testing after tr
- F07 [high/verified] The supplied BOIN description gives the target DLT rate, maximum enrollment, dose levels, and a simulation statement but does not provide co
- F08 [high/verified] The protocol specifies a 60-participant randomized comparison but does not state its sample-size assumptions, statistical decision threshold

## AX1-019 — finding 11건, 주입 결함 6건, 토큰 58,841

| 결과 | 주입 결함(요약) | 원 규범 문서 | 매칭 finding |
|---|---|---|---|
| 🟡 span만 적중 | After the recommended Phase 2 dose is selected from tolerability data, all subsequent participants will receiv | ICH-E4-1994 · II OBTAINING DOSE-RESPONSE INF | F03 |
| 🟡 span만 적중 | In this open-label, single-arm Phase 1/2 study, treatment activity will be assessed against historical respons | ICH-E4-1994 · IV GUIDANCE AND ADVICE | F05 |
| 🟡 span만 적중 | Dose-response analyses will be limited to the randomized expansion cohort, and data from dose-escalation parti | ICH-E4-1994 · II OBTAINING DOSE-RESPONSE INF | F07 |
| 🟡 span만 적중 | After enrolling the initial three participants at 10 mg, the study will proceed directly to a fixed 10 mg expa | MFDS-1443-01-2025 · 1 안내서-1443-01 2025. 8. 29. 제정 | F01 |
| 🟡 span만 적중 | All participants will receive the fixed 200 mg dose supplied in a single capsule strength throughout the study | FDA-DOSE-OPT-2024 · D Drug Formulation | F02 |
| 🟡 span만 적중 | Results from the expansion cohort will serve as the primary efficacy package for the planned marketing applica | FDA-EXPANSION-COHORTS-2022 · C Communications and Interacti | F04 |

주입 결함과 무관한 finding(정상판 기준 잘못 경고 후보, 사람 검토 필요):
- F06 [high/verified] The protocol specifies at least 60 randomized subjects but provides no sample-size assumptions, decision thresholds, stratification factors,
- F08 [high/verified] The protocol places the dose-modification rules for hepatotoxicity, interstitial lung disease/pneumonitis, and other adverse reactions in an
- F09 [high/verified] The investigational-product description identifies sotorasib and its mechanism but does not describe anticipated product risks, precautions,
- F10 [low/verified] The liver-test schedule does not expressly specify more frequent testing when transaminase and/or bilirubin abnormalities develop. Liver fun

## AX1-020 — finding 11건, 주입 결함 6건, 토큰 60,239

| 결과 | 주입 결함(요약) | 원 규범 문서 | 매칭 finding |
|---|---|---|---|
| 🟡 span만 적중 | The study team will review emerging adverse-event data periodically and decide during the trial whether enroll | FDA-DOSE-OPT-2024 · C Safety and Tolerability | F03 |
| 🟡 span만 적중 | Patients with moderate hepatic impairment and the CYP2C19 poor-metabolizer genotype will be enrolled in the sa | FDA-DOSE-OPT-2024 · A Clinical Pharmacokinetics, P | F06 |
| ❌ 놓침 | Results from the expansion cohort will serve as the primary efficacy package for the planned marketing applica | FDA-EXPANSION-COHORTS-2022 · C Communications and Interacti | - |
| 🟡 span만 적중 | The expansion cohort will enroll 80 patients at 200 mg twice daily immediately after the first three participa | FDA-DOSE-OPT-2024 · III DOSAGE OPTIMIZATION RECOMM | F02 |
| 🟡 span만 적중 | Blood samples will be collected for exploratory biomarker testing, but no pharmacokinetic sampling schedule or | FDA-DOSE-OPT-2024 · A Clinical Pharmacokinetics, P | F04 |
| 🟡 span만 적중 | The recommended Phase 2 dose will be selected solely from the highest tolerated dose in the escalation cohort, | FDA-DOSE-OPT-2024 · A Clinical Pharmacokinetics, P | F00, F01 |

주입 결함과 무관한 finding(정상판 기준 잘못 경고 후보, 사람 검토 필요):
- F05 [high/verified] The protocol limits randomized-cohort PK collection to steady-state trough samples and specifies only a dose-proportionality power model, wi
- F07 [high/verified] The protocol identifies the BOIN target, maximum sample size, dose levels, and number of simulated scenarios but does not provide the scenar
- F08 [high/verified] The protocol specifies baseline, every-three-week, and monthly liver testing but does not state intensified testing after transaminase or bi
- F09 [medium/verified] The supplied protocol text refers hepatotoxicity, interstitial lung disease/pneumonitis, and other adverse-reaction management to Appendix B
- F10 [medium/verified] The protocol asserts that DV-101 is sotorasib and supplies a SMILES and target annotation, but the sentence contains no authoritative record

