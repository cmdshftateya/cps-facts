"""Stage 3: validation. Checks are 'fail' (stops the build) or 'warn' (reported only).

validate() returns a report dict; report["failed"] is the list of failing check ids.
"""
import statistics
from collections import Counter

from . import program as program_mod
from .common import CPS_YEARS, ROSTER_YEAR, SUPPRESSED
from .metrics import REGISTRY

# thresholds that fail the build
MIN_ISBE_JOIN = 0.95      # share of roster schools with an ISBE RCDTS (Phase 0 result: 95.9%)
MIN_BUDGET_JOIN = 0.99    # share of roster schools with a CPS budget unit (Phase 0: 99.7%)
RACE_SUM_RANGE = (99.0, 101.0)   # race shares should add to 100 within rounding
VALUE_RANGES = {"pct": (0, 100), "percentile": (0, 100), "level": (1, 5)}


class Report:
    def __init__(self):
        self.checks = []

    def add(self, cid, severity, title, bad, detail="", examples=None, total=None):
        status = "pass" if not bad else ("FAIL" if severity == "fail" else "warn")
        self.checks.append({"id": cid, "severity": severity, "status": status, "title": title,
                            "count": len(bad) if hasattr(bad, "__len__") else int(bad),
                            "total": total, "detail": detail,
                            "examples": [str(e) for e in (examples if examples is not None else bad)][:12]
                            if bad else []})


