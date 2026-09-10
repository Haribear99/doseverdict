# grounded recall 실패 원인 — no_arena

span 적중 결함 115건 중 grounded 48건 / 규제 근거 인용 없음 0건 / 비규제 근거만 3건 / **다른 규제 문서 인용 64건**.

출처 절(hold-out)은 검색에서 제외되므로 정답 문서 인용은 같은 문서의 다른 절을 찾은 경우다.

| 정답 문서 | 놓친 수 |
|---|---|
| FDA-DOSE-OPT-2024 | 25 |
| ICH-E4-1994 | 21 |
| FDA-EXPANSION-COHORTS-2022 | 11 |
| MFDS-1443-01-2025 | 10 |

| 정답 문서 → 대신 인용한 문서 | 건수 |
|---|---|
| FDA-DOSE-OPT-2024 → MFDS-1443-01-2025 | 10 |
| ICH-E4-1994 → FDA-DOSE-OPT-2024 | 10 |
| FDA-EXPANSION-COHORTS-2022 → ICH-E6R3-2025 | 9 |
| ICH-E4-1994 → MFDS-1443-01-2025 | 7 |
| FDA-DOSE-OPT-2024 → FDA-EXPANSION-COHORTS-2022 | 6 |
| MFDS-1443-01-2025 → FDA-DOSE-OPT-2024 | 6 |
| FDA-DOSE-OPT-2024 → ICH-E6R3-2025 | 5 |
| MFDS-1443-01-2025 → ICH-E6R3-2025 | 4 |
| FDA-EXPANSION-COHORTS-2022 → MFDS-1443-01-2025 | 2 |
| ICH-E4-1994 → FDA-EXPANSION-COHORTS-2022 | 2 |
| ICH-E4-1994 → ICH-E6R3-2025 | 2 |
| FDA-DOSE-OPT-2024 → ICH-E4-1994 | 2 |
| MFDS-1443-01-2025 → FDA-EXPANSION-COHORTS-2022 | 1 |

## Verifier 판정별 주입 결함 적중률 (F00·V 제외)

| 판정 | finding 수 | 결함 적중 | 적중률 |
|---|---|---|---|
| held | 25 | 12 | 0.48 |
| verified | 166 | 107 | 0.64 |
