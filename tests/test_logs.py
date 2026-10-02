"""Check that DECISIONS.md, WORKLOG.md and emails.md keep the format tools/logs.py parses.

    python3 -m unittest tests.test_logs
"""
import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import logs  # noqa: E402

DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
WHO = ("Owner", "Delegated", "Agent")


class Decisions(unittest.TestCase):
    def setUp(self):
        self.ds = logs.decisions()
        self.ids = {d["id"] for d in self.ds}

    def test_every_heading_parses(self):
        heads = [h for h, _ in logs.sections(logs.DECISIONS)]
        self.assertEqual(len(heads), len(self.ds), "a '## ' heading doesn't match '## D-0xx · Title'")

    def test_ids_sequential(self):
        self.assertEqual([d["id"] for d in self.ds], [f"D-{i:03d}" for i in range(1, len(self.ds) + 1)])

    def test_required_fields(self):
        for d in self.ds:
            with self.subTest(d["id"]):
                self.assertRegex(d["date"] or "", DATE)
                self.assertTrue((d["who"] or "").startswith(WHO), d["who"])
                self.assertTrue(d["tags"], "no tags")
                self.assertTrue(d["where"] and d["decision"] and d["why"])
                self.assertLessEqual(len(d["title"]), 80)

    def test_status_and_supersedes(self):
        for d in self.ds:
            with self.subTest(d["id"]):
                m = re.fullmatch(r"Active|Superseded by (D-\d{3})", d["status"] or "")
                self.assertTrue(m, d["status"])
                if m.group(1):
                    new = next(x for x in self.ds if x["id"] == m.group(1))
                    self.assertEqual(new["supersedes"], d["id"])
                if d["supersedes"]:
                    old = next(x for x in self.ds if x["id"] == d["supersedes"])
                    self.assertEqual(old["status"], f"Superseded by {d['id']}")


class Worklog(unittest.TestCase):
    def test_entries(self):
        es = logs.worklog()
        self.assertTrue(es)
        known = {d["id"] for d in logs.decisions()}
        for e in es:
            with self.subTest(e["session"]):
                self.assertTrue(e["asked"] and e["done"], "needs **Asked:** and **Done:**")
                self.assertRegex(e["when"], r"^\d{4}-\d{2}-\d{2}")
                self.assertLessEqual(set(e["decision_ids"]), known)

    def test_every_dated_heading_parses(self):
        heads = [h for h, _ in logs.sections(logs.WORKLOG) if re.match(r"## \d{4}-", h)]
        self.assertEqual(len(heads), len(logs.worklog()), "a dated heading doesn't match '## when · title · `id`'")

    def test_threads(self):
        ts = logs.threads()
        self.assertTrue(ts)
        for t in ts:
            self.assertTrue(t["text"], f"thread '{t['label']}' should be '- **Label:** text'")


class Outreach(unittest.TestCase):
    def test_fields(self):
        os_ = logs.outreach()
        self.assertTrue(os_)
        for o in os_:
            with self.subTest(o["n"]):
                self.assertTrue(o["sent"] and o["status"] and o["related"])
                self.assertRegex(o["status"], r"^(Draft, not sent|Awaiting reply|Answered \d{4}-\d{2}-\d{2}|Bounced|No reply, closed)")


if __name__ == "__main__":
    unittest.main()
