# Validation report

Generated 2026-10-02T20:52:22Z · roster 2026-27 · **639 schools** · **PASS**

By type: charter 100, contract 16, district 519, options 4 · by grade band: ES 472, HS 144, combo 23
With coordinates 639 · subdistrict 639 · ISBE record 613 · FY27 budget 630

## Checks

| Status | Check | Count | Detail |
|---|---|---|---|
| warn | Coordinates carried over from a predecessor charter (same-site inference) (`coords_predecessor`) | 6 | CPS pages describe the conversions as same-building; not verified per site. |
| warn | CPS community area differs from the area containing the coordinates (`community_area_mismatch`) | 6 / 639 |  |
| warn | Schools with no ISBE record (CPS data only) (`isbe_unmatched`) | 26 / 639 |  |
| warn | Medium-confidence crosswalk matches (shipped with a caveat flag) (`medium_confidence`) | 7 |  |
| warn | Schools with no usable FY27 budget (`budget_missing`) | 9 |  |
| warn | Students in the retired 'Asian/Pacific Islander' category (SY2024-25, not carried) (`retired_race_category`) | 1 |  |
| warn | CPS 20th-day vs ISBE enrollment (SY2024-25) differ by >25% and 30+ students (`enrollment_vs_isbe`) | 1 | Median difference 0.6% across 613 schools; the files use different snapshots. |
| warn | CPS budget per pupil outside the outlier band (flagged, not trimmed) (`budget_pp_outlier`) | 18 |  |
| warn | ISBE per-pupil expenditure outside 3xIQR fences (flagged, not trimmed) (`ppe_outlier`) | 1 |  |
| warn | Schools under the low-n threshold in 2026-27 (`low_n`) | 4 |  |
| warn | ISBE '*' values dropped to no-data on metrics a school cannot have (`star_dropped`) | 2 |  |
| pass | Duplicate school IDs (`dup_ids`) |  |  |
| pass | One RCDTS assigned to more than one school (`dup_rcdts`) |  |  |
| pass | Schools missing name, type or governance (`missing_fields`) |  |  |
| pass | Program overrides or program sentences incomplete (unknown school or program, no source URL, no sentence) (`program_context`) |  |  |
| pass | City Data Portal school classifications this build does not recognize (no admission label shown) (`program_unknown_class`) |  |  |
| pass | Roster enrollment sum differs from the CPS file's district total (`roster_total`) |  | Roster sum 304,687. |
| pass | Schools without coordinates (`missing_coords`) |  |  |
| pass | Schools not in exactly one Board subdistrict (`missing_subdistrict`) |  |  |
| pass | Schools not in exactly one ward (`missing_ward`) |  |  |
| pass | Coordinates outside Chicago's bounding box (`coords_outside_chicago`) |  |  |
| pass | ISBE join below 95% (`isbe_join`) |  | 613 of 639 schools (95.9%) have an RCDTS. |
| pass | Crosswalk RCDTS not found in the 2025 Report Card (`rcdts_not_in_isbe`) |  |  |
| pass | Roster schools absent from crosswalk.csv (`crosswalk_coverage`) |  |  |
| pass | Low-confidence crosswalk match ships ISBE values (`low_confidence_ships_isbe`) |  |  |
| pass | CPS budget join below 99% (`budget_join`) |  | 637 of 639 schools have a budget unit; 630 have a nonzero FY27 budget. |
| pass | By-fund budget does not add up to the school total (`budget_fund_sum`) |  |  |
| pass | Predecessor ID not found in any earlier CPS file (`predecessor_missing`) |  |  |
| pass | CPS membership / demographics totals disagree (`cps_totals_agree`) |  |  |
| pass | Grade-level enrollment does not add up to the total (`cps_grade_sum`) |  |  |
| pass | Race shares do not add to 100% (schools with 30+ students) (`race_sum`) |  |  |
| pass | Metrics missing from the registry (`unknown_metric`) |  |  |
| pass | Values in a school year the registry does not list (`year_not_in_registry`) |  |  |
| pass | Non-numeric, non-'*' values (`non_numeric_value`) |  |  |
| pass | Percentages / percentiles / levels outside their valid range (`percent_range`) |  |  |
| pass | Zero or negative dollar/score values (should be no data) (`zero_dollars`) |  |  |
| pass | Grade 11 ela estimate: SAT-2024 vs ACT-2025 rank correlation below 0.85 (`g11_ela_rank_corr`) |  | Spearman rho 0.909 across 142 schools. |
| pass | Grade 11 math estimate: SAT-2024 vs ACT-2025 rank correlation below 0.85 (`g11_math_rank_corr`) |  | Spearman rho 0.913 across 142 schools. |

