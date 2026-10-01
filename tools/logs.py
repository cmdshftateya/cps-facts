"""Skim the project's logs without reading them whole: decisions, the work log, open threads, outreach.

    python3 tools/logs.py                          # brief: open threads, latest sessions, active decisions (one line each)
    python3 tools/logs.py decisions                # index of every decision
    python3 tools/logs.py decisions D-004 D-010    # full text of those entries
    python3 tools/logs.py decisions --tag budget   # filter by tag (repeatable); --active hides superseded ones
    python3 tools/logs.py decisions --grep ACT     # case-insensitive search over the full text
    python3 tools/logs.py decisions --tags         # tags with counts
    python3 tools/logs.py decisions --next         # next free D-0xx id
    python3 tools/logs.py worklog                  # index of sessions, newest first; -n 5 for the latest five
    python3 tools/logs.py worklog 3413053b         # full entry for a session (prefix match)
    python3 tools/logs.py worklog --grep stash     # sessions mentioning a word; --decision D-013 for those citing a decision
    python3 tools/logs.py threads                  # open threads from WORKLOG.md
    python3 tools/logs.py outreach                 # emails sent and whether they've been answered

Every command takes --json for the parsed records. The formats are documented at the top of
DECISIONS.md, WORKLOG.md and emails.md; tests/test_logs.py fails if a file drifts from them.
Standard library only.
"""
import argparse
import json
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
DECISIONS, WORKLOG, OUTREACH = REPO / "DECISIONS.md", REPO / "WORKLOG.md", REPO / "emails.md"

DEC_HEAD = re.compile(r"^## (D-\d{3}) · (.+)$")
LOG_HEAD = re.compile(r"^## (.+?) · (.+) · `([0-9a-f]{8})`$")
FIELD = re.compile(r"^(?:- )?\*\*([A-Z][A-Za-z ]*):\*\* ?(.*)$")
DEC_ID = re.compile(r"D-\d{3}")


def sections(path, level="## "):
    """Split a markdown file into (heading, body lines), skipping anything inside code fences."""
    out, cur, fence = [], None, False
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("```"):
            fence = not fence
        if not fence and line.startswith(level):
            cur = (line, [])
            out.append(cur)
        elif cur and not fence:
            cur[1].append(line)
    return out


def fields(body):
    """`**Key:** value` lines (bulleted or not) -> {key: value}; a value runs until the next field or blank line."""
    f, key = {}, None
    for line in body:
        m = FIELD.match(line)
        if m:
            key = m.group(1).lower()
            f[key] = m.group(2).strip()
        elif key and line.strip():
            f[key] += " " + line.strip()
        else:
            key = None
    return f


def decisions():
    out = []
    for head, body in sections(DECISIONS):
        m = DEC_HEAD.match(head)
        if not m:
            continue
        f = fields(body)
        out.append({
            "id": m.group(1), "title": m.group(2), "date": f.get("date"), "status": f.get("status"),
            "supersedes": f.get("supersedes"), "who": f.get("who"),
            "tags": [t.strip() for t in f.get("tags", "").split(",") if t.strip()],
            "where": f.get("where"), "decision": f.get("decision"), "why": f.get("why"),
        })
    return out


def worklog():
    out = []
    for head, body in sections(WORKLOG):
        m = LOG_HEAD.match(head)
        if not m:
            continue
        f = fields(body)
        text = "\n".join(body)
        out.append({
            "session": m.group(3), "when": m.group(1), "title": m.group(2),
            "asked": f.get("asked"), "done": f.get("done"), "obstacles": f.get("obstacles"),
            "decisions": f.get("decisions"), "commits": f.get("commits"),
            "decision_ids": sorted(set(DEC_ID.findall(f.get("decisions") or ""))),
            "text": text.strip(),
        })
    return out


def threads():
    for head, body in sections(WORKLOG):
        if head.strip() == "## Open threads":
            out = []
            for line in body:
                if line.startswith("- "):
                    m = re.match(r"- \*\*(.+?)\*\*:? ?(.*)", line)
                    out.append({"label": m.group(1).rstrip(":") if m else line[2:60], "text": (m.group(2) if m else line[2:]).strip()})
                elif line.strip() == "---":
                    break
            return out
    return []


def outreach():
    out = []
    for head, body in sections(OUTREACH):
        m = re.match(r"^## (\d+)\. (.+)$", head)
        if not m:
            continue
        f = fields(body)
        out.append({"n": int(m.group(1)), "title": m.group(2), "sent": f.get("sent"), "status": f.get("status"),
                    "related": f.get("related"), "subject": f.get("subject")})
    return out


def clip(s, n):
    s = s or ""
    return s if len(s) <= n else s[: n - 1] + "…"


def show_decision(d):
    print(f"## {d['id']} · {d['title']}")
    print(f"{d['date']} · {d['status']} · {d['who']} · tags: {', '.join(d['tags'])} · {d['where']}")
    if d["supersedes"]:
        print(f"Supersedes {d['supersedes']}")
    print(f"\nDecision: {d['decision']}\n\nWhy: {d['why']}\n")


