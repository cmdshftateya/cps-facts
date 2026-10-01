# CPS School ID -> ISBE RCDTS crosswalk: review notes

File: `crosswalk.csv`. It has one row for each of the 639 schools in the SY2026-27 20th-day roster. It is matched against the ISBE 2025 Report Card (`isbe25_General.csv`). The Chicago rows are RCDTS `15-016-2990-*` with `Level=School`, 621 rows in all. RCDTS values are stored with the hyphens removed and the trailing `C` kept, so `15-016-2990-25-232C` becomes `15016299025232C`.

## Method

1. **legacy_portal (518).** These come from the union of Chicago Data Portal `c7jj-qjvh` (`isbe_id`, used as is with the trailing letter kept) and `cp7s-7gxg` (the 15-digit ID inside `state_school_report_card_url`). Only IDs that appear in the ISBE 2025 Chicago rows are kept, and the two sources never conflict. As a spot check, the CPS and ISBE names were compared by shared words. Only one mapping had no word in common: 400104 INSTITUTO - HEALTH maps to "IHSCA Charter High School", which is correct because IHSCA is the abbreviation.
2. **manual_name / manual_name_address (95).** The 121 schools left over were matched by hand to ISBE Chicago rows that no other school had claimed. The checks used were the name (ISBE abbreviations such as `Noble St Chtr-`, `Univ of Chicago Chtr-`, `Acero Chtr Sch Network -`), the grade span, the school type, and the CPS address where several campuses share a name or a building. Each `notes` cell gives the ISBE name that was matched. Every network had exactly as many unclaimed ISBE rows as unmatched CPS campuses: CICS 13, Noble 17, YCCS 17, LEARN 7, KIPP 4, Perspectives 4, UChicago 3, NLCP 2.
3. **no_isbe_record (26).** No ISBE row exists for these schools. They are ALOP, SAFE, Excel contract options schools, early-childhood centers, district specialty and alternative high schools, and Catalyst Maria HS.

The script checks that no RCDTS is assigned to two CPS schools.

## Counts

| method | high | medium | low | total |
|---|---|---|---|---|
| legacy_portal | 518 | 0 | 0 | 518 |
| manual_name | 84 | 6 | 0 | 90 |
| manual_name_address | 4 | 1 | 0 | 5 |
| no_isbe_record | 25 | 1 | 0 | 26 |
| **total** | 631 | 8 | 0 | 639 |

613 of the 639 schools (95.9%) have an RCDTS.

## Rows needing a human look (medium; no rows are low)

None of these is in doubt about which school it is. They are flagged because the ISBE data may not describe the school as it runs today.

- **610602 FUENTES, 610603 SANTIAGO, 610604 DE LAS CASAS, 610605 CISNEROS, 610606 TAMAYO.** These five Acero charter campuses became CPS district-run in SY2026-27. Their old charter IDs were 400082, 400114, 400081, 400101 and 400084. They are mapped to their Acero RCDTS (`...261C`, `267C`, `262C`, `266C`, `260C`), so the ISBE 2025 results describe the school while it was still a charter. ISBE may give them new district RCDTS codes in the future.
- **610607 CHICAGO ARTS HS.** This is ChiArts, which was contract school 400022 through SY2025-26. It is mapped to ISBE "Chicago HS for the Arts" (`150162990250851`), so the ISBE data describes the contract years.
- **400066 PERSPECTIVES - MATH & SCI HS.** It is mapped to ISBE "Perspectives Chtr - IIT Campus" (`...053C`, grades 6-12). The match rests on the 3663 S Wabash address, which is the IIT-area campus historically called Perspectives/IIT Math & Science Academy. It was also the only Perspectives row left after the other three campuses matched by name.
- **400182 CATALYST MARIA HS (no_isbe_record).** ISBE reports Catalyst Maria as a single K-12 school (`...232C`), and the legacy crosswalk maps that row to 400115 CATALYST - MARIA. ISBE figures shown for 400115 therefore include this high school's students, while the high school itself has no ISBE row. Decide whether to show 400115's ISBE values with a caveat or to suppress them.

Related legacy mapping worth a note: **400086 URBAN PREP HS** maps by legacy ID to Urban Prep Englewood (`...010C`). By SY2026-27 it is a single combined Urban Prep high school, so the 2025 Englewood row covers only part of it.

## ISBE 2025 Chicago rows left unclaimed (8)

All of these are campuses that closed or merged and are no longer in the SY2026-27 roster. That is expected, because ISBE 2025 covers SY2024-25.

| RCDTS | ISBE name | reason |
|---|---|---|
| 15016299025259C | Acero - Octavio Paz Elem | ACERO - PAZ (400083) is in the SY2024-25 roster and gone from SY2025-26 on: closed |
| 15016299025049C | Acero - Sor Juana Ines de la Cruz K-12 | ACERO - DE LA CRUZ (400121) is in SY2024-25 and gone from SY2025-26 on: closed. It is not the same school as district SOR JUANA 610589, which has its own district RCDTS `...2971` |
| 15016299025079C | Aspira Charter - Business and Finance HS | 400172 is in the roster through SY2025-26 and absent in SY2026-27: closed |
| 15016299025074C | ASPIRA Charter - Early College Prep HS | 400013 is in the roster through SY2025-26 and absent in SY2026-27: closed |
| 15016299025110C | ASPIRA Charter - Haugan Campus | 400017 is in SY2024-25 and gone from SY2025-26 on: closed |
| 15016299025015C | EPIC Academy High School | 400094 is in the roster through SY2025-26 and absent in SY2026-27: closed |
| 150162990252951 | Plato Learning Acad Elem School | PLATO (contract, 400068) is in SY2024-25 and gone from SY2025-26 on: closed |
| 15016299025013C | Urban Prep Chtr Acad Bronzeville HS | 400105 is in the roster through SY2025-26. By SY2026-27 Urban Prep is a single school, 400086, which keeps the Englewood RCDTS |

## Caveats

- **Specialty and alternative high schools.** No ISBE row was found under any name variant for the eight district schools Northside Learning, Southside Occupational, Vaughn, Graham Training, York, Simpson, Jefferson and Peace & Education. The search covered the whole ISBE General sheet, not just the 2990 rows. These are marked no_isbe_record with high confidence, on the basis that they are absent from the 2025 Report Card file. They could still be reported somewhere else, such as at district level.
- **No web lookups.** Every match was resolved from the local data: names, grades, addresses, and the CPS rosters from SY2023-24 to SY2026-27. Nothing was checked against illinoisreportcard.com.
- **Rebuilding.** The rebuild script is `cw3.py` in the session scratchpad. It holds the manual mapping table, and the same table is reflected in the `notes` column of `crosswalk.csv`.
