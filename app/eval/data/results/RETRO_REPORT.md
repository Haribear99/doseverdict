# 실사례 후향 검증 결과 (`retro`, 자동 생성 2026-09-29T05:37, `python -m app.eval.retro analyze`)

사전 등록: `docs/retro_prereg.md`. n = 43(양성 14). 판정: **신호 확인 안 됨(null) — S1 AUROC CI가 0.5를 포함**

| 점수 | 설명 | AUROC [95% CI] | PR-AUC (무작위 기준 0.326) |
|---|---|---|---|
| S1 | 1차: 검증된 용량최적화 finding 수 | 0.440 [0.270, 0.621] | 0.350 |
| S2 | 2차: 용량최적화 finding 중증도 가중합(검증+보류) | 0.516 [0.330, 0.701] | 0.406 |
| B1 | 키워드 규칙(초록, LLM 없음) | 0.466 [0.379, 0.555] | 0.316 |
| B2 | 승인연도(시대 교란 점검) | 0.499 [0.325, 0.677] | 0.342 |
| B3 | 축③ 라벨 규칙(승인 후 라벨 — 참고용) (n=31) | 0.679 [0.473, 0.854] | 0.481 |
| B4 | 사후 대조군: 약 이름을 준 모델 기억(도구 없음) (n=43) | 0.709 [0.530, 0.866] | 0.651 |

S1−B1 AUROC 차이 95% CI (-0.24, 0.185), S1−B2 (-0.312, 0.188) (기술용).
재식별 탐침: gpt-6-sol이 마스킹 입력에서 성분명을 맞힌 비율 1.000.
사후 탐침(사전 등록 밖): SMILES 제거 1.0, SMILES·표적·기전 제거 0.977 — 출판 초록 본문만으로도 재식별된다.

## 사후 기술통계(사전 등록 밖)

- 검증된 용량최적화 finding이 1개 이상인 케이스 43/43 — 양성·음성 가리지 않고 지적한다(평균 S1 양성 3.57, 음성 3.83).
- F00(TCR) 기권 43/43 — 라벨 차단, 마스킹으로 ChEMBL 이름 조회(IC50) 실패, 초록 PK는 8건에서 일부만 추출 → 입력 부족으로 전형값 없이 멈춤.
- S1과 모델 기억(B4)의 Spearman ρ = -0.26 (p = 0.092) — 에이전트 점수가 기억 신호를 따라가지 않았다(오염을 배제하는 증거는 아님).
- 토큰 합계 1,197,050(케이스당 27,838), 탐침·기억 대조군 별도.

## 케이스별

