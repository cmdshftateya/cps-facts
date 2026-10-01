# High school test outcome: SAT to ACT break (proposal)

**Problem.** REQUIREMENTS.md line 35 promises "SAT proficiency" for high schools. The 2025 ISBE Report Card has no SAT data. Grade 11 now takes the ACT, and the site's 3-year trend (2023, 2024, 2025) spans the switch.

## 1. Facts

- **The test changed in spring 2025 (SY2024-25).** Illinois used the SAT for grade 11 from spring 2017 through spring 2024. ISBE's College Board contract ended 6/30/2024. A routine state procurement then awarded ACT a six-year contract (2024-25 to 2029-30). From spring 2025, grade 11 takes the ACT (ELA, math, science; the ACT replaces the separate grade-11 ISA), grade 10 takes PreACT Secure and grade 9 takes PreACT 9 Secure. Source: ISBE *ACT FAQ* (6/7/2024), isbe.net/Documents/ACT-FAQ.pdf.
- **2025 has a second break: new cut scores.** ISBE adopted new, lower proficiency cut scores (board action 8/13/2025) for the IAR, ISA and ACT, and applied them to spring 2025 data. It published **no** prior-year data re-scored to the new cuts. The IASB tells boards not to read 2025 proficiency gains as improvement and to use growth instead (Chalkbeat 10/30/2025; IASB Journal Jan/Feb 2026). *This also breaks grades 3-8 IAR trends, so the methodology note must cover elementary schools too.*
- **No overlap year.** The 2024 file has no ACT columns and the 2025 file has no SAT columns. No year has both tests.
- **The jump is policy, not learning.** CPS ELA proficiency was 22.4% in 2024 (SAT) and 40.1% in 2025 (ACT). Math went from 18.6% to 25.3%. Statewide ELA went from 31.1% to 51.7%, and math from 26.1% to 39.3%. The median CPS high school's ELA rate went from 6.2% to 19.2%.
- **Glossary caveat.** The 2025 glossary describes the ACT with four HS levels (L3 and L4 count as proficient). Some of its entries still say "levels 3 and 4 on SAT", which is stale text.

### What each file contains (Chicago = RCDTS `15-016-2990…`, school rows)

The HS universe is 150 RCDTS: schools with a grade-11 test value in any of the three years.

| Year (file / sheet) | Grade-11 columns | Chicago schools with a numeric value |
|---|---|---|
| 2023 `23-RC-Pub-Data-Set.xlsx` / `SAT` (`Type` column, no `Level`) | `SAT Reading/Math Average Score`; `SAT Reading/Math Total Students Level 1-4 %`. **No proficiency-rate column**: derive it as L3 % + L4 %. | 148 |
| 2024 `isbe2024.xlsx` / `SAT` | `SAT ELA Proficiency Rate - Total`, `SAT Math Proficiency Rate - Total` (equal to L3+L4 within 0.1); average scores; levels | 149 (614 rows are non-blank, but 465 are `*` at K-8 schools) |
| 2025 `isbe25_ACT.csv` | `ACT ELA/Math/Science Proficiency Rate Grade 11 - Total`, `ACT ELA/Math/Science Average Score - Grade 11`, `ACT … Participation Rate Grade 11 - Total` | 148 |
| 2025, same sheet | `HS Assessment ELA/Math/Science Proficiency Rate - Total` | 149 rows match the ACT value exactly. The other 20 are `*` at K-8 schools. **So 2025 "HS Assessment" = ACT grade 11 only** (PreACT is not pooled in). |
| 2025, same sheet | `ACT ELA/Math Growth Percentile Grade 11- Total` (144); `HS Assessment ELA/Math Growth Percentile - Total` (146; matches ACT-11 at only 3 of 148 schools, so it is pooled across grades 9-11); `PreACT Secure … Grade 10 - Total` (144); `PreACT 9 Secure … Grade 9 - Total` (128) | as listed |

**Relative standing survives the break.** Across the 146 schools with all three years, the Spearman rank correlation for ELA proficiency is 0.85 between SAT 2024 and ACT 2025. Between SAT 2023 and SAT 2024 it is 0.83. Math is similar: 0.88 for ACT math 2025 vs SAT math 2024, and 0.81 for SAT math 2024 vs SAT ELA 2024. So ranking schools *within a year* is defensible. Comparing *levels* across years is not.

### Non-test HS metrics: same definition all three years (General sheet; numeric count of the 150 for 2023 / 2024 / 2025)

