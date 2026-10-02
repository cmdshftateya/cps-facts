"""Ask: a private chart builder over the published data.

v1 is deterministic: pick X and Y metrics, years and filters from menus; the server
builds the SQL, labels the outliers (largest residuals from the trend line) and the
page draws the chart. Same choices, same chart, no model, no cost.

Optional: with ANTHROPIC_API_KEY set, a question box also appears, where Claude writes
the SQL from plain English (each question costs API money; the page shows how much).
Local only: binds 127.0.0.1, never deployed (it lives outside site/).

    .venv/bin/python tools/ask/server.py [--port 8899]
"""
import argparse
import csv
import json
import math
import sqlite3
import sys
import threading
import time
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from pipeline.metrics import REGISTRY, SOURCES  # noqa: E402

HERE = Path(__file__).resolve().parent
MODEL = "claude-opus-5-5"
PRICE_IN, PRICE_OUT = 4.00, 20.00          # $ per million tokens, Claude Opus 5.5 standard rate
MAX_TOOL_ROUNDS = 10
SQL_ROW_CAP = 100                          # rows returned to the model from run_sql
CHART_ROW_CAP = 1000

SCHOOL_COLS = ["school_id", "name", "long_name", "type", "governance", "network", "school_type",
               "grades_served", "band", "community_area", "ward", "subdistrict", "lat", "lon"]


# ---------- data ----------

def build_db():
    db = sqlite3.connect(":memory:", check_same_thread=False)
    db.execute(f"CREATE TABLE schools ({', '.join(SCHOOL_COLS)})")
    with open(ROOT / "data" / "schools.csv", newline="") as f:
        rows = [[r[c] or None for c in SCHOOL_COLS] for r in csv.DictReader(f)]
    db.executemany(f"INSERT INTO schools VALUES ({','.join('?' * len(SCHOOL_COLS))})", rows)

    db.execute("CREATE TABLE vals (school_id, metric, school_year, value REAL, status, unit, source)")
    with open(ROOT / "data" / "school_values.csv", newline="") as f:
        rows = [(r["school_id"], r["metric"], r["school_year"],
                 float(r["value"]) if r["status"] == "value" and r["value"] not in ("", "*") else None,
                 r["status"], r["unit"], r["source"]) for r in csv.DictReader(f)]
    db.executemany("INSERT INTO vals VALUES (?,?,?,?,?,?,?)", rows)
    db.execute("CREATE INDEX vals_m ON vals (metric, school_year)")
    db.execute("CREATE INDEX vals_s ON vals (school_id)")
    db.execute("PRAGMA query_only = ON")
    return db


DB = build_db()
DB_LOCK = threading.Lock()


def run_query(sql, cap):
    s = sql.strip().rstrip(";")
    if not s.lower().startswith(("select", "with")):
        raise ValueError("Only SELECT (or WITH ... SELECT) queries are allowed.")
    with DB_LOCK:
        deadline = time.time() + 5
        DB.set_progress_handler(lambda: 1 if time.time() > deadline else 0, 10000)
        try:
            cur = DB.execute(s)
            cols = [d[0] for d in cur.description]
            rows = cur.fetchmany(cap + 1)
        finally:
            DB.set_progress_handler(None, 0)
    return cols, rows[:cap], len(rows) > cap


def data_dictionary():
    with DB_LOCK:
        counts = DB.execute("SELECT metric, school_year, SUM(status='value'), SUM(status='suppressed') "
                            "FROM vals GROUP BY 1, 2").fetchall()
    have = {}
    for m, y, n, sup in counts:
        have.setdefault(m, []).append(f"{y} ({n}" + (f", {sup} suppressed" if sup else "") + ")")
    lines = []
    for mid, m in REGISTRY.items():
        if mid not in have:
            continue
        line = f"- `{mid}`: {m['label']} [unit {m['unit']}; source {m['source']}; years {', '.join(have[mid])}]"
        if m["breaks"]:
            line += f" BREAK at {', '.join(m['breaks'])}: not comparable with earlier years."
        if m["note"]:
            line += f" Note: {m['note']}"
        lines.append(line)
    extra = sorted(set(have) - set(REGISTRY))
    if extra:
        lines.append(f"- Also present (grade-level 20th-day enrollment counts, unit count): {', '.join(extra)}")
    src = "\n".join(f"- {k}: {v['name']}" for k, v in SOURCES.items())
    return "\n".join(lines), src


