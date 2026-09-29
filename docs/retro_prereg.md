# 실사례 후향 검증 — 사전 등록 (2026-09-29, 실행 전 커밋)

## 질문
FDA가 최초 승인 때 **용량최적화 PMR/PMC**(일반 대상 인구에서 다른 용량의 노출·안전성·유효성 비교)를 부과한 항암제를, DoseVerdict가 **승인 전 공개 정보만으로** 더 자주 짚는가.

## 표본
- 정답: `app/eval/data/pmr_ground_truth.jsonl`(승인서한 원문으로 판정, 09-11 수집) + `pmr_ground_truth_ext.jsonl`(09-29 추가, 서한 원문 인용이 있는 것만). 비항암(tofacitinib·remibrutinib)과 판정 불명(gefitinib)은 제외한다.
- 입력: 약물별 최초 1상(FIH) 결과 논문 초록. PubMed 출판일이 FDA 승인일보다 앞선 것만 쓴다. 초록 400자 미만이면 제외한다. 약물명·브랜드명·스폰서 코드명은 `DV-Rxx`로 가린다(`app/eval/retro_build.py`).
- 표본 크기는 자료 확보 결과로 정해지며, 결과를 보고 케이스를 넣거나 빼지 않는다. 제외 사유는 빌더 로그 그대로 공개한다.

## 누설 차단
| 경로 | 조치 |
|---|---|
| CT.gov 등록정보 현재 버전(승인 후 추가된 용량 비교 팔 포함 사례 확인: NCT03600883) | 입력으로 쓰지 않음. 에이전트의 유사 시험 검색은 `DV_ASOF_DATE` 이전 시작 시험만(`AREA[StartDate]RANGE`) |
| openFDA 라벨(승인 후 문서) | `DV_BLIND_LABEL=1` — 조회하지 않고 '라벨 없음'과 같게 처리 |
| Open Targets 승인약 목록(현재 시점 상태) | as-of 모드에서 쓰지 않음 |
| 규제 코퍼스 | 약물명 0건 확인(15개 약물명 grep). 다만 2022~2025 가이던스는 오래된 승인 시점보다 뒤의 규범이다 — 누설이 아니라 **시대 차이**로 보고 아래 B2로 점검 |
| LLM 사전 지식(마스킹된 초록에서 약을 알아볼 가능성) | 재식별 탐침(아래 P1)으로 측정 |
| ChEMBL 활성값 | 승인 후 등재값이 섞일 수 있음 — 한계로 공개 |

## 실행 설정
현재 배포 기본(lean: Reviewer 규제 1인, gpt-6-sol, strict, 인용문 250자), 케이스당 1회. 상태는 `app/eval/data/results/states/retro/`.

## 점수(사전 고정)
- **S1(1차)**: `category = dose_optimization`, `verdict = defect`, `verifier_status = verified`인 finding 수.
- **S2(2차)**: `dose_optimization` defect finding의 중증도 가중합(critical 4·high 3·medium 2·low 1), 검증 상태 무관(verified + held).

## 비교 기준(사전 고정)
- **B1 키워드 규칙**(입력 초록에 대해, LLM 없음): 아래 패턴 중 걸린 개수.
  `MTD (was |were )?(not|never) (reached|identified|established|determined)` · `maximum tolerated dose (was |were )?(not|never)` · `no dose[- ]limiting toxicit` · `no DLTs?` · `(highest|maximum) (dose|dose level) (tested|evaluated|studied|administered)`
- **B2 승인연도**: 늦을수록 높은 점수(Project Optimus 이후 양성 집중이라는 시대 교란 점검).
- **B3 축③ 라벨 규칙**(`app/eval/axis3.py`, 승인 후 라벨 사용 — 참고용, 누설 있음).

## 지표와 판정
- AUROC(동률 0.5), 부트스트랩 95% CI(층화 재표본 5,000회, seed 0), PR-AUC(무작위 기준 = 양성 비율).
- **판정**: S1 AUROC의 CI 하한 > 0.5면 "신호 있음", 아니면 "신호 확인 안 됨(null)"으로 그대로 보고한다.
- S1 − B1, S1 − B2 AUROC 차이의 쌍대 부트스트랩 CI는 기술(記述)용으로 보고한다(표본이 작아 유의성 주장에 쓰지 않음).
- 양성 사례별로 적중 여부와 finding 원문(주장·인용 규범)을 표로 공개한다.

## 재식별 탐침(P1)
같은 마스킹 입력을 gpt-6-sol에 주고 "이 약의 성분명은?"만 묻는다(도구 없음). 정답률을 보고하고, 맞힌 케이스를 뺀 부분집합의 S1 AUROC를 2차로 보고한다.

## 사후 분석
이 문서에 없는 분석은 모두 "사후"로 표기한다.
