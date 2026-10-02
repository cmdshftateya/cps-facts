# CPS Facts — Source Audit (Phase 0)

Retrieved **2026-09-30**. Every file below was downloaded and opened; counts are measured, not taken from page descriptions. Items I could not verify are marked **UNVERIFIED**.

## 0. Summary — what changes in REQUIREMENTS.md

| # | Finding | Impact |
|---|---|---|
| 1 | **Newest roster/enrollment is SY2026-27, not SY2025-26.** CPS posted 20th-day files dated 2026-09-21 (639 schools, 304,687 students). The portal's *School Locations* stops at SY2526 and *School Profile* at **SY2425**. | "Current year" must be defined per metric (see §2). The map backbone should be the SY2627 roster. |
| 2 | **No CPS-ID ↔ RCDTS crosswalk is published.** Neither the Profile nor Locations dataset carries RCDTS. A deterministic crosswalk exists only through two legacy portal datasets: **81.1%** of the SY2627 roster (518/639). | Phase 1 needs a hand-reviewed `crosswalk.csv`. ~120 schools, mostly charters, need name/address matching plus manual review. |
| 3 | **The public CPS budget Excel files have no dollar totals for district-run schools, but the CPS interactive-report "Download Data" export does.** It is a line-item file (419,800 rows; unit × fund × account × program) with FY26 adopted/projected and FY27 proposed dollars and positions. Units are `U` + the profile's `finance_id`, so schools join by ID: 627 directly, 10 more by name, 637/639 total. | Budget totals, per pupil and by funding source are available after all. The export is a manual, signed-in download: refresh by hand. See §3.3. |
| 4 | **SAT is gone.** The 2025 Report Card has zero SAT columns; the state high-school test is the **ACT** (grade 11). | Replace "SAT proficiency" with "ACT / HS-assessment proficiency". |
| 5 | **Definition breaks across years.** SY2526 file says "Economically Disadvantaged" (71.8% district); SY2627 says "Low Income" (68.9%). "Students with Disabilities" became "Students with IEPs". | Year-over-year demographic deltas need a methodology caveat. |
| 6 | **Roster churn is real, and now sourced.** Per `charter-conversions.md`: the five Acero schools (CPS board vote 2025-02-27) and ChiArts (vote 2025-11-05) became district-managed in the same buildings, effective July 2026. The old→new ID pairing is by name only, since no source publishes IDs. EPIC and both ASPIRA high schools closed with no successor. Urban Prep Bronzeville and Virtual Academy (HS/ES) are **unconfirmed**. | Needs an ID-lineage table so 3-year deltas follow conversions but not closures. Closed schools drop out of the SY2627 map. |
| 7 | **Subdistrict boundaries: resolved.** The Senate file `ERSB_20_Sub_District_Map_FA1_SB_15.zip` has the a/b labels (`District 1a`…`10b`) and matches the Board of Elections' official citywide map (PA 103-0584, adopted 2024-03-18) in a side-by-side check. All 645 schools fall in exactly one polygon. The earlier `ESRB_20_…11-3-23` file has the same polygons but D1–D20 numbering; do not use it. | See §3.6. |

## 1. Source inventory

| ID | Source | Latest year | Grain | Access | Verified |
|---|---|---|---|---|---|
| **CPS-MEM** | CPS 20th-day membership ("Schools by Grade") | **SY2026-27** (2026-09-21) | school × grade | static xlsx | ✅ |
| **CPS-DEM1** | CPS 20th-day LEP/IEP/Low-income | SY2026-27 | school | static xlsx | ✅ |
| **CPS-DEM2** | CPS 20th-day racial/ethnic | SY2026-27 | school | static xlsx | ✅ |
| **CPS-BUD-DM** | FY27 School Budget Overview – District Managed | FY2027 | school (name only) | static xlsx | ✅ |
| **CPS-BUD-CC** | FY27 Budget Overview – Charter/Contract/ALOP | FY2027 | school (name only) | static xlsx | ✅ |
| **CPS-BUD-BI** | CPS FY27 interactive-report line-item export | FY2027 (proposed) + FY26 projected | unit × fund × account | manual export (sign-in) | ✅ |
| **CHI-LOC** | Chicago Data Portal `pb6d-zzuh` School Locations | SY2526 | school | Socrata JSON | ✅ |
| **CHI-PROF** | Chicago Data Portal `3dhs-m3w4` School Profile | SY2425 | school | Socrata JSON | ✅ |
| **ISBE-RC** | ISBE 2025 Report Card Public Data Set | 2025 (SY2024-25) | school | static xlsx (40 MB) | ✅ |
| **SUBDIST** | ILSenate redistricting `ERSB_20_Sub_District_Map_FA1_SB_15` | enacted map (2024) | polygon | static zip | ✅ visual match to official PDF |
| **CHI-GEO** | Portal community areas `igwz-8jzy`, wards `p293-wvbd` | current | polygon | Socrata | ✔ IDs only; not downloaded |

