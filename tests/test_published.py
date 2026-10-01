"""Sanity checks on the committed outputs (data/ and site/), so CI needs no downloads.

    python3 -m unittest tests.test_published
"""
import csv
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
        with open(ROOT / "site" / "downloads" / "schools.csv", newline="") as f:
            self.assertGreater(sum(1 for _ in csv.DictReader(f)), 600)


if __name__ == "__main__":
    unittest.main()
