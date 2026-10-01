"""Official 2018 ACT-SAT concordance (ACT / College Board), parsed from the published PDF.

Used only to put school-MEAN SAT scores on the ACT scale for the optional "score vs national
benchmark (estimate)" view. Concordance matches ranks of students who take both tests; applied to
school means it is approximate. Tables used: B1 (SAT Math -> ACT Math), C1 (SAT ERW -> ACT English+Reading,
a 2-72 sum, halved here to a 1-36 average).
"""
import re

from pypdf import PdfReader

from .common import RAW

PDF = RAW / "act_sat_concordance.pdf"
# ACT College Readiness Benchmarks: English 18, Reading 22 (ELA 20, the mean of the two), Math 22.
BENCH = {"ela": 20.0, "math": 22.0}


def _pairs(text):
    out = {}
    for a, b in re.findall(r"\*?(\d{2,3}) (\d{2,3})(?=\s|$)", text):
        out[int(a)] = int(b)
    return out


def load():
    pages = [p.extract_text() or "" for p in PdfReader(str(PDF)).pages]
    b1 = pages[1].split("Table B2")[0]
    c1 = pages[2].split("ACT SAT ACT SAT")[0]
    math = {s: a for s, a in _pairs(b1.split("Table B1")[1]).items() if 200 <= s <= 800}
    erw = {s: a / 2 for s, a in _pairs(c1.split("Table C1")[1]).items() if 200 <= s <= 800}
    # sanity: SAT scores step by 10 over the published range, ACT values never decrease as SAT rises
    assert len(math) == 55 and len(erw) == 53, (len(math), len(erw))
    for t in (math, erw):
        v = [t[k] for k in sorted(t)]
        assert all(x <= y for x, y in zip(v, v[1:])), "concordance not monotonic"
    assert math[800] == 36 and erw[800] == 36.0 and math[500] == 18
    return {"math": math, "ela": erw}


def to_act(table, sat_mean):
    """Linear interpolation between published 10-point SAT steps; clamped to the table range."""
    ks = sorted(table)
    if sat_mean <= ks[0]:
        return float(table[ks[0]])
    if sat_mean >= ks[-1]:
        return float(table[ks[-1]])
    lo = max(k for k in ks if k <= sat_mean)
    hi = min(k for k in ks if k >= sat_mean)
    if lo == hi:
        return float(table[lo])
    return table[lo] + (table[hi] - table[lo]) * (sat_mean - lo) / (hi - lo)
