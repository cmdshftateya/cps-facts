"""Reader for the ISBE Illinois Report Card public data sets (2023, 2024, 2025).

Columns are looked up by exact header (after whitespace/case normalisation), never by
position. A missing column raises, so a renamed header fails the build instead of
silently producing blanks. Values: float, '*' (ISBE-suppressed) or absent (no data).
Percentages stay on ISBE's 0-100 scale.
"""
from .common import RAW, SUPPRESSED, norm_header, read_sheet, to_num

# report-card year -> school-year label
RC_YEAR = {2023: "2022-23", 2024: "2023-24", 2025: "2024-25"}
CHICAGO_PREFIX = "150162990"

# 5Essentials "Ambitious Instruction" is blank for all 621 Chicago schools in 2025, so it is not carried.
# metric -> header, or a tuple of headers to sum (2023 SAT proficiency = Level 3 % + Level 4 %)
SPEC = {
    2025: {
        "General": {
            "attendance_rate": "Student Attendance Rate",
            "chronic_absent": "Chronic Absenteeism",
            "grad_4yr": "High School 4-Year Graduation Rate - Total",
            "ninth_on_track": "% 9th Grade on Track",
            "postsec_12mo": "% Graduates enrolled in a Postsecondary Institution within 12 months",
            "isbe_enrollment": "# Student Enrollment",
            "pct_homeless": "% Student Enrollment - Homeless",
            "pct_youth_in_care": "% Student Enrollment - Youth in Care",
            "fe_leaders": "Five Essential Survey Leaders Level",
            "fe_teachers": "Five Essential Survey Collaborative Teachers Level",
            "fe_families": "Five Essential Survey Involved Families Level",
            "fe_environment": "Five Essential Survey Supportive Environment Level",
        },
        "Finance": {
            "ppe_total": "$ Total Per-Pupil Expenditures - Subtotal",
            "ppe_site": "$ Site-level PEr-Pupil Expenditures - Subtotal",  # sic: ISBE typo
            "ppe_central": "$ District Centralized Per-Pupil Expenditure - Subtotal",
        },
        "IAR": {
            "iar_ela_prof": "IAR ELA Proficiency Rate - Total",
            "iar_math_prof": "IAR Math Proficiency Rate - Total",
            "ela_growth": "ELA Growth Percentile - Total",
            "math_growth": "Math Growth Percentile",
        },
        "ACT": {
            "act_ela_prof": "ACT ELA Proficiency Rate Grade 11 - Total",
            "act_math_prof": "ACT Math Proficiency Rate Grade 11 - Total",
            "act_ela_avg": "ACT ELA Average Score - Grade 11",
            "act_math_avg": "ACT Math Average Score - Grade 11",
            "act_ela_part": "ACT ELA Participation Rate Grade 11 - Total",
            "act_math_part": "ACT Math Participation Rate Grade 11 - Total",
            "act_ela_growth": "ACT ELA Growth Percentile Grade 11- Total",
            "act_math_growth": "ACT Math Growth Percentile Grade 11- Total",
        },
    },
    2024: {
        "General": {
            "attendance_rate": "Student Attendance Rate",
            "chronic_absent": "Chronic Absenteeism",
            "grad_4yr": "High School 4-Year Graduation Rate - Total",
            "ninth_on_track": "% 9th Grade on Track",
            "postsec_12mo": "% Graduates enrolled in a Postsecondary Institution within 12 months",
            "isbe_enrollment": "# Student Enrollment",
        },
        "IAR": {
            "iar_ela_prof": "IAR ELA Proficiency Rate - Total",
            "iar_math_prof": "IAR Math Proficiency Rate - Total",
        },
        "IAR (2)": {
            "ela_growth": "ELA Growth Percentile - Total",
            "math_growth": "Math Growth Percentile",
        },
        "SAT": {
            "sat_ela_prof": "SAT ELA Proficiency Rate - Total",
            "sat_math_prof": "SAT Math Proficiency Rate - Total",
            "sat_ela_avg": "SAT Reading Average Score",
            "sat_math_avg": "SAT Math Average Score",
            "sat_ela_part": "% SAT ELA Participation",
            "sat_math_part": "% Students SAT Math Participation",
        },
    },
    2023: {
        "General": {
            "attendance_rate": "Student Attendance Rate",
            "chronic_absent": "Chronic Absenteeism",
            "grad_4yr": "High School 4-Year Graduation Rate - Total",
            "ninth_on_track": "% 9th Grade on Track",
            "postsec_12mo": "% Graduates enrolled in a Postsecondary Institution within 12 months",
            "isbe_enrollment": "# Student Enrollment",
        },
        "SAT": {
            "sat_ela_prof": ("SAT Reading Total Students Level 3 %", "SAT Reading Total Students Level 4 %"),
            "sat_math_prof": ("SAT Math Total Students Level 3 %", "SAT Math Total Students Level 4 %"),
            "sat_ela_avg": "SAT Reading Average Score",
            "sat_math_avg": "SAT Math Average Score",
            "sat_ela_part": "% SAT ELA Participation",
            "sat_math_part": "% Students SAT Math Participation",
        },
    },
}


