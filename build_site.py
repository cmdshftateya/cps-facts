"""Phase 2 site build: data/schools.json -> site/data/schools.json (projected map coordinates + context geometry).

    .venv/bin/python build_site.py

Projection is equirectangular with a cos(latitude) correction (fine at city scale). Geometry is
simplified at build time; the page does no projection and loads no tiles.
"""
import html
import json
import math
import re
import shutil
from pathlib import Path

from pipeline import geo

ROOT = Path(__file__).parent
OUT = ROOT / "site"
W = 1000.0
TOL = 0.6  # simplification tolerance, SVG units


def _dp(pts, tol):
    if len(pts) < 3:
        return pts
    (x1, y1), (x2, y2) = pts[0], pts[-1]
    dx, dy = x2 - x1, y2 - y1
    norm = math.hypot(dx, dy) or 1e-9
    idx, dmax = 0, 0.0
    for i in range(1, len(pts) - 1):
        d = abs(dy * pts[i][0] - dx * pts[i][1] + x2 * y1 - y2 * x1) / norm
        if d > dmax:
            idx, dmax = i, d
    if dmax <= tol:
        return [pts[0], pts[-1]]
    return _dp(pts[:idx + 1], tol)[:-1] + _dp(pts[idx:], tol)


def _inline(t):
    t = html.escape(t, quote=False)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    return re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", t)


def methodology():
    """NOTES.md -> site/methodology.html (minimal converter: headings, tables, lists, paragraphs)."""
    out, lines, i = [], (ROOT / "NOTES.md").read_text().split("\n"), 0
    while i < len(lines):
        ln = lines[i]
        if ln.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            rows = [r for r in rows if not set("".join(r)) <= set("-: ")]
            out.append("<table><thead><tr>" + "".join(f"<th>{_inline(c)}</th>" for c in rows[0]) + "</tr></thead><tbody>"
                       + "".join("<tr>" + "".join(f"<td>{_inline(c)}</td>" for c in r) + "</tr>" for r in rows[1:]) + "</tbody></table>")
            continue
        m = re.match(r"(#+) (.*)", ln)
        if m:
            n = min(len(m.group(1)) + 0, 3)
            out.append(f"<h{n}>{_inline(m.group(2))}</h{n}>")
        elif re.match(r"(\d+[a-z]?\.|-) ", ln):
            out.append(f"<p class=li>{_inline(ln)}</p>")
        elif ln.strip():
            out.append(f"<p>{_inline(ln)}</p>")
        i += 1
    page = ("<!doctype html><html lang=en><head><meta charset=utf-8><meta name=viewport content='width=device-width, initial-scale=1'>"
            "<meta name=robots content='noindex'><title>Methodology — CPS Facts</title><link rel=stylesheet href=chicago.css>"
            "<style>body{max-width:900px;margin:0 auto;padding:16px;font-family:var(--font-text);line-height:1.5;background:var(--page);color:var(--ink)}"
            "h1,h2,h3{font-family:var(--font-display);text-transform:uppercase}table{border-collapse:collapse;font:14px var(--font-ui)}"
            "td,th{border:1px solid var(--rule-firm);padding:6px 8px;vertical-align:top;text-align:left}p.li{margin:.4em 0}"
            "code{font-family:var(--font-mono);font-size:.9em}a{color:var(--blue)}</style></head><body>"
            "<p><a href=./>&larr; Back to the map</a></p>" + "\n".join(out) + "</body></html>")
    (OUT / "methodology.html").write_text(page)


def main():
    data = json.load(open(ROOT / "data" / "schools.json"))
    sub = geo.load_subdistricts()
    ca = geo.load_community_areas()

    lons = [p[0] for _, rings, _ in sub.features for r in rings for p in r]
    lats = [p[1] for _, rings, _ in sub.features for r in rings for p in r]
    lon0, lon1, lat0, lat1 = min(lons), max(lons), min(lats), max(lats)
    k = math.cos(math.radians((lat0 + lat1) / 2))
    scale = W / ((lon1 - lon0) * k)
    H = (lat1 - lat0) * scale
    pad = 12.0

    def proj(lon, lat):
        return ((lon - lon0) * k * scale + pad, (lat1 - lat) * scale + pad)

    def path(rings):
        out = []
        for r in rings:
            raw = [proj(*p[:2]) for p in r]
            if raw[0] == raw[-1] and len(raw) > 3:  # closed ring: split at the farthest vertex so the chord isn't degenerate
                j = max(range(len(raw)), key=lambda i: (raw[i][0] - raw[0][0]) ** 2 + (raw[i][1] - raw[0][1]) ** 2)
                pts = _dp(raw[:j + 1], TOL)[:-1] + _dp(raw[j:], TOL)[:-1]
            else:
                pts = _dp(raw, TOL)
            if len(pts) >= 3:
                out.append("M" + "L".join(f"{x:.1f},{y:.1f}" for x, y in pts) + "Z")
        return "".join(out)

    subs = [{"id": label, "d": path(rings)} for label, rings, _ in sub.features]
    areas = [path(rings) for _, rings, _ in ca.features]

    for s in data["schools"]:
        s["x"], s["y"] = (round(v, 1) for v in proj(s.pop("lon"), s.pop("lat")))
    data["map"] = {"viewbox": [round(W + 2 * pad, 1), round(H + 2 * pad, 1)], "subdistricts": subs, "areas": areas}

    (OUT / "data").mkdir(parents=True, exist_ok=True)
    with open(OUT / "data" / "schools.json", "w") as f:
        json.dump(data, f, separators=(",", ":"))
    shutil.copy(ROOT.parent / "politics" / "chicago.css", OUT / "chicago.css") if (ROOT.parent / "politics" / "chicago.css").exists() else None
    methodology()
    print(f"{len(data['schools'])} schools, viewbox {data['map']['viewbox']}, {(OUT / 'data' / 'schools.json').stat().st_size / 1e6:.2f} MB")


if __name__ == "__main__":
    main()
