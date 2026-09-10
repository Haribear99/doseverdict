# grounded recall 실패 원인 — no_calc

span 적중 결함 105건 중 grounded 51건 / 규제 근거 인용 없음 0건 / 비규제 근거만 0건 / **다른 규제 문서 인용 54건**.

출처 절(hold-out)은 검색에서 제외되므로 정답 문서 인용은 같은 문서의 다른 절을 찾은 경우다.

| 정답 문서 | 놓친 수 |
|---|---|
| ICH-E4-1994 | 20 |
| FDA-DOSE-OPT-2024 | 17 |
| MFDS-1443-01-2025 | 9 |
| FDA-EXPANSION-COHORTS-2022 | 8 |

| 정답 문서 → 대신 인용한 문서 | 건수 |
|---|---|
| ICH-E4-1994 → FDA-DOSE-OPT-2024 | 13 |
| FDA-DOSE-OPT-2024 → ICH-E6R3-2025 | 10 |
| FDA-EXPANSION-COHORTS-2022 → ICH-E6R3-2025 | 7 |
| FDA-DOSE-OPT-2024 → FDA-EXPANSION-COHORTS-2022 | 5 |
| FDA-DOSE-OPT-2024 → MFDS-1443-01-2025 | 4 |
| MFDS-1443-01-2025 → FDA-EXPANSION-COHORTS-2022 | 3 |
| MFDS-1443-01-2025 → FDA-DOSE-OPT-2024 | 3 |
| MFDS-1443-01-2025 → ICH-E6R3-2025 | 3 |
| ICH-E4-1994 → ICH-E6R3-2025 | 3 |
| ICH-E4-1994 → MFDS-1443-01-2025 | 2 |
| ICH-E4-1994 → FDA-EXPANSION-COHORTS-2022 | 2 |
| FDA-EXPANSION-COHORTS-2022 → MFDS-1443-01-2025 | 1 |

## Verifier 판정별 주입 결함 적중률 (F00·V 제외)

| 판정 | finding 수 | 결함 적중 | 적중률 |
|---|---|---|---|
| held | 38 | 16 | 0.42 |
| verified | 154 | 90 | 0.58 |
