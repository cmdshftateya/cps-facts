# Grade 11 "computed" comparison — method (draft)

Companion to `hs-assessment-proposal.md`. Purpose: let users compare high schools across the 2024→2025 SAT→ACT break on one scale, as a **settings toggle** ("Grade 11 test measure"). Retrieved 2026-09-30.

## Toggle
| Option | What it shows | Across the break? |
|---|---|---|
| **State proficiency %** (default) | ISBE-published % proficient. SAT 2023–24, ACT 2025. | **No.** Separate segments; no deltas or cross-year ranks. |
| **Score vs national benchmark (estimate)** | School mean score, put on the ACT scale, minus the ACT College Readiness Benchmark, in points. | Yes, labelled as an estimate. |

## Why not recompute "% proficient"
ISBE publishes only school-level aggregates: mean scores and the share at each performance level. There are no student-level scores, so a different cut score can't be applied to the distribution. What can be done honestly is compare the **mean** to a fixed national benchmark.

## Inputs (all verified present for Chicago schools)
| Year | Columns | Chicago schools with a value | Observed range |
|---|---|---|---|
| 2023 | `SAT Reading Average Score`, `SAT Math Average Score` | 149 / 149 | Reading 360–665 (median 415), Math 340–667 (median 397) |
| 2024 | same | 150 / 150 | Reading 315–668 (median 405), Math 319–659 (median 392) |
| 2025 | `ACT ELA / Math / Science Average Score - Grade 11` | 149 (1 `*`) | ELA 8.2–27.8 (median 14.1), Math 12.1–29.6 (median 14.6), Science 13.1–28.7 |

The SAT ranges fit the 200–800 section scales, so "Reading" is taken to be EBRW. **Unconfirmed**: ISBE's column name says "Reading"; check the glossary.

## Benchmarks (national, published, stable)
- **ACT:** English 18, Math 22, Reading 22, Science 23, **ELA 20**. Source: ACT, College Readiness Benchmarks.
- **SAT:** EBRW 480, Math 530. Source: College Board.
- **Open question:** ISBE's ACT column is "ELA". If it is ACT's ELA composite, use 20. If it is the English subscore, use 18. Decide before implementation by reading ISBE's glossary or asking ISBE. Show the choice on the methodology page.

## Putting SAT years on the ACT scale
Use the **official 2018 ACT–SAT concordance tables** (ACT / College Board): EBRW→ACT English/ELA and SAT Math→ACT Math. Convert each school's SAT mean, then subtract the ACT benchmark. 2025 values need no conversion.

Rules:
1. Convert the mean score, never student scores (we don't have them).
2. Show the result rounded to whole points and mark the SAT-derived years "est.".
3. Do not show the number if the underlying mean is `*`.
4. Concordance gives scores of equal rank among students testing together; it is not an equating. Applying it to school means is approximate and gets less reliable at the extremes.

## What the number can and can't claim
- **Can:** "This school's average junior scored about N points below/above the national college-readiness benchmark," comparable across 2023–2025 within the estimate's error.
- **Can't:** a % of students ready. Illinois tests every junior; national benchmarks come from self-selected test takers, so Chicago looks lower than a like-for-like comparison would.
- **Also in 2025:** ISBE lowered proficiency cut scores. Benchmark gaps don't depend on ISBE cut scores, which is the point of the toggle.

## Sanity check before shipping
Rank-correlate the converted 2024 value with the 2025 value across the ~148 schools present in both. The proposal measured 0.85 on proficiency %; the converted-mean metric should be at least as high. If not, drop the toggle.

## Methodology-page text (draft)
"Illinois changed its grade 11 test from the SAT (through 2024) to the ACT (from 2025) and also lowered proficiency cut scores in 2025. State proficiency rates are therefore not comparable before and after. The alternative view converts each school's mean score to the ACT scale using the official ACT–SAT concordance and compares it with ACT's national College Readiness Benchmark. It is an estimate, not an official measure."

## Sources
- ACT College Readiness Benchmarks: https://www.act.org/content/act/en/college-and-career-readiness/benchmarks.html
- ACT–SAT concordance (2018): https://act.org/content/act/en/products-and-services/the-act/scores/act-sat-concordance.html
- ISBE 2023/2024/2025 Report Card public data sets: https://www.isbe.net/Pages/Illinois-State-Report-Card-Data.aspx
