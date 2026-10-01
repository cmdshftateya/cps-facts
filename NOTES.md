# Notes and Caveats

How CPS Facts picks years, matches schools across sources, and where the numbers have limits. Last updated 2026-09-30. These are the detailed working notes; the reader-facing page is `METHODOLOGY.md`. Technical detail lives in `sources.md`.

## 1. What we chose, and why

| Choice | What we did | Why |
|---|---|---|
| **Which year is "current"** | The map shows the SY2026-27 roster (639 schools, CPS 20th-day count of 2026-09-21). | It is the newest roster CPS publishes. The city's school-location file is a year behind (SY2025-26). |
| **Different metrics have different years** | Enrollment and demographics are SY2026-27. Test scores, attendance, graduation and per-pupil spending are SY2024-25, from the 2025 Illinois Report Card. Every number shows its own year. | The state publishes outcomes about a year late. The 2026 Report Card is not out yet; expect late October 2026. |
| **Matching CPS schools to state records** | CPS and the state use different school IDs, so we built a lookup table (`crosswalk.csv`): 613 of 639 schools matched, 26 have no state record. 518 matched through old city datasets that carry both IDs; 95 were matched by hand from names and addresses. No state record is matched to two schools. | There is no official CPS-to-ISBE ID list. |
| **Spending** | The default spending figure is the state's per-pupil expenditure, which includes costs the district pays centrally (such as central office and special services). CPS's own school budget is shown beside it. | School budgets omit central costs, so they understate what a school really costs. The state figure is the fairer comparison, especially for charters. |
| **CPS budget numbers** | The public Excel files have no dollar totals for district-run schools, but CPS's interactive budget reports let anyone export a line-item file (unit × fund × account). We downloaded it by hand and add up each school's lines: FY27 proposed budget, FY26 projected spending, positions, and a breakdown by funding source (`budget_units.csv`, `budget_unit_funds.csv`). 637 of 639 schools are matched, using the district's own finance ID. | These are CPS's official numbers, not our estimates. The export can't be fetched automatically, so we refresh it by hand once a year. |
| **High-school test scores** | Illinois switched its grade 11 test from the SAT (through 2024) to the ACT (from 2025) and also lowered proficiency cut scores in 2025. The site never connects, ranks, or computes change across that break. A settings toggle offers an estimate on one scale: each school's average score compared with the national college-readiness benchmark (`hs-score-benchmark-method.md`). | Comparing 2024 and 2025 proficiency would show a large "improvement" that is mostly policy. |
| **Elementary test scores** | Same cut-score change in 2025, so no trend lines or changes between 2024 and 2025. | Same reason. |
| **School board subdistricts** | We use the Illinois Senate's shapefile of the 20 enacted subdistricts (1a–10b) and place each school by its coordinates. We checked it against the Board of Elections' official map. | The Board of Elections publishes only PDF pictures of the map, not data. |
| **Charter schools that became district schools** | Five Acero schools and ChiArts became district-managed in the same buildings in July 2026. We link each to its former charter so history is kept (`charter-conversions.md`). | Otherwise those schools would show no history. |
| **CPS's interactive budget dashboard** | You can retrieve this data yourself: open "Interactive Reports 2027" on the [CPS FY27 budget page](https://www.cps.edu/about/finance/budget/budget-2027/) and export the line-item report. We download that export by hand and don't automate it. | The dashboard opens through a shared guest login built into that link, which we chose not to script, so it can't feed an automated build. |
| **Catalyst Maria** | The state reports Catalyst Maria as one K-12 school. We attach the state's figures to the main school (400115) and show the high school (400182) as "no separate state data", with its CPS enrollment and demographics. | Attaching the same numbers to both would duplicate them, and for the high school they would mostly describe younger students. |

## 2. Caveats users should know

**Years and comparability**
1. Test scores and spending are about a year older than enrollment. A school's profile can mix SY2026-27 and SY2024-25 values; each carries a year label.
2. 2025 state test results are not comparable to earlier years (new test for grade 11, lower cut scores for every grade).
3. CPS changed how it labels low-income students and students with disabilities between SY2025-26 and SY2026-27. District-wide the share fell from 71.8% to 68.9%. We have not confirmed whether the definition or only the label changed, so we show no demographic changes across that point.
4. The state's per-pupil spending is FY2025 (July 2024 to June 2025), the same year as SY2024-25. Its enrollment denominator matches CPS's SY2024-25 count exactly (0.0% median difference, 604 schools). ISBE has not confirmed this in writing (see `emails.md`).