| 케이스 | 약물 | 승인 | PMR | S1 | S2 | B1 | F00 | 재식별 | 토큰 |
|---|---|---|---|---|---|---|---|---|---|
| RETRO-07 | futibatinib | 2022 | ● | 6 | 14 | 0 | abstain | 예 | 29,316 |
| RETRO-33 | cabozantinib | 2012 | ● | 5 | 14 | 0 | abstain | 예 | 26,941 |
| RETRO-39 | ponatinib | 2012 | ● | 5 | 12 | 0 | abstain | 예 | 28,718 |
| RETRO-01 | adagrasib | 2022 | ● | 4 | 9 | 0 | abstain | 예 | 30,194 |
| RETRO-11 | inavolisib | 2024 | ● | 4 | 11 | 0 | abstain | 예 | 26,680 |
| RETRO-13 | lenvatinib | 2015 | ● | 4 | 8 | 0 | abstain | 예 | 26,855 |
| RETRO-36 | infigratinib | 2021 | ● | 4 | 9 | 0 | abstain | 예 | 33,774 |
| RETRO-42 | selinexor | 2019 | ● | 4 | 12 | 0 | abstain | 예 | 27,230 |
| RETRO-03 | ceritinib | 2014 | ● | 3 | 9 | 0 | abstain | 예 | 28,037 |
| RETRO-10 | idelalisib | 2014 | ● | 3 | 8 | 0 | abstain | 예 | 24,761 |
| RETRO-23 | sotorasib | 2021 | ● | 3 | 11 | 0 | abstain | 예 | 27,100 |
| RETRO-40 | quizartinib | 2023 | ● | 2 | 6 | 0 | abstain | 예 | 25,857 |
| RETRO-41 | ribociclib | 2017 | ● | 2 | 4 | 0 | abstain | 예 | 27,577 |
| RETRO-38 | panobinostat | 2015 | ● | 1 | 3 | 1 | abstain | 예 | 27,597 |
| RETRO-09 | ibrutinib | 2013 | ○ | 6 | 14 | 0 | abstain | 예 | 27,223 |
| RETRO-30 | afatinib | 2013 | ○ | 6 | 13 | 0 | abstain | 예 | 28,932 |
| RETRO-05 | erdafitinib | 2019 | ○ | 5 | 11 | 0 | abstain | 예 | 28,329 |
| RETRO-06 | everolimus | 2009 | ○ | 5 | 10 | 0 | abstain | 예 | 28,923 |
| RETRO-12 | lazertinib | 2024 | ○ | 5 | 13 | 1 | abstain | 예 | 33,786 |
| RETRO-17 | palbociclib | 2015 | ○ | 5 | 12 | 0 | abstain | 예 | 29,440 |
| RETRO-24 | tovorafenib | 2024 | ○ | 5 | 13 | 0 | abstain | 예 | 26,777 |
| RETRO-25 | tucatinib | 2020 | ○ | 5 | 11 | 0 | abstain | 예 | 28,937 |
| RETRO-27 | vorasidenib | 2024 | ○ | 5 | 13 | 0 | abstain | 예 | 25,593 |
| RETRO-28 | zongertinib | 2025 | ○ | 5 | 14 | 1 | abstain | 예 | 26,325 |
| RETRO-02 | brigatinib | 2017 | ○ | 4 | 11 | 0 | abstain | 예 | 35,419 |
| RETRO-08 | glasdegib | 2018 | ○ | 4 | 9 | 0 | abstain | 예 | 32,737 |
| RETRO-14 | nilotinib | 2007 | ○ | 4 | 13 | 0 | abstain | 예 | 29,866 |
| RETRO-15 | osimertinib | 2015 | ○ | 4 | 10 | 0 | abstain | 예 | 25,796 |
| RETRO-26 | vandetanib | 2011 | ○ | 4 | 8 | 0 | abstain | 예 | 27,798 |
| RETRO-32 | bosutinib | 2012 | ○ | 4 | 7 | 0 | abstain | 예 | 25,852 |
| RETRO-35 | elacestrant | 2023 | ○ | 4 | 8 | 1 | abstain | 예 | 27,524 |
| RETRO-43 | sonidegib | 2015 | ○ | 4 | 10 | 0 | abstain | 예 | 28,181 |
| RETRO-16 | pacritinib | 2022 | ○ | 3 | 8 | 0 | abstain | 예 | 29,191 |
| RETRO-18 | pirtobrutinib | 2023 | ○ | 3 | 7 | 2 | abstain | 예 | 30,099 |
| RETRO-20 | repotrectinib | 2023 | ○ | 3 | 8 | 0 | abstain | 예 | 24,481 |
| RETRO-21 | ruxolitinib | 2011 | ○ | 3 | 7 | 0 | abstain | 예 | 28,925 |
| RETRO-22 | selpercatinib | 2020 | ○ | 3 | 8 | 0 | abstain | 예 | 24,074 |
| RETRO-29 | acalabrutinib | 2017 | ○ | 3 | 8 | 0 | abstain | 예 | 25,817 |
| RETRO-31 | alpelisib | 2019 | ○ | 3 | 8 | 0 | abstain | 예 | 26,819 |
| RETRO-19 | pralsetinib | 2020 | ○ | 2 | 5 | 0 | abstain | 예 | 21,485 |
| RETRO-34 | capivasertib | 2023 | ○ | 2 | 5 | 0 | abstain | 예 | 28,707 |
| RETRO-04 | crizotinib | 2011 | ○ | 1 | 3 | 0 | abstain | 예 | 26,431 |
| RETRO-37 | mobocertinib | 2021 | ○ | 1 | 3 | 0 | abstain | 예 | 22,946 |

## 양성 사례의 용량최적화 finding 원문