METRICS_TEXT, SOURCES_TEXT = data_dictionary()

SYSTEM = f"""You are the data analyst behind CPS Facts, a site with facts about every Chicago public school. \
This is a private tool for the site's owner: he asks questions in plain English, often dictated and terse, and \
you answer with charts and short, exact explanations.

## Database (SQLite, read-only)

`schools` — one row per school (639): {", ".join(SCHOOL_COLS)}.
  `type` is district/charter/contract/options etc.; `band` is ES/MS/HS; `name` is the short display name.
`vals` — long format, one row per school × metric × school year: school_id, metric, school_year ('2024-25' style), \
value (REAL; NULL when suppressed), status ('value' or 'suppressed'), unit, source.
  Percentages are 0–100. Dollars are plain numbers.

Metrics:
{METRICS_TEXT}

Sources:
{SOURCES_TEXT}

Pivot pattern for two metrics per school:
```sql
SELECT s.school_id, s.name,
  MAX(CASE WHEN v.metric='pct_low_income' AND v.school_year='2024-25' THEN v.value END) AS x,
  MAX(CASE WHEN v.metric='math_growth'    AND v.school_year='2024-25' THEN v.value END) AS y
FROM schools s JOIN vals v USING (school_id)
GROUP BY s.school_id
HAVING x IS NOT NULL AND y IS NOT NULL
```

## Tools

- `run_sql`: explore (check years, counts, distributions) before charting when unsure.
- `make_chart`: draw a chart. Its SQL must return `name` and `y`, plus `x` for scatter; optional `school_id`, \
`group` (a category to color by) and `label` (a short text shown instead of name). The server labels the outliers \
itself (scatter: the schools farthest from the trend line) and tells you which ones it labeled.

## Data rules (these are the site's integrity rules; never break them)

- Suppressed is not zero and missing is not zero. Exclude them, and say how many schools were left out if it matters.
- Every number has a school year. Put the year(s) in the chart subtitle. Pair years sensibly across axes \
(usually the same school year) and say which you used.
- Never compute change across a BREAK listed above (e.g. IAR proficiency 2023-24 → 2024-25 is not comparable).
- Outliers are labeled, never dropped.
- If a question is ambiguous, pick the most reasonable reading, say in one line which one, and go. Examples: \
"poverty" = pct_low_income; "grew in math" = math_growth (a growth percentile, 50 = typical), not a change in proficiency.
- A question with two goals ("grew the most but had the highest poverty") is usually best as a scatter of the two, \
with the answer named from the labeled corner.

## Answer style

After the chart, 2–5 sentences: the direct answer with school names and values, n, years, and any caveat that \
changes the reading. Plain text, no headings. Don't repeat the chart title. Don't invent numbers: only state \
values you got from a tool."""

TOOLS = [
    {
        "name": "run_sql",
        "description": "Run a read-only SQLite SELECT against the `schools` and `vals` tables. Returns up to "
                       f"{SQL_ROW_CAP} rows. Use it to explore before charting.",
        "input_schema": {
            "type": "object",
            "properties": {"sql": {"type": "string", "description": "A single SELECT or WITH query."}},
            "required": ["sql"],
        },
    },
    {
        "name": "make_chart",
        "description": "Draw a chart for the user from a SQL query. Scatter: the query returns name, x, y (one row per "
                       "school). Bar: name, y (already ordered and limited, e.g. top 20). Optional columns: school_id, "
                       "group, label. Returns the number of points and the outliers that were labeled.",
        "input_schema": {
            "type": "object",
            "properties": {
                "kind": {"type": "string", "enum": ["scatter", "bar"]},
                "sql": {"type": "string"},
                "title": {"type": "string", "description": "Short headline that states the finding or the comparison."},
                "subtitle": {"type": "string", "description": "What is plotted, the school year(s), the filter, and n."},
                "x_label": {"type": "string", "description": "Axis label with unit, e.g. 'Low income students (%), 2024-25'."},
                "y_label": {"type": "string"},
                "label_outliers": {"type": "integer", "description": "How many outliers to label (scatter). Default 8."},
                "label_names": {"type": "array", "items": {"type": "string"},
                                "description": "School names to always label, e.g. ones the user asked about."},
                "trend_line": {"type": "boolean", "description": "Draw the least-squares line (scatter). Default true."},
                "note": {"type": "string", "description": "Footnote: source names and caveats."},
            },
            "required": ["kind", "sql", "title", "y_label"],
        },
    },
]


