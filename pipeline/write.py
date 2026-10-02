"""Stage 4: write data/schools.json, data/schools.csv, data/school_values.csv and the validation report."""
import csv
import json

from .common import CPS_YEARS, DATA, ROSTER_YEAR, SUPPRESSED
from .cps import GRADE_ORDER
from .metrics import REGISTRY

FLAT_LATEST = [  # metrics written to schools.csv as latest value + year
    "pct_white", "pct_black", "pct_latinx", "pct_asian", "pct_multiracial", "pct_native", "pct_pacific", "pct_mena",
    "pct_race_na", "pct_low_income", "pct_el", "pct_iep", "pct_homeless", "pct_youth_in_care",
    "cps_budget_fy27", "cps_budget_per_pupil", "cps_budget_fy26_projected", "cps_positions_fy27",
    "ppe_total", "ppe_site", "ppe_central",
    "iar_ela_prof", "iar_math_prof", "ela_growth", "math_growth", "attendance_rate", "chronic_absent",
    "grad_4yr", "ninth_on_track", "postsec_12mo", "sat_ela_prof", "sat_math_prof", "act_ela_prof", "act_math_prof",
    "act_ela_avg", "act_math_avg", "fe_leaders", "fe_teachers", "fe_families", "fe_environment",
]


def _latest(series):
    """(year, value) for the newest year; suppressed counts as a value (it is a statement, not a gap)."""
    if not series:
        return "", ""
    y = max(series)
    return y, series[y]


def _file_for(meta, metric, year):
    """Retrieval date of the file behind (metric, year)."""
    reg = REGISTRY[metric]
    src = meta["sources"][reg["source"]]["files"]
    for name, info in src.items():
        if reg["source"] in ("CPS-MEM", "CPS-DEM1", "CPS-DEM2"):
            if name.endswith(f"_{year[2:4]}{year[-2:]}.xlsx"):
                return info["retrieved"]
        elif reg["source"] == "ISBE-RC":
            if name == f"isbe_rc_{int('20' + year[-2:])}.xlsx":
                return info["retrieved"]
        else:
            return info["retrieved"]
    return ""