**Missing or suppressed values**
5. The state hides values for small groups and marks them `*`. We show "suppressed", never 0. A blank means the state has no data (for example, a graduation rate for an elementary school).
6. CPS's own enrollment and demographic files don't hide small numbers; they show 0. In very small schools, percentages can swing on a handful of students, so we label schools under 30 students instead of hiding anything.
7. CPS's files do not include students in temporary living situations. That figure comes from the state (SY2024-25) only.

**Matching and roster**
8. 26 schools have no state record (program schools, early-childhood centers, some alternative high schools). They show CPS data only.
9. Seven crosswalk matches are "medium confidence". Most are the former Acero and ChiArts schools: their state figures describe the charter that closed, not today's district-run school. They are labeled that way.
10. The Urban Prep campus in Englewood is now one combined school. The 2025 state figures cover only part of it.
11. Urban Prep: the board renewed both campuses for two years, through 2026-27 (WTTW, 2025-05-29); the "closing" story we found is from November 2022. CPS's 20th-day file now lists one combined Urban Prep HS (400086). Virtual Academy is open (grades K-12, medically fragile students) but CPS counts its students at their brick-and-mortar schools, so it has no 20th-day row of its own; its $16.4M budget unit (U26931) is not in any school total.
12. EPIC and the two ASPIRA high schools closed with no successor and are not on the SY2026-27 map.
13. Enrollment is the 20th-day (September) count. The state and CPS profile pages use other snapshots, so totals will differ slightly.
14. The Illinois Report Card is revised after release (eight updates between October 2025 and May 2026). We record the data version we used.

**Budget vs. spending**
15. A school's budget and what is spent per pupil are different things; the site shows both and labels them. The CPS figure is a *proposed* FY27 budget (FY26 projected spending is as of July 2026). A school's budget excludes some centrally paid costs; the state per-pupil figure includes them.
15a. The export's total ($10.11B) matches CPS's published FY27 budget ($10.11B). It is $5.38B in school units and $4.77B in district-wide lines (pensions, debt, capital, facilities, transportation, central offices), less $571M of negative lines. The dashboard's $8.72B was a partial view we could not rebuild; it does not affect school totals, which join by unit ID.
15b. Some budgets look extreme per pupil (18 schools under $5,000, 7 over $60,000, for example the SAFE schools at about $60,000). These are small or specialized programs; the map flags them and does not trim them.
16. Charter, contract, ALOP and SAFE schools are funded by tuition and grants, not the district-school formula. Their CPS budget numbers are not comparable to district-run schools.

**The estimated high-school score comparison**
17. It converts SAT averages to the ACT scale with an official table designed for individual scores, so applied to school averages it is approximate. The national benchmarks come from a self-selected group of test takers, while Illinois tests every junior. It is labeled "estimate".
18. The state's ACT "ELA" column is the ACT ELA score (English, reading and writing; Illinois grade 11 takes the ACT with Writing), so the national benchmark is 20. ISBE has not confirmed this in writing.

**Other details**
19. A school's CPS budget of $0 is shown as no data, not 0 (six YCCS campuses and Chicago Arts HS).
20. Catalyst Maria's budget unit covers both campuses ($22.1M). Per pupil is computed on their combined 1,105 students (about $20k) and shown on both schools, labeled. This is our inference from the numbers; confirm with CPS.
21. State "*" on SAT/ACT/graduation at schools with no high-school grades is shown as no data, not "suppressed".
22. 5Essentials "Ambitious Instruction" is blank for every Chicago school in 2025 and is not shown; a level of 0 means not rated.
23. The six converted schools have no coordinates in any city dataset; they use the old charter's location, flagged.
24. CPS demographic shares are published as CPS gives them, never hidden. Schools under 30 students get a small-school label.

## 3. Still being confirmed
- Confirm with CPS whether the low-income / disability change was a definition change (caveat 3).
- Questions to CPS and ISBE (Catalyst Maria budget unit, low-income and IEP labels, per-pupil year, ACT ELA) were sent. We are waiting for replies and will record any answers in the caveats above.
- Re-run the audit when the 2026 Illinois Report Card is released.
