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
- Quantile bins, medians, range bars and subdistrict averages use the comparison set: "Comparable schools" (the default; leaves out every school with a `program`), "All schools", or "District-run only" (also leaves out those). Left-out schools stay on the map dimmed and in the table. The setting is remembered in localStorage with a `setv` stamp, so a comparison set saved before the default changed is ignored.
- School context (`pipeline/program.py`): `program` comes from the hand-kept `program_overrides.csv` (source URL per school; the build fails without one) plus preschool-only centers from the CPS School Type; `admission` (exam or application) and `sped_cluster` come from the Data Portal School Profile (`classification_description`, `significantlymodifiedmod`). A classification text the module does not know raises the warning `program_unknown_class` so a new CPS category is not silently unlabeled. `admission` is `mixed` when an exam-classified school also has an attendance boundary, plus hand overrides in `ADMISSION_OVERRIDES` (Carnegie mixed; Goode application). `grad_5yr` is read from the same ISBE General sheet as `grad_4yr`. Which programs leave the default comparison set is `comparable: false` in `meta.programs`.
- Settings persist in the URL hash (`s_*`) and localStorage; the URL wins.
- Table view: Map/Table toggle in the header (`#v=table` in the URL; on screens under 760px the table is the default). It shares the map's filters, lists the fixed facts plus the current color-by metric, sorts on any column (schools with no value sort last, never as zero), and a row click opens the same profile panel.
- Grade 11 benchmark-estimate toggle, the enrollment-change diverging palette and the sequential ramp override (`site/sequential.css`; both from `node tools/diverging_palette.mjs`) are built (ACT "ELA" is the ACT ELA score, benchmark 20; ISBE has not confirmed in writing).
- Tests: `.venv/bin/python -m unittest discover tests`. `test_gates` corrupts the built data in memory and checks each validation gate fails (needs `raw/`, skipped without it). `test_published` checks the committed `data/` and `site/` outputs and runs in GitHub Actions on every push (`.github/workflows/test.yml`).
- Data and sources page: `site/data.html` is generated by `build_site.py` from `sources_catalog.py` (publisher, dataset, links and field names for each source; edit it when a source or URL changes) and the metric list in `data/schools.json`. `NOTES.md` becomes the Methodology page; write it for readers outside the project, with no references to internal files.
- Share pages: `build_site.py` also writes `site/s/<id>/index.html` and `site/s/<id>/card.png` for every school (`pipeline/share.py`; re-run alone with `.venv/bin/python -m pipeline.share`, about 30 s on 4 cores, no `raw/` needed). Link-preview bots never see the `#` part of a URL, so each page carries that school's title, description and 1200×630 card, and its script sends browsers on to `/#school=<id>`. The map keeps the selected school in the path (`/s/<id>/#…`), so a copied address bar or the phone's share button gets the school's preview; nav links in `index.html` are root-absolute for that reason. The card shows the name, a badge (six-point star with initials; colour and pattern from a hash of id and name, identity only), the school's spot on the city outline, and students, low income and 4-year graduation (high and combined schools) or attendance, each with its school year; suppressed and missing are spelled out. Fonts are vendored in `tools/fonts/` (Barlow, SIL OFL) and drawing uses Pillow, so cards come out the same on any machine; a card is rewritten only when its pixels change, and `?v=<hash>` on the image URL makes platforms refetch it. After a deploy, check one link in a preview debugger (Facebook Sharing Debugger, LinkedIn Post Inspector) to refresh their caches.
- Share button (school panel): draws a 1080×1440 snapshot in the browser (`drawSnap` in `index.html`, same badge hash and colours as `pipeline/share.py`; keep the two in step) and passes it with a text summary and the `/s/<id>/` link to `navigator.share`. Fonts load from `site/fonts/`, which `build_site.py` copies from `tools/fonts/`. Browsers without file sharing get a download and a clipboard copy.
- Downloads: `build_site.py` copies the `data/` files into `site/downloads/` and writes `site/data.html`; the social preview image and icons come from `tools/make_og.py` (needs `rsvg-convert`) and are committed.

# Deploying and updating

The site is static: a Cloudflare Worker serving only the `site/` directory (see `wrangler.jsonc`; custom domain `schools.ateya.org`). There is no server code and no database.

**Update the data, then deploy (a push to `main` is the whole deploy)**
```
.venv/bin/python build.py              # refresh data/ (add --skip-fetch to reuse raw/)
.venv/bin/python build_site.py         # data/ -> site/ (map data, Methodology and Data pages, downloads)
.venv/bin/python -m unittest discover tests
git add -A && git commit && git push   # data/ and site/ are committed, so each update is a reviewable diff
```
Pushing to `main` does two things automatically:
- **GitHub Actions** runs `tests/test_published.py` (`.github/workflows/test.yml`); see the Actions tab.
- **Cloudflare Workers Builds** deploys `site/` to schools.ateya.org (dashboard: Workers & Pages > cps-facts > Settings > Builds; logs on the Builds tab). The build command is empty because `site/` is committed already; the deploy command is `npx wrangler deploy`.

The pipeline itself never runs on Cloudflare or in CI (`raw/` is not in git). When a source or URL changes, edit `sources_catalog.py` as well, so the Data and sources page stays accurate. When the methodology changes, edit `METHODOLOGY.md` (it becomes the Methodology page) and, for the detail behind it, `NOTES.md`.

**If the site does not update, or will not open**
- Check the Builds tab. Confirm what is live with `npx wrangler versions list` (Node 22), or compare the live `index.html` with `site/index.html` (Cloudflare adds a small script, so sizes differ by about 1 KB). A manual deploy is always possible with `npx wrangler deploy`.
- "Could not resolve host" for `schools.ateya.org` while `dig @1.1.1.1 schools.ateya.org` returns addresses means a local resolver (often the home router) cached the "no such domain" answer from before the custom domain was attached. The site is fine. Flush the Mac cache (`sudo dscacheutil -flushcache; sudo killall -HUP mDNSResponder`), set DNS to 1.1.1.1 (`networksetup -setdnsservers Wi-Fi 1.1.1.1 8.8.8.8`; undo with `... empty`), restart the router, or wait. To test the live site regardless: `curl --resolve schools.ateya.org:443:104.21.24.51 https://schools.ateya.org/`.

**One-time setup**
- Wrangler needs Node 22 or newer. Install it with nvm (`nvm install 22`) and run `. ~/.nvm/nvm.sh && nvm use 22` in a new shell if `node -v` shows an older version.
- `npx wrangler login` opens a browser to authorize Cloudflare; it must be approved by a person.
- The first deploy attaches `schools.ateya.org` as a custom domain (DNS and the certificate can take a few minutes). Check status in the Cloudflare dashboard if the site does not load.

**What lives where**
- In git: code, docs, the small curated CSVs (`budget_units.csv`, `budget_unit_funds.csv`, `crosswalk.csv`, `lineage.csv`), `data/` outputs and `site/`.
- Local only, never pushed: `raw/` (downloads, rebuilt by `fetch.py` from the URLs and hashes in `raw/MANIFEST.json`) and the hand-downloaded CPS budget export `raw/fy27_bi_budget_book.csv`. Nothing is stored in cloud storage, to avoid ongoing cost.
- The repo `cmdshftateya/cps-facts` on GitHub is public (MIT for code). Issues are enabled and linked from the site header, the Methodology and Data pages, and the README; templates are in `.github/ISSUE_TEMPLATE/`. Keep credentials and the hand-downloaded budget export out of the repo.