## Examples (first 12 per non-passing check)

**Coordinates carried over from a predecessor charter (same-site inference)** (`coords_predecessor`, 6)
- 610602
- 610603
- 610604
- 610605
- 610606
- 610607

**CPS community area differs from the area containing the coordinates** (`community_area_mismatch`, 6)
- ('400145', 'ARCHER HEIGHTS', 'LOWER WEST SIDE')
- ('400150', 'OAKLAND', 'CHATHAM')
- ('400161', 'ROSELAND', 'WEST PULLMAN')
- ('610572', 'SOUTH CHICAGO', 'SOUTH SHORE')
- ('610573', 'SOUTH CHICAGO', 'SOUTH SHORE')
- ('610599', 'JEFFERSON PARK', 'PORTAGE PARK')

**Schools with no ISBE record (CPS data only)** (`isbe_unmatched`, 26)
- 400147 CHICAGO EXCEL HS
- 400173 PATHWAYS - BRIGHTON PARK HS
- 400175 EXCEL SOUTH SHORE HS
- 400176 EXCEL SOUTHWEST HS
- 400182 CATALYST MARIA HS
- 609744 NORTHSIDE LEARNING HS
- 609745 SOUTHSIDE HS
- 609748 YORK HS
- 609750 SIMPSON HS
- 609766 VAUGHN HS
- 609769 GRAHAM HS
- 609783 JEFFERSON HS

**Medium-confidence crosswalk matches (shipped with a caveat flag)** (`medium_confidence`, 7)
- 400066 PERSPECTIVES - MATH & SCI HS
- 610602 FUENTES
- 610603 SANTIAGO
- 610604 DE LAS CASAS
- 610605 CISNEROS
- 610606 TAMAYO
- 610607 CHICAGO ARTS HS

**Schools with no usable FY27 budget** (`budget_missing`, 9)
- 400126 YCCS - ASSOCIATION HOUSE
- 400129 YCCS - PROGRESSIVE LEADERSHIP
- 400131 YCCS - CAMPOS
- 400136 YCCS - OLIVE HARVEY
- 400141 YCCS - TRUMAN
- 400144 YCCS - WEST
- 400182 CATALYST MARIA HS
- 610572 SAFE ACHIEVE ES
- 610607 CHICAGO ARTS HS

**Students in the retired 'Asian/Pacific Islander' category (SY2024-25, not carried)** (`retired_race_category`, 1)
- 609720

**CPS 20th-day vs ISBE enrollment (SY2024-25) differ by >25% and 30+ students** (`enrollment_vs_isbe`, 1)
- 400115 CATALYST - MARIA: CPS 539 vs ISBE 1092

**CPS budget per pupil outside the outlier band (flagged, not trimmed)** (`budget_pp_outlier`, 18)
- 400123 YCCS - SCHOLASTIC ACHIEVEMENT: $213
- 400124 YCCS - MCKINLEY: $475
- 400125 YCCS - ASPIRA PANTOJA: $909
- 400128 YCCS - CCA ACADEMY: $453
- 400130 YCCS - YOUTH DEVELOPMENT: $423
- 400133 YCCS - INNOVATIONS: $301
- 400135 YCCS - LATINO YOUTH: $244
- 400139 YCCS - SULLIVAN: $313
- 400143 YCCS - WEST TOWN: $524
- 400145 YCCS - YOUTH CONNECTION: $701
- 400150 YCCS - CHATHAM: $2,893
- 609748 YORK HS: $111,485

**ISBE per-pupil expenditure outside 3xIQR fences (flagged, not trimmed)** (`ppe_outlier`, 1)
- 610245 DOUGLASS HS: $54,695

**Schools under the low-n threshold in 2026-27** (`low_n`, 4)
- 610245 DOUGLASS HS (29)
- 610572 SAFE ACHIEVE ES (6)
- 610573 SAFE ACHIEVE HS (27)
- 610601 SAFE ACHIEVE WEST HS (26)

**ISBE '*' values dropped to no-data on metrics a school cannot have** (`star_dropped`, 2)
- 2083 high-school-only values at schools with no grade 9-12
- 488 IAR values at schools with no grade 3-8

## Coverage by metric (schools with a value / suppressed / no data)