### URLs

```
CPS-MEM   https://www.cps.edu/globalassets/cps-pages/about-cps/district-data/demographics/2026-27-demographics-20th-day-membership-report.xlsx
CPS-DEM1  …/demographics/2026-27-demographics-lep-iep-low-income-20th-day-report.xlsx
CPS-DEM2  …/demographics/2026-27-demographics-racial-ethnic-20th-day-report.xlsx
          (earlier years: demographics_20thday_sy2026_forweb.xlsx, …_sy2025_final.xlsx, …_sy2024_finalv2.xlsx;
           lepiepfrm_ and racialethnic_ variants follow the same pattern; index page:
           https://www.cps.edu/about/district-data/demographics/ )
CPS-BUD-DM https://www.cps.edu/globalassets/cps-pages/about-cps/finance/budget/budget-2027/docs/fy2027_budget_overview_district_managed_schools.xlsx
CPS-BUD-CC …/budget-2027/docs/fy2027-budget-overview-charter-contract-alop-schools.xlsx
          FY26: …/budget-2026/docs/fy2026-budget-overview-district-managed.xlsx
                …/budget-2026/docs/fy2026_budget_overview_charter_contract_alop_schools_.xlsx
CHI-LOC   https://data.cityofchicago.org/resource/pb6d-zzuh.json
CHI-PROF  https://data.cityofchicago.org/resource/3dhs-m3w4.json
ISBE-RC   https://www.isbe.net/_layouts/Download.aspx?SourceUrl=/Documents/2025-Report-Card-Public-Data-Set.xlsx
          (2024: …/Documents/24-RC-Pub-Data-Set.xlsx, 55 MB; index page: https://www.isbe.net/Pages/Illinois-State-Report-Card-Data.aspx)
SUBDIST   https://www.ilsenateredistricting.com/images/shape-files/ERSB_20_Sub_District_Map_FA1_SB_15.zip
          official PDF (for the methodology page): https://cboeprod.blob.core.usgovcloudapi.net/prod/2025-05/Citywide%20CPS%20Board%20Districts.pdf
```

**Fetching notes for `build.py`:** `cps.edu` needs a browser-like `User-Agent`. `chicagoelections.gov` returns 403 to scripted requests. The 2022-23 and older CPS demographic links are on the index page, and the newest files use a different naming scheme each year, so scrape the index page rather than hardcoding URLs.

## 2. Years — what we can actually show

| Fact family | Latest available | 3-yr series available | Notes |
|---|---|---|---|
| Enrollment / grade | **SY2026-27** | 2024-25, 2025-26, 2026-27 (+ SY2023-24 file exists) | 20th-day counts. 632 schools appear in all four years. |
| Demographics | SY2026-27 | same | Definitions changed; see §3.2. |
| Budget | FY2027 (built on Fall 2025 enrollment) | FY2026 file also downloaded | FY27 ≈ school year 2026-27 but uses prior-fall counts. |
| ISBE spending (PPE) | 2025 Report Card | 2024 file downloaded, **not profiled** | **UNVERIFIED** which fiscal year the PPE covers. ISBE's page says "prior fiscal year"; the glossary is silent. Confirm before labeling. |
| Outcomes | 2025 Report Card (SY2024-25) | 2024, 2023 files exist | The **2026 Report Card is not out yet** (2025 edition was first published 2025-10-24); expect late Oct 2026. Re-run the audit then. |

**Consequence for the Year-policy setting:** "Aligned year" will mostly resolve to **SY2024-25**, the only year all four families share. "Latest per metric" will mix SY2026-27 enrollment with SY2024-25 outcomes, so the per-value year badge is essential, not optional.

