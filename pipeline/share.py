"""Per-school share pages: site/s/<id>/index.html (link-preview tags) and site/s/<id>/card.png (1200x630).

    .venv/bin/python -m pipeline.share      # from site/data/schools.json; build_site.py also calls write_all()

School links on the map live after a '#', which link-preview bots never see, so every school would
otherwise share the site-wide og.png. Each /s/<id>/ page carries that school's title, description and
card, then sends a browser on to /#school=<id>. Fonts are vendored in tools/fonts (SIL OFL), so the
output is the same on every machine. The badge colour and pattern come from a hash of the school id
and name: identity only, never data.
"""
import hashlib
import html
import json
import math
import re
import shutil
from concurrent.futures import ProcessPoolExecutor
from functools import lru_cache
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
FONTS = ROOT / "tools" / "fonts"
SITE_URL = "https://schools.ateya.org"
PAGE, INK, INK2, BLUE = "#0c0e10", "#f0ece5", "#b9b3a9", "#4bb3e8"
LAND, EDGE = "#262a2f", "#3a3f45"
HUES = ["#4bb3e8", "#e6635b", "#e8b84b", "#5fbf8f", "#b39ce8", "#f08a4b"]
TYPES = {"district": "District-run", "charter": "Charter", "contract": "Contract", "options": "Options"}
DROP = {"HS", "ES", "MS", "HIGH", "SCHOOL", "ACADEMY", "ELEMENTARY", "CHARTER", "THE", "OF", "MD", "CAMPUS"}
W, H, X = 1200, 630, 2  # card size; drawn at X times and downsampled for anti-aliasing


@lru_cache(maxsize=None)
def _font(name, size):
    return ImageFont.truetype(str(FONTS / f"{name}.ttf"), round(size * X))


def sy(y):
    return "SY" + y[2:]


def display_name(s):
    return s.get("long_name") or re.sub(r"\bHS\b", "High School", s["name"].title().replace("Hs", "HS"))


def initials(s):
    words = [w for w in re.split(r"[\s-]+", s["name"]) if w not in DROP and len(w) > 1]
    return "".join(w[0] for w in words[:2]) or s["name"][0]


def badge_style(s):
    h = hashlib.sha256(f"{s['id']}|{s['name']}".encode()).digest()
    return HUES[h[0] % len(HUES)], h[1] % 4, (0.50, 0.56, 0.62)[h[2] % 3]


def latest(s, k):
    """(display value, year label) for the latest year of metric k. Never turns missing or suppressed into 0."""
    v = s["m"].get(k) or {}
    if not v:
        return "No data", ""
    y = max(v)
    x = v[y]
    if x == "*":
        return "Suppressed", sy(y)
    if k == "enrollment":
        return f"{x:,}", sy(y)
    return ("<1%" if 0 < x < 0.5 else f"{x:.0f}%"), sy(y)


def outcome(s):
    return ("4-year graduation", "grad_4yr") if s["band"] in ("HS", "combo") else ("Attendance", "attendance_rate")


def stats(s):
    return [("Students", "enrollment"), ("Low income", "pct_low_income"), outcome(s)]


def kicker(s):
    return f"{TYPES.get(s['type'], s['type'])} · Grades {s['grades_served']} · {s['community_area'].title()}"


def description(s):
    parts = [f"{TYPES.get(s['type'], s['type'])} school, grades {s['grades_served']}, {s['community_area'].title()}, Chicago."]
    for label, k in stats(s):
        v, y = latest(s, k)
        parts.append(f"{label}: {v}" + (f" ({y})." if y else "."))
    return " ".join(parts) + " Sources: CPS and the Illinois Report Card."


# ---------- drawing

def _star(cx, cy, R, r, rot=0.0):
    return [(cx + (R if i % 2 == 0 else r) * math.cos(math.radians(rot - 90 + i * 30)),
             cy + (R if i % 2 == 0 else r) * math.sin(math.radians(rot - 90 + i * 30))) for i in range(12)]


