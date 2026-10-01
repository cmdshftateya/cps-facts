# Data pipeline (Phase 1)

```
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python build.py              # fetch -> normalize -> validate -> write
.venv/bin/python build.py --skip-fetch # reuse raw/
.venv/bin/python -m tests.test_gates   # corrupts the data in memory; every gate must fire
```

Raw downloads are cached in `raw/` (retrieval dates and hashes in `raw/MANIFEST.json`; delete a file to re-fetch). The CPS budget export `raw/fy27_bi_budget_book.csv` is downloaded by hand; the build reads the committed `budget_units.csv`, `budget_unit_funds.csv`, `crosswalk.csv` and `lineage.csv`.

## Outputs (`data/`, written only if validation passes)
- `schools.json`: `meta` (sources and file dates, metric registry with units, years and comparability `breaks`, flag texts, fund names, rules) + `schools[]`. Per school, `m[metric][school_year]` is a number, `"*"` (suppressed) or absent (no data). Percentages are 0-100.
- `schools.csv`: one row per school; latest value and year for headline metrics.
- `school_values.csv`: long format, every value with metric, school year, status, unit, source and retrieved date (includes enrollment by grade).
- `validation_report.md` / `.json`: checks (fail/warn), coverage per metric, rules, source versions. The report is written even when the build fails.

## Rules worth knowing
- CPS demographics are never hidden; schools under 30 students get a `low_n` label.
- ISBE `*` on a metric the school cannot have (SAT/ACT/graduation at a school with no grades 9-12; IAR with no grades 3-8) becomes no data.
- 5Essentials level 0 = not rated -> no data. "Ambitious Instruction" is blank for every school in 2025 and is not carried.
- A $0 CPS budget unit is no data (`budget_zero_unit`).
- Converted schools (`lineage.csv`) take pre-conversion enrollment/demographics from the predecessor ID; ISBE series follow the crosswalk RCDTS. Both are flagged.
- Catalyst Maria (400115/400182): one budget unit covers both campuses, so per-pupil uses their combined enrollment on both (flagged); the total stays on 400115.
- Grade 11 "score vs ACT benchmark" (`g11_ela_gap`, `g11_math_gap`): SAT years converted with the official concordance and marked estimated; rank-correlation sanity check on every build. See `hs-score-benchmark-method.md`.
- Outliers are flagged, never trimmed.

# Phase 2: map and panel
```
.venv/bin/python build_site.py          # data/schools.json -> site/data/schools.json (projected x/y, subdistrict + community-area paths)
cd site && python3 -m http.server 8000  # then open http://localhost:8000
```
`site/index.html` is the whole app (HTML + CSS + one inline script) plus `chicago.css` and `data/schools.json`; no runtime network beyond that JSON. `build_site.py` projects lat/lon (equirectangular, cos-latitude corrected), simplifies geometry and copies `chicago.css` from `../politics`. Re-run it whenever `build.py` regenerates `data/schools.json`.

Behavior worth knowing:
- Values come from `m[metric][year]`. "Latest per metric" takes each school's newest year; "Aligned" shows only that year, otherwise "no data for SYxx" (no fallback).
- Sparklines use only years after a metric's last comparability break (`meta.metrics[].breaks`), so IAR, grade 11 and the 2026-27 low-income/IEP relabel never show a trend across the break. Grade 11 SAT and ACT are merged into one series with a break at 2024-25.
- Quantile bins, medians and subdistrict averages use the comparison set (all schools, or district-run only).
- Settings persist in the URL hash (`s_*`) and localStorage; the URL wins.
- Not built yet: the grade 11 benchmark-estimate toggle (waiting on the ACT "ELA" column meaning), a diverging palette for enrollment change, and the table view (Phase 3).

# Deploying and updating

The site is static: a Cloudflare Worker serving only the `site/` directory (see `wrangler.jsonc`; custom domain `schools.ateya.org`). There is no server code and no database.

**Update the data, then redeploy**
```
.venv/bin/python build.py              # refresh data/ (add --skip-fetch to reuse raw/)
.venv/bin/python build_site.py         # data/schools.json -> site/data/schools.json
git add -A && git commit && git push   # data/ and site/data/ are committed, so each update is a reviewable diff
```
Pushing to `main` deploys automatically: the GitHub repo is connected to the Worker through Cloudflare Workers Builds (dashboard: Workers & Pages > cps-facts > Settings > Builds). The build command is empty because `site/` is committed already; the deploy command is `npx wrangler deploy`. Build logs are on the Worker's Builds tab. The pipeline itself never runs on Cloudflare (`raw/` is not in git). A manual deploy is still possible with `npx wrangler deploy`.

**One-time setup**
- Wrangler needs Node 22 or newer. Install it with nvm (`nvm install 22`) and run `. ~/.nvm/nvm.sh && nvm use 22` in a new shell if `node -v` shows an older version.
- `npx wrangler login` opens a browser to authorize Cloudflare; it must be approved by a person.
- The first deploy attaches `schools.ateya.org` as a custom domain (DNS and the certificate can take a few minutes). Check status in the Cloudflare dashboard if the site does not load.

**What lives where**
- In git: code, docs, the small curated CSVs (`budget_units.csv`, `budget_unit_funds.csv`, `crosswalk.csv`, `lineage.csv`), `data/` outputs and `site/`.
- Local only, never pushed: `raw/` (downloads, rebuilt by `fetch.py` from the URLs and hashes in `raw/MANIFEST.json`) and the hand-downloaded CPS budget export `raw/fy27_bi_budget_book.csv`. Nothing is stored in cloud storage, to avoid ongoing cost.
- The repo `cmdshftateya/cps-facts` on GitHub is private.
