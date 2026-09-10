# grounded recall 실패 원인 — full

span 적중 결함 111건 중 grounded 44건 / 규제 근거 인용 없음 0건 / 비규제 근거만 0건 / **다른 규제 문서 인용 67건**.

출처 절(hold-out)은 검색에서 제외되므로 정답 문서 인용은 같은 문서의 다른 절을 찾은 경우다.

| 정답 문서 | 놓친 수 |
|---|---|
| FDA-DOSE-OPT-2024 | 21 |
| ICH-E4-1994 | 21 |
| FDA-EXPANSION-COHORTS-2022 | 14 |
| MFDS-1443-01-2025 | 11 |

| 정답 문서 → 대신 인용한 문서 | 건수 |
|---|---|
| ICH-E4-1994 → FDA-DOSE-OPT-2024 | 15 |
| FDA-EXPANSION-COHORTS-2022 → ICH-E6R3-2025 | 10 |
| FDA-DOSE-OPT-2024 → ICH-E6R3-2025 | 8 |
| FDA-DOSE-OPT-2024 → FDA-EXPANSION-COHORTS-2022 | 6 |
| FDA-DOSE-OPT-2024 → MFDS-1443-01-2025 | 5 |
| MFDS-1443-01-2025 → FDA-EXPANSION-COHORTS-2022 | 4 |
| MFDS-1443-01-2025 → ICH-E6R3-2025 | 4 |
| FDA-EXPANSION-COHORTS-2022 → MFDS-1443-01-2025 | 3 |
| FDA-DOSE-OPT-2024 → ICH-E4-1994 | 3 |
| MFDS-1443-01-2025 → FDA-DOSE-OPT-2024 | 3 |
| ICH-E4-1994 → ICH-E6R3-2025 | 3 |
| ICH-E4-1994 → FDA-EXPANSION-COHORTS-2022 | 2 |
| FDA-EXPANSION-COHORTS-2022 → FDA-DOSE-OPT-2024 | 1 |
| ICH-E4-1994 → MFDS-1443-01-2025 | 1 |