**Locations lag:** CHI-LOC is SY2526 and CHI-PROF is SY2425. Against the SY2627 roster, 633 IDs match CHI-LOC, 6 SY2627 schools are missing from it, and 12 CHI-LOC schools are gone from the SY2627 roster. Coordinates for the 6 new IDs are absent from every portal dataset. Phase 1 either carries coordinates over from the predecessor charter building (same-site inference, **UNVERIFIED**) or geocodes them.

## 3. Per-source detail

### 3.1 Enrollment — CPS-MEM (`Schools by Grade`)
- **Header is not on row 1.** Row 1 is a group banner; the field row is 2 (3 in the SY2023-24 file). Detect by finding the cell `School ID`.
- Fields: `School ID, School Name, Network, Governance, School Type, Community Area, Total, PE, PK, K, 1…12`. Rows: 639 (2627), 643 (2526), 647 (2425), 647 (2324). A `-- District Total --` row has a blank ID: drop it.
- IDs are unique per file and stored as text.
- **Governance values:** `District`, `Charter`, `Contract`, `ALOP`, `SAFE` (capitalised `Safe` in older files). This is the authoritative governance field. `Network` values include `Charter`, `Options`, `ISP`, `Contract`, `Network 1–17`.
- **School Type** (`Traditional / Options / Specialty / Early Childhood`) is not the same as the Requirements "type" (district / charter / contract / options). Derive: `Charter→charter`, `Contract/ALOP/SAFE→contract`, `School Type=Options→options`, else district.
- Join across years: 2627∩2526 = 633, 2627∩2425 = 633, all four years = 632.

### 3.2 Demographics — CPS-DEM1 / CPS-DEM2 (sheet `Schools`)
- DEM1 fields: `…, Total, State English Learners N/%, Students with IEPs N/%, Low Income N/%` (header row 2). Percentages are 0–1 fractions, not 0–100.
- DEM2 fields: N/Pct pairs for White, Black/African American, Native American/Alaskan, Latino, Multiracial, Asian, Hawaiian/Pacific Islander, Not Available, Middle Eastern/North African. Header labels contain embedded newlines.
- **No suppression markers** appear in the CPS files: small cells are literal 0s. The "suppressed, never 0" rule can therefore only be honoured for ISBE-sourced values. For CPS counts, the real risk is small-n percentages (e.g. a school with 3 students): set a minimum-n display rule in Phase 1.
- **Definition drift:** SY2526 "Economically Disadvantaged" / "Students with Disabilities" → SY2627 "Low Income" / "Students with IEPs". The district-level share dropped 71.8% → 68.9%. I did not verify what changed, so treat 3-year demographic deltas as **not comparable until the definition is confirmed with CPS**.
- **Not available from CPS files: students in temporary living situations.** Source it from ISBE (`% Student Enrollment - Homeless`, `- Youth in Care`), SY2024-25 only, with `*` suppression.
- **Do not use CHI-PROF `student_count_*` for enrollment.** In SY2425 it disagrees with the 20th-day file for 589 of 646 joined schools (e.g. 346 vs 348). Profile is a different snapshot. Use CPS-MEM, and use CHI-PROF only for non-count fields (address, network, lat/long, `finance_id`).

### 3.3 Spending
**CPS-BUD-DM** (sheets `Traditional` 506 rows, `Alt-Spec` ~18 rows, 65 / 38 columns)
- Fields are staffing FTEs by role plus: `Fall 2025 Total Enrollment`, `Per-Pupil Total For Need-Based Flexible Funding`, `Per-Pupil Total For Title I Funding`, `Discretionary Non-FTE Funding`, `Whole School Safety Funding`, `SDI Allocation`.
- **There is no total-dollars or total-per-pupil column,** and no breakdown matching the Requirements ("SBB / equity grant / Title I / special-ed positions"). CPS dropped student-based budgeting in FY25. Dollar values would require applying salary assumptions to FTEs, which I do not recommend publishing as a "CPS budget".
- The FY27 interactive BI portal (`biportal.cps.edu`, "CPS FY27 Budget") may expose dollars. A sub-agent found it is **not anonymous**: without credentials it serves an Oracle BI sign-in page. The public cps.edu HTML embeds a shared guest login in the link, but I did not use it (entering credentials is something you should decide, not me). Whether it exposes per-school dollars or export is therefore **UNVERIFIED**; see `bi-portal.md`.
- A footer row `PROJECTED ADDITIONAL RESOURCES BUDGETED CITYWIDE` must be dropped.