| Metric | Year | Value | Suppressed | No data |
|---|---|---|---|---|
| enrollment | 2024-25 | 639 | 0 | 0 |
| enrollment | 2025-26 | 639 | 0 | 0 |
| enrollment | 2026-27 | 639 | 0 | 0 |
| pct_white | 2024-25 | 639 | 0 | 0 |
| pct_white | 2025-26 | 639 | 0 | 0 |
| pct_white | 2026-27 | 639 | 0 | 0 |
| pct_black | 2024-25 | 639 | 0 | 0 |
| pct_black | 2025-26 | 639 | 0 | 0 |
| pct_black | 2026-27 | 639 | 0 | 0 |
| pct_latinx | 2024-25 | 639 | 0 | 0 |
| pct_latinx | 2025-26 | 639 | 0 | 0 |
| pct_latinx | 2026-27 | 639 | 0 | 0 |
| pct_asian | 2024-25 | 639 | 0 | 0 |
| pct_asian | 2025-26 | 639 | 0 | 0 |
| pct_asian | 2026-27 | 639 | 0 | 0 |
| pct_multiracial | 2024-25 | 639 | 0 | 0 |
| pct_multiracial | 2025-26 | 639 | 0 | 0 |
| pct_multiracial | 2026-27 | 639 | 0 | 0 |
| pct_native | 2024-25 | 639 | 0 | 0 |
| pct_native | 2025-26 | 639 | 0 | 0 |
| pct_native | 2026-27 | 639 | 0 | 0 |
| pct_pacific | 2024-25 | 639 | 0 | 0 |
| pct_pacific | 2025-26 | 639 | 0 | 0 |
| pct_pacific | 2026-27 | 639 | 0 | 0 |
| pct_mena | 2024-25 | 639 | 0 | 0 |
| pct_mena | 2025-26 | 639 | 0 | 0 |
| pct_mena | 2026-27 | 639 | 0 | 0 |
| pct_race_na | 2024-25 | 639 | 0 | 0 |
| pct_race_na | 2025-26 | 639 | 0 | 0 |
| pct_race_na | 2026-27 | 639 | 0 | 0 |
| pct_el | 2024-25 | 639 | 0 | 0 |
| pct_el | 2025-26 | 639 | 0 | 0 |
| pct_el | 2026-27 | 639 | 0 | 0 |
| pct_iep | 2024-25 | 639 | 0 | 0 |
| pct_iep | 2025-26 | 639 | 0 | 0 |
| pct_iep | 2026-27 | 639 | 0 | 0 |
| pct_low_income | 2024-25 | 639 | 0 | 0 |
| pct_low_income | 2025-26 | 639 | 0 | 0 |
| pct_low_income | 2026-27 | 639 | 0 | 0 |
| pct_homeless | 2024-25 | 383 | 230 | 26 |
| pct_youth_in_care | 2024-25 | 19 | 594 | 26 |
| ppe_total | 2024-25 | 611 | 0 | 28 |
| ppe_site | 2024-25 | 611 | 0 | 28 |
| ppe_central | 2024-25 | 611 | 0 | 28 |
| cps_budget_fy27 | 2026-27 | 630 | 0 | 9 |
| cps_budget_fy26_projected | 2025-26 | 630 | 0 | 9 |
| cps_budget_fy26_adopted | 2025-26 | 625 | 0 | 14 |
| cps_budget_per_pupil | 2026-27 | 631 | 0 | 8 |
| cps_positions_fy27 | 2026-27 | 630 | 0 | 9 |
| attendance_rate | 2022-23 | 607 | 0 | 32 |
| attendance_rate | 2023-24 | 607 | 0 | 32 |
| attendance_rate | 2024-25 | 607 | 6 | 26 |
| chronic_absent | 2022-23 | 606 | 0 | 33 |
| chronic_absent | 2023-24 | 604 | 3 | 32 |
| chronic_absent | 2024-25 | 606 | 1 | 32 |
| grad_4yr | 2022-23 | 142 | 0 | 497 |
| grad_4yr | 2023-24 | 143 | 1 | 495 |
| grad_4yr | 2024-25 | 142 | 2 | 495 |
| ninth_on_track | 2022-23 | 124 | 0 | 515 |
| ninth_on_track | 2023-24 | 121 | 5 | 513 |
| ninth_on_track | 2024-25 | 123 | 3 | 513 |
| postsec_12mo | 2022-23 | 137 | 0 | 502 |
| postsec_12mo | 2023-24 | 143 | 0 | 496 |
| postsec_12mo | 2024-25 | 114 | 27 | 498 |
| isbe_enrollment | 2022-23 | 607 | 0 | 32 |
| isbe_enrollment | 2023-24 | 613 | 0 | 26 |
| isbe_enrollment | 2024-25 | 613 | 0 | 26 |
| iar_ela_prof | 2023-24 | 483 | 0 | 156 |
| iar_ela_prof | 2024-25 | 483 | 1 | 155 |
| iar_math_prof | 2023-24 | 483 | 0 | 156 |
| iar_math_prof | 2024-25 | 483 | 1 | 155 |
| ela_growth | 2023-24 | 482 | 1 | 156 |
| ela_growth | 2024-25 | 482 | 1 | 156 |
| math_growth | 2023-24 | 482 | 1 | 156 |
| math_growth | 2024-25 | 482 | 1 | 156 |
| sat_ela_prof | 2022-23 | 142 | 0 | 497 |
| sat_ela_prof | 2023-24 | 143 | 1 | 495 |
| sat_math_prof | 2022-23 | 142 | 0 | 497 |
| sat_math_prof | 2023-24 | 143 | 1 | 495 |
| sat_ela_avg | 2022-23 | 142 | 0 | 497 |
| sat_ela_avg | 2023-24 | 143 | 1 | 495 |
| sat_math_avg | 2022-23 | 142 | 0 | 497 |
| sat_math_avg | 2023-24 | 143 | 1 | 495 |
| sat_ela_part | 2022-23 | 142 | 0 | 497 |
| sat_ela_part | 2023-24 | 143 | 1 | 495 |
| sat_math_part | 2022-23 | 142 | 0 | 497 |
| sat_math_part | 2023-24 | 143 | 1 | 495 |
| act_ela_prof | 2024-25 | 143 | 1 | 495 |
| act_math_prof | 2024-25 | 143 | 1 | 495 |
| act_ela_avg | 2024-25 | 143 | 1 | 495 |
| act_math_avg | 2024-25 | 143 | 1 | 495 |
| act_ela_part | 2024-25 | 143 | 1 | 495 |
| act_math_part | 2024-25 | 143 | 1 | 495 |
| act_ela_growth | 2024-25 | 139 | 5 | 495 |
| act_math_growth | 2024-25 | 139 | 5 | 495 |
| fe_leaders | 2024-25 | 582 | 0 | 57 |
| fe_teachers | 2024-25 | 581 | 0 | 58 |
| fe_families | 2024-25 | 572 | 0 | 67 |
| fe_environment | 2024-25 | 138 | 0 | 501 |
| g11_ela_gap | 2022-23 | 142 | 0 | 497 |
| g11_ela_gap | 2023-24 | 143 | 1 | 495 |
| g11_ela_gap | 2024-25 | 143 | 1 | 495 |
| g11_math_gap | 2022-23 | 142 | 0 | 497 |
| g11_math_gap | 2023-24 | 143 | 1 | 495 |
| g11_math_gap | 2024-25 | 143 | 1 | 495 |