**RETRO-01 adagrasib**
- F01 [verified/high] The sentence identifies safety, tolerability, and observed pharmacokinetics as the basis for the 600 mg twice-daily RP2D but gives no comparison with the other regimens studied. When selecting dosages for further evaluat — span: "The recommended phase II dose (RP2D) was 600 mg twice a day on the basis of safety, tolerability, and observed pharmacokinetics properties."
- F02 [verified/medium] The sentence identifies the escalation designs and general transition triggers but does not specify their numerical thresholds or allocation rules. Dosing rules are expressed in the protocol for a titration design in whi — span: "Patients with advanced KRASG12C-mutant solid tumors were treated with DV-R01 150 mg orally once daily, 300 mg once daily, 600 mg once daily, 1,200 mg once daily"
- F03 [verified/medium] The sentence identifies the study populations but gives no expansion-cohort specifications. Sponsors of first-in-human multiple-expansion-cohort trials should provide the scientific rationale for studying each proposed c — span: "We report results from a phase I/IB study of DV-R01 in non-small-cell lung cancer, colorectal cancer, and other solid tumors harboring the KRASG12C mutation."
- F07 [verified/medium] The sentence reports responses among 15 evaluable patients at 600 mg twice daily but provides no response results for other doses. Multiple dosages should be compared in a trial designed to assess antitumor activity, saf — span: "After a median follow-up of 19.6 months, eight of 15 patients (53.3%; 95% CI, 26.6 to 78.7) with RECIST-evaluable KRASG12C-mutant non-small-cell lung cancer tre"

**RETRO-03 ceritinib**
- F01 [verified/high] The synopsis says expansion patients received the maximum tolerated dose but gives no comparison with lower doses to explain that selection. When selecting dosages for further evaluation, safety and tolerability should b — span: "In an expansion phase of the study, patients received the maximum tolerated dose."
- F02 [verified/high] The response rate combines patients receiving at least 400 mg per day rather than reporting responses by individual dose. Multiple dosages should be compared in a trial designed to assess antitumor activity, safety, and  — span: "Among 114 patients with NSCLC who received at least 400 mg of DV-R03 per day, the overall response rate was 58% (95% confidence interval [CI], 48 to 67)."
- F03 [verified/high] The sentence gives the administered dose range and schedule but no dose-specific pharmacokinetic or exposure–response results. A PK sampling and analysis plan should be included in each protocol. — span: "Methods: In this phase 1 study, we administered oral DV-R03 in doses of 50 to 750 mg once daily to patients with advanced cancers harboring genetic alterations "

**RETRO-07 futibatinib**
- F02 [verified/high] The synopsis uses a stronger daily-dosing exposure–phosphorus relationship to support 20 mg daily as the RP2D without presenting dose-specific comparative activity and tolerability results. Multiple dosages should be com — span: "Serum phosphorus increased dose dependently with DV-R07 on both schedules, but a stronger exposure-response relationship was observed with q.d. dosing, supporti"
- F03 [verified/high] The synopsis identifies 20 mg daily as the MTD and does not provide a benefit–risk comparison with lower daily doses in this sentence. Safety and tolerability should be compared across multiple dosages when selecting dos — span: "The maximum tolerated dose (MTD) was determined to be 20 mg q.d.; no MTD was defined for the t.i.w. schedule."
- F05 [verified/high] The synopsis pools partial responses and stable disease across patients without reporting response results by dose or schedule. Multiple dosages should be compared in trials designed to assess antitumor activity, safety, — span: "Overall, partial responses were observed in five patients [FGFR2 fusion-positive intrahepatic cholangiocarcinoma (n = 3) and FGFR1-mutant primary brain tumor (n"
- F06 [verified/medium] The synopsis specifies a standard 3+3 design and the tested dose ranges but provides no design operating characteristics. The trial should be sized to allow sufficient assessment of safety and antitumor activity for each — span: "Patients And Methods: Following a standard 3+3 dose-escalation design, eligible patients with advanced solid tumors refractory to standard therapies received 8-"
- F07 [verified/medium] The synopsis states dose proportionality for daily dosing and saturation for some three-times-weekly doses without giving PK sampling or analysis methods. A PK sampling and analysis plan should be included in each protoc — span: "Pharmacokinetics were dose proportional across all q.d. doses but not all t.i.w. doses evaluated, with saturation observed between 80 and 200 mg t.i.w."
- F10 [verified/low] The investigational-product summary supplies a structure and FGFR3 target designation but no clinical toxicity or dose-selection data. The structure alert is suitable only for class classification and is not validated to — span: "DV-R07 is an oral small molecule (Fibroblast growth factor receptor inhibitor). SMILES: C=CC(=O)N1CC[C@H](n2nc(C#Cc3cc(OC)cc(OC)c3)c3c(N)ncnc32)C1. Target: FGFR"