def _num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def validate(schools, meta, t, problems):
    R = Report()
    n = len(schools)
    ids = [s["id"] for s in schools]

    # ----- structure -----
    dup = [i for i, c in Counter(ids).items() if c > 1]
    R.add("dup_ids", "fail", "Duplicate school IDs", dup, total=n)
    rc = [s["rcdts"] for s in schools if s["rcdts"]]
    dup_rc = [i for i, c in Counter(rc).items() if c > 1]
    R.add("dup_rcdts", "fail", "One RCDTS assigned to more than one school", dup_rc, total=len(rc))
    R.add("missing_fields", "fail", "Schools missing name, type or governance",
          [s["id"] for s in schools if not (s["name"] and s["type"] and s["governance"])], total=n)
    R.add("program_context", "fail", "Program overrides or program sentences incomplete (unknown school or program, no source URL, no sentence)",
          program_mod.problems(schools, t["programs"]), total=len(t["programs"]))
    roster_total = sum(s["m"]["enrollment"][ROSTER_YEAR] for s in schools)
    R.add("roster_total", "fail", "Roster enrollment sum differs from the CPS file's district total",
          [] if roster_total == _district_total(t) else [f"roster {roster_total} vs district {_district_total(t)}"],
          detail=f"Roster sum {roster_total:,}.")

    # ----- geography -----
    R.add("missing_coords", "fail", "Schools without coordinates", problems["unmatched_loc"], total=n)
    R.add("missing_subdistrict", "fail", "Schools not in exactly one Board subdistrict",
          [s["id"] for s in schools if not s.get("subdistrict")], total=n)
    R.add("missing_ward", "fail", "Schools not in exactly one ward", [s["id"] for s in schools if not s.get("ward")], total=n)
    R.add("coords_predecessor", "warn", "Coordinates carried over from a predecessor charter (same-site inference)",
          problems["coords_from_pred"], detail="CPS pages describe the conversions as same-building; not verified per site.")
    R.add("community_area_mismatch", "warn", "CPS community area differs from the area containing the coordinates",
          problems["ca_mismatch"], total=n)
    out_of_city = [s["id"] for s in schools if s.get("lat") and not (41.6 < s["lat"] < 42.1 and -87.95 < s["lon"] < -87.5)]
    R.add("coords_outside_chicago", "fail", "Coordinates outside Chicago's bounding box", out_of_city, total=n)

    # ----- joins -----
    with_rc = [s for s in schools if s["rcdts"]]
    R.add("isbe_join", "fail", f"ISBE join below {MIN_ISBE_JOIN:.0%}",
          [] if len(with_rc) / n >= MIN_ISBE_JOIN else [f"{len(with_rc)}/{n}"],
          detail=f"{len(with_rc)} of {n} schools ({len(with_rc) / n:.1%}) have an RCDTS.", total=n)
    no_rc = [f'{s["id"]} {s["name"]}' for s in schools if not s["rcdts"]]
    R.add("isbe_unmatched", "warn", "Schools with no ISBE record (CPS data only)", no_rc, total=n)
    in_isbe = t["isbe"]["2024-25"]
    R.add("rcdts_not_in_isbe", "fail", "Crosswalk RCDTS not found in the 2025 Report Card",
          [f'{s["id"]} {s["rcdts"]}' for s in with_rc if s["rcdts"] not in in_isbe], total=len(with_rc))
    R.add("crosswalk_coverage", "fail", "Roster schools absent from crosswalk.csv",
          [s["id"] for s in schools if s["id"] not in t["crosswalk"]], total=n)
    low_conf = [s["id"] for s in schools if s["rcdts"] and t["crosswalk"][s["id"]]["confidence"] == "low"
                and any(REGISTRY[m]["source"] == "ISBE-RC" for m in s["m"])]
    R.add("low_confidence_ships_isbe", "fail", "Low-confidence crosswalk match ships ISBE values", low_conf)
    R.add("medium_confidence", "warn", "Medium-confidence crosswalk matches (shipped with a caveat flag)",
          [f'{s["id"]} {s["name"]}' for s in with_rc if t["crosswalk"][s["id"]]["confidence"] == "medium"])
    with_budget = [s for s in schools if "cps_budget_fy27" in s["m"]]
    bj = [s for s in schools if s.get("budget_units")]
    R.add("budget_join", "fail", f"CPS budget join below {MIN_BUDGET_JOIN:.0%}",
          [] if len(bj) / n >= MIN_BUDGET_JOIN else [f"{len(bj)}/{n}"],
          detail=f"{len(bj)} of {n} schools have a budget unit; {len(with_budget)} have a nonzero FY27 budget.", total=n)
    R.add("budget_missing", "warn", "Schools with no usable FY27 budget",
          [f'{s["id"]} {s["name"]}' for s in schools if "cps_budget_fy27" not in s["m"]])
    # fund breakdown must add up to the unit total
    bad_funds = []
    for s in with_budget:
        f = sum(s.get("budget_funds", {}).values())
        if abs(f - s["m"]["cps_budget_fy27"][ROSTER_YEAR]) > max(5, 0.001 * s["m"]["cps_budget_fy27"][ROSTER_YEAR]):
            bad_funds.append(f'{s["id"]} funds {f:,.0f} vs total {s["m"]["cps_budget_fy27"][ROSTER_YEAR]:,.0f}')
    R.add("budget_fund_sum", "fail", "By-fund budget does not add up to the school total", bad_funds, total=len(with_budget))
    pred_bad = [s["id"] for s in schools if s.get("predecessor") and s["predecessor"] not in t["mem"]["2025-26"]
                and s["predecessor"] not in t["mem"]["2024-25"]]
    R.add("predecessor_missing", "fail", "Predecessor ID not found in any earlier CPS file", pred_bad)

    # ----- CPS internal consistency -----
    tot_bad, grade_bad, race_bad, nopct = [], [], [], []
    for y in CPS_YEARS:
        mem, d1, d2 = t["mem"][y], t["dem1"][y], t["dem2"][y]
        for sid, r in mem.items():
            if sid not in d1 or sid not in d2:
                tot_bad.append(f"{y} {sid} missing from a demographics file")
                continue
            if not (r["total"] == int(d1[sid]["total"]) == int(d2[sid]["total"])):
                tot_bad.append(f'{y} {sid}: mem {r["total"]} / lepiep {d1[sid]["total"]} / race {d2[sid]["total"]}')
            if sum(r["grades"].values()) != r["total"]:
                grade_bad.append(f'{y} {sid}: grades {sum(r["grades"].values())} vs total {r["total"]}')
            if r["total"] >= 30:
                s_ = sum(v for k, v in d2[sid].items() if k.endswith("_pct") and _num(v))
                if not (RACE_SUM_RANGE[0] <= s_ <= RACE_SUM_RANGE[1]):
                    race_bad.append(f"{y} {sid}: race shares sum to {s_:.1f}")
    R.add("cps_totals_agree", "fail", "CPS membership / demographics totals disagree", tot_bad)
    R.add("cps_grade_sum", "fail", "Grade-level enrollment does not add up to the total", grade_bad)
    R.add("race_sum", "fail", "Race shares do not add to 100% (schools with 30+ students)", race_bad)
    retired = [sid for sid, r in t["dem2"]["2024-25"].items() if r.get("asian_pi_retired_n")]
    R.add("retired_race_category", "warn", "Students in the retired 'Asian/Pacific Islander' category (SY2024-25, not carried)",
          retired)

    # ----- value sanity -----
    unknown, range_bad, year_bad, zero_bad, type_bad = [], [], [], [], []
    for s in schools:
        for metric, series in s["m"].items():
            reg = REGISTRY.get(metric)
            if reg is None:
                unknown.append(metric)
                continue
            for y, v in series.items():
                if y not in reg["years"]:
                    year_bad.append(f"{s['id']} {metric} {y}")
                if v == SUPPRESSED:
                    continue
                if not _num(v):
                    type_bad.append(f"{s['id']} {metric} {y} = {v!r}")
                    continue
                lo_hi = VALUE_RANGES.get(reg["unit"])
                if lo_hi and not (lo_hi[0] <= v <= lo_hi[1]):
                    range_bad.append(f"{s['id']} {metric} {y} = {v}")
                if reg["unit"] == "usd" and v <= 0:
                    zero_bad.append(f"{s['id']} {metric} {y} = {v}")
                if reg["unit"] in ("score",) and v <= 0:
                    zero_bad.append(f"{s['id']} {metric} {y} = {v}")
    R.add("unknown_metric", "fail", "Metrics missing from the registry", sorted(set(unknown)))
    R.add("year_not_in_registry", "fail", "Values in a school year the registry does not list", year_bad)
    R.add("non_numeric_value", "fail", "Non-numeric, non-'*' values", type_bad)
    R.add("percent_range", "fail", "Percentages / percentiles / levels outside their valid range", range_bad)
    R.add("zero_dollars", "fail", "Zero or negative dollar/score values (should be no data)", zero_bad)

    # ----- cross-source reasonableness (warnings) -----
    diffs = []
    for s in schools:
        e1 = s["m"].get("enrollment", {}).get("2024-25")
        e2 = s["m"].get("isbe_enrollment", {}).get("2024-25")
        if e1 and _num(e2) and e2 > 0:
            diffs.append((abs(e1 - e2) / e2, s["id"], s["name"], e1, e2))
    big = sorted([d for d in diffs if d[0] > 0.25 and abs(d[3] - d[4]) >= 30], reverse=True)
    med = statistics.median(d[0] for d in diffs) if diffs else 0
    R.add("enrollment_vs_isbe", "warn", "CPS 20th-day vs ISBE enrollment (SY2024-25) differ by >25% and 30+ students",
          [f"{b[1]} {b[2]}: CPS {b[3]} vs ISBE {b[4]}" for b in big],
          detail=f"Median difference {med:.1%} across {len(diffs)} schools; the files use different snapshots.")
    R.add("budget_pp_outlier", "warn", "CPS budget per pupil outside the outlier band (flagged, not trimmed)",
          [f'{s["id"]} {s["name"]}: ${s["m"]["cps_budget_per_pupil"][ROSTER_YEAR]:,}' for s in schools if "budget_pp_outlier" in s["flags"]])
    R.add("ppe_outlier", "warn", "ISBE per-pupil expenditure outside 3xIQR fences (flagged, not trimmed)",
          [f'{s["id"]} {s["name"]}: ${s["m"]["ppe_total"]["2024-25"]:,}' for s in schools if "ppe_outlier" in s["flags"]])
    R.add("low_n", "warn", f"Schools under the low-n threshold in {ROSTER_YEAR}",
          [f'{s["id"]} {s["name"]} ({s["m"]["enrollment"][ROSTER_YEAR]})' for s in schools if "low_n" in s["flags"]])
    R.add("star_dropped", "warn", "ISBE '*' values dropped to no-data on metrics a school cannot have",
          [] if not (problems["hs_star_dropped"] + problems["iar_star_dropped"]) else [
              f'{problems["hs_star_dropped"]} high-school-only values at schools with no grade 9-12',
              f'{problems["iar_star_dropped"]} IAR values at schools with no grade 3-8'])

    # ----- grade 11 estimate sanity (method doc: converted 2024 vs ACT 2025 rank correlation, ship only if >= 0.85) -----
    for sub_ in ("ela", "math"):
        pairs = [(s["m"][f"g11_{sub_}_gap"]["2023-24"], s["m"][f"g11_{sub_}_gap"]["2024-25"]) for s in schools
                 if _num(s["m"].get(f"g11_{sub_}_gap", {}).get("2023-24")) and _num(s["m"].get(f"g11_{sub_}_gap", {}).get("2024-25"))]
        rho = _spearman([a for a, _ in pairs], [b for _, b in pairs]) if len(pairs) > 10 else 0
        R.add(f"g11_{sub_}_rank_corr", "warn", f"Grade 11 {sub_} estimate: SAT-2024 vs ACT-2025 rank correlation below 0.85",
              [] if rho >= 0.85 else [f"rho {rho:.3f} across {len(pairs)} schools"],
              detail=f"Spearman rho {rho:.3f} across {len(pairs)} schools.")

    # ----- coverage by metric (informational) -----
    coverage = {}
    for metric, reg in REGISTRY.items():
        row = {}
        for y in reg["years"]:
            vals = [s["m"].get(metric, {}).get(y) for s in schools]
            row[y] = {"value": sum(_num(v) for v in vals),
                      "suppressed": sum(v == SUPPRESSED for v in vals),
                      "none": sum(v is None for v in vals)}
        coverage[metric] = row

    failed = [c["id"] for c in R.checks if c["status"] == "FAIL"]
    return {"generated": meta["generated"], "schools": n, "failed": failed,
            "warnings": [c["id"] for c in R.checks if c["status"] == "warn"],
            "checks": R.checks, "coverage": coverage,
            "counts": {
                "by_type": dict(Counter(s["type"] for s in schools)),
                "by_band": dict(Counter(s["band"] for s in schools)),
                "with_isbe": len(with_rc), "with_budget": len(with_budget),
                "with_coords": sum(1 for s in schools if s.get("lat")),
                "with_subdistrict": sum(1 for s in schools if s.get("subdistrict")),
            }}


def _rank(v):
    order = sorted(range(len(v)), key=lambda i: v[i])
    r = [0.0] * len(v)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and v[order[j + 1]] == v[order[i]]:
            j += 1
        for k in range(i, j + 1):
            r[order[k]] = (i + j) / 2 + 1
        i = j + 1
    return r


def _spearman(a, b):
    ra, rb = _rank(a), _rank(b)
    ma, mb = statistics.mean(ra), statistics.mean(rb)
    num = sum((x - ma) * (y - mb) for x, y in zip(ra, rb))
    den = (sum((x - ma) ** 2 for x in ra) * sum((y - mb) ** 2 for y in rb)) ** 0.5
    return num / den if den else 0


def _district_total(t):
    from .common import RAW
    from .common import read_sheet
    rows = read_sheet(RAW / "cps_mem_2627.xlsx", "Schools by Grade")
    h = next(i for i, r in enumerate(rows[:6]) if "School ID" in [str(c).strip() for c in r])
    ti = [str(c).strip() for c in rows[h]].index("Total")
    for r in rows[h + 1:]:
        if "District Total" in str(r[1]):
            return int(float(r[ti]))
    raise ValueError("district total row not found")