def _badge(d, s, x, y, size):
    col, pat, inner = badge_style(s)
    cx, cy, R = (x + size / 2) * X, (y + size / 2) * X, (size / 2 - 1) * X
    d.polygon(_star(cx, cy, R, R * inner * 1.155), fill=col)
    mark = _mix(col, PAGE, .5)
    if pat == 1:
        d.polygon(_star(cx, cy, R * .8, R * .8 * inner * 1.155), outline=mark, width=3 * X)
    elif pat == 2:
        for i in range(6):
            a = math.radians(i * 60 - 90)
            px, py, rr = cx + R * .78 * math.cos(a), cy + R * .78 * math.sin(a), R * .06
            d.ellipse([px - rr, py - rr, px + rr, py + rr], fill=mark)
    elif pat == 3:
        d.polygon([(cx + R * .5 * math.cos(math.radians(i * 60)), cy + R * .5 * math.sin(math.radians(i * 60))) for i in range(6)], outline=mark, width=3 * X)
    ini = initials(s)
    d.text((cx, cy), ini, font=_font("BarlowCondensed-ExtraBold", size * (.34 if len(ini) == 2 else .42)), fill=PAGE, anchor="mm")
    return col


def _mix(a, b, t):
    a, b = (tuple(int(h[i:i + 2], 16) for i in (1, 3, 5)) for h in (a, b))
    return "#" + "".join(f"{round(x * (1 - t) + y * t):02x}" for x, y in zip(a, b))


def _wrap(d, text, font, width):
    lines, cur = [], ""
    for w in text.split():
        t = f"{cur} {w}".strip()
        if cur and d.textlength(t, font=font) > width:
            lines.append(cur)
            cur = w
        else:
            cur = t
    return lines + [cur]


def _fit_name(d, name, width, max_lines=3):
    for size in range(84, 39, -2):
        f = _font("BarlowCondensed-Black", size)
        lines = _wrap(d, name, f, width * X)
        if len(lines) <= max_lines and all(d.textlength(l, font=f) <= width * X for l in lines):
            return f, size, lines
    return f, size, lines


def _rings(path_d):
    for ring in re.findall(r"M([^Z]+)Z", path_d):
        yield [tuple(map(float, p.split(","))) for p in ring.split("L")]


def _map_box(geo):
    """Map scale and origin: 430px tall, right-aligned with a 48px margin."""
    vw, vh = geo["viewbox"]
    k = 430 / vh
    return k, W - 48 - vw * k, 70


_BASE = {}


def _base(geo):
    """Background, flag stripes and the city outline by subdistrict: the same on every card, so drawn once."""
    key = (tuple(geo["viewbox"]), tuple(sub["d"] for sub in geo["subdistricts"]))
    if key not in _BASE:
        img = Image.new("RGB", (W * X, H * X), PAGE)
        d = ImageDraw.Draw(img)
        d.rectangle([0, 0, W * X, 16 * X], fill=BLUE)
        d.rectangle([0, (H - 16) * X, W * X, H * X], fill=BLUE)
        k, ox, oy = _map_box(geo)
        for sub in geo["subdistricts"]:
            for ring in _rings(sub["d"]):
                d.polygon([((ox + x * k) * X, (oy + y * k) * X) for x, y in ring], fill=LAND, outline=EDGE, width=X)
        _BASE.clear()
        _BASE[key] = img
    return _BASE[key].copy()