**RETRO-10 idelalisib**
- F01 [verified/high] The synopsis identifies a later-development dose as under review but does not state how that dose was selected. Multiple dosages should be compared in a trial designed to assess antitumor activity, safety, and tolerabili — span: "The dose selected for later development is the dose under review."
- F02 [verified/high] The reported sentence gives the number and range of dose levels and describes once- or twice-daily continuous treatment, but gives no PK sampling plan. A PK sampling and analysis plan should be included in each protocol. — span: "Patients were treated at 6 dose levels of oral DV-R10 (range 50-350 mg once or twice daily) and remained on continuous therapy while deriving clinical benefit."
- F04 [verified/medium] The sentence reports an overall response rate and its response categories, without reporting results by dose or schedule. Multiple dosages should be compared in a trial designed to assess antitumor activity, safety, and  — span: "The overall response rate was 72%, with 39% of patients meeting the criteria for partial response per DV-R10 and 33% meeting the recently updated criteria of PR"

**RETRO-11 inavolisib**
- F01 [verified/high] The synopsis identifies a later-development dose as under review but gives no dose-level comparisons or selection rationale in this sentence. Multiple dosages should be compared in a trial designed to assess antitumor ac — span: "The dose selected for later development is the dose under review."
- F03 [verified/high] The sentence asserts that no PK DDIs were observed without giving the sampling or analysis supporting that assertion. A PK sampling and analysis plan should be included in each protocol. — span: "No PK drug-drug interactions (DDIs) were observed among the study treatments when administered."
- F04 [verified/high] The conclusion characterizes safety as manageable but provides no cross-dose tolerability comparison in that sentence. When selecting dosages for further evaluation or as the recommended dosage, safety and tolerability s — span: "Conclusion: DV-R11 plus palbociclib and ET demonstrated a manageable safety profile, lack of DDIs, and promising preliminary antitumor activity."
- F05 [verified/medium] The two named arms differ in endocrine partner, while this sentence gives neither DV-R11 dose assignments nor prior-therapy eligibility criteria. Expansion cohorts intended to further assess the optimal dose or schedule  — span: "Methods: Women ≥18 years of age received DV-R11, palbociclib, and letrozole (Inavo + Palbo + Letro arm) or fulvestrant (Inavo + Palbo + Fulv arm) until unaccept"

**RETRO-13 lenvatinib**
- F01 [verified/medium] The synopsis identifies a dose for later development and concludes that doses up to 25 mg per day were well tolerated, but does not present a dose-specific benefit–risk comparison. Multiple dosages should be compared in  — span: "The dose selected for later development is the dose under review.

Conclusion: E7080 is well tolerated at doses up to 25 mg per day."
- F02 [verified/medium] The results give the overall enrollment, dose range, two dose-limiting toxicities at 32 mg, and a 25 mg MTD, without cohort denominators or escalation rules. Clinical data from all sources should be analyzed for dose-rel — span: "Results: Eighty-two patients received E7080 in dose cohorts from 0.2 to 32 mg. Dose-limiting toxicities were grade 3 proteinuria (two patients) at 32 mg, and th"
- F03 [verified/medium] The report describes dose-linear kinetics and no accumulation after four weeks, but gives no exposure–response or exposure–toxicity analysis. An established concentration-response relationship is often not needed, but ma — span: "E7080 has dose-linear kinetics with no drug accumulation after 4 weeks' administration."
- F05 [verified/medium] The sampling description specifies collection days but not within-day post-dose times or the PK analysis plan. A PK sampling and analysis plan should be included in each protocol. — span: "Samples for pharmacokinetic analyses were collected on days 1, 8, 15 and 22 of cycle 1 and day 1 of cycle 2."

**RETRO-23 sotorasib**
- F01 [verified/high] The synopsis identifies a later-development dose but does not give its selection rule or comparative rationale. Multiple dosages should be compared in a trial designed to assess antitumor activity, safety, and tolerabili — span: "The dose selected for later development is the dose under review."
- F02 [verified/high] The results report no observed dose-limiting toxic effects or treatment-related deaths but provide no escalation decision rules or dose-specific observation details. Expansion cohorts intended to further evaluate safety  — span: "No dose-limiting toxic effects or treatment-related deaths were observed."
- F03 [held/high] The results give aggregate enrollment by tumor type across escalation and expansion but not enrollment, exposure, activity, or toxicity by dose or the rationale and stopping rules for each expansion cohort. The backgroun — span: "A total of 129 patients (59 with NSCLC, 42 with colorectal cancer, and 28 with other tumors) were included in dose escalation and expansion cohorts."
- F05 [verified/medium] The methods name pharmacokinetics as a secondary endpoint without describing its sampling or analysis plan. A PK sampling and analysis plan should be included in each protocol. — span: "Key secondary end points were pharmacokinetics and objective response, as assessed according to Response Evaluation Criteria in Solid Tumors (RECIST), version 1"