# ---------- charts ----------

def fit(points):
    n = len(points)
    mx = sum(p["x"] for p in points) / n
    my = sum(p["y"] for p in points) / n
    sxx = sum((p["x"] - mx) ** 2 for p in points)
    if sxx == 0:
        return None
    b = sum((p["x"] - mx) * (p["y"] - my) for p in points) / sxx
    a = my - b * mx
    syy = sum((p["y"] - my) ** 2 for p in points)
    r = b * math.sqrt(sxx / syy) if syy else 0
    return {"a": a, "b": b, "r": r}


def build_chart(spec):
    kind = spec.get("kind", "scatter")
    cols, rows, truncated = run_query(spec["sql"], CHART_ROW_CAP)
    need = {"name", "y"} | ({"x"} if kind == "scatter" else set())
    missing = need - set(cols)
    if missing:
        raise ValueError(f"Query must return columns {sorted(need)}; missing {sorted(missing)}. Got {cols}.")
    points, dropped = [], 0
    for row in rows:
        p = dict(zip(cols, row))
        try:
            p["y"] = float(p["y"])
            if kind == "scatter":
                p["x"] = float(p["x"])
        except (TypeError, ValueError):
            dropped += 1
            continue
        points.append({k: p.get(k) for k in ("school_id", "name", "x", "y", "group", "label") if k in p})
    if not points:
        raise ValueError("The query returned no plottable rows.")

    line = None
    if kind == "scatter":
        line = fit(points) if len(points) > 2 else None
        n_label = max(0, int(spec.get("label_outliers", 8)))
        always = {s.lower() for s in spec.get("label_names", [])}
        if line:
            res = [p["y"] - (line["a"] + line["b"] * p["x"]) for p in points]
            sd = math.sqrt(sum(r * r for r in res) / len(res)) or 1
            for p, r in zip(points, res):
                p["resid_z"] = round(r / sd, 2)
            ranked = sorted(range(len(points)), key=lambda i: -abs(points[i]["resid_z"]))
        else:
            ranked = []
        for i in ranked[:n_label]:
            points[i]["outlier"] = True
        for p in points:
            if str(p["name"]).lower() in always:
                p["outlier"] = True
        if spec.get("trend_line", True) is False:
            line = {**line, "hidden": True} if line else None

    chart = {"id": uuid.uuid4().hex[:8], "kind": kind, "points": points, "fit": line, "truncated": truncated,
             "dropped": dropped,
             **{k: spec.get(k) for k in ("title", "subtitle", "x_label", "y_label", "note", "sql",
                                         "label_outliers", "label_names", "trend_line")}}
    labeled = [p for p in points if p.get("outlier")]
    summary = {
        "points": len(points),
        "rows_without_numbers_dropped": dropped,
        "truncated_at": CHART_ROW_CAP if truncated else None,
        "groups": sorted({str(p["group"]) for p in points if p.get("group") is not None}) or None,
    }
    if kind == "scatter":
        summary["x_range"] = [min(p["x"] for p in points), max(p["x"] for p in points)]
        summary["y_range"] = [min(p["y"] for p in points), max(p["y"] for p in points)]
        if line:
            summary["trend"] = {"slope": round(line["b"], 4), "intercept": round(line["a"], 2), "r": round(line["r"], 3)}
        summary["labeled_outliers"] = [
            {"name": p["name"], "x": p["x"], "y": p["y"], "resid_z": p.get("resid_z"),
             "side": "above trend" if p.get("resid_z", 0) > 0 else "below trend"} for p in labeled]
    else:
        summary["bars"] = [{"name": p["name"], "y": p["y"]} for p in points[:40]]
    return chart, summary


# ---------- deterministic builder (no model) ----------

FILTERS = {"type": "School type", "band": "Grade band"}


def catalog():
    """Metrics present in data/, with years and labels, plus filter values, for the builder's menus."""
    with DB_LOCK:
        have = DB.execute("SELECT metric, school_year, COUNT(value) FROM vals GROUP BY 1, 2 ORDER BY 1, 2").fetchall()
        filters = {f: [r[0] for r in DB.execute(f"SELECT {f}, COUNT(*) c FROM schools GROUP BY 1 ORDER BY c DESC")]
                   for f in FILTERS}
    years = {}
    for m, y, n in have:
        if n:
            years.setdefault(m, []).append(y)
    metrics = [{"id": mid, "label": m["label"], "unit": m["unit"], "family": m["family"], "years": years[mid],
                "breaks": m["breaks"], "note": m["note"], "source": SOURCES.get(m["source"], {}).get("name", m["source"])}
               for mid, m in REGISTRY.items() if mid in years]
    return {"metrics": metrics, "filters": filters, "filter_labels": FILTERS}


