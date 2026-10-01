"""Write site/og.png (1200x630 social preview) and site/apple-touch-icon.png.

    python3 tools/make_og.py        # needs rsvg-convert (brew install librsvg)

Static brand assets; re-run only when the mark or palette changes. Colours are chicago.css tokens.
"""
import pathlib
import subprocess

SITE = pathlib.Path(__file__).resolve().parent.parent / "site"
PAGE, INK, INK2, BLUE, RED = "#0c0e10", "#f0ece5", "#b9b3a9", "#4bb3e8", "#e6635b"
STAR = [(.5, 0), (.644, .25), (.933, .25), (.789, .5), (.933, .75), (.644, .75), (.5, 1), (.356, .75), (.067, .75), (.211, .5), (.067, .25), (.356, .25)]


def star(cx, cy, size, fill):
    pts = " ".join(f"{cx - size / 2 + x * size:.1f},{cy - size / 2 + y * size:.1f}" for x, y in STAR)
    return f'<polygon points="{pts}" fill="{fill}"/>'


og = f"""<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630" viewBox="0 0 1200 630">
<rect width="1200" height="630" fill="{PAGE}"/>
<rect y="70" width="1200" height="34" fill="{BLUE}"/><rect y="526" width="1200" height="34" fill="{BLUE}"/>
{star(1010, 315, 230, RED)}
<text x="84" y="290" font-family="Barlow Condensed, Helvetica Neue, Arial, sans-serif" font-weight="900" font-size="150" fill="{INK}" letter-spacing="4">CPS FACTS</text>
<text x="84" y="360" font-family="Helvetica Neue, Helvetica, Arial, sans-serif" font-size="36" fill="{INK2}">Every Chicago public school on one map:</text>
<text x="84" y="406" font-family="Helvetica Neue, Helvetica, Arial, sans-serif" font-size="36" fill="{INK2}">enrollment, outcomes and spending, with sources.</text>
<text x="84" y="480" font-family="Helvetica Neue, Helvetica, Arial, sans-serif" font-size="30" fill="{BLUE}">schools.ateya.org</text>
</svg>"""
icon = f"""<svg xmlns="http://www.w3.org/2000/svg" width="180" height="180" viewBox="0 0 32 32"><rect width="32" height="32" fill="{PAGE}"/>
<rect y="5.5" width="32" height="5" fill="#2f9bd4"/><rect y="21.5" width="32" height="5" fill="#2f9bd4"/>
<path d="M16,-1L20.91,7.5L30.72,7.5L25.81,16L30.72,24.5L20.91,24.5L16,33L11.09,24.5L1.28,24.5L6.19,16L1.28,7.5L11.09,7.5Z" fill="#d92d3d"/></svg>"""
for name, svg in (("og", og), ("apple-touch-icon", icon)):
    subprocess.run(["rsvg-convert", "-o", str(SITE / f"{name}.png")], input=svg.encode(), check=True)