**CPS-BUD-CC** (sheets `FY27 Charter Schools` 81 rows, `FY27 Contract, ALOP, SAFE`)
- Does carry dollars: `Estimated Per Capita Tuition Charge`, Title I/II/IV, bilingual, SDI; contract sheet adds core instructional, non-instructional, special-ed, facilities. Enrollment is the FY26 20th/10th day.

**Join: name only** for the public Excel files (neither has a school ID). **The line-item export below joins by ID.**

| | Roster (SY2627) | Matched by normalised name | Unmatched |
|---|---|---|---|
| District-run | 523 | 518 (99.0%) | 5 (`MILITARY LEADERSHIP HS`, `BACK OF THE YARDS ES`, `HOLMES HS`, `OGDEN HS`, `DISNEY II HS`) |
| Charter / contract / ALOP / SAFE | 116 | 73 (62.9%) | 43. Charter naming differs (`CICS - AVALON/SOUTH SHORE` vs `CICS AVALON`, etc.). |

**CPS-BUD-BI: FY27 interactive-report line-item export** (`raw/fy27_bi_budget_book.csv`, 76 MB, downloaded by the project owner 2026-09-30; Latin-1 encoded, so read with `encoding='latin-1'`)
- Columns: `Unit, Unit Name, Fund Grant, Fund Grant Name, Account, Account Name, Program, Program Name, FY26 Adopted Budget, FY26 Ending Budget, FY26 Projected Expenditures, FY27 Proposed Budget, FY26 Budgeted Positions, FY26 Ending Positions, FY27 Proposed Positions`. 1,002 units (schools plus departments and city-wide lines).
- **Join:** unit `U20071` = `finance_id` `20071` in the city's SY2425 profile (`3dhs-m3w4`); names agree (checked). 627 of 639 roster schools match directly. The 12 misses: five Acero conversions plus ChiArts (found by name; the Acero conversions already have district units such as `U23691`), Urban Prep (two units, summed), KIPP Academy, Belding, Wentworth (found by name), Catalyst Maria HS (its budget is unit `U66433`, which belongs to 400115) and Safe Achieve ES (no unit). Result: 637 / 639 in `budget_units.csv`; 2 have none.
- **Totals:** school units sum to $5.38B FY27 (the earlier $5.34B came from a by-fund file missing two schools, fixed in Phase 1) (about 50% of the file). Per-pupil median (÷ 20th-day enrollment): district $18.7k, charter $19.7k, contract $19.3k, ALOP $18.9k, SAFE $60k. Largest funds in school units: core instructional positions 33%, special education 22%, charter core funding 16%, general education 7%, need-based flexible 4%.
- **Not reconciled:** the file's grand total ($10.11B) exceeds the dashboard's unit-page total ($8.72B); includes capital and building-operations funds and 22 negative lines (−$571M). We use only school units, but this is **UNVERIFIED** at district level.
- **Access:** manual only. The dashboard is a sign-in; the project owner exported this file. `build.py` reads the committed `budget_units.csv` and `budget_unit_funds.csv` and does not fetch the dashboard.
- **FY27 is "proposed"**, and FY26 projected spending is as of July 2026.
- Outputs: `budget_units.csv` (school_id → unit(s), FY26 adopted, FY26 projected, FY27 proposed, positions) and `budget_unit_funds.csv` (school_id × fund, FY27).

**ISBE-RC `Finance` sheet** (621 Chicago school rows)
- Fields used: `$ Total Per-Pupil Expenditures - Subtotal`, `$ Site-level PEr-Pupil Expenditures - Subtotal` (sic: typo in header), `$ District Centralized Per-Pupil Expenditure - Subtotal`, plus Federal / State-Local splits and `# School Enrollment`.
- Filled for 619 of 621. Chicago median **$20,967** total, **$14,950** site-level, **$6,655** centralized. Range $5,124–$54,695, so outliers need a validation flag, not silent trimming.
- Charter median (≈$20.6k) ≈ non-charter (≈$21.1k) when using the *Total* column. This supports the Requirements claim that the ISBE figure is the comparable measure.
- The `Finance` sheet has 4,695 rows vs 4,693 elsewhere; I did not investigate why. Read columns by header name, never by position.