def write_all(schools, meta, report):
    DATA.mkdir(exist_ok=True)
    clean = []
    for s in schools:
        c = {k: v for k, v in s.items() if not k.startswith("_")}
        clean.append(c)
    with open(DATA / "schools.json", "w", encoding="utf-8") as f:
        json.dump({"meta": meta, "schools": clean}, f, separators=(",", ":"), ensure_ascii=False)

    # --- schools.csv: one row per school ---
    cols = ["school_id", "name", "long_name", "type", "governance", "network", "school_type", "program", "grades_served", "band",
            "address", "lat", "lon", "subdistrict", "community_area", "ward", "rcdts", "predecessor_id",
            "enrollment_2026_27", "enrollment_2025_26", "enrollment_2024_25", "enrollment_change_count",
            "enrollment_change_pct"]
    for m in FLAT_LATEST:
        cols += [m, m + "_year"]
    cols += ["budget_units", "flags"]
    with open(DATA / "schools.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(cols)
        for s in clean:
            enr = s["m"].get("enrollment", {})
            ch = s.get("enrollment_change", {})
            row = [s["id"], s["name"], s.get("long_name", ""), s["type"], s["governance"], s["network"], s["school_type"],
                   s.get("program", ""),
                   s["grades_served"], s["band"], s["address"] or "", s["lat"] or "", s["lon"] or "",
                   s.get("subdistrict") or "", s["community_area"], s.get("ward") or "", s["rcdts"] or "",
                   s.get("predecessor", ""), enr.get("2026-27", ""), enr.get("2025-26", ""), enr.get("2024-25", ""),
                   ch.get("count", ""), ch.get("pct", "") if ch.get("pct") is not None else ""]
            for m in FLAT_LATEST:
                y, v = _latest(s["m"].get(m))
                row += [v, y]
            row += [s.get("budget_units", ""), ";".join(s["flags"])]
            w.writerow(row)

    # --- school_values.csv: long format, every value with its source, year and retrieval date ---
    with open(DATA / "school_values.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["school_id", "metric", "school_year", "value", "status", "unit", "source", "retrieved"])
        for s in schools:
            for metric, series in s["m"].items():
                reg = REGISTRY[metric]
                for y in sorted(series):
                    v = series[y]
                    w.writerow([s["id"], metric, y, "" if v == SUPPRESSED else v,
                                "suppressed" if v == SUPPRESSED else "value", reg["unit"], reg["source"],
                                _file_for(meta, metric, y)])
            # grade-level enrollment, all three years
            # only grades inside the school's enrolled span (a 0 inside the span is a real 0; outside it is "not offered")
            for y, grades in sorted(s["_grades_by_year"].items()):
                nz = [i for i, g in enumerate(GRADE_ORDER) if grades.get(g, 0) > 0]
                span = GRADE_ORDER[nz[0]:nz[-1] + 1] if nz else []
                for g in span:
                    n = grades[g]
                    w.writerow([s["id"], f"enrollment_grade_{g}", y, n, "value", "count", "CPS-MEM",
                                _file_for(meta, "enrollment", y)])

    (DATA / "validation_report.json").write_text(json.dumps(report, indent=1, ensure_ascii=False))
    (DATA / "validation_report.md").write_text(render_report(report, meta), encoding="utf-8")


def render_report(rep, meta):
    L = []
    ok = not rep["failed"]
    L.append("# Validation report")
    L.append("")
    L.append(f"Generated {rep['generated']} · roster {meta['roster_year']} · **{rep['schools']} schools** · "
             + ("**PASS**" if ok else f"**FAIL**: {', '.join(rep['failed'])}"))
    L.append("")
    c = rep["counts"]
    L.append(f"By type: {', '.join(f'{k} {v}' for k, v in sorted(c['by_type'].items()))} · "
             f"by grade band: {', '.join(f'{k} {v}' for k, v in sorted(c['by_band'].items()))}")
    L.append(f"With coordinates {c['with_coords']} · subdistrict {c['with_subdistrict']} · ISBE record {c['with_isbe']} · "
             f"FY27 budget {c['with_budget']}")
    L.append("")
    L.append("## Checks")
    L.append("")
    L.append("| Status | Check | Count | Detail |")
    L.append("|---|---|---|---|")
    order = {"FAIL": 0, "warn": 1, "pass": 2}
    for ch in sorted(rep["checks"], key=lambda x: order[x["status"]]):
        cnt = f"{ch['count']}" + (f" / {ch['total']}" if ch["total"] else "") if ch["status"] != "pass" else ""
        L.append(f"| {ch['status']} | {ch['title']} (`{ch['id']}`) | {cnt} | {ch['detail']} |")
    L.append("")
    L.append("## Examples (first 12 per non-passing check)")
    for ch in rep["checks"]:
        if ch["status"] != "pass" and ch["examples"]:
            L.append("")
            L.append(f"**{ch['title']}** (`{ch['id']}`, {ch['count']})")
            for e in ch["examples"]:
                L.append(f"- {e}")
    L.append("")
    L.append("## Coverage by metric (schools with a value / suppressed / no data)")
    L.append("")
    L.append("| Metric | Year | Value | Suppressed | No data |")
    L.append("|---|---|---|---|---|")
    for metric, years in rep["coverage"].items():
        for y, cv in years.items():
            L.append(f"| {metric} | {y} | {cv['value']} | {cv['suppressed']} | {cv['none']} |")
    L.append("")
    L.append("## Rules applied")
    for k, v in meta["rules"].items():
        L.append(f"- `{k}`: {v}")
    L.append("")
    L.append("## Source files")
    for sid, s in meta["sources"].items():
        for name, info in s.get("files", {}).items():
            L.append(f"- {sid} `{name}` retrieved {info['retrieved']}")
    for y, r in meta["sources"]["ISBE-RC"].get("revisions", {}).items():
        L.append(f"- ISBE Report Card {y}: {r}")
    L.append("")
    return "\n".join(L)
