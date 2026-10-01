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
- Outliers are flagged, never trimmed.
