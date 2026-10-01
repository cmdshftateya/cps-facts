# CPS Facts — Requirements (draft v0.4 — Phase 0 audit applied; see `sources.md`)

**Goal:** One map-first page that documents every Chicago Public Schools school — who attends, how many, what's spent, and how students do — with every number sourced and dated.

**Home:** Standalone site at **schools.ateya.org** — its own repo, favicon, OG images and about page. Not linked into the politics hub's card grid (a plain cross-link from the board guide is fine).

**Theme:** Copy the "Chicago School" design system from `../politics/chicago.css` into this repo (vendored copy; token values unchanged): dark default + real light mode, no rounding, no shadows, 1px hairline grids, hover inverts, condensed display type, flag-star motif, **no webfonts / no CDN / no network at runtime**.

---

## 1. Scope

| In v1 | Later |
|---|---|
| All schools in CPS's current-year School Profile / Locations data (district-run, charter, contract, options) | Historical trend lines per school beyond 3 years |
| 4 fact families: demographics, enrollment, spending, outcomes | Network/ward/community-area rollup pages |
| Roster = **SY2026-27** (CPS 20th-day, 2026-09-21). Enrollment/demographics: SY2026-27 + prior 2 years. Outcomes/spending: latest published (2025 Report Card, SY2024-25) | Attendance-boundary "which school am I zoned for" lookup |
| Board of Ed subdistrict overlay (cross-links to the politics site's 2026 board guide) | Capacity / utilization, facilities condition |

## 2. Data (per school, per school year)

**Identity:** CPS school ID, ISBE RCDTS ID (join key to state data), name, type (district / charter / contract / options), governance, grade span, network, address, lat/lon, Board of Ed subdistrict, community area, ward.

**Enrollment:** 20th-day total; by grade; 3-year change (count + %).

**Demographics (% of enrollment):** race/ethnicity, low-income, English learners, diverse learners (IEP), students in temporary living situations.

**Spending:**
- CPS school-level budget. **Source: the CPS FY27 interactive-report line-item export (`Budget_Book_FY27.csv`, manual download from the BI "Download Data" tab).** One row per unit × fund × account × program with FY26 adopted/projected and FY27 proposed dollars and positions. Aggregated to a school total, per pupil (÷ 20th-day enrollment), and by funding source. Units join to schools through the city profile's `finance_id` (`U` + id). The public Excel files (staffing/per-pupil components) remain as a cross-check.
- ISBE Report Card site-level per-pupil expenditure (ESSA) — **the comparable measure**, because it includes centrally-paid costs that school budgets omit.
- Both are carried where available; **ISBE per-pupil expenditure is the default** for map, rankings and medians (a setting, §3a). The panel shows both, labeled, with the fiscal year (to confirm).

**Outcomes:**
- Elementary: IAR ELA/math proficiency, growth percentile (where published), attendance, chronic absenteeism. **ISBE lowered IAR cut scores in 2025 without re-scoring prior years: no trend lines or deltas across 2024→2025.**
- High school: grade 11 state test (**SAT through 2024, ACT from 2025**; never compared across the break — see `hs-assessment-proposal.md`), 4-yr graduation rate, freshman on-track, college enrollment, attendance, chronic absenteeism. Graduation, on-track, attendance, absenteeism and postsecondary enrollment carry the 3-year trend.
- Survey: 5Essentials rating (if available for the year).

**Every value carries:** source ID, school year, retrieved date. ISBE `*` = "suppressed"; blank = "no data"; never 0. CPS files have no suppression markers (small cells are literal 0): publish as given, with a small-school label under 30 students. Low-income / disability labels changed between SY2526 and SY2627: no demographic deltas across that change until CPS confirms comparability. Temporary-living share comes from ISBE (SY2024-25) only.

### Sources (audited in Phase 0 — details, URLs, join coverage in `sources.md`)
- Chicago Data Portal: *CPS School Locations SY2526*, *School Profile Information*, attendance boundaries.
- CPS: school-level budgets (FY2026 released July 2025; check FY2027), district data / demographics & enrollment files.
- ISBE Illinois Report Card: per-pupil expenditure, assessments, graduation, absenteeism.
- Subdistricts: Illinois Senate `ERSB_20_Sub_District_Map_FA1_SB_15` shapefile (matches the Board of Elections' official map; all schools fall in one subdistrict).
- **ID join:** CPS School ID ↔ ISBE RCDTS via `crosswalk.csv` (613/639 matched, 26 no ISBE record). Roster changes (Acero/ChiArts conversions, closures) tracked per `charter-conversions.md`.

## 3. The map

- **Geographic, vector, self-rendered.** Boundaries + points projected to SVG at build time (Python, same pattern as `site_build.py`). No basemap tiles — they'd break the no-network rule and the flat aesthetic. Context layer = city outline, lake edge, subdistrict lines on hairline `--rule`.
- **One marker per school**, sized optionally by enrollment. Every school is a filled square. When coloring by **school type**, governance is also encoded by **shape and fill** (nothing rounded), and the legend draws each type with its shape (D-026 dropped the shapes from metric views):
  - District-run: filled square
  - Charter: hollow square (2px stroke in the type color)
  - Contract / options: filled diamond (square rotated 45°)
  - Schools excluded from comparisons (see §3a) keep their color but drop to 40% opacity.
- **"Color by" selector** — one metric at a time, using the existing 6-step `--seq-*` ramp (quantile bins, legend shows bin edges). Categorical metrics (school type) use `--s1..s4`. Any diverging scale (e.g., enrollment change) needs a new palette run through the same validator.
- **Optional choropleth mode** (setting): shade Board subdistricts (or community areas) by enrollment-weighted average of the chosen metric.
- **Filters:** school type, grade band (ES / HS / combo), network, subdistrict, "has data for this metric".
- **Search** by name, ID, or address/neighborhood (client-side, like the board guide's search).
- **Click → school panel** (right rail desktop, bottom sheet mobile): all four fact families in hairline-gridded cells, citywide median beside each number, sparkline for 3-year trends, sources footer.
- **Hover** shows name + current metric value, instant (no fade).
- **Shareable state:** URL hash encodes metric, filters, settings and selected school.

### 3a. Settings menu

A single square button fixed to the **bottom-right** corner (flag star icon, hairline border; hover inverts). Click opens a panel anchored above it; Esc, outside-click or the button again closes it. Hidden by default, keyboard-reachable, and on mobile it opens as a bottom sheet.

| Setting | Options | Default |
|---|---|---|
| Comparison set | All schools / District-run only (charter + contract/options shown but excluded from rankings, quantile bins and city medians) | All schools |
| Spending figure | ISBE per-pupil expenditure / CPS budget per pupil | ISBE per-pupil expenditure |
| Year policy | Latest available per metric / Aligned year (picker lists the school years present in the data) | Latest per metric |
| Size by enrollment | On / Off | Off |
| Map mode | School points / Subdistrict shading | School points |
| Grade 11 test measure | State proficiency % (never compared across 2024→2025) / Score vs national benchmark (estimate; SAT years converted by ACT–SAT concordance, see `hs-score-benchmark-method.md`) | State proficiency % |
| Theme | Auto / Dark / Light | Auto |

Rules:
- Changing any setting recomputes bins, medians and ranks client-side — no reload.
- Under "Latest per metric", every number in the panel and table shows its school-year badge (e.g., `SY24–25`), and the legend warns when the colored metric's year differs across schools.
- A small inline line under the legend states the active non-default settings ("District-run only · CPS budget · SY24–25"), so a screenshot is self-describing.
- Under "Aligned year", a school missing a metric for the chosen year shows **no data** for it (hatched marker / "—" in panel and table) — never a fallback to another year.
- Settings persist in the URL hash (shareable) and in localStorage (remembered), URL wins.

## 4. Companion views

- **Table view** of all schools, sortable, same filters — the accessible equivalent of the map and the mobile default.
- **Methodology page** (built from `METHODOLOGY.md`): source list, join logic (CPS ID ↔ RCDTS), definitions, suppression rules, known caveats (charter spending comparability, budget vs. expenditure).
- **CSV/JSON download** of the normalized dataset.

## 5. Non-functional

- Static site at schools.ateya.org, served by a **Cloudflare Worker with static assets only** — no Worker script, no server-side logic. `wrangler.jsonc` points `assets.directory` at `site/` (committed, so a push to `main` deploys it through Cloudflare Workers Builds); custom domain `schools.ateya.org` attached in Cloudflare. Plain HTML + `chicago.css` + one inline JS bundle + `data/schools.json`. No framework, no runtime fetches beyond same-origin JSON.
- Page weight target < 1.5 MB incl. data; first render < 1s on mid laptop.
- Works at 360px wide; keyboard-navigable markers; color never the only encoding (legend + values in panel/table).
- Rebuild is one command: `python build.py` (fetch → normalize → validate → render). Raw downloads cached in `raw/` with retrieval date.
- Validation step fails the build on: schools missing coordinates, unjoined IDs above a threshold, percentages outside 0–100, duplicate IDs.

## 6. Phases

0. **Source audit** — ✅ done. Outputs: `sources.md`, `crosswalk.csv`, `hs-assessment-proposal.md`, `charter-conversions.md`, `bi-portal.md`.
1. **Data pipeline** — ✅ done. normalized `schools.json` + CSV + validation report. See `PIPELINE.md`.
2. **Map + panel** — color-by, filters, search, school panel.
3. **Table, methodology, downloads.** — ✅ done (`site/data.html`, `site/downloads/`).
4. **Launch** — deployed to schools.ateya.org with OG images, favicon, public repo and issue links. Remaining: cross-link from the politics site's board guide (subdistrict → schools), and the 2026 Report Card refresh.

## 7. Decisions

1. **Home:** standalone at schools.ateya.org. *(decided)*
2. **Charter / contract schools:** visually distinct markers; inclusion in comparisons is a toggle. *(decided)*
3. **Spending figure:** both carried; toggle in settings. *(decided)*
4. **Year policy:** toggle in settings. *(decided)*
5. **Hosting:** Cloudflare Worker, static assets only. *(decided)*
6. **Aligned year with missing data:** show no data, no fallback. *(decided)*
7. **Year backbone:** SY2026-27 roster. *(decided)* Aligned-year will mostly resolve to SY2024-25, the only year all four families share.
8. **CPS budget:** school dollar totals and by-fund breakdown from the BI line-item export (user-downloaded; refreshed by hand once a year, not by `build.py`). *(decided)* 637/639 schools join; the build reads the committed `budget_units.csv` / `budget_unit_funds.csv`.
9. **HS test:** per `hs-assessment-proposal.md`, plus a settings toggle for a benchmark-based estimate per `hs-score-benchmark-method.md`. *(decided; ISBE "ELA" column meaning to confirm)*
10. **Catalyst Maria HS (400182):** no ISBE row of its own; ISBE reports it under 400115. Show ISBE values on 400115 only; 400182 shows "no separate state data" plus CPS enrollment/demographics. *(decided)*

Plain-language record of choices and caveats: `NOTES.md` (detailed notes) and `METHODOLOGY.md` (source for the Methodology page, §4).