def _normalize_rcdts(s):
    return str(s).replace("-", "").strip()


def _chicago_rows(rows):
    hdr = [norm_header(h) for h in rows[0]]
    ri = hdr.index("rcdts")
    ti = hdr.index("level") if "level" in hdr else hdr.index("type")
    for r in rows[1:]:
        rc = _normalize_rcdts(r[ri])
        if rc.startswith(CHICAGO_PREFIX) and str(r[ti]).strip() == "School":
            yield rc, r


def read_year(rc_year):
    """-> {rcdts: {metric: value}} for Chicago school rows of one Report Card year."""
    path = RAW / f"isbe_rc_{rc_year}.xlsx"
    out = {}
    for sheet, mapping in SPEC[rc_year].items():
        rows = read_sheet(path, sheet)
        hdr = [norm_header(h) for h in rows[0]]

        def col(name):
            n = norm_header(name)
            if n not in hdr:
                raise KeyError(f"ISBE {rc_year} sheet {sheet!r}: column {name!r} not found")
            return hdr.index(n)

        idx = {m: ([col(c) for c in spec] if isinstance(spec, tuple) else col(spec))
               for m, spec in mapping.items()}
        for rc, r in _chicago_rows(rows):
            rec = out.setdefault(rc, {})
            for m, i in idx.items():
                if isinstance(i, list):
                    parts = [to_num(r[j]) for j in i]
                    if any(p == SUPPRESSED for p in parts):
                        v = SUPPRESSED
                    elif any(p is None for p in parts):
                        v = None
                    else:
                        v = round(sum(parts), 2)
                else:
                    v = to_num(r[i])
                if m.startswith("fe_") and v == 0:
                    v = None  # level 0 pairs with a blank score everywhere: "not rated", not a rating
                if v is not None:
                    rec[m] = v
    return out


def read_names(rc_year):
    """-> {rcdts: ISBE school name} (used for validation and notes only)."""
    rows = read_sheet(RAW / f"isbe_rc_{rc_year}.xlsx", "General")
    hdr = [norm_header(h) for h in rows[0]]
    ni = hdr.index("school name")
    return {rc: str(r[ni]).strip() for rc, r in _chicago_rows(rows)}


def revision(rc_year=2025):
    """Latest entry of the workbook's 'Revision History' sheet, recorded as the data version."""
    rows = read_sheet(RAW / f"isbe_rc_{rc_year}.xlsx", "Revision History")
    best = None
    for r in rows:
        n = to_num(r[0]) if r else None
        if isinstance(n, float) and (best is None or n > best[0]):
            best = (n, str(r[1]).strip())
    return f"revision {int(best[0])}, {best[1]}" if best else ""
