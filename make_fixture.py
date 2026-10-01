"""Synthetic site/data/schools.json that follows SCHEMA.md. Placeholder until the Phase 1 pipeline (build.py) exists."""
import json, random
random.seed(7)
SY = "2024-25"
SUBS = [f"{n}{l}" for n in range(1, 11) for l in "ab"]
NETWORKS = ["Network 1", "Network 2", "Network 3", "Network 4", "Network 5", "Charter", "Options"]
HOODS = ["Austin", "Englewood", "Pilsen", "Lincoln Park", "Rogers Park", "Bronzeville", "Hyde Park", "Logan Square", "Gage Park", "Beverly"]
STREETS = ["Cicero Ave", "Halsted St", "Western Ave", "Kedzie Ave", "Pulaski Rd", "Ashland Ave", "Damen Ave", "State St"]

def clamp(v, lo=0, hi=100): return max(lo, min(hi, v))
def metric(v, trend=None):
    r = random.random()
    if r < 0.04: return {"v": "*", "sy": SY}
    if r < 0.08: return {"v": None, "sy": SY}
    m = {"v": round(v, 1), "sy": SY}
    if trend: m["t"] = [round(t, 1) for t in trend]
    return m

schools = []
for i in range(639):
    t = random.choices(["district", "charter", "contract", "options"], [0.72, 0.17, 0.05, 0.06])[0]
    band = random.choices(["ES", "HS", "combo"], [0.7, 0.2, 0.1])[0]
    x = clamp(random.gauss(500, 140), 60, 940); y = clamp(random.gauss(520, 230), 40, 960)
    south_west = (x - 400) / 600 + (y - 500) / 900   # synthetic "disadvantage" gradient so the map shows a pattern
    base = clamp(50 - 30 * south_west + random.gauss(0, 8))
    enr = int(clamp(random.lognormvariate(6.1, 0.55), 40, 2800, ))
    e1, e2 = enr * random.uniform(0.9, 1.1), enr * random.uniform(0.85, 1.15)
    hisp = clamp(random.gauss(45, 28)); black = clamp(random.gauss(30 + 20 * south_west, 25), 0, 100 - hisp)
    white = clamp(random.gauss(15, 12), 0, 100 - hisp - black); asian = clamp(random.gauss(4, 3), 0, 100 - hisp - black - white)
    m = {
        "enroll": {"v": enr, "sy": "2026-27", "t": [round(e2), round(e1), enr]},
        "enroll_chg": {"v": round((enr - e2) / e2 * 100, 1), "sy": "2026-27"},
        "low_income": {"v": round(clamp(70 - 25 * -south_west + random.gauss(0, 10)), 1), "sy": "2026-27"},
        "el": {"v": round(clamp(random.gauss(18, 15)), 1), "sy": "2026-27"},
        "iep": {"v": round(clamp(random.gauss(16, 6)), 1), "sy": "2026-27"},
        "pct_hispanic": {"v": round(hisp, 1), "sy": "2026-27"}, "pct_black": {"v": round(black, 1), "sy": "2026-27"},
        "pct_white": {"v": round(white, 1), "sy": "2026-27"}, "pct_asian": {"v": round(asian, 1), "sy": "2026-27"},
        "isbe_pp": metric(random.gauss(21000, 5000)), "cps_pp": metric(random.gauss(15000, 4500)),
        "attendance": metric(clamp(random.gauss(92 + base / 25, 2), 70, 99), [clamp(random.gauss(90 + base / 25, 2), 70, 99) for _ in range(3)]),
        "chronic": metric(clamp(random.gauss(40 - base / 3, 10)), [clamp(random.gauss(40 - base / 3, 10)) for _ in range(3)]),
    }
    if band in ("ES", "combo"):
        m["ela"] = metric(clamp(base + random.gauss(0, 10))); m["math"] = metric(clamp(base - 5 + random.gauss(0, 10)))
    if band in ("HS", "combo"):
        m["grade11"] = metric(clamp(base - 10 + random.gauss(0, 10)))
        m["grad"] = metric(clamp(random.gauss(70 + base / 5, 8)), [clamp(random.gauss(70 + base / 5, 5)) for _ in range(3)])
    schools.append({
        "id": str(400000 + i), "rcdts": f"150162990{i:05d}C", "name": f"Fixture School {i + 1}",
        "type": t, "band": band, "network": "Charter" if t == "charter" else random.choice(NETWORKS[:5] + ["Options"]),
        "subdistrict": random.choice(SUBS), "community": random.choice(HOODS),
        "address": f"{random.randint(100, 9999)} S {random.choice(STREETS)}",
        "x": round(x, 1), "y": round(y, 1), "m": m,
    })
out = {"generated": "fixture", "roster_sy": "2026-27",
       "sources": {"cps_mem": "CPS 20th-day membership", "isbe_rc": "Illinois Report Card 2025", "cps_bud": "CPS FY27 budget export"},
       "viewbox": [1000, 1000], "context": [], "schools": schools}
json.dump(out, open("site/data/schools.json", "w"), separators=(",", ":"))
print(len(schools), "schools")
