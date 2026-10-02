"""Sanity checks on the committed outputs (data/ and site/), so CI needs no downloads.

    python3 -m unittest tests.test_published
"""
import csv
import html
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).parent.parent


class TestPublished(unittest.TestCase):
    def test_site_data_matches_pipeline_output(self):
        a = json.load(open(ROOT / "data" / "schools.json"))["schools"]
        b = json.load(open(ROOT / "site" / "data" / "schools.json"))["schools"]
        self.assertEqual([s["id"] for s in a], [s["id"] for s in b], "run build_site.py after build.py")

    def test_ids_unique_and_placed(self):
        schools = json.load(open(ROOT / "site" / "data" / "schools.json"))["schools"]
        ids = [s["id"] for s in schools]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertGreater(len(ids), 600)
        for s in schools:
            self.assertIsNotNone(s.get("x"), s["id"])
            self.assertIsNotNone(s.get("y"), s["id"])

    def test_percentages_in_range(self):
        for s in json.load(open(ROOT / "data" / "schools.json"))["schools"]:
            for metric, years in s["m"].items():
                if metric.startswith("pct_"):
                    for y, v in years.items():
                        if isinstance(v, (int, float)):
                            self.assertTrue(0 <= v <= 100, f"{s['id']} {metric} {y} = {v}")

    def test_downloads_are_current(self):
        for name in ("schools.csv", "school_values.csv", "schools.json", "validation_report.md"):
            self.assertEqual((ROOT / "data" / name).read_bytes(), (ROOT / "site" / "downloads" / name).read_bytes(), name)
        for name in ("crosswalk.csv", "lineage.csv", "budget_units.csv", "budget_unit_funds.csv", "program_overrides.csv"):
            self.assertEqual((ROOT / name).read_bytes(), (ROOT / "site" / "downloads" / name).read_bytes(), name)
        with open(ROOT / "site" / "downloads" / "schools.csv", newline="") as f:
            self.assertGreater(sum(1 for _ in csv.DictReader(f)), 600)

    def test_share_pages(self):
        """Every school has /s/<id>/ with its own preview tags and card; numbers on it carry a year; no stale pages."""
        from pipeline import share
        schools = json.load(open(ROOT / "site" / "data" / "schools.json"))["schools"]
        out = ROOT / "site" / "s"
        self.assertEqual(sorted(p.name for p in out.iterdir() if p.is_dir()), sorted(s["id"] for s in schools), "run build_site.py")
        for s in schools:
            page = (out / s["id"] / "index.html").read_text()
            self.assertIn(f'og:url content="https://schools.ateya.org/s/{s["id"]}/"', page)
            self.assertIn(f'https://schools.ateya.org/s/{s["id"]}/card.png?v=', page)
            self.assertIn(f'u.set("school",{json.dumps(s["id"])})', page)
            self.assertTrue((out / s["id"] / "card.png").stat().st_size > 10_000, s["id"])
            for _, k in share.stats(s):
                v, y = share.latest(s, k)
                self.assertTrue(v == "No data" or y.startswith("SY"), f"{s['id']} {k}: {v} has no year")
            self.assertIn(html.escape(share.description(s), quote=True), page)

    def test_card_never_shows_missing_as_zero(self):
        from pipeline import share
        s = {"m": {"grad_4yr": {"2024-25": "*"}, "attendance_rate": {}, "pct_low_income": {"2026-27": 0.3}}}
        self.assertEqual(share.latest(s, "grad_4yr"), ("Suppressed", "SY24-25"))
        self.assertEqual(share.latest(s, "attendance_rate"), ("No data", ""))
        self.assertEqual(share.latest(s, "pct_low_income"), ("<1%", "SY26-27"))


if __name__ == "__main__":
    unittest.main()
