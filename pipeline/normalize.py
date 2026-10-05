"""Stage 2: join every source onto the SY2026-27 roster and build one record per school.

Value model (school["m"]): metric -> {school_year: value}
  number     a real value
  "*"        suppressed (ISBE marker, or our minimum-n rule for CPS demographics)
  (absent)   no data. Never 0 unless the source says 0.
"""
import csv
import datetime
import json
import statistics
from collections import Counter, defaultdict

from . import concordance, cps, geo, isbe
from . import program as program_mod
from .common import CPS_YEARS, RAW, ROOT, ROSTER_YEAR, SUPPRESSED
from .metrics import ISBE_YEARS, REGISTRY, SOURCES

# --- display rules (documented in the validation report and NOTES) ---
DEMO_LOW_N_FLAG = 30       # flagged low_n (label only; CPS values are published as given, never hidden)
BUDGET_PP_LOW, BUDGET_PP_HIGH = 5000, 60000   # per-pupil budget outlier flags (flag, never trim)

HS_ONLY = ["grad_4yr", "grad_5yr", "ninth_on_track", "postsec_12mo", "sat_ela_prof", "sat_math_prof", "sat_ela_avg",
           "sat_math_avg", "sat_ela_part", "sat_math_part", "act_ela_prof", "act_math_prof", "act_ela_avg",
           "act_math_avg", "act_ela_part", "act_math_part", "act_ela_growth", "act_math_growth"]
IAR_ONLY = ["iar_ela_prof", "iar_math_prof", "ela_growth", "math_growth"]

# Per-school ISBE caveats from crosswalk_notes.md / NOTES.md. Shown beside the ISBE numbers.
ISBE_CAVEATS = {
    "400086": "isbe_partial_campus",        # Urban Prep: 2025 state row is Englewood only
    "400115": "isbe_k12_shared",            # Catalyst Maria: state row covers K-12 incl. 400182
    "400182": "no_separate_state_data",
    "400066": "isbe_match_by_address",      # Perspectives Math & Sci: match rests on address
}
for _id in ("610602", "610603", "610604", "610605", "610606"):
    ISBE_CAVEATS[_id] = "isbe_predecessor_charter"
ISBE_CAVEATS["610607"] = "isbe_predecessor_contract"

# CPS budget unit U66433 covers both Catalyst Maria campuses ($22.1M / 564 students = $39k per pupil, but ~$20k on the
# combined 1,105). Per-pupil uses combined enrollment on both schools, flagged; the budget total stays on 400115 only.
BUDGET_K12_SHARED = {"400115": ("400115", "400182"), "400182": ("400115", "400182")}

FLAG_TEXT = {
    "budget_k12_shared": "The CPS budget unit covers both Catalyst Maria campuses (K-12); per-pupil uses their combined enrollment.",
    "isbe_predecessor_charter": "State figures describe the charter that closed, not today's district-run school.",
    "isbe_predecessor_contract": "State figures describe the contract-era school.",
    "isbe_partial_campus": "State figures cover only part of today's combined school.",
    "isbe_k12_shared": "State figures cover the K-12 school, including Catalyst Maria HS.",
    "no_separate_state_data": "The state reports this school under 400115; no separate state data.",
    "isbe_match_by_address": "State record matched by campus address; confirm.",
    "coords_from_predecessor": "Coordinates carried over from the predecessor charter at the same site.",
    "history_from_predecessor": "Earlier-year enrollment and demographics come from the predecessor charter ID.",
    "low_n": f"Fewer than {DEMO_LOW_N_FLAG} students: percentages swing on a handful of students.",
    "budget_pp_outlier": "CPS budget per pupil is unusually low or high (small or specialised program).",
    "budget_not_comparable": "Charter, contract, ALOP and SAFE budgets are not comparable to district-run schools.",
    "budget_zero_unit": "The CPS budget unit for this school shows $0; shown as no data.",
    "no_budget_unit": "No CPS budget unit found.",
    "ppe_outlier": "ISBE per-pupil expenditure is a statistical outlier for Chicago schools.",
    "community_area_mismatch": "CPS community area differs from the area containing the coordinates.",
}


