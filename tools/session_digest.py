"""Summarize Claude Code sessions for this repo, so WORKLOG.md can be kept current.

    python3 tools/session_digest.py              # list every session (start, end, first prompt, logged?)
    python3 tools/session_digest.py --missing    # only sessions not yet in WORKLOG.md (the SessionStart hook runs this)
    python3 tools/session_digest.py 3413053b     # one session: prompts, commits, and the assistant's longer reports

Reads the transcripts Claude Code keeps in ~/.claude/projects/<encoded repo path>/ (worktree
sessions included). A session counts as logged when its 8-character id appears in a WORKLOG.md entry heading.
Commits are found from `git commit -m` calls in the transcript and matched to current hashes by
subject, since history rewrites change hashes. Times are local. Standard library only.
"""
import datetime as dt
import glob
import json
import os
import pathlib
import re
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
WORKLOG = REPO / "WORKLOG.md"
ACTIVE_MIN = 30  # a session touched this recently may still be running


def transcript_dirs():
    root = str(REPO).split("/.claude/worktrees/")[0]  # from inside a worktree, use the main checkout's transcripts
    enc = re.sub(r"[^A-Za-z0-9]", "-", root)
    base = pathlib.Path.home() / ".claude" / "projects"
    return [pathlib.Path(p) for p in [base / enc, *glob.glob(str(base / (enc + "--claude-worktrees-*")))] if os.path.isdir(p)]


def text_of(content):
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return " ".join(c.get("text", "") for c in content if isinstance(c, dict) and c.get("type") == "text")
    return ""


def load(path):
    s = {"id": path.stem, "worktree": "--claude-worktrees-" in path.parent.name, "ts": [], "prompts": [], "reports": [], "subjects": [], "title": None}
    for line in open(path, encoding="utf-8", errors="replace"):
        try:
            d = json.loads(line)
        except ValueError:
            continue
        if d.get("timestamp"):
            s["ts"].append(d["timestamp"])
        if d.get("type") in ("summary", "custom-title"):
            s["title"] = d.get("customTitle") or d.get("summary") or s["title"]
        if d.get("type") == "user" and not d.get("isMeta"):
            t = re.sub(r"<system-reminder>.*?</system-reminder>", "", text_of(d.get("message", {}).get("content")), flags=re.S).strip()
            if t and not t.startswith("<") and not t.startswith("[Request interrupted"):
                s["prompts"].append((d["timestamp"], t))
        if d.get("type") == "assistant":
            for c in d.get("message", {}).get("content") or []:
                if c.get("type") == "text" and len(c["text"]) > 400:
                    s["reports"].append((d["timestamp"], c["text"]))
                if c.get("type") == "tool_use" and c.get("name") == "Bash":
                    for m in re.finditer(r"git commit[^\n]*?-m\s+(['\"])(.+?)(?:\1|\n)", c["input"].get("command", "")):
                        s["subjects"].append(m.group(2).strip())
    return s


def local(ts):
    return dt.datetime.fromisoformat(ts.replace("Z", "+00:00")).astimezone().strftime("%Y-%m-%d %H:%M")


def sessions():
    out = [load(p) for d in transcript_dirs() for p in d.glob("*.jsonl")]
    return sorted((s for s in out if s["prompts"]), key=lambda s: min(s["ts"]))


def commits_for(subjects):
    log = subprocess.run(["git", "-C", str(REPO), "log", "--all", "--format=%h\t%ad\t%s", "--date=format:%Y-%m-%d %H:%M"], capture_output=True, text=True).stdout
    rows = [r.split("\t", 2) for r in log.splitlines() if r.count("\t") >= 2]
    found = []
    for subj in subjects:
        hit = next((r for r in rows if r[2] == subj.splitlines()[0]), None)
        found.append(f"{hit[0]} {hit[1]} {hit[2]}" if hit else f"(not in current history) {subj.splitlines()[0]}")
    return found


def logged_ids():
    # only entry headings count ("## ... · `id`"); an id mentioned in prose or Open threads is not an entry
    heads = [l for l in WORKLOG.read_text().splitlines() if l.startswith("## ")] if WORKLOG.exists() else []
    return {i for l in heads for i in re.findall(r"`([0-9a-f]{8})`", l)}


def row(s, logged):
    age = (dt.datetime.now(dt.timezone.utc) - dt.datetime.fromisoformat(max(s["ts"]).replace("Z", "+00:00"))).total_seconds() / 60
    flags = ("logged" if s["id"][:8] in logged else "NOT LOGGED") + (", worktree" if s["worktree"] else "") + (", maybe active" if age < ACTIVE_MIN else "")
    first = " ".join(s["prompts"][0][1].split())[:90]
    return f"{s['id'][:8]}  {local(min(s['ts']))} -> {local(max(s['ts']))[11:]}  [{flags}]  {s['title'] or first}"


def main(argv):
    logged = logged_ids()
    if argv and argv[0] == "--missing":
        current = None
        if not sys.stdin.isatty():  # SessionStart hook passes {"session_id": ...} on stdin
            try:
                current = json.load(sys.stdin).get("session_id")
            except ValueError:
                pass
        missing = [s for s in sessions() if s["id"][:8] not in logged and s["id"] != current]
        if missing:
            print(f"WORKLOG.md is missing {len(missing)} session(s). Per AGENTS.md, add an entry for each finished one "
                  "(sessions marked 'maybe active' may still be running). Details: python3 tools/session_digest.py <id>")
            for s in missing:
                print("  " + row(s, logged))
        return
    if argv:
        s = next((s for s in sessions() if s["id"].startswith(argv[0])), None)
        if not s:
            sys.exit(f"no session starting with {argv[0]}")
        print(row(s, logged), "\n\nPROMPTS")
        for ts, t in s["prompts"]:
            print(f"- [{local(ts)}] {' '.join(t.split())[:1500]}")
        print("\nCOMMITS")
        for c in commits_for(s["subjects"]) or ["(none)"]:
            print("- " + c)
        print("\nREPORTS (assistant messages over 400 characters)")
        for ts, t in s["reports"]:
            print(f"\n[{local(ts)}]\n{t}")
        return
    for s in sessions():
        print(row(s, logged))


if __name__ == "__main__":
    main(sys.argv[1:])
