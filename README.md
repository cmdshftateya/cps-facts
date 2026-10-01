# CPS Facts

A sourced map of every Chicago public school: enrollment, demographics, test scores, attendance, graduation and spending, each value labeled with its school year and source. Live at **https://schools.ateya.org**.

- **Methodology and caveats:** [NOTES.md](NOTES.md) (also on the site's Methodology page)
- **Data downloads:** https://schools.ateya.org/data.html (the same files are in [`data/`](data))
- **Sources and joins:** [sources.md](sources.md), [PIPELINE.md](PIPELINE.md)

## Found an error or have a question?

[Open an issue](../../issues/new/choose). Wrong value, wrong school match, a missing school, or a methodology question are all welcome. Please include the school name or CPS ID and the metric.

## Run it

```
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python build.py            # fetch, normalize, validate -> data/
.venv/bin/python build_site.py       # data/ -> site/
.venv/bin/python -m unittest tests.test_gates
cd site && python3 -m http.server 8000
```

Deploying and updating: see "Deploying and updating" in [PIPELINE.md](PIPELINE.md). The hand-downloaded CPS budget export is not in the repo; the committed `budget_units.csv` and `budget_unit_funds.csv` are built from it.

## License

Code: MIT ([LICENSE](LICENSE)). The data comes from public CPS, Illinois State Board of Education and City of Chicago sources; see [sources.md](sources.md) for each source's terms and URL.