def read_csv(name):
    with open(ROOT / name, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def derive_type(governance, school_type):
    g = governance.lower()
    if g == "charter":
        return "charter"
    if g in ("contract", "alop", "safe"):
        return "contract"
    if school_type.lower() == "options":
        return "options"
    return "district"


def grade_span(grades):
    """Lowest-highest enrolled grade label, and ES / HS / combo band."""
    order = cps.GRADE_ORDER
    present = [g for g in order if grades.get(g, 0) > 0]
    if not present:
        return "", ""
    lo, hi = present[0], present[-1]
    top = order.index(hi)
    first_hs = order.index("9")
    if order.index(lo) >= first_hs:
        band = "HS"
    elif top >= first_hs:
        band = "combo"
    else:
        band = "ES"
    span = lo if lo == hi else f"{lo}-{hi}"
    return span, band


def r1(x):
    return round(x, 1)


def load_all():
    """Read every source once. Returns a dict of raw tables used by build()."""
    t = {"mem": {}, "dem1": {}, "dem2": {}, "labels": {}}
    for y in CPS_YEARS:
        t["mem"][y] = cps.read_membership(y)
        t["dem1"][y], t["labels"][y] = cps.read_lepiep(y)
        t["dem2"][y] = cps.read_race(y)
    t["isbe"] = {isbe.RC_YEAR[y]: isbe.read_year(y) for y in isbe.RC_YEAR}
    t["isbe_names"] = isbe.read_names(2025)
    t["isbe_revision"] = {isbe.RC_YEAR[y]: isbe.revision(y) for y in isbe.RC_YEAR}
    t["loc"] = {r["school_id"]: r for r in json.load(open(RAW / "chi_loc.json"))}
    t["prof"] = {r["school_id"]: r for r in json.load(open(RAW / "chi_prof.json"))}
    t["crosswalk"] = {r["school_id"]: r for r in read_csv("crosswalk.csv")}
    t["programs"] = program_mod.load_overrides()
    t["lineage"] = {r["school_id"]: r for r in read_csv("lineage.csv")}
    t["budget"] = {r["school_id"]: r for r in read_csv("budget_units.csv")}
    funds = defaultdict(dict)
    for r in read_csv("budget_unit_funds.csv"):
        funds[r["school_id"]][r["fund"]] = float(r["fy27_proposed_budget"])
    t["funds"] = funds
    t["concordance"] = concordance.load()
    t["layers"] = {"sub": geo.load_subdistricts(), "ca": geo.load_community_areas(), "ward": geo.load_wards()}
    t["manifest"] = json.load(open(RAW / "MANIFEST.json"))
    return t


def series_source(t, table, sid, year):
    """Row for school `sid` in a per-year CPS table, falling back to a converted school's predecessor."""
    rows = t[table][year]
    if sid in rows:
        return rows[sid], None
    pred = t["lineage"].get(sid, {}).get("predecessor_id")
    if pred and pred in rows:
        return rows[pred], pred
    return None, None


def build(t):
    roster = t["mem"][ROSTER_YEAR]
    schools = []
    problems = {"unmatched_loc": [], "coords_from_pred": [], "subdistrict_none": [], "ca_mismatch": [],
                "hs_star_dropped": 0, "iar_star_dropped": 0}
    fund_totals = Counter()
    for sid_funds in t["funds"].values():
        for k, v in sid_funds.items():
            fund_totals[k] += v
    fund_code = {name: f"f{i + 1:02d}" for i, (name, _) in enumerate(fund_totals.most_common())}

    ppe_vals = [v for rc in t["isbe"]["2024-25"].values() for k, v in rc.items() if k == "ppe_total" and v != SUPPRESSED]
    q1, _, q3 = statistics.quantiles(ppe_vals, n=4) if len(ppe_vals) > 3 else (0, 0, 0)
    ppe_lo, ppe_hi = q1 - 3 * (q3 - q1), q3 + 3 * (q3 - q1)

    for sid, mem in sorted(roster.items()):
        flags = []
        m = defaultdict(dict)
        pred = t["lineage"].get(sid, {}).get("predecessor_id")
        hist_years = []

        # ---------- identity ----------
        s = {"id": sid, "name": mem["name"]}
        prof = t["prof"].get(sid) or (t["prof"].get(pred) if pred else None)
        if prof and prof.get("long_name") and sid in t["prof"]:
            s["long_name"] = prof["long_name"]
        xw = t["crosswalk"].get(sid)
        s["rcdts"] = xw["rcdts"] if xw and xw["rcdts"] else None
        s["type"] = derive_type(mem["governance"], mem["school_type"])
        s["governance"] = mem["governance"]
        s["network"] = mem["network"]
        s["school_type"] = mem["school_type"]
        program_mod.assign(s, mem["school_type"], t["programs"], t["prof"].get(sid))
        s["grades_served"], s["band"] = grade_span(mem["grades"])
        s["grades"] = {g: n for g, n in mem["grades"].items() if n > 0}
        if pred:
            s["predecessor"] = pred

        # ---------- location ----------
        loc = t["loc"].get(sid)
        if loc is None and pred and pred in t["loc"]:
            loc = t["loc"][pred]
            flags.append("coords_from_predecessor")
            problems["coords_from_pred"].append(sid)
        if loc is None:
            problems["unmatched_loc"].append(sid)
            s["address"], s["lat"], s["lon"] = None, None, None
            s["subdistrict"], s["ward"] = None, None
        else:
            s["address"] = loc["address"].strip()
            s["lat"], s["lon"] = round(float(loc["lat"]), 5), round(float(loc["long"]), 5)
            hits = {k: t["layers"][k].lookup(s["lon"], s["lat"]) for k in ("sub", "ca", "ward")}
            s["subdistrict"] = hits["sub"][0] if len(hits["sub"]) == 1 else None
            s["ward"] = int(hits["ward"][0]) if len(hits["ward"]) == 1 else None
            if len(hits["sub"]) != 1:
                problems["subdistrict_none"].append((sid, len(hits["sub"])))
            if len(hits["ca"]) == 1 and hits["ca"][0].upper() != mem["community_area"].upper():
                problems["ca_mismatch"].append((sid, mem["community_area"], hits["ca"][0]))
                flags.append("community_area_mismatch")
        s["community_area"] = mem["community_area"]

        # ---------- enrollment + CPS demographics, three school years ----------
        grades_by_year = {}
        for y in CPS_YEARS:
            row, via = series_source(t, "mem", sid, y)
            if row is None:
                continue
            if via:
                hist_years.append(y)
            total = row["total"]
            m["enrollment"][y] = total
            grades_by_year[y] = row["grades"]
            d1, _ = series_source(t, "dem1", sid, y)
            d2, _ = series_source(t, "dem2", sid, y)

            def pct(v):
                if v is None:
                    return None
                return r1(v)

            for key in ("el", "iep", "li"):
                mid = {"el": "pct_el", "iep": "pct_iep", "li": "pct_low_income"}[key]
                if d1 and d1.get(key + "_pct") is not None:
                    m[mid][y] = pct(d1[key + "_pct"])
            for key in ("white", "black", "latinx", "asian", "multiracial", "native", "pacific", "mena", "race_na"):
                if d2 and d2.get(key + "_pct") is not None:
                    m["pct_" + key][y] = pct(d2[key + "_pct"])
            if y == ROSTER_YEAR and total < DEMO_LOW_N_FLAG:
                flags.append("low_n")
        if hist_years:
            flags.append("history_from_predecessor")
            s["history_from_predecessor"] = hist_years
        # 3-year enrollment change, first to last year carried
        ys = [y for y in CPS_YEARS if y in m["enrollment"]]
        if len(ys) >= 2:
            a, b = m["enrollment"][ys[0]], m["enrollment"][ys[-1]]
            s["enrollment_change"] = {"from": ys[0], "to": ys[-1], "count": b - a,
                                      "pct": round((b - a) / a * 100, 1) if a else None}

        # ---------- ISBE ----------
        has_hs = any(mem["grades"].get(g, 0) for g in ("9", "10", "11", "12")) or any(
            gy.get(g, 0) for gy in grades_by_year.values() for g in ("9", "10", "11", "12"))
        has_iar = any(gy.get(g, 0) for gy in grades_by_year.values() for g in ("3", "4", "5", "6", "7", "8"))
        if s["rcdts"]:
            for y in ISBE_YEARS:
                rec = t["isbe"][y].get(s["rcdts"])
                if not rec:
                    continue
                for metric, v in rec.items():
                    # '*' on a metric the school cannot have (e.g. SAT at a K-8) is "not applicable", not "suppressed"
                    if v == SUPPRESSED and metric in HS_ONLY and not has_hs:
                        problems["hs_star_dropped"] += 1
                        continue
                    if v == SUPPRESSED and metric in IAR_ONLY and not has_iar:
                        problems["iar_star_dropped"] += 1
                        continue
                    if metric not in REGISTRY:
                        raise KeyError(f"ISBE metric {metric} missing from REGISTRY")
                    m[metric][y] = v if v == SUPPRESSED else (round(v) if REGISTRY[metric]["unit"] in ("usd", "count") else round(v, 2))
            ppe = m.get("ppe_total", {}).get("2024-25")
            if isinstance(ppe, float) or isinstance(ppe, int):
                if ppe < ppe_lo or ppe > ppe_hi:
                    flags.append("ppe_outlier")
        # grade 11 score vs ACT benchmark: SAT years converted with the concordance (estimates), ACT year direct
        for sub_, bench in (("ela", concordance.BENCH["ela"]), ("math", concordance.BENCH["math"])):
            for y in ("2022-23", "2023-24"):
                v = m.get(f"sat_{sub_}_avg", {}).get(y)
                if v == SUPPRESSED:
                    m[f"g11_{sub_}_gap"][y] = SUPPRESSED
                elif isinstance(v, (int, float)):
                    m[f"g11_{sub_}_gap"][y] = round(concordance.to_act(t["concordance"][sub_], v) - bench, 1)
            v = m.get(f"act_{sub_}_avg", {}).get("2024-25")
            if v == SUPPRESSED:
                m[f"g11_{sub_}_gap"]["2024-25"] = SUPPRESSED
            elif isinstance(v, (int, float)):
                m[f"g11_{sub_}_gap"]["2024-25"] = round(v - bench, 1)
        if sid in ISBE_CAVEATS:
            flags.append(ISBE_CAVEATS[sid])

        # ---------- CPS budget ----------
        b = t["budget"].get(sid)
        if b and b["budget_units"]:
            s["budget_units"] = b["budget_units"]
            fy27 = float(b["fy27_proposed_budget"]) if b["fy27_proposed_budget"] else None
            fy26a = float(b["fy26_adopted_budget"]) if b["fy26_adopted_budget"] else None
            fy26p = float(b["fy26_projected_expenditures"]) if b["fy26_projected_expenditures"] else None
            if fy27:
                m["cps_budget_fy27"][ROSTER_YEAR] = round(fy27)
                total = m["enrollment"].get(ROSTER_YEAR)
                if sid in BUDGET_K12_SHARED:
                    flags.append("budget_k12_shared")
                    total = sum(roster[x]["total"] for x in BUDGET_K12_SHARED[sid])
                if total:
                    pp = round(fy27 / total)
                    m["cps_budget_per_pupil"][ROSTER_YEAR] = pp
                    if pp < BUDGET_PP_LOW or pp > BUDGET_PP_HIGH:
                        flags.append("budget_pp_outlier")
                if b["fy27_proposed_positions"]:
                    m["cps_positions_fy27"][ROSTER_YEAR] = round(float(b["fy27_proposed_positions"]), 1)
            else:
                flags.append("budget_zero_unit")
            if fy26a:
                m["cps_budget_fy26_adopted"]["2025-26"] = round(fy26a)
            if fy26p:
                m["cps_budget_fy26_projected"]["2025-26"] = round(fy26p)
            if t["funds"].get(sid):
                s["budget_funds"] = {fund_code[k]: round(v) for k, v in
                                     sorted(t["funds"][sid].items(), key=lambda kv: -kv[1]) if abs(v) >= 0.5}
        elif sid not in BUDGET_K12_SHARED:
            flags.append("no_budget_unit")
        if sid in BUDGET_K12_SHARED and not (b and b["budget_units"]):
            # no unit of its own: per-pupil comes from the shared unit on the partner campus
            partner = next(x for x in BUDGET_K12_SHARED[sid] if x != sid)
            pb = t["budget"].get(partner, {})
            if pb.get("fy27_proposed_budget"):
                total = sum(roster[x]["total"] for x in BUDGET_K12_SHARED[sid])
                m["cps_budget_per_pupil"][ROSTER_YEAR] = round(float(pb["fy27_proposed_budget"]) / total)
                flags.append("budget_k12_shared")
        if s["type"] != "district":
            flags.append("budget_not_comparable")

        s["m"] = {k: v for k, v in m.items() if v}
        s["flags"] = sorted(set(flags))
        s["_grades_by_year"] = grades_by_year
        schools.append(s)

    meta = build_meta(t, fund_code, problems, (ppe_lo, ppe_hi))
    return schools, meta, problems


def build_meta(t, fund_code, problems, ppe_fence):
    man = t["manifest"]

    def files(prefix):
        return {k: {"retrieved": v["retrieved"], "sha256": v["sha256"][:16], "url": v["url"]}
                for k, v in sorted(man.items()) if k.startswith(prefix)}

    src = {k: dict(v) for k, v in SOURCES.items()}
    prefix = {"CPS-MEM": "cps_mem", "CPS-DEM1": "cps_lepiep", "CPS-DEM2": "cps_race", "CHI-LOC": "chi_loc",
              "CHI-PROF": "chi_prof", "CHI-CA": "chi_community_areas", "CHI-WARD": "chi_wards",
              "SUBDIST": "subdistricts", "CONCORD": "act_sat_concordance", "ISBE-RC": "isbe_rc", "CPS-BUD-BI": "fy27_bi"}
    for k, p in prefix.items():
        src[k]["files"] = files(p)
    src["ISBE-RC"]["revisions"] = t["isbe_revision"]
    src["XWALK"]["files"] = {"crosswalk.csv": {"retrieved": "2026-09-30", "note": "project-built; see crosswalk_notes.md"}}
    return {
        "schema": 1,
        "generated": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "roster_year": ROSTER_YEAR,
        "cps_years": CPS_YEARS,
        "isbe_years": ISBE_YEARS,
        "value_model": "m[metric][school_year]: number, \"*\" = suppressed, absent = no data. Percentages 0-100.",
        "rules": {
            "demo_low_n_flag": DEMO_LOW_N_FLAG,
            "budget_per_pupil_outlier": [BUDGET_PP_LOW, BUDGET_PP_HIGH],
            "ppe_outlier_fence_3xIQR": [round(ppe_fence[0]), round(ppe_fence[1])],
            "isbe_star_on_inapplicable_metric": "dropped to no-data (HS metrics at schools with no grade 9-12, IAR at schools with no grade 3-8)",
        },
        "sources": src,
        "metrics": REGISTRY,
        "flags": FLAG_TEXT,
        **program_mod.meta(),
        "funds": {code: name for name, code in fund_code.items()},
    }