def card_png(s, geo):
    img = _base(geo)
    d = ImageDraw.Draw(img)
    k, ox, oy = _map_box(geo)
    vw = geo["viewbox"][0]
    T = lambda p: ((ox + p[0] * k) * X, (oy + p[1] * k) * X)

    col = _badge(d, s, 64, 62 + 14, 150)
    px, py = T((s["x"], s["y"]))
    r = 50 * X  # translucent halo, composited over just its own square
    box = tuple(round(v) for v in (px - r, py - r, px + r, py + r))
    patch = img.crop(box).convert("RGBA")
    halo = Image.new("RGBA", patch.size, (0, 0, 0, 0))
    ImageDraw.Draw(halo).ellipse([0, 0, patch.size[0] - 1, patch.size[1] - 1], fill=col + "38")
    img.paste(Image.alpha_composite(patch, halo).convert("RGB"), box[:2])
    d = ImageDraw.Draw(img)
    d.polygon(_star(px, py, 31 * X, 18 * X), fill=col, outline=PAGE, width=3 * X)

    # name block
    tx, tw = 64 + 150 + 30, 1200 - 48 - vw * k - 24 - (64 + 150 + 30)
    d.text((tx * X, 62 * X), kicker(s), font=_font("Barlow-SemiBold", 24), fill=BLUE, anchor="lt")
    f, size, lines = _fit_name(d, display_name(s).upper(), tw)
    y = 62 + 38
    for line in lines:
        d.text((tx * X, y * X), line, font=f, fill=INK, anchor="lt")
        y += size * .98

    # three numbers, each with its school year
    gap, x0, colw = 16, 64, (760 - 32) / 3
    for i, (label, key) in enumerate(stats(s)):
        x = x0 + i * (colw + gap)
        v, yr = latest(s, key)
        d.rectangle([x * X, 372 * X, (x + colw) * X, 376 * X], fill=col)
        big = 64 if v[0].isdigit() or v[0] == "<" else 40
        d.text((x * X, 444 * X), v, font=_font("BarlowCondensed-ExtraBold", big), fill=INK if v[0].isdigit() or v[0] == "<" else INK2, anchor="ls")
        d.text((x * X, 458 * X), label, font=_font("Barlow-Medium", 24), fill=INK, anchor="lt")
        if yr:
            d.text((x * X, 490 * X), yr, font=_font("Barlow-Regular", 20), fill=INK2, anchor="lt")

    foot = "schools.ateya.org"
    fy = (H - 40) * X
    d.text((64 * X, fy), foot, font=_font("Barlow-SemiBold", 22), fill=BLUE, anchor="ls")
    d.text((64 * X + d.textlength(foot + " ", font=_font("Barlow-SemiBold", 22)), fy),
           "· CPS and Illinois Report Card data, every number with its school year", font=_font("Barlow-Medium", 22), fill=INK2, anchor="ls")

    out = img.resize((W, H), Image.LANCZOS).quantize(colors=48, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    return out


def page_html(s, card_version):
    e = lambda t: html.escape(t, quote=True)
    name, desc = display_name(s), description(s)
    url, img = f"{SITE_URL}/s/{s['id']}/", f"{SITE_URL}/s/{s['id']}/card.png?v={card_version}"
    title = f"{name} · CPS Facts"
    sid = json.dumps(s["id"])
    return f"""<!doctype html><html lang=en><head><meta charset=utf-8><meta name=viewport content="width=device-width, initial-scale=1">
<title>{e(title)}</title><meta name=description content="{e(desc)}"><link rel=canonical href="{url}">
<link rel=icon href=/favicon.svg type=image/svg+xml><link rel=apple-touch-icon href=/apple-touch-icon.png>
<meta property=og:type content=website><meta property=og:site_name content="CPS Facts"><meta property=og:title content="{e(name)}">
<meta property=og:description content="{e(desc)}"><meta property=og:url content="{url}">
<meta property=og:image content="{img}"><meta property=og:image:width content=1200><meta property=og:image:height content=630>
<meta property=og:image:alt content="{e(name)}: {e(desc)}">
<meta name=twitter:card content=summary_large_image><meta name=twitter:title content="{e(name)}"><meta name=twitter:description content="{e(desc)}"><meta name=twitter:image content="{img}">
<script>var u=new URLSearchParams(location.hash.slice(1));u.set("school",{sid});location.replace("/#"+u)</script>
<link rel=stylesheet href=/chicago.css><style>body{{max-width:720px;margin:0 auto;padding:16px;font-family:var(--font-text);background:var(--page);color:var(--ink)}}img{{max-width:100%;height:auto}}a{{color:var(--blue)}}</style>
</head><body><h1>{e(name)}</h1><p>{e(desc)}</p><p><a href="/#school={e(s['id'])}">Open this school on the CPS Facts map</a></p>
<img src="card.png?v={card_version}" width=1200 height=630 alt=""></body></html>
"""


def _write_one(args):
    s, geo, dest = args
    dest.mkdir(parents=True, exist_ok=True)
    png = dest / "card.png"
    img = card_png(s, geo)
    # rewrite only when the pixels change, so a rebuild with the same data leaves git clean
    if not png.exists() or Image.open(png).convert("RGB").tobytes() != img.convert("RGB").tobytes():
        img.save(png, optimize=True)
    version = hashlib.sha256(png.read_bytes()).hexdigest()[:8]
    (dest / "index.html").write_text(page_html(s, version))


def write_all(data, site):
    out = Path(site) / "s"
    ids = {s["id"] for s in data["schools"]}
    with ProcessPoolExecutor() as pool:
        list(pool.map(_write_one, [(s, data["map"], out / s["id"]) for s in data["schools"]], chunksize=16))
    for old in out.iterdir():  # schools that left the roster
        if old.is_dir() and old.name not in ids:
            shutil.rmtree(old)
    return len(ids)


if __name__ == "__main__":
    site = ROOT / "site"
    n = write_all(json.load(open(site / "data" / "schools.json")), site)
    print(f"{n} share pages and cards in {site / 's'}")
