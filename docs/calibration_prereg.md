# 특이도 보정 A/B — 사전 등록 (2026-09-30, 실행 전 커밋)

## 배경
특이도 평가 B(`docs/specificity_prereg.md`)에서, 결함을 넣지 않은 기준 시놉시스에서도 실행당 defect finding이 6.42건 나왔다(문장 특이도 0.64). 원인은 findings 지시문의 커버리지 요구 "Cover every review question whose hypothesis the protocol_text confirms"로 본다. 이 결과는 이미 보고됐고, 이 A/B는 그 결과를 본 뒤 설계했다.

## 변경(한 변수)
`DV_FINDINGS_CALIBRATED=1`이면 findings 지시문에서 커버리지 문장을 빼고 다음 규칙을 더한다(`app/agents/findings.py::_CALIBRATION_RULE`).
- 인용 근거의 구체 요건을 그 문장이 어길 때만 보고한다.
- 이미 다룬 내용은 보고하지 않는다.
- 근거가 요구하지 않는 세부를 일반적으로 더 원하는 지적은 하지 않는다.
- finding이 적거나 0건이어도 된다.

## 팔
| 팔 | 음성(결함 없는 기준 시놉시스 4종 × 3회) | 양성(원 20케이스) |
|---|---|---|
| 현재 | `clean_base`(기존 12회) | `lean_v3` + `lean_v3b`(기존 2회) |
| 보정 | `clean_base_cal`(새 12회) | `lean_cal`(새 1회, `run_eval --configs lean --suffix _cal`) |

## 판정(사전 고정, `app/eval/specificity.py::calibration`)
- **채택**은 세 조건을 모두 만족할 때다.
  - 음성 문장 특이도가 0.10 이상 오른다.
  - 양성 문장 민감도 하락이 0.05 이하다(현재 = 2회 평균).
  - grounded recall 쌍대 차이의 점추정 하락이 0.05 이하다.
- 그 외는 **기각**하고 현재 설정을 유지한다. 결과는 어느 쪽이든 공개한다.
- 보정 팔은 양성 1회뿐이다. 같은 설정의 실행 간 변동(grounded 약 0.067, 6.3절)보다 작은 차이는 점추정으로만 해석한다.

## 채택 시 후속
기본값을 켜고 데모 캐시 ①~⑤를 다시 만든다. 적대 테스트 ⑥~⑧도 채택된 설정으로 실행한다. 기존 평가 수치는 모두 "보정 전 코드" 결과로 표기를 바꾼다.
