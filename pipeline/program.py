"""What each school does, for schools whose numbers are not comparable with a neighborhood school's.

`program_overrides.csv` is hand-kept: one row per school, with the public page that describes it
(and, where the general sentence is not specific enough, its own sentence). Preschool-only centers
come from the CPS 20th-day "School Type" column. A school with no program has no `program` key.
Comparison rules (which programs leave medians and color bins) are not applied here.
"""
import csv

from .common import ROOT

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


# Context that does not take a school out of comparisons (it still gets a label on its panel).
# `admission` comes from the City Data Portal School Profile `classification_description`;
# `sped_cluster` from its `significantlymodifiedmod` flag (the school hosts special-education cluster programs).
ADMISSION = {
    "exam": ("Admission by entrance exam",
             "Admits students by application and entrance exam, so results partly reflect who is admitted. Some of these schools share a building with a neighborhood program."),
    "application": ("Admission by application or lottery",
                    "Admits students by application or lottery rather than by home address, so results partly reflect who applies and is admitted."),
}
CLUSTER = ("Hosts special-education cluster programs",
           "Students in the cluster program are assigned from outside the attendance area, so the share of students with IEPs, budget per pupil and test averages reflect that program as well as the neighborhood.")

# first words of each `classification_description` -> admission; None = no admission context to show
_ADMISSION_BY_START = {
    "Schools that offer a rigorous curriculum": "exam",              # selective enrollment
    "Schools that provide an accelerated": "exam",                   # regional gifted and academic centers
    "Provides a challenging liberal arts": "exam",                   # classical
    "For students who wish to develop leadership": "application",    # military academies
    "Schools that specialize in a specific subject": "application",  # magnet
    "Schools that are open to all Chicago children": "application",  # charter
    "Schools that are operated by private entities": "application",  # contract
    "Students receive a college-preparatory": "application",         # career academies
    "Schools that have an attendance boundary": None,
    "These schools limit their student populations": None,
    "Schools that have their own processes": None,                   # covered by `program`
    "Schools for students with disabilities": None,                  # covered by `program`
}


def from_profile(prof):
    """-> (admission or None, sped_cluster bool, description_is_known) from one School Profile row."""
    if not prof:
        return None, False, True
    d = (prof.get("classification_description") or "").strip()
    cluster = str(prof.get("significantlymodifiedmod")).lower() == "true"
    if not d:
        return None, cluster, True
    for start, adm in _ADMISSION_BY_START.items():
        if d.startswith(start):
            return adm, cluster, True
    return None, cluster, False


def load_overrides():
    with open(ROOT / "program_overrides.csv", newline="", encoding="utf-8") as f:
        return {r["school_id"]: r for r in csv.DictReader(f)}


def meta():
    """Every program leaves the default comparison set (`comparable` false); admission and cluster context does not."""
    out = {k: {"label": v[0], "sentence": v[1], "comparable": False} for k, v in PROGRAMS.items()}
    return {"programs": out,
            "admission": {k: {"label": v[0], "sentence": v[1]} for k, v in ADMISSION.items()},
            "cluster": {"label": CLUSTER[0], "sentence": CLUSTER[1]}}


def assign(school, school_type, overrides, prof=None):
    """Set school['program'] (and 'program_note' when the row has its own sentence), 'admission' and 'sped_cluster'."""
    adm, cluster, _ = from_profile(prof)
    if adm:
        school["admission"] = adm
    if cluster:
        school["sped_cluster"] = True
    row = overrides.get(school["id"])
    if row:
        school["program"] = row["program"]
        if row["sentence"].strip():
            school["program_note"] = row["sentence"].strip()
    elif school_type == "Early Childhood":
        school["program"] = "early_childhood"


def unknown_descriptions(profiles):
    """Portal classification texts this module does not know yet (a new CPS category would be silently unlabeled)."""
    return sorted({(p.get("classification_description") or "").strip() for p in profiles
                   if not from_profile(p)[2]})


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