**RETRO-33 cabozantinib**
- F01 [verified/high] The report gives an MTD of 175 mg daily but does not identify a rule for selecting the later-development dose or compare dose levels in this sentence. Multiple dosages should be compared in a trial designed to assess ant — span: "The MTD was 175 mg daily."
- F02 [verified/high] The report attributes expansion of the MTC-enriched cohort to early observations of clinical benefit but gives no cohort design details in this sentence. The background information for each expansion cohort should contai — span: "Early observations of clinical benefit in a phase I study of DV-R33, which included patients with medullary thyroid cancer (MTC), led to expansion of an MTC-enr"
- F03 [verified/high] The report identifies a dose-escalation study but gives no escalation design, cohort sizes, or DLT assessment window in this sentence. Phase 1 clinical trials are designed to determine the side effects associated with in — span: "A phase I dose-escalation study of oral DV-R33 was conducted in patients with advanced solid tumors."
- F04 [verified/high] The report names pharmacokinetics as an endpoint but provides no PK sampling or analysis plan in this sentence. A PK sampling and analysis plan should be included in each protocol and should be sufficient to characterize — span: "Primary end points included evaluation of safety, pharmacokinetics, and maximum-tolerated dose (MTD) determination."
- F07 [verified/medium] The report concludes that the safety profile is acceptable without qualifying that conclusion by dose in this sentence. Safety and tolerability should be compared across multiple dosages when selecting dosages for furthe — span: "Conclusion: DV-R33 has an acceptable safety profile and is active in MTC."

**RETRO-36 infigratinib**
- F01 [verified/high] The synopsis attributes the 125 mg daily MTD to four reported DLT cases, including grade 1 corneal toxicity, but gives neither the DLT definition and dose-level denominators nor a comparison of safety and activity across — span: "The MTD, 125 mg daily, was determined on the basis of dose-limiting toxicities in four patients (100 mg, grade 3 aminotransferase elevations [n = 1]; 125 mg, hy"
- F02 [verified/medium] The synopsis identifies the expansion populations and schedules but does not give a scientific rationale, planned sample size, stopping rules, or PK sampling plan for each arm. Sponsors of first-in-human multiple expansi — span: "During expansion at the MTD, patients with FGFR1-amplified squamous cell non-small-cell lung cancer (sqNSCLC; arm 1) or other solid tumors with FGFR genetic alt"
- F03 [verified/medium] The synopsis reports partial responses at doses of at least 100 mg without response counts or exposure results separately for each dose and schedule. Dosages selected for administration in clinical trials should be adequ — span: "Antitumor activity (seven partial responses [six confirmed]) was demonstrated with DV-R36 doses ≥ 100 mg in patients with FGFR1-amplified sqNSCLC and FGFR3-muta"
- F05 [verified/medium] The synopsis compares schedule-specific dose-adjustment or interruption percentages without giving arm denominators, treatment duration, allocation method, or adverse-event-specific modification rules. When selecting dos — span: "However, adverse event-related dose adjustments/interruptions were less frequent with the 3-weeks-on/1-week-off (50.0%) versus the continuous (73.7%) schedule."

**RETRO-38 panobinostat**
- F02 [verified/high] The synopsis names 40 mg as the weekly phase II recommended dose without a formal MTD but provides no comparative results explaining its selection. When selecting dosages for further evaluation or as the recommended dosa — span: "In patients with lymphoma and myeloma, 40 mg was the recommended dose for phase II evaluation (formal MTD not determined) of weekly DV-R38, and 60 mg was the MT"