`High School 4-Year Graduation Rate - Total` 148/149/147 · `High School 5-Year Graduation Rate - Total` 148/148/148 · `Student Attendance Rate` 150/150/149 · `Chronic Absenteeism` 150/150/149 · `% 9th Grade on Track` 129/125/128 (missing ~20 YCCS/alternative charters, Urban Prep and DeVry) · `% Graduates enrolled in a Postsecondary Institution within 12 months` 141/149/117 (2025 is thin) · `High School Dropout Rate - Total` 105/110/104.

## 2. Options

- **A. Raw proficiency, broken trend.** Show SAT 2023-24 and ACT 2025 rates, with the sparkline split at the break. *Honest and simple. However, the large step up in 2025 still invites misreading, and a 2025 color ramp in raw % cannot be compared with older years.*
- **B. Percentile within CPS high schools, per year.** Rank each school among CPS high schools on that year's test and plot that rank as a continuous line. *The line is comparable, backed by rho ≈ 0.85. However, it hides absolute levels, and one-year rank moves are noisy.*
- **C. Drop the test as the headline and lead with continuous metrics.** *Fully comparable. However, it breaks the REQUIREMENTS promise, and parents expect a test score.*

## 3. Recommendation: A for display and B for comparison, with the test de-emphasized in trends

1. **Rename the metric** to "Grade 11 state test (SAT through 2024, ACT from 2025)". Update REQUIREMENTS.md line 35 to match.
2. **School panel test cell.** Headline: 2025 `ACT ELA Proficiency Rate Grade 11 - Total` and `ACT Math Proficiency Rate Grade 11 - Total`, next to the CPS-HS median for the same year. Subline: "Ranks Nth of 148 CPS high schools". Use the `ACT …` columns, not `HS Assessment …`: the values are identical, but the ACT names keep working if ISBE later pools grades. Add `ACT ELA/Math Participation Rate Grade 11 - Total` as a footnote when participation is below 90%.
3. **Sparkline.** Draw 2023 and 2024 (SAT) as one connected segment and 2025 (ACT) as an unconnected dot with a different marker. Add a vertical break tick labelled "test & cut scores changed". **Never connect across 2024 to 2025.** Show **no delta badge** on the 2025 test value. Once 2026 lands, 2025 to 2026 is a clean ACT-to-ACT segment.
4. **Rankings, sorting and map color-by.** Use one year at a time only, preferably the CPS-HS percentile of the current year. Do not offer "change since 2023/2024" on any proficiency metric, including IAR for elementary schools, which also got new cuts. Use one set of color-ramp breaks per year; never share breaks across years.
5. **Trend-capable HS metrics** (sparklines and deltas allowed): 4-year graduation rate, freshman on-track, attendance rate, chronic absenteeism, and postsecondary enrollment within 12 months (flag that 2025 coverage is thin, at 117 schools). These should carry the "3-year trend" story for high schools.
6. **Growth.** Show `ACT ELA/Math Growth Percentile Grade 11- Total` as a 2025-only value (50 = typical growth statewide; CPS is 49.8). No trend, because no prior ACT-to-ACT growth exists. Before treating it as a headline metric, confirm with ISBE how the 2025 SGP was computed across the PSAT10-to-ACT change. PreACT 9/10 proficiency is 2025-only and secondary; put it behind a "more" toggle.
7. **Methodology page must say:**
   - Illinois switched grade-11 testing from SAT (2017–2024) to ACT (spring 2025) after a state procurement.
   - In the same year ISBE lowered proficiency cut scores for all state tests and did not re-score earlier years.
   - 2025 proficiency is therefore not comparable to 2024 or earlier. Citywide ELA rose from 22% to 40% largely for these reasons.
   - The site never connects, subtracts or ranks across that break. Within-year comparisons and ranks are valid. Graduation, on-track, attendance, absenteeism and postsecondary enrollment are unaffected.
   - Proficiency = levels 3+4 for SAT and ACT. 2023 is derived as Level 3 % + Level 4 %.
   - `*` = suppressed, fewer than 10 students.
   - Cite the ISBE ACT FAQ and the 2025 Report Card glossary.

**Tradeoffs.** Users get no single 3-year test line, which is the cost of honesty. Within-year percentiles depend on which schools are in the CPS-HS set, so the denominator must be stated. Small alternative schools (YCCS) often lack on-track and growth values, so show "n/a", never 0.

*Reproduce with the 2023, 2024 and 2025 Report Card public data sets. Chicago school rows are those with an RCDTS starting `150162990` and `Type`/`Level` = School. The 2023 file was downloaded from the ISBE link given in the task.*