### 3.4 Outcomes — ISBE-RC (Chicago = RCDTS prefix `15-016-2990`, `Level=School`)

| Requirement | ISBE column | Chicago schools with a value (of 621) |
|---|---|---|
| IAR ELA / Math proficiency | `IAR ELA Proficiency Rate - Total`, `IAR Math…` (sheet `IAR`) | 488 / 488 |
| Growth | `ELA Growth Percentile - Total` and Math equivalent (sheet `IAR`); `HS Assessment … Growth Percentile` | not profiled |
| HS proficiency | `ACT ELA/Math Proficiency Rate Grade 11 - Total`, `HS Assessment … - Total` (sheet `ACT`). **No SAT.** | 149 (ACT), ~169 (HS assessment) |
| 4-yr graduation | `High School 4-Year Graduation Rate - Total` (`General`) | 188 |
| Freshman on-track | `% 9th Grade on Track` (`General`) | 276 (some `*`) |
| College enrollment | `% Graduates enrolled in a Postsecondary Institution within 12 months` (`General`) | 146 (some `*`) |
| Attendance | `Student Attendance Rate` | 621 |
| Chronic absenteeism | `Chronic Absenteeism` | 615 |
| 5Essentials | `Five Essential Survey … ` (7 domain scores) + `… Level` (1–5) | 590 scores / 621 levels |

- Suppression is the literal string **`*`**; blanks mean not applicable. Both must map to "suppressed" / "no data" respectively, never 0.
- Values are percentages 0–100 (strings like `37.10`). Different scale from CPS fractions (0–1).
- Chicago HS counts fit the table: ~170 high schools in CPS-LOC, 188 with a graduation rate.
- Sheet names with spaces/parentheses: `General`, `General (2)`, `ACT`, `IAR`, `Finance`, `Discipline`, `KIDS`, … Large workbook (40 MB, 900-column sheets): convert needed sheets to CSV once and cache.
- **ISBE revises after release** (8 revisions through 2026-05-14, including graduation-rate redactions, post-secondary enrollment and CTE). Record the data-set revision in the "retrieved" stamp.

### 3.5 Joins

