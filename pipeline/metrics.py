"""Metric registry: what every value in schools.json means.

Each metric lists its source id, unit, school years carried, and any `breaks`:
school years at which the series stops being comparable with the year before it.
The front end must not draw a line, delta or shared color break across a break.
"""
from .common import CPS_YEARS

ISBE_YEARS = ["2022-23", "2023-24", "2024-25"]  # Report Card 2023, 2024, 2025


def M(label, unit, family, source, years, breaks=(), note=""):
    return {"label": label, "unit": unit, "family": family, "source": source,
            "years": list(years), "breaks": list(breaks), "note": note}


REGISTRY = {}

# --- enrollment (CPS 20th day) ---
REGISTRY["enrollment"] = M("20th-day enrollment", "count", "enrollment", "CPS-MEM", CPS_YEARS)

# --- demographics, CPS, % of 20th-day enrollment ---
_LABEL_BREAK = "CPS relabelled this group between SY2025-26 and SY2026-27 (district share fell 71.8% -> 68.9%); comparability unconfirmed, so no deltas across it."
for key, label in [("white", "White"), ("black", "Black / African American"), ("latinx", "Latino"),
                   ("asian", "Asian"), ("multiracial", "Multiracial"), ("native", "Native American / Alaskan"),
                   ("pacific", "Hawaiian / Pacific Islander"), ("mena", "Middle Eastern / North African"),
                   ("race_na", "Race not available")]:
    REGISTRY[f"pct_{key}"] = M(f"{label} (% of enrollment)", "pct", "demographics", "CPS-DEM2", CPS_YEARS)
REGISTRY["pct_el"] = M("English learners (%)", "pct", "demographics", "CPS-DEM1", CPS_YEARS)
REGISTRY["pct_iep"] = M("Students with IEPs / disabilities (%)", "pct", "demographics", "CPS-DEM1", CPS_YEARS,
                        breaks=["2026-27"], note=_LABEL_BREAK)
REGISTRY["pct_low_income"] = M("Low income / economically disadvantaged (%)", "pct", "demographics", "CPS-DEM1", CPS_YEARS,
                               breaks=["2026-27"], note=_LABEL_BREAK)
REGISTRY["pct_homeless"] = M("Students in temporary living situations (%)", "pct", "demographics", "ISBE-RC", ["2024-25"],
                             note="ISBE only; CPS files do not carry this.")
REGISTRY["pct_youth_in_care"] = M("Youth in care (%)", "pct", "demographics", "ISBE-RC", ["2024-25"])

# --- spending ---
REGISTRY["ppe_total"] = M("Per-pupil expenditure, total ($)", "usd", "spending", "ISBE-RC", ["2024-25"],
                          note="Includes centrally paid costs; the comparable measure. Fiscal year to be confirmed.")
REGISTRY["ppe_site"] = M("Per-pupil expenditure, site-level ($)", "usd", "spending", "ISBE-RC", ["2024-25"])
REGISTRY["ppe_central"] = M("Per-pupil expenditure, district-centralized ($)", "usd", "spending", "ISBE-RC", ["2024-25"])
REGISTRY["cps_budget_fy27"] = M("CPS FY27 proposed budget ($)", "usd", "spending", "CPS-BUD-BI", ["2026-27"],
                                note="Proposed, not spent. Excludes some centrally paid costs.")
REGISTRY["cps_budget_fy26_projected"] = M("CPS FY26 projected expenditures ($)", "usd", "spending", "CPS-BUD-BI", ["2025-26"],
                                          note="Projection as of July 2026.")
REGISTRY["cps_budget_fy26_adopted"] = M("CPS FY26 adopted budget ($)", "usd", "spending", "CPS-BUD-BI", ["2025-26"])
REGISTRY["cps_budget_per_pupil"] = M("CPS FY27 budget per pupil ($)", "usd", "spending", "CPS-BUD-BI", ["2026-27"],
                                     note="FY27 proposed budget / SY2026-27 20th-day enrollment.")
