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

from pipeline import geo, isbe
import sources_catalog as sc

ROOT = Path(__file__).parent
OUT = ROOT / "site"
REPO = "https://github.com/cmdshftateya/cps-facts"
SITE_URL = "https://schools.ateya.org"
DOWNLOADS = [  # (source under data/, label, what it is)
    ("schools.csv", "Schools, one row per school", "Roster, location, enrollment, demographics and the latest value of every metric, each with its school year."),
    ("school_values.csv", "All values, long format", "One row per school, metric and school year, with status (value or suppressed; suppressed rows have a blank value), unit, source and retrieval date. A school-metric-year with no row has no data."),
    ("schools.json", "Schools, JSON", "The same data as the schools table plus metric metadata (labels, units, comparability breaks)."),
    ("validation_report.md", "Validation report", "What the build checked and what it found."),
]
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
    t = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", r'<a href="\2">\1</a>', t)
    return re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", t)


def head(title, desc, path):
    return ("<!doctype html><html lang=en><head><meta charset=utf-8><meta name=viewport content='width=device-width, initial-scale=1'>"
            f"<title>{title}</title><meta name=description content=\"{desc}\"><link rel=canonical href={SITE_URL}/{path}>"
            "<link rel=icon href=favicon.svg type=image/svg+xml><link rel=apple-touch-icon href=apple-touch-icon.png>"
            f"<meta property=og:type content=website><meta property=og:site_name content='CPS Facts'><meta property=og:title content=\"{title}\">"
            f"<meta property=og:description content=\"{desc}\"><meta property=og:url content={SITE_URL}/{path}>"
            f"<meta property=og:image content={SITE_URL}/og.png><meta property=og:image:width content=1200><meta property=og:image:height content=630>"
            f"<meta name=twitter:card content=summary_large_image><meta name=twitter:title content=\"{title}\"><meta name=twitter:description content=\"{desc}\">"
            f"<meta name=twitter:image content={SITE_URL}/og.png><link rel=stylesheet href=chicago.css>"
            "<style>body{max-width:900px;margin:0 auto;padding:16px;font-family:var(--font-text);line-height:1.5;background:var(--page);color:var(--ink)}"
            "h1,h2,h3{font-family:var(--font-display);text-transform:uppercase}table{border-collapse:collapse;font:14px var(--font-ui)}"
            "td,th{border:1px solid var(--rule-firm);padding:6px 8px;vertical-align:top;text-align:left}p.li{margin:.4em 0}"
            "code{font-family:var(--font-mono);font-size:.9em}a{color:var(--blue)}footer{margin-top:2em;padding-top:1em;border-top:1px solid var(--rule-firm);color:var(--muted);font-size:14px}"
            "</style></head><body><p><a href=./>&larr; Back to the map</a> · <a href=methodology.html>Methodology</a> · <a href=data.html>Data and sources</a></p>")


FOOT = (f"<footer>Found an error or have a question? <a href={REPO}/issues>Open an issue on GitHub</a>. "
        f"Code and data are in the <a href={REPO}>public repository</a>.</footer></body></html>")


def _size(p):
    n = p.stat().st_size
    return f"{n / 1e6:.1f} MB" if n >= 1e6 else f"{max(1, round(n / 1e3))} KB"


def _links(pairs):
    return "<br>".join(f'<a href="{html.escape(u)}">{html.escape(t)}</a>' for t, u in pairs)


def _metric_rows(meta):
    ds = {"CPS-MEM": "CPS 20th-day membership"}
    rows = []
    for key, m in meta["metrics"].items():
        if key in sc.OTHER_FIELDS:
            dataset, field = sc.OTHER_FIELDS[key]
        else:  # ISBE: find the sheet and header in the newest edition that carries the metric
            dataset, field = "ISBE Report Card", ""
            for yr in sorted(isbe.SPEC, reverse=True):
                hit = next(((sh, cols[key]) for sh, cols in isbe.SPEC[yr].items() if key in cols), None)
                if hit:
                    sheet, col = hit
                    col = " + ".join(col) if isinstance(col, tuple) else col
                    field = f"sheet {sheet}, column \"{col}\"" + sc.OTHER_FIELDS_NOTE.get(key, "")
                    break
        unit = {"pct": "%", "usd": "$", "count": "count", "score": "score", "percentile": "percentile", "level": "level 1-5", "points": "points"}.get(m["unit"], m["unit"])
        rows.append(f"<tr><td>{html.escape(m['label'])}</td><td>{html.escape(unit)}</td><td>{', '.join(y for y in m['years'])}</td>"
                    f"<td>{html.escape(dataset)}</td><td>{html.escape(field)}</td></tr>")
    return "".join(rows)


