"""CPS Facts build. Phase 1 stages: fetch -> normalize -> validate -> write.

    .venv/bin/python build.py              # full run
    .venv/bin/python build.py --skip-fetch # use files already in raw/

Raw downloads are cached in raw/ (see raw/MANIFEST.json for retrieval dates). The CPS budget
export (raw/fy27_bi_budget_book.csv) is downloaded by hand once a year; this build reads the
committed budget_units.csv / budget_unit_funds.csv derived from it. Data files are written to
data/ only when validation passes; the report is always written.
"""
import argparse
import sys
import time

from pipeline import fetch, normalize, validate, write
from pipeline.common import DATA


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--skip-fetch", action="store_true")
    args = ap.parse_args()

    t0 = time.time()
    if not args.skip_fetch:
        print("fetch ...", flush=True)
        fetch.run()
    print("read sources ...", flush=True)
    t = normalize.load_all()
    print("normalize ...", flush=True)
    schools, meta, problems = normalize.build(t)
    print("validate ...", flush=True)
    report = validate.validate(schools, meta, t, problems)

    DATA.mkdir(exist_ok=True)
    if report["failed"]:
        (DATA / "validation_report.md").write_text(write.render_report(report, meta), encoding="utf-8")
        print(f"\nVALIDATION FAILED: {', '.join(report['failed'])}\nSee data/validation_report.md", file=sys.stderr)
        for c in report["checks"]:
            if c["status"] == "FAIL":
                print(f"  - {c['title']}: {c['count']}  e.g. {c['examples'][:3]}", file=sys.stderr)
        sys.exit(1)
    write.write_all(schools, meta, report)
    print(f"ok: {len(schools)} schools, {len(report['warnings'])} warnings, {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
