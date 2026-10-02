"""Program context: the override list is well formed and the Data Portal classification mapping covers every value.

    .venv/bin/python -m unittest tests.test_program
"""
import json
import unittest
from pathlib import Path

from pipeline import program

ROOT = Path(__file__).resolve().parent.parent


class Program(unittest.TestCase):
    def test_overrides_have_source_and_known_program(self):
        rows = program.load_overrides()
        self.assertGreater(len(rows), 40)
        for sid, r in rows.items():
            self.assertIn(r["program"], program.PROGRAMS, sid)
            self.assertTrue(r["source_url"].startswith("https://"), sid)

    def test_profile_mapping(self):
        self.assertEqual(program.from_profile({"classification_description": "Schools that offer a rigorous curriculum with mainly honors", "significantlymodifiedmod": True}), ("exam", True, True))
        self.assertEqual(program.from_profile({"classification_description": "Schools that have an attendance boundary. x", "significantlymodifiedmod": False}), (None, False, True))
        self.assertFalse(program.from_profile({"classification_description": "A category CPS invented", "significantlymodifiedmod": False})[2])

    def test_published_programs_leave_the_default_set(self):
        d = json.load(open(ROOT / "data" / "schools.json"))
        progs = d["meta"]["programs"]
        self.assertTrue(all(v["comparable"] is False for v in progs.values()))
        for s in d["schools"]:
            if "program" in s:
                self.assertIn(s["program"], progs)
                self.assertTrue(s.get("program_note") or progs[s["program"]]["sentence"], s["id"])
            self.assertFalse("admission" in s and s["admission"] not in d["meta"]["admission"], s["id"])


if __name__ == "__main__":
    unittest.main()