**Backbone ID = CPS `School ID`** (6-digit text; `4xxxxx` is typically charter, `6xxxxx` district-run; IDs are stable across the four years except the 6 conversions in §0 #6).

| Join | Coverage | Method |
|---|---|---|
| CPS-MEM ↔ DEM1/DEM2 (same year) | 100% (same `School ID`, same roster) | exact ID |
| CPS-MEM 2627 ↔ CHI-LOC 2526 | 633 / 639 (99.1%) | exact ID; 6 new, 12 gone |
| CPS-MEM 2526 ↔ CHI-LOC 2526 | 643 / 643 | exact ID |
| CPS-MEM 2627 ↔ CHI-PROF 2425 | 633 / 639 (profile has 652 rows incl. 8 not in LOC) | exact ID |
| CPS ↔ ISBE (RCDTS) | **613 / 639 (95.9%)**; 26 have no ISBE record | 518 legacy-portal + 95 hand-matched; see `crosswalk.csv`, `crosswalk_notes.md` |
| CPS ↔ ISBE, remaining 121 | by name fuzzy | auto-match ≈49 high-confidence; ≈74 need manual review (charter naming like `Noble St Chtr-Comer College Prep` vs `NOBLE - COMER`) |
| CPS-MEM ↔ CPS budget (district) | 518 / 523 (99.0%) | normalised name |
| CPS-MEM ↔ CPS budget (non-district) | 73 / 116 (62.9%) | normalised name + manual alias list |
| School point ↔ subdistrict | 645 / 645 | point-in-polygon, no ties |

**Crosswalk construction (the one non-obvious step).** Two Chicago Data Portal datasets carry the state ID:
- `c7jj-qjvh` *CPS Schools 2013-2014*: field `isbe_id` (15 chars, e.g. `15016299025230C` — trailing letter on some) keyed by `schoolid`; 648 rows with IDs.
- `cp7s-7gxg` *School Progress Reports SY1617*: `state_school_report_card_url` (`…iirc.niu.edu/School.aspx?schoolid=150162990252963`); regex the 15-digit RCDTS; 536 rows.
- They agree wherever both exist (0 conflicts). Combined with a strip of hyphens (ISBE writes `15-016-2990-25-2963`), they resolve 521 of 645 SY2526 schools to an RCDTS that exists in the 2025 Report Card (518 of the SY2627 roster).
- The unmapped 121 are almost all charters (84), 22 district-run (recent openings/renames), 8 ALOP, 4 contract, 3 SAFE. Many are legitimately absent from ISBE (alternative / early-childhood programs).
- **Ruled out:** `legacy_unit_id`, `finance_id` and the 4-digit RCDTS suffix do not match (≤ 37 coincidental hits).
- Recommended Phase 1 artifact: committed `crosswalk.csv` (`school_id, rcdts, method, reviewed`). Validation fails the build if a school flagged `reviewed=false` ships an ISBE value.

**Budget name join.** Names in the budget files equal the 20th-day `School Name` for district schools. Normalise whitespace/case, then keep an explicit alias list for charters.

### 3.6 Geography
- **Coordinates:** CHI-LOC `lat`, `long` (text, 645 rows, no gaps). `the_geom` also present. CHI-PROF has `school_latitude/longitude`.
- **Community area:** present as a *name* in all CPS 20th-day files (uppercase). Join to `igwz-8jzy` by name, or derive spatially.
- **Ward:** not in any school file. Derive spatially from `p293-wvbd` (Wards 2023-).
- **Grade category:** CHI-LOC `grade_cat` is only `ES` (475) / `HS` (170). It has no middle/combo band. The Requirements filter "ES / HS / combo" needs to be derived from the 20th-day grade columns (lowest and highest non-zero grade).
- **Subdistrict:** `ERSB_20_Sub_District_Map_FA1_SB_15.shp` (EPSG:4326, 20 features, `LONGNAME` = `District 1a` … `District 10b`, ≈137k population each). All 645 school points land in exactly one polygon, no ties.
  - Verified by rendering it next to the Board of Elections' official citywide PDF (the PDF is a map image, not data, so the check is visual, not numeric). Layout matches.
  - The Board of Elections' per-subdistrict PDFs are listed at `chicagoelections.gov/districts-maps/legislative-maps` (works in a browser; returns 403 to `curl`). The PDFs are on `cboeprod.blob.core.usgovcloudapi.net` and download fine by script.
  - The sibling file `ESRB_20_District_Numbered_Map_11-3-23` has identical polygons labelled D1–D20, so it must not be used for the a/b names.
  - Still **unverified**: that FA1 to SB15 is word-for-word the text enacted as PA 103-0584. Population figures and geometry match the official map; if you want certainty, ask the Board of Elections for the metes-and-bounds description.

## 4. Known caveats to carry into the methodology page
1. Per-year definition changes in low-income / disability labels (§3.2).
2. CPS budget ≠ expenditure; district-run budget file is positions, not dollars (§3.3). ISBE PPE includes centrally paid costs.
3. Charters, contract schools and ALOP schools are budgeted by tuition, not by the district-school model; they are not comparable on the CPS-budget measure.
4. ISBE PPE fiscal year unconfirmed (§2).
5. Governance changes between years (6 charter → district-run conversions) break naive 3-year deltas.
6. Enrollment is 20th-day (Sept). ISBE enrollment and CPS profile counts are different snapshots.

## 5. Decisions (updated)
1. **Year backbone: SY2026-27 roster.** *(decided)*
2. **Spending default:** ISBE per-pupil expenditure is the map/ranking default; CPS budget is shown as FTEs + per-pupil components for district-run schools and as dollars for charter/contract. *(decided)* The CPS BI-portal route is investigated in `bi-portal.md`: it needs a sign-in, so it is not usable for an automated build.
3. **"SAT" → HS test metric:** replace with ACT / HS assessment. Comparability across the SAT→ACT break is being worked out in `hs-assessment-proposal.md`. *(pending proposal)*
4. **Crosswalk review:** done by an agent: 613/639 matched, 26 no ISBE record, no duplicate RCDTS, 0 low-confidence rows, 7 medium rows listed in `crosswalk_notes.md`. Output in `crosswalk.csv`. *(done; medium rows need your glance)*
5. **Charter→district conversions:** verified online in `charter-conversions.md`. *(in progress)*

## 6. Things I did not do
- Did not profile the ISBE 2024/2023 files or the FY26 budget beyond headers.
- Did not download community area / ward geometry.
- Raw downloads and scratch scripts are in the session scratchpad, not in this repo; `raw/` is created in Phase 1.
