# How CPS Facts works

Every value on the map shows its school year and source. This page explains the choices behind the numbers and where they have limits. "SY2024-25" means the 2024–25 school year.

## Which years you see
- Enrollment and demographics are SY2026-27: CPS's 20th-day count (September 21, 2026) for 639 schools.
- Test scores, attendance, graduation and per-pupil spending are SY2024-25, from the 2025 Illinois Report Card. The state publishes outcomes about a year late; the 2026 report is expected in late October 2026. A school's profile can therefore mix years, and each number is labeled.
- Enrollment is a September snapshot. CPS and state profile pages use other snapshots, so totals can differ slightly.

## Missing and hidden values
- **Suppressed** means the state hid the value for a small group. **No data** means the source has none (for example, a graduation rate for an elementary school). Neither is zero.
- CPS publishes small-school numbers as they are, so percentages can swing on a few students. Schools under 30 students are labeled "n<30".

## Not every school does the same job
- About 50 schools serve a different group of students than a neighborhood school. They are special-education schools (admission is through a student's IEP), transition programs for students about 18 to 22, schools inside detention facilities, a school for parenting students, short-term placements, dropout-recovery high schools and preschool-only centers. Each shows a short note on its page saying what it does. We list them, with a public source for each, in "What each school does" on the Data and sources page.
- Their enrollment, spending per student, attendance and graduation are not comparable with other schools. A dropout-recovery school's four-year graduation rate, for example, counts students who arrived already behind. By default the color groups, city medians and ranges leave these schools out. They stay on the map (dimmed), in the table and in downloads. Choose "All schools" under Comparison set in Settings to count them.
- Some schools admit students by entrance exam, application or lottery, so their results partly reflect who is admitted. About 140 neighborhood schools host special-education cluster programs, so their IEP share, budget per pupil and test averages reflect that program as well as the neighborhood. These schools are labeled but still counted in comparisons, because they are real peers of nearby schools. A building can hold both a selective and a neighborhood program; the data cannot separate them.
- The "What the school does" filter shows one group at a time. The list of special schools is built by hand from public pages and has not been confirmed by CPS.

## Test scores
- In 2025 Illinois lowered proficiency cut scores for every grade, and grade 11 switched from the SAT to the ACT. We never show trends or changes across that break, because most of the apparent "improvement" would be policy.
- "Vs. college-ready" is an estimate that does hold across the break: a school's average score minus the ACT's national college-readiness benchmark (20 in English, 22 in math). SAT averages are converted to the ACT scale with an official table designed for individual students, so school results are approximate. See the [full method](https://github.com/cmdshftateya/cps-facts/blob/main/hs-score-benchmark-method.md).

## Spending
- **Per-pupil spending** is the state's figure for fiscal year 2025. It includes costs the district pays centrally, so it is the fairer comparison, especially for charters.
- **Per-pupil budget** is CPS's proposed FY27 budget for the school divided by its enrollment. It leaves out some central costs. We add up the line items from CPS's interactive budget reports; their total matches the published $10.11B budget. You can retrieve the same data from "Interactive Reports 2027" on the [CPS FY27 budget page](https://www.cps.edu/about/finance/budget/budget-2027/).
- Charter, contract, ALOP and SAFE schools are funded differently, so their budgets are not comparable with district-run schools. Very high or low figures usually belong to small or specialized programs; we flag them rather than hide them.

## Matching schools
- CPS and the state use different school IDs, so we built a lookup table, downloadable on the [Data and sources](data.html) page. 613 of 639 schools match. The other 26 (program schools, early-childhood centers, some alternative high schools) show CPS data only.
- Five Acero schools and ChiArts became district-run in July 2026. We link each to its former charter to keep its history, and their state figures describe that charter. They use the old charter's location on the map ([sources for each conversion](https://github.com/cmdshftateya/cps-facts/blob/main/charter-conversions.md)).
- The state reports Catalyst Maria as one K-12 school, so its state figures appear on the main school (400115) and not the high school. Its CPS budget covers both campuses, so per-pupil uses their combined 1,105 students.
- Urban Prep Englewood is now one combined school, and the 2025 state figures cover only part of it. EPIC and the two ASPIRA high schools closed and are not on the map.
- School board subdistricts come from the Illinois Senate's map of the 20 subdistricts, with each school placed by its coordinates. We checked it against the Board of Elections' official map.

## Still being confirmed
- CPS changed how it labels low-income students and students with disabilities between SY2025-26 and SY2026-27 (the district share fell from 71.8% to 68.9%). We don't know whether the definition changed, so we show no demographic changes across that point.
- We have asked CPS and the state to confirm a few details, including the Catalyst Maria budget, the fiscal year of the state's per-pupil figure and the ACT "ELA" column. We have no replies yet and will update this page with their answers. The 2026 Illinois Report Card is expected in late October 2026; the site will be updated then.

Where every number comes from, with links and field names: [Data and sources](data.html).
