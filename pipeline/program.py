"""What each school does, for schools whose numbers are not comparable with a neighborhood school's.

`program_overrides.csv` is hand-kept: one row per school, with the public page that describes it
(and, where the general sentence is not specific enough, its own sentence). Preschool-only centers
come from the CPS 20th-day "School Type" column. A school with no program has no `program` key.
Comparison rules (which programs leave medians and color bins) are not applied here.
"""
import csv
import json

from .common import DATA, ROOT

# code -> (label shown on the site, sentence for the school panel). Neutral wording, no judgments.
PROGRAMS = {
    "sped_specialty": ("Special-education school",
                       "Admits students through their individualized education programs (IEPs). Enrollment, spending per student and test results describe a specialized group of students and are not comparable with other schools. Many students take the state's alternate assessment, so proficiency may be missing."),
    "sped_transition": ("Transition program",
                        "Serves students about 18 to 22 who have met graduation requirements and are building job and independent-living skills. It is listed as grade 12 but is not a high school in the usual sense."),
    "detention": ("School in a detention facility",
                  "Serves students held in a detention facility. Enrollment changes daily, so counts and rates are not comparable with other schools."),
    "parenting": ("School for parenting students",
                  "Serves pregnant and parenting students. Enrollment is small, so rates and spending per student are not comparable with other schools."),
    "behavioral_referral": ("Short-term placement",
                            "Short-term placement for students referred by their home school, who are meant to return there. Enrollment is small and changes during the year, so rates are not comparable with other schools."),
    "reengagement": ("Dropout-recovery school",
                     "Serves students who left school and are returning, many already behind on credits. Four-year graduation rates and attendance are not comparable with other high schools, and many students attend shorter days."),
    "early_childhood": ("Preschool only",
                        "Serves preschool children only. No tests or outcomes are published for it. Some classrooms are special-education preschool, so the share of students with IEPs can be high."),
}


def load_overrides():
    with open(ROOT / "program_overrides.csv", newline="", encoding="utf-8") as f:
        return {r["school_id"]: r for r in csv.DictReader(f)}


def meta():
    return {k: {"label": v[0], "sentence": v[1]} for k, v in PROGRAMS.items()}


def assign(school, school_type, overrides):
    """Set school['program'] (and 'program_note' when the row has its own sentence)."""
    row = overrides.get(school["id"])
    if row:
        school["program"] = row["program"]
        if row["sentence"].strip():
            school["program_note"] = row["sentence"].strip()
    elif school_type == "Early Childhood":
        school["program"] = "early_childhood"


def problems(schools, overrides):
    """-> list of strings; empty when every override and every program school is well formed."""
    ids = {s["id"] for s in schools}
    bad = []
    for sid, r in overrides.items():
        if sid not in ids:
            bad.append(f"{sid} not in roster")
        if r["program"] not in PROGRAMS:
            bad.append(f"{sid} unknown program {r['program']!r}")
        if not r["source_url"].startswith("https://"):
            bad.append(f"{sid} no source URL")
    for s in schools:
        p = s.get("program")
        if p and not (s.get("program_note") or PROGRAMS.get(p, ("", ""))[1]):
            bad.append(f"{s['id']} no sentence")
    return bad


def patch_published():
    """Add `program` to the committed data/ files without re-reading raw/ (same result as a full build)."""
    path = DATA / "schools.json"
    d = json.load(open(path, encoding="utf-8"))
    ov = load_overrides()
    for s in d["schools"]:
        s.pop("program", None)
        s.pop("program_note", None)
        assign(s, s["school_type"], ov)
    assert not problems(d["schools"], ov)
    d["meta"]["programs"] = meta()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(d, f, separators=(",", ":"), ensure_ascii=False)
    prog = {s["id"]: s.get("program", "") for s in d["schools"]}
    path = DATA / "schools.csv"
    rows = list(csv.reader(open(path, newline="", encoding="utf-8")))
    h = rows[0]
    if "program" in h:
        i = h.index("program")
        for r in rows[1:]:
            r[i] = prog[r[0]]
    else:
        i = h.index("school_type") + 1
        h.insert(i, "program")
        for r in rows[1:]:
            r.insert(i, prog[r[0]])
    with open(path, "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerows(rows)
    print(sum(1 for v in prog.values() if v), "schools with a program")


if __name__ == "__main__":
    patch_published()