def downloads():
    """data/ and the lookup tables -> site/downloads/, and site/data.html (files, sources, field dictionary)."""
    (OUT / "downloads").mkdir(exist_ok=True)
    meta = json.load(open(ROOT / "data" / "schools.json"))["meta"]
    rows = []
    for name, label, what in DOWNLOADS:
        src = ROOT / "data" / name
        shutil.copy(src, OUT / "downloads" / name)
        rows.append(f"<tr><td><a href=downloads/{name} download>{html.escape(label)}</a><br><code>{name}</code></td>"
                    f"<td>{what}</td><td>{_size(src)}</td></tr>")
    ours = []
    for label, path, what in sc.OURS:
        name = path.split("/")[-1]
        src = ROOT / name
        shutil.copy(src, OUT / "downloads" / name)
        ours.append(f"<tr><td><a href={path} download>{html.escape(label)}</a><br><code>{name}</code></td><td>{what}</td><td>{_size(src)}</td></tr>")
    srcs = []
    for sid, publisher, title, pages, years, uses, files, how in sc.SOURCES:
        srcs.append(f"<h3 id={sid}>{html.escape(title)}</h3><p class=li><strong>Publisher:</strong> {html.escape(publisher)}</p>"
                    f"<p class=li><strong>Where:</strong> {_links(pages)}</p>"
                    f"<p class=li><strong>Years we use:</strong> {html.escape(years)}</p>"
                    f"<p class=li><strong>What we take from it:</strong> {html.escape(uses)}</p>"
                    + (f"<p class=li><strong>Original files we used:</strong><br>{_links(files)}</p>" if files else "")
                    + f"<p class=li><strong>To get it yourself:</strong> {html.escape(how)}</p>")
    scroll = "<div style='overflow-x:auto'>"
    body = ("<h1>Data and sources</h1>"
            "<p>Everything on the map comes from public sources, listed below with the publisher, the dataset name, a link and the field we read, "
            "so you can check any number against the original. The processed files we publish are listed first.</p>"
            "<p><a href=#files>Our data files</a> · <a href=#sources>Original sources</a> · <a href=#fields>What each value is and where it comes from</a> · <a href=#reading>Reading the files</a></p>"
            "<h2 id=files>Our data files</h2>"
            "<p>Free to reuse. Please cite the original publishers as well. Suggested citation: CPS Facts (schools.ateya.org), data retrieved 2026-09-30.</p>"
            + scroll + "<table><thead><tr><th>File</th><th>Contents</th><th>Size</th></tr></thead><tbody>" + "".join(rows) + "".join(ours) + "</tbody></table></div>"
            "<h2 id=sources>Original sources</h2>"
            "<p>Retrieved 2026-09-30 unless noted. Every value carries its own school year, because the sources publish at different times: "
            "CPS enrollment and demographics are SY2026-27, while the state's test, attendance, graduation and spending figures are SY2024-25.</p>"
            + "".join(srcs) +
            "<h2 id=fields>What each value is and where it comes from</h2>"
            "<p>Percentages are 0 to 100. For the state's data, sheet and column names are exactly as ISBE prints them in the 2025 Report Card workbook (or the edition named in the Years column when a measure was dropped later).</p>"
            + scroll + "<table><thead><tr><th>Value</th><th>Unit</th><th>School years</th><th>Dataset</th><th>Field in the original</th></tr></thead><tbody>"
            + _metric_rows(meta) + "<tr><td>Enrollment change (count and %)</td><td>count, %</td><td>2024-25 to 2026-27</td><td>Calculated</td><td>SY2026-27 20th-day enrollment minus SY2025-26 (and SY2024-25)</td></tr></tbody></table></div>"
            "<h2 id=reading>Reading the files</h2>"
            "<p><code>schools.csv</code> has one row per school with the latest value of each measure and its year. <code>school_values.csv</code> has one row per "
            "school, measure and year (<code>school_id, metric, school_year, value, status, unit, source, retrieved</code>). "
            "<code>status</code> is <code>value</code> or <code>suppressed</code> (the state hid a small group). A suppressed row has a blank <code>value</code>. If a school has no row for a measure and year, the source has no data for it. '"
            "In <code>schools.csv</code> both cases are blank, so use <code>school_values.csv</code> to tell them apart. Neither is zero. <code>school_id</code> is the CPS School ID, and <code>rcdts</code> is the state's school ID.</p>"
            "<p>Before comparing across years, read the <a href=methodology.html>methodology and caveats</a>: the 2025 state tests are not comparable with earlier years, "
            "and test scores and spending are about a year older than enrollment.</p>"
            f"<p>The code that builds these files is MIT licensed and public: <a href={REPO}>{REPO.split('//')[1]}</a>.</p>")
    (OUT / "data.html").write_text(head("Data and sources — CPS Facts", "Where every number on CPS Facts comes from: publisher, dataset, link and field, plus downloadable CSV and JSON.", "data.html") + body + FOOT)


def methodology():
    """METHODOLOGY.md -> site/methodology.html (minimal converter: headings, tables, lists, paragraphs)."""
    out, lines, i = [], (ROOT / "METHODOLOGY.md").read_text().split("\n"), 0
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
    page = (head("Methodology — CPS Facts", "How CPS Facts chooses years, matches schools across sources, and where the numbers have limits.", "methodology.html")
            + "\n".join(out) + FOOT)
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
    downloads()
    print(f"{len(data['schools'])} schools, viewbox {data['map']['viewbox']}, {(OUT / 'data' / 'schools.json').stat().st_size / 1e6:.2f} MB")


if __name__ == "__main__":
    main()
