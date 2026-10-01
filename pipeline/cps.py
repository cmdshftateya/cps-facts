"""Readers for the CPS 20th-day files (membership, LEP/IEP/low-income, race).

Header rows are not on row 1: a banner row sits above the field row, so the
field row is found by locating the cell 'School ID'. Percentages in the CPS files
are 0-1 fractions; they are converted to 0-100 here.
"""
from .common import RAW, CPS_YEARS, norm_header, read_sheet, to_id, to_num

YEAR_FILE = {"2024-25": "2425", "2025-26": "2526", "2026-27": "2627"}

GRADE_ORDER = ["PE", "PK", "K"] + [str(g) for g in range(1, 13)]

RACE_GROUPS = {
    "white": "white",
    "black/african american": "black",
    "native american/ alaskan": "native",
    "latinx": "latinx",
    "multiracial": "multiracial",
    "asian": "asian",
    "hawaiian/ pacific islander": "pacific",
    "not available": "race_na",
    "middle eastern/northern african": "mena",
    # 2024-25 only, one student district-wide; folded into nothing and reported
    "asian/ pacific islander (retired)": "asian_pi_retired",
}


def _find_header(rows):
    for i, r in enumerate(rows[:6]):
        if any(str(c).strip() == "School ID" for c in r):
            return i
    raise ValueError("no 'School ID' header row found")


def _rows(path, sheet):
    rows = read_sheet(path, sheet)
    h = _find_header(rows)
    return rows[h - 1] if h > 0 else [], rows[h], rows[h + 1:]


def _grade_label(h):
    s = str(h).strip()
    if s.endswith(".0"):
        s = s[:-2]
    return s


def read_membership(year):
    """-> {school_id: {name, network, governance, school_type, community_area, total, grades{}}}"""
    path = RAW / f"cps_mem_{YEAR_FILE[year]}.xlsx"
    _, hdr, body = _rows(path, "Schools by Grade")
    cols = [_grade_label(h) for h in hdr]
    out = {}
    for r in body:
        sid = to_id(r[cols.index("School ID")])
        if not sid:  # '-- District Total --' row
            continue
        rec = dict(zip(cols, r))
        grades = {}
        for g in GRADE_ORDER:
            if g in rec:
                v = to_num(rec[g])
                grades[g] = int(v) if isinstance(v, float) else 0
        out[sid] = {
            "name": str(rec["School Name"]).strip(),
            "network": str(rec["Network"]).strip(),
            "governance": str(rec["Governance"]).strip(),
            "school_type": str(rec["School Type"]).strip(),
            "community_area": str(rec["Community Area"]).strip(),
            "total": int(to_num(rec["Total"])),
            "grades": grades,
        }
    return out


def read_lepiep(year):
    """-> {school_id: {total, el_n, el_pct, iep_n, iep_pct, li_n, li_pct, li_label, iep_label}}"""
    path = RAW / f"cps_lepiep_{YEAR_FILE[year]}.xlsx"
    banner, hdr, body = _rows(path, "Schools")
    # banner row names the three groups above their N / % column pairs
    groups = {}
    last = ""
    for i, b in enumerate(banner):
        if str(b).strip():
            last = str(b).strip()
        groups[i] = last
    out = {}
    for r in body:
        sid = to_id(r[0])
        if not sid:
            continue
        cells = {}
        for i, h in enumerate(hdr):
            g = groups.get(i, "")
            if g in ("State English Learners",):
                cells["el_" + ("n" if h == "N" else "pct")] = to_num(r[i])
            elif g in ("Students with Disabilities", "Students with IEPs"):
                cells["iep_" + ("n" if h == "N" else "pct")] = to_num(r[i])
            elif g in ("Economically Disadvantaged", "Low Income"):
                cells["li_" + ("n" if h == "N" else "pct")] = to_num(r[i])
        cells["total"] = to_num(r[hdr.index("Total")])
        for k in ("el_pct", "iep_pct", "li_pct"):
            if isinstance(cells.get(k), float):
                cells[k] *= 100
        out[sid] = cells
    labels = {
        "iep_label": next(g for g in groups.values() if g in ("Students with Disabilities", "Students with IEPs")),
        "li_label": next(g for g in groups.values() if g in ("Economically Disadvantaged", "Low Income")),
    }
    return out, labels


def read_race(year):
    """-> {school_id: {total, <key>_n, <key>_pct ...}}; pct as 0-100."""
    path = RAW / f"cps_race_{YEAR_FILE[year]}.xlsx"
    banner, hdr, body = _rows(path, "Schools")
    groups, last = {}, ""
    for i, b in enumerate(banner):
        if str(b).strip():
            last = norm_header(b)
        groups[i] = last
    out = {}
    for r in body:
        sid = to_id(r[0])
        if not sid:
            continue
        rec = {"total": to_num(r[hdr.index("Total")])}
        for i, h in enumerate(hdr):
            key = RACE_GROUPS.get(groups.get(i, ""))
            if not key:
                continue
            if str(h).strip() == "No":
                rec[key + "_n"] = to_num(r[i])
            elif str(h).strip() == "Pct":
                v = to_num(r[i])
                rec[key + "_pct"] = v * 100 if isinstance(v, float) else v
        out[sid] = rec
    unknown = {g for g in groups.values() if g and g not in RACE_GROUPS and g != "school information"}
    if unknown:
        raise ValueError(f"unrecognised race groups in {path.name}: {unknown}")
    return out