## Rules applied
- `demo_low_n_flag`: 30
- `budget_per_pupil_outlier`: [5000, 60000]
- `ppe_outlier_fence_3xIQR`: [238, 42512]
- `isbe_star_on_inapplicable_metric`: dropped to no-data (HS metrics at schools with no grade 9-12, IAR at schools with no grade 3-8)

## Source files
- CONCORD `act_sat_concordance.pdf` retrieved 2026-10-01
- CPS-MEM `cps_mem_2425.xlsx` retrieved 2026-09-30
- CPS-MEM `cps_mem_2526.xlsx` retrieved 2026-09-30
- CPS-MEM `cps_mem_2627.xlsx` retrieved 2026-09-30
- CPS-DEM1 `cps_lepiep_2425.xlsx` retrieved 2026-09-30
- CPS-DEM1 `cps_lepiep_2526.xlsx` retrieved 2026-09-30
- CPS-DEM1 `cps_lepiep_2627.xlsx` retrieved 2026-09-30
- CPS-DEM2 `cps_race_2425.xlsx` retrieved 2026-09-30
- CPS-DEM2 `cps_race_2526.xlsx` retrieved 2026-09-30
- CPS-DEM2 `cps_race_2627.xlsx` retrieved 2026-09-30
- CPS-BUD-BI `fy27_bi_budget_book.csv` retrieved 2026-09-30
- CHI-LOC `chi_loc.json` retrieved 2026-09-30
- CHI-PROF `chi_prof.json` retrieved 2026-09-30
- CHI-CA `chi_community_areas.geojson` retrieved 2026-09-30
- CHI-WARD `chi_wards.geojson` retrieved 2026-09-30
- SUBDIST `subdistricts.zip` retrieved 2026-09-30
- ISBE-RC `isbe_rc_2023.xlsx` retrieved 2026-09-30
- ISBE-RC `isbe_rc_2024.xlsx` retrieved 2026-09-30
- ISBE-RC `isbe_rc_2025.xlsx` retrieved 2026-09-30
- XWALK `crosswalk.csv` retrieved 2026-09-30
- ISBE Report Card 2022-23: revision 8, 2024-05-15
- ISBE Report Card 2023-24: revision 7, 2025-05-30
- ISBE Report Card 2024-25: revision 8, 2026-05-14