**RETRO-39 ponatinib**
- F02 [verified/high] The report gives a once-daily dose range but no dose-level PK sampling or analysis plan. A PK sampling and analysis plan should be included in each protocol. — span: "DV-R39 was administered once daily at doses ranging from 2 to 60 mg."
- F03 [verified/high] The synopsis refers to a later-development dose without identifying it or explaining its selection. Multiple dosages should be compared in a trial(s) designed to assess antitumor activity, safety, and tolerability to sup — span: "The dose selected for later development is the dose under review."
- F04 [verified/medium] The report identifies dose escalation and total enrollment but does not say whether expansion cohorts existed or describe cohort-specific objectives. Sponsors of FIH multiple expansion cohort trials should provide the sc — span: "Methods: In this phase 1 dose-escalation study, we enrolled 81 patients with resistant hematologic cancers, including 60 with CML and 5 with Ph-positive ALL."
- F06 [verified/medium] The report gives response percentages for mutation-defined groups without reporting their dose-specific denominators or exposures. Multiple dosages should be compared in a trial(s) designed to assess antitumor activity,  — span: "Of 12 patients who had chronic-phase CML with the T315I mutation, 100% had a complete hematologic response and 92% had a major cytogenetic response. Of 13 patie"
- F07 [verified/medium] The background describes BCR-ABL inhibition but gives no broader target-profile data or dose-specific benefit–risk analysis. When selecting dosages for further evaluation or as the recommended dosage, safety and tolerabi — span: "DV-R39 (DV-R39) is a potent oral tyrosine kinase inhibitor that blocks native and mutated BCR-ABL, including the gatekeeper mutant T315I, which is uniformly res"

**RETRO-40 quizartinib**
- F04 [verified/high] The synopsis reports complete inhibition in an in vitro plasma inhibitory assay without identifying the tested dose or presenting dose-specific results. Multiple dosages should be compared in a trial designed to assess a — span: "FLT3-ITD phosphorylation was completely inhibited in an in vitro plasma inhibitory assay."
- F05 [verified/high] The synopsis reports a 200 mg/day maximum-tolerated dose and grade 3 QT prolongation as the dose-limiting toxicity, without a comparison of candidate doses in this sentence. Safety and tolerability should be compared acr — span: "The maximum-tolerated dose was 200 mg/day, and the dose-limiting toxicity was grade 3 QT prolongation."

**RETRO-41 ribociclib**
- F01 [verified/medium] The synopsis reports a 900 mg/day MTD and a 600 mg/day RDE but gives no comparative dose-level rationale in this sentence. Safety and tolerability should be compared across multiple dosages when selecting dosages for fur — span: "The MTD and RDE were established as 900 and 600 mg/day 3-weeks-on/1-week-off, respectively."
- F02 [verified/medium] The synopsis reports an exposure trend and mean half-life but no dose-level exposure–toxicity or exposure–activity analysis in this sentence. A PK sampling and analysis plan should be included in each protocol. — span: "Plasma exposure increases were slightly higher than dose proportional; mean half-life at the RDE was 32.6 hours."

**RETRO-42 selinexor**
- F01 [verified/high] The synopsis gives a qualitative tolerability and activity rationale for 35 mg/m2 but no dose-level results supporting the comparison. Multiple dosages should be compared in a trial designed to assess antitumor activity, — span: "The recommended phase II dose of 35 mg/m2 given twice a week was chosen based on better patient tolerability and no demonstrable improvement in radiologic respo"
- F02 [verified/high] The synopsis reports dose proportionality and no accumulation without providing dose-level exposure distributions or exposure–response results. Pharmacokinetic information can be used to choose doses that ensure adequate — span: "Pharmacokinetics were dose proportional, with no evidence of drug accumulation."
- F03 [verified/high] The synopsis identifies the MTD and schedule but does not give the DLT definition, observation window, escalation rules, or dose-level safety results. Safety and tolerability should be compared across the multiple dosage — span: "The maximum-tolerated dose was defined at 65 mg/m2 using a twice-a-week (days 1 and 3) dosing schedule."
- F04 [held/medium] The synopsis reports a leukocyte biomarker plateau at 28 mg/m2 and tumor-biopsy findings without giving dose-specific biomarker variability or a comparison with 35 mg/m2. It is all too common to discover, at the end of a — span: "Dose-dependent elevations in XPO1 mRNA in leukocytes were demonstrated up to a dose level of 28 mg/m2 before plateauing, and paired tumor biopsies showed nuclea"
- F08 [verified/low] The synopsis provides a SMILES string and names XPO1 as the target but gives no potency or structure-based evidence linked to dose selection. Multiple dosages should be compared in a trial designed to assess antitumor ac — span: "SMILES: O=C(/C=C\n1cnc(-c2cc(C(F)(F)F)cc(C(F)(F)F)c2)n1)NNc1cnccn1. Target: XPO1."