def cmd_decisions(a):
    ds = decisions()
    if a.next:
        print(f"D-{max(int(d['id'][2:]) for d in ds) + 1:03d}")
        return
    if a.tags:
        counts = {}
        for d in ds:
            for t in d["tags"]:
                counts[t] = counts.get(t, 0) + 1
        rows = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
        print(json.dumps(dict(rows), indent=1) if a.json else "\n".join(f"{n:3}  {t}" for t, n in rows))
        return
    if a.ids:
        want = {"D-%03d" % int(re.sub(r"\D", "", i)) for i in a.ids}
        ds = [d for d in ds if d["id"] in want]
    for t in a.tag or []:
        ds = [d for d in ds if t in d["tags"]]
    if a.active:
        ds = [d for d in ds if d["status"] == "Active"]
    if a.grep:
        g = a.grep.lower()
        ds = [d for d in ds if g in json.dumps(d, ensure_ascii=False).lower()]
    if a.json:
        print(json.dumps(ds, indent=1, ensure_ascii=False))
    elif a.ids:
        for d in ds:
            show_decision(d)
    else:
        for d in ds:
            flag = "" if d["status"] == "Active" else f"  [{d['status']}]"
            print(f"{d['id']}  {d['date']}  {clip(d['who'].split(' (')[0], 14):14}  {d['title']}{flag}  ({', '.join(d['tags'])})")


def cmd_worklog(a):
    es = worklog()
    if a.ids:
        es = [e for e in es if any(e["session"].startswith(i) for i in a.ids)]
    if a.decision:
        es = [e for e in es if a.decision.upper() in e["decision_ids"]]
    if a.grep:
        es = [e for e in es if a.grep.lower() in (e["title"] + e["text"]).lower()]
    if a.n:
        es = es[: a.n]
    if a.json:
        print(json.dumps(es, indent=1, ensure_ascii=False))
    elif a.ids:
        for e in es:
            print(f"## {e['when']} · {e['title']} · {e['session']}\n\n{e['text']}\n")
    else:
        for e in es:
            ds = f"  [{', '.join(e['decision_ids'])}]" if e["decision_ids"] else ""
            print(f"{e['session']}  {clip(e['when'], 28):28}  {e['title']}{ds}")


def cmd_threads(a):
    ts = threads()
    if a.json:
        print(json.dumps(ts, indent=1, ensure_ascii=False))
    else:
        for t in ts:
            print(f"- {t['label']}: {clip(t['text'], 140 if a.short else 10_000)}")


def cmd_outreach(a):
    os_ = outreach()
    if a.json:
        print(json.dumps(os_, indent=1, ensure_ascii=False))
    else:
        for o in os_:
            print(f"{o['n']}. {o['title']}  ·  {o['status']}  ·  sent {o['sent']}  ·  related: {o['related']}")


def cmd_brief(a):
    if a.json:
        print(json.dumps({"threads": threads(), "worklog": worklog()[:3], "decisions": decisions(), "outreach": outreach()},
                         indent=1, ensure_ascii=False))
        return
    print("Open threads (WORKLOG.md):")
    cmd_threads(argparse.Namespace(json=False, short=True))
    print("\nLatest sessions (python3 tools/logs.py worklog <id> for one):")
    cmd_worklog(argparse.Namespace(ids=[], decision=None, grep=None, n=3, json=False))
    print("\nActive decisions (python3 tools/logs.py decisions D-0xx for one):")
    cmd_decisions(argparse.Namespace(next=False, tags=False, ids=[], tag=None, active=True, grep=None, json=False))
    pending = [o for o in outreach() if (o["status"] or "").lower().startswith("awaiting")]
    if pending:
        print(f"\nOutreach awaiting reply: {', '.join(o['title'] for o in pending)}")


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = p.add_subparsers(dest="cmd")
    b = sub.add_parser("brief")
    d = sub.add_parser("decisions")
    d.add_argument("ids", nargs="*")
    d.add_argument("--tag", action="append")
    d.add_argument("--grep")
    d.add_argument("--active", action="store_true")
    d.add_argument("--tags", action="store_true")
    d.add_argument("--next", action="store_true")
    w = sub.add_parser("worklog")
    w.add_argument("ids", nargs="*")
    w.add_argument("--grep")
    w.add_argument("--decision")
    w.add_argument("-n", type=int)
    t = sub.add_parser("threads")
    t.add_argument("--short", action="store_true")
    o = sub.add_parser("outreach")
    for s in (p, b, d, w, t, o):
        s.add_argument("--json", action="store_true")
    a = p.parse_args(argv)
    {"decisions": cmd_decisions, "worklog": cmd_worklog, "threads": cmd_threads,
     "outreach": cmd_outreach}.get(a.cmd, cmd_brief)(a)


if __name__ == "__main__":
    sys.exit(main())
