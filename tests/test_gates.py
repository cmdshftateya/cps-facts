"""Corrupt the built dataset in memory and confirm the validation gates fail.

    .venv/bin/python -m unittest tests.test_gates
"""
import copy
import unittest
from pathlib import Path



def run(mutate, expect, t, schools, meta, problems):
    from pipeline import validate
    s = copy.deepcopy(schools)
    p = copy.deepcopy(problems)
    mutate(s, p)
    failed = validate.validate(s, meta, t, p)["failed"]
    assert expect in failed, f"{expect} did not fail (failed: {failed})"
    print(f"ok  {expect}")


def main():
    from pipeline import normalize, validate
    t = normalize.load_all()
    schools, meta, problems = normalize.build(t)
    assert validate.validate(schools, meta, t, problems)["failed"] == [], "baseline must pass"
    print("ok  baseline passes")

    run(lambda s, p: s.append(copy.deepcopy(s[0])), "dup_ids", t, schools, meta, problems)

    def no_coords(s, p):
        s[0]["lat"] = s[0]["lon"] = None
        p["unmatched_loc"].append(s[0]["id"])
    run(no_coords, "missing_coords", t, schools, meta, problems)

    def bad_pct(s, p):
        s[0]["m"]["pct_low_income"]["2026-27"] = 120
    run(bad_pct, "percent_range", t, schools, meta, problems)

    def zero_dollars(s, p):
        s[1]["m"]["ppe_total"] = {"2024-25": 0}
    run(zero_dollars, "zero_dollars", t, schools, meta, problems)

    def drop_isbe(s, p):
        for x in s[:60]:
            x["rcdts"] = None
    run(drop_isbe, "isbe_join", t, schools, meta, problems)

    def dup_rcdts(s, p):
        s[1]["rcdts"] = s[0]["rcdts"]
    run(dup_rcdts, "dup_rcdts", t, schools, meta, problems)

    def funds_off(s, p):
        x = next(x for x in s if x.get("budget_funds"))
        k = next(iter(x["budget_funds"]))
        x["budget_funds"][k] += 100000
    run(funds_off, "budget_fund_sum", t, schools, meta, problems)

    def program_no_sentence(s, p):
        s[0]["program"] = "not_a_program"
    run(program_no_sentence, "program_context", t, schools, meta, problems)

    def no_subdistrict(s, p):
        s[0]["subdistrict"] = None
    run(no_subdistrict, "missing_subdistrict", t, schools, meta, problems)

    def unknown_metric(s, p):
        s[0]["m"]["made_up"] = {"2026-27": 1}
    run(unknown_metric, "unknown_metric", t, schools, meta, problems)

    def low_conf(s, p):
        x = next(x for x in s if x["rcdts"])
        t["crosswalk"][x["id"]] = dict(t["crosswalk"][x["id"]], confidence="low")
    saved = copy.deepcopy(t["crosswalk"])
    run(low_conf, "low_confidence_ships_isbe", t, schools, meta, problems)
    t["crosswalk"] = saved
    print("all gates fire")


@unittest.skipUnless((Path(__file__).parent.parent / "raw" / "cps_mem_2425.xlsx").exists(), "needs the raw/ downloads (python build.py)")
class TestGates(unittest.TestCase):
    def test_all_gates_fire(self):
        main()


if __name__ == "__main__":
    unittest.main()