REGISTRY["cps_positions_fy27"] = M("CPS FY27 proposed positions (FTE)", "count", "spending", "CPS-BUD-BI", ["2026-27"])

# --- outcomes: ISBE, all school years carried ---
for mid, label, unit, extra in [
    ("attendance_rate", "Student attendance rate (%)", "pct", {}),
    ("chronic_absent", "Chronic absenteeism (%)", "pct", {}),
    ("grad_4yr", "4-year graduation rate (%)", "pct", {}),
    ("ninth_on_track", "Freshman on-track (%)", "pct", {}),
    ("postsec_12mo", "Graduates enrolled in postsecondary within 12 months (%)", "pct", {}),
    ("isbe_enrollment", "ISBE enrollment (count)", "count", {}),
]:
    REGISTRY[mid] = M(label, unit, "outcomes" if mid != "isbe_enrollment" else "enrollment", "ISBE-RC", ISBE_YEARS, **extra)

_CUT = "ISBE lowered proficiency cut scores in 2025 and did not re-score earlier years: not comparable across 2024-25."
REGISTRY["iar_ela_prof"] = M("IAR ELA proficiency (%)", "pct", "outcomes", "ISBE-RC", ["2023-24", "2024-25"],
                             breaks=["2024-25"], note=_CUT)
REGISTRY["iar_math_prof"] = M("IAR math proficiency (%)", "pct", "outcomes", "ISBE-RC", ["2023-24", "2024-25"],
                              breaks=["2024-25"], note=_CUT)
REGISTRY["ela_growth"] = M("ELA growth percentile", "percentile", "outcomes", "ISBE-RC", ["2023-24", "2024-25"], breaks=["2024-25"])
REGISTRY["math_growth"] = M("Math growth percentile", "percentile", "outcomes", "ISBE-RC", ["2023-24", "2024-25"], breaks=["2024-25"])

_HS = "Grade 11 state test: SAT through SY2023-24, ACT from SY2024-25 with new cut scores. Never compare across the break."
REGISTRY["sat_ela_prof"] = M("SAT ELA proficiency (%)", "pct", "outcomes", "ISBE-RC", ["2022-23", "2023-24"],
                             note="2022-23 is derived as Level 3 % + Level 4 %. " + _HS)
REGISTRY["sat_math_prof"] = M("SAT math proficiency (%)", "pct", "outcomes", "ISBE-RC", ["2022-23", "2023-24"],
                              note="2022-23 is derived as Level 3 % + Level 4 %. " + _HS)
REGISTRY["sat_ela_avg"] = M("SAT reading average score", "score", "outcomes", "ISBE-RC", ["2022-23", "2023-24"], note=_HS)
REGISTRY["sat_math_avg"] = M("SAT math average score", "score", "outcomes", "ISBE-RC", ["2022-23", "2023-24"], note=_HS)
REGISTRY["sat_ela_part"] = M("SAT ELA participation (%)", "pct", "outcomes", "ISBE-RC", ["2022-23", "2023-24"])
REGISTRY["sat_math_part"] = M("SAT math participation (%)", "pct", "outcomes", "ISBE-RC", ["2022-23", "2023-24"])
REGISTRY["act_ela_prof"] = M("ACT ELA proficiency, grade 11 (%)", "pct", "outcomes", "ISBE-RC", ["2024-25"], note=_HS)
REGISTRY["act_math_prof"] = M("ACT math proficiency, grade 11 (%)", "pct", "outcomes", "ISBE-RC", ["2024-25"], note=_HS)
REGISTRY["act_ela_avg"] = M("ACT ELA average score, grade 11", "score", "outcomes", "ISBE-RC", ["2024-25"],
                            note=_HS + " ISBE's 'ELA' column: ACT ELA composite vs English subscore unconfirmed.")
