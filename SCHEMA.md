# schools.json contract (Phase 1 output ↔ Phase 2 input)

Phase 2 (`site/index.html`) reads only `data/schools.json`. Phase 1's `build.py` must emit this shape; until then `make_fixture.py` writes a synthetic file.

```
{ "generated": ISO date, "roster_sy": "2026-27",
  "sources": { id: label },
  "viewbox": [w, h],             // SVG units for x/y below
  "context": [ "<svg path d>" ], // city outline, lake, subdistrict lines (hairline); may be empty
  "schools": [ {
    "id": "400009", "rcdts": "15016299025229C" | null, "name": str,
    "type": "district" | "charter" | "contract" | "options",
    "band": "ES" | "HS" | "combo", "network": str,
    "subdistrict": "1a".."10b", "community": str, "address": str,
    "x": num, "y": num,           // projected at build time into viewbox
    "m": { metric_id: { "v": number | null | "*", "sy": "2024-25", "t": [oldest..newest]? } }
  } ] }
```

- `v: null` = no data, `v: "*"` = suppressed (ISBE). Never 0 for either.
- `t` = up to 3-year trend, oldest first. Omit for 2024→2025 test-score metrics (cut scores changed).
- Metric ids: `enroll`, `enroll_chg`, `low_income`, `el`, `iep`, `pct_hispanic`, `pct_black`, `pct_white`, `pct_asian`, `isbe_pp`, `cps_pp`, `ela`, `math`, `grade11`, `attendance`, `chronic`, `grad`.
