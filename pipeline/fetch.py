"""Stage 1: download raw source files into raw/ and record a manifest.

Files already in raw/ are reused (delete one to force a re-download).
raw/MANIFEST.json holds source id, url, retrieved date, size and sha256 per file.
"""
import datetime
import hashlib
import json
import sys
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "raw"
MANIFEST = RAW / "MANIFEST.json"
UA = {"User-Agent": "Mozilla/5.0 (cps-facts data pipeline)"}

CPS = "https://www.cps.edu/globalassets/cps-pages/about-cps/district-data/demographics/"
ISBE = "https://www.isbe.net/_layouts/Download.aspx?SourceUrl=/Documents/"
SOC = "https://data.cityofchicago.org/resource/"
SENATE = "https://www.ilsenateredistricting.com/images/shape-files/"

# (source id, local file name, url)
SOURCES = [
    ("CPS-MEM", "cps_mem_2627.xlsx", CPS + "2026-27-demographics-20th-day-membership-report.xlsx"),
    ("CPS-MEM", "cps_mem_2526.xlsx", CPS + "demographics_20thday_sy2026_forweb.xlsx"),
    ("CPS-MEM", "cps_mem_2425.xlsx", CPS + "demographics_20thday_sy2025_final.xlsx"),
    ("CPS-DEM1", "cps_lepiep_2627.xlsx", CPS + "2026-27-demographics-lep-iep-low-income-20th-day-report.xlsx"),
    ("CPS-DEM1", "cps_lepiep_2526.xlsx", CPS + "demographics_lepiepfrm_20thday_sy2026_forweb.xlsx"),
    ("CPS-DEM1", "cps_lepiep_2425.xlsx", CPS + "demographics_lepiepfrm_20thday_sy2025_final.xlsx"),
    ("CPS-DEM2", "cps_race_2627.xlsx", CPS + "2026-27-demographics-racial-ethnic-20th-day-report.xlsx"),
    ("CPS-DEM2", "cps_race_2526.xlsx", CPS + "demographics_racialethnic_20thday_sy2026_forweb.xlsx"),
    ("CPS-DEM2", "cps_race_2425.xlsx", CPS + "demographics_racialethnic_20thday_sy2025_final.xlsx"),
    ("CHI-LOC", "chi_loc.json", SOC + "pb6d-zzuh.json?$limit=5000"),
    ("CHI-PROF", "chi_prof.json", SOC + "3dhs-m3w4.json?$limit=5000"),
    ("CHI-CA", "chi_community_areas.geojson", "https://data.cityofchicago.org/resource/igwz-8jzy.geojson?$limit=200"),
    ("CHI-WARD", "chi_wards.geojson", "https://data.cityofchicago.org/resource/p293-wvbd.geojson?$limit=100"),
    ("SUBDIST", "subdistricts.zip", SENATE + "ERSB_20_Sub_District_Map_FA1_SB_15.zip"),
    ("ISBE-RC", "isbe_rc_2025.xlsx", ISBE + "2025-Report-Card-Public-Data-Set.xlsx"),
    ("ISBE-RC", "isbe_rc_2024.xlsx", ISBE + "24-RC-Pub-Data-Set.xlsx"),
    ("ISBE-RC", "isbe_rc_2023.xlsx", ISBE + "23-RC-Pub-Data-Set.xlsx"),
]


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def download(url, dest):
    tmp = dest.with_suffix(dest.suffix + ".part")
    with requests.get(url, headers=UA, stream=True, timeout=120) as r:
        r.raise_for_status()
        with open(tmp, "wb") as f:
            for chunk in r.iter_content(1 << 20):
                f.write(chunk)
    tmp.rename(dest)


def run():
    RAW.mkdir(exist_ok=True)
    manifest = json.loads(MANIFEST.read_text()) if MANIFEST.exists() else {}
    today = datetime.date.today().isoformat()
    for source, name, url in SOURCES:
        dest = RAW / name
        if not dest.exists():
            print(f"fetch  {name}")
            download(url, dest)
            manifest[name] = {"source": source, "url": url, "retrieved": today}
        elif name not in manifest:
            # present but not recorded (e.g. fetched by hand): stamp with file mtime
            mtime = datetime.date.fromtimestamp(dest.stat().st_mtime).isoformat()
            manifest[name] = {"source": source, "url": url, "retrieved": mtime}
        manifest[name]["bytes"] = dest.stat().st_size
        manifest[name]["sha256"] = sha256(dest)
    # the manually exported BI file is not fetched; record it if present
    bi = RAW / "fy27_bi_budget_book.csv"
    if bi.exists():
        manifest[bi.name] = {
            "source": "CPS-BUD-BI",
            "url": "manual export from biportal.cps.edu (not fetched)",
            "retrieved": manifest.get(bi.name, {}).get("retrieved", "2026-09-30"),
            "bytes": bi.stat().st_size,
            "sha256": sha256(bi),
        }
    MANIFEST.write_text(json.dumps(manifest, indent=2, sort_keys=True))
    return manifest


if __name__ == "__main__":
    run()
    sys.exit(0)