CATALOG = catalog()
METRIC = {m["id"]: m for m in CATALOG["metrics"]}


def plot(req):
    """Build a chart from menu choices. Same choices, same chart: no model involved."""
    kind = req.get("kind", "scatter")
    if kind not in ("scatter", "bar"):
        raise ValueError("kind must be scatter or bar")
    axes = ["y"] + (["x"] if kind == "scatter" else [])
    sel, params = [], []
    for ax in axes:
        a = req.get(ax) or {}
        m = METRIC.get(a.get("metric"))
        if not m or a.get("year") not in m["years"]:
            raise ValueError(f"Pick a metric and one of its school years for {ax.upper()}.")
        sel.append(f"MAX(CASE WHEN v.metric = ? AND v.school_year = ? THEN v.value END) AS {ax}")
        params += [m["id"], a["year"]]
    where, wparams = [], []
    for f in FILTERS:
        vals = [v for v in (req.get("filters") or {}).get(f, []) if v in CATALOG["filters"][f]]
        if vals:
            where.append(f"s.{f} IN ({','.join('?' * len(vals))})")
            wparams += vals
    color = req.get("color_by") if req.get("color_by") in FILTERS else None
    sql = (f"SELECT s.school_id, s.name{f', s.{color} AS \"group\"' if color else ''}, {', '.join(sel)}\n"
           f"FROM schools s JOIN vals v USING (school_id)\n"
           + (f"WHERE {' AND '.join(where)}\n" if where else "")
           + "GROUP BY s.school_id\nHAVING " + " AND ".join(f"{ax} IS NOT NULL" for ax in axes))
    if kind == "bar":
        n = max(1, min(60, int(req.get("top", 20))))
        sql += f"\nORDER BY y {'ASC' if req.get('order') == 'asc' else 'DESC'}\nLIMIT {n}"
    literal = sql
    for p_ in params[:len(sel) * 2] + wparams:   # inline the checked values so the SQL box can be edited and re-run
        literal = literal.replace("?", "'" + str(p_).replace("'", "''") + "'", 1)

    ym = METRIC[req["y"]["metric"]]
    xm = METRIC[req["x"]["metric"]] if kind == "scatter" else None
    lab = lambda m, y: f"{m['label']}, {y}"
    filt = "; ".join(f"{FILTERS[f]}: {', '.join(v)}" for f, v in (req.get("filters") or {}).items() if v)
    spec = {
        "kind": kind, "sql": literal,
        "y_label": lab(ym, req["y"]["year"]),
        "x_label": lab(xm, req["x"]["year"]) if xm else None,
        "title": (f"{ym['label']} vs {xm['label'][0].lower() + xm['label'][1:]}" if xm else
                  f"{'Lowest' if req.get('order') == 'asc' else 'Highest'} {ym['label'][0].lower() + ym['label'][1:]}"),
        "label_outliers": int(req.get("label_outliers", 8)),
        "label_names": [s_.strip() for s_ in req.get("label_names", []) if s_.strip()],
        "trend_line": req.get("trend_line", True),
    }
    used = [m for m in (ym, xm) if m]
    notes = [f"Sources: {'; '.join(dict.fromkeys(m['source'] for m in used))}.",
             "Suppressed and missing values are left out, never counted as zero."]
    notes += [f"{m['label']}: {m['note']}" for m in used if m["note"]]
    spec["note"] = " ".join(notes)
    chart, summary = build_chart(spec)
    spec_years = sorted({req[a]["year"] for a in axes})
    chart["subtitle"] = (f"{summary['points']} schools · school year{'s' if len(spec_years) > 1 else ''} "
                         f"{' and '.join(spec_years)}" + (f" · {filt}" if filt else ""))
    return chart, summary


# ---------- conversation ----------

CONVERSATIONS = {}


def client():
    import anthropic
    return anthropic.Anthropic()


