"""Shared helpers: paths, school-year labels, value parsing."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "raw"
DATA = ROOT / "data"
CACHE = RAW / "cache"

ROSTER_YEAR = "2026-27"
CPS_YEARS = ["2024-25", "2025-26", "2026-27"]   # 20th-day files carried
SUPPRESSED = "*"                                  # ISBE suppression marker, kept as-is


def to_num(v):
    """Parse a spreadsheet cell. Returns float, SUPPRESSED ('*') or None (no data)."""
    if v is None:
        return None
    if isinstance(v, (int, float)):
        return float(v)
    s = str(v).strip()
    if s == "":
        return None
    if s == "*":
        return SUPPRESSED
    s = s.replace(",", "").replace("$", "")
    try:
        return float(s)
    except ValueError:
        return None


def to_id(v):
    """School IDs are text; calamine may hand back '400009' or 400009.0."""
    if v is None:
        return ""
    if isinstance(v, float) and v.is_integer():
        return str(int(v))
    return str(v).strip()


def norm_header(h):
    """Collapse whitespace/newlines and lowercase, for tolerant header matching."""
    return re.sub(r"\s+", " ", str(h).replace("\n", " ")).strip().lower()


def read_sheet(path, sheet):
    from python_calamine import CalamineWorkbook
    wb = CalamineWorkbook.from_path(str(path))
    return wb.get_sheet_by_name(sheet).to_python(skip_empty_area=False)