REGISTRY["act_math_avg"] = M("ACT math average score, grade 11", "score", "outcomes", "ISBE-RC", ["2024-25"], note=_HS)
REGISTRY["act_ela_part"] = M("ACT ELA participation, grade 11 (%)", "pct", "outcomes", "ISBE-RC", ["2024-25"])
REGISTRY["act_math_part"] = M("ACT math participation, grade 11 (%)", "pct", "outcomes", "ISBE-RC", ["2024-25"])
REGISTRY["act_ela_growth"] = M("ACT ELA growth percentile, grade 11", "percentile", "outcomes", "ISBE-RC", ["2024-25"],
                               note="2025 only; method across the PSAT10-to-ACT change unconfirmed.")
REGISTRY["act_math_growth"] = M("ACT math growth percentile, grade 11", "percentile", "outcomes", "ISBE-RC", ["2024-25"])

for dom, label in [("leaders", "Effective leaders"), ("teachers", "Collaborative teachers"),
                   ("families", "Involved families"), ("environment", "Supportive environment")]:
    REGISTRY[f"fe_{dom}"] = M(f"5Essentials: {label} (level 1-5)", "level", "outcomes", "ISBE-RC", ["2024-25"])

_GAP = ("Average score minus ACT's national College Readiness Benchmark, in points (ELA 20, math 22). SAT years are ESTIMATES: "
        "school mean SAT scores converted with the official 2018 ACT-SAT concordance (ERW -> English+Reading / 2; SAT Math -> ACT Math). "
        "Comparable across years as an estimate; it is not a share of students.")
REGISTRY["g11_ela_gap"] = M("Grade 11 ELA score vs ACT benchmark (points, estimate)", "points", "outcomes", "ISBE-RC",
                            ["2022-23", "2023-24", "2024-25"], note=_GAP)
REGISTRY["g11_math_gap"] = M("Grade 11 math score vs ACT benchmark (points, estimate)", "points", "outcomes", "ISBE-RC",
                             ["2022-23", "2023-24", "2024-25"], note=_GAP)
for _k in ("g11_ela_gap", "g11_math_gap"):
    REGISTRY[_k]["estimated_years"] = ["2022-23", "2023-24"]
    REGISTRY[_k]["benchmark"] = 20 if "ela" in _k else 22

SOURCES = {
    "CONCORD": {"name": "ACT / College Board ACT-SAT concordance tables (2018)", "page": "https://www.act.org/content/dam/act/unsecured/documents/ACT-SAT-Concordance-Tables.pdf"},
    "CPS-MEM": {"name": "CPS 20th-day membership (Schools by Grade)", "page": "https://www.cps.edu/about/district-data/demographics/"},
    "CPS-DEM1": {"name": "CPS 20th-day English learners / IEP / low income", "page": "https://www.cps.edu/about/district-data/demographics/"},
    "CPS-DEM2": {"name": "CPS 20th-day racial/ethnic", "page": "https://www.cps.edu/about/district-data/demographics/"},
    "CPS-BUD-BI": {"name": "CPS FY27 budget interactive-report line-item export (manual download)", "page": "https://www.cps.edu/about/finance/budget/budget-2027/"},
    "CHI-LOC": {"name": "Chicago Data Portal: CPS School Locations (SY2025-26)", "page": "https://data.cityofchicago.org/resource/pb6d-zzuh"},
    "CHI-PROF": {"name": "Chicago Data Portal: CPS School Profile Information (SY2024-25)", "page": "https://data.cityofchicago.org/resource/3dhs-m3w4"},
    "CHI-CA": {"name": "Chicago Data Portal: community areas", "page": "https://data.cityofchicago.org/resource/igwz-8jzy"},
    "CHI-WARD": {"name": "Chicago Data Portal: wards (2023-)", "page": "https://data.cityofchicago.org/resource/p293-wvbd"},
    "SUBDIST": {"name": "Illinois Senate: CPS Board subdistrict map ERSB_20_Sub_District_Map_FA1_SB_15", "page": "https://www.ilsenateredistricting.com/"},
    "ISBE-RC": {"name": "Illinois Report Card public data sets (2023, 2024, 2025)", "page": "https://www.isbe.net/Pages/Illinois-State-Report-Card-Data.aspx"},
    "XWALK": {"name": "CPS ID to ISBE RCDTS crosswalk (project-built, crosswalk.csv)", "page": ""},
}