def ask(conv_id, message):
    history = CONVERSATIONS.setdefault(conv_id, [])
    start = len(history)
    history.append({"role": "user", "content": message})
    charts, queries, usage = [], [], {"input": 0, "output": 0, "cache_read": 0, "cache_write": 0}
    c = client()
    for _ in range(MAX_TOOL_ROUNDS):
        try:
            resp = c.beta.messages.create(
                model=MODEL,
                max_tokens=16000,
                system=SYSTEM,
                tools=TOOLS,
                messages=history,
                cache_control={"type": "ephemeral"},
                output_config={"effort": "medium"},
                betas=["server-side-fallback-2026-07-01"],
                fallbacks="default",
            )
        except Exception:
            del history[start:]  # drop this question's partial turns so the next question starts clean
            raise
        u = resp.usage
        usage["input"] += u.input_tokens
        usage["output"] += u.output_tokens
        usage["cache_read"] += u.cache_read_input_tokens or 0
        usage["cache_write"] += u.cache_creation_input_tokens or 0
        history.append({"role": "assistant", "content": resp.content})

        if resp.stop_reason == "refusal":
            return reply("The model declined this request.", charts, queries, usage)
        if resp.stop_reason != "tool_use":
            text = "\n\n".join(b.text for b in resp.content if b.type == "text")
            return reply(text, charts, queries, usage)

        results = []
        for b in resp.content:
            if b.type != "tool_use":
                continue
            try:
                if b.name == "run_sql":
                    cols, rows, trunc = run_query(b.input["sql"], SQL_ROW_CAP)
                    queries.append(b.input["sql"])
                    out = {"columns": cols, "rows": rows, "truncated_at": SQL_ROW_CAP if trunc else None}
                elif b.name == "make_chart":
                    chart, out = build_chart(b.input)
                    charts.append(chart)
                else:
                    raise ValueError(f"Unknown tool {b.name}")
                results.append({"type": "tool_result", "tool_use_id": b.id, "content": json.dumps(out, default=str)})
            except (ValueError, KeyError, sqlite3.Error) as e:
                results.append({"type": "tool_result", "tool_use_id": b.id, "content": f"Error: {e}", "is_error": True})
        history.append({"role": "user", "content": results})
    return reply("Stopped after too many tool calls.", charts, queries, usage)


def reply(text, charts, queries, usage):
    uncached = usage["input"]
    cost = (uncached * PRICE_IN + usage["cache_write"] * PRICE_IN * 1.25 + usage["cache_read"] * PRICE_IN * 0.1
            + usage["output"] * PRICE_OUT) / 1e6
    return {"text": text, "charts": charts, "queries": queries, "usage": usage, "cost_usd": round(cost, 4)}


# ---------- http ----------

class Handler(BaseHTTPRequestHandler):
    def _send(self, code, body, ctype="application/json"):
        data = body if isinstance(body, bytes) else json.dumps(body, default=str).encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            return self._send(200, (HERE / "index.html").read_bytes(), "text/html; charset=utf-8")
        if self.path == "/api/status":
            import os
            return self._send(200, {"model": MODEL, "key": bool(os.environ.get("ANTHROPIC_API_KEY"))})
        if self.path == "/api/catalog":
            return self._send(200, CATALOG)
        self._send(404, {"error": "not found"})

    def do_POST(self):
        try:
            body = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
            if self.path == "/api/chat":
                return self._send(200, ask(body.get("conv_id") or "default", body["message"]))
            if self.path == "/api/plot":    # the deterministic builder
                chart, summary = plot(body)
                return self._send(200, {"chart": chart, "summary": summary})
            if self.path == "/api/chart":   # re-run an edited chart spec without the model
                chart, summary = build_chart(body)
                return self._send(200, {"chart": chart, "summary": summary})
            if self.path == "/api/reset":
                CONVERSATIONS.pop(body.get("conv_id"), None)
                return self._send(200, {"ok": True})
            self._send(404, {"error": "not found"})
        except Exception as e:  # surface every failure in the page; this is a local tool
            self._send(400, {"error": f"{type(e).__name__}: {e}"})

    def log_message(self, fmt, *args):
        sys.stderr.write("%s %s\n" % (self.command, self.path))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8899)
    port = ap.parse_args().port
    print(f"Ask: http://127.0.0.1:{port}  (model {MODEL})", flush=True)
    ThreadingHTTPServer(("127.0.0.1", port), Handler).serve_forever()


if __name__ == "__main__":
    main()
