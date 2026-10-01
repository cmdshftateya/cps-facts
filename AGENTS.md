# Agent instructions: CPS Facts

This file is for coding agents (Claude Code reads it through `CLAUDE.md`). Read it before you start work. Keep it short and current: if something here turns out to be wrong, fix it in the same session.

## The project

The project is a static, map-first site at **https://schools.ateya.org** covering every Chicago public school: enrollment, demographics, outcomes and spending. Every value carries its source and school year. The owner is Abdulrahman Ateya; the repo is public at `cmdshftateya/cps-facts`.

| Read this | For |
|---|---|
| [WORKLOG.md](WORKLOG.md) | What happened in every session so far, and the **Open threads** list. Read it first. |
| [DECISIONS.md](DECISIONS.md) | Settled choices. Don't reopen them without new evidence. |
| [REQUIREMENTS.md](REQUIREMENTS.md) | Scope, phases and display rules |
| [PIPELINE.md](PIPELINE.md) | How to build, test, update and deploy, plus troubleshooting |
| [METHODOLOGY.md](METHODOLOGY.md) | The short, reader-facing Methodology page (the site builds it) |
| [NOTES.md](NOTES.md) | Detailed caveats and working notes behind it; keep them in step |
| [sources.md](sources.md), `sources_catalog.py` | Source audit, and the public description of each source |

```
.venv/bin/python build.py --skip-fetch          # raw/ -> data/ (validation gates; fails loudly)
.venv/bin/python build_site.py                  # data/ -> site/
.venv/bin/python -m unittest tests.test_gates tests.test_published
cd site && python3 -m http.server 8000          # pick a free port; other sessions may hold 8765/8792
python3 tools/session_digest.py --missing       # sessions not yet in WORKLOG.md
python3 tools/logs.py                           # brief: open threads, latest sessions, active decisions
python3 tools/logs.py decisions D-004           # one decision in full; also --tag, --grep, --next; worklog, threads, outreach
```

## Ground rules

- **A push to `main` deploys to production** through Cloudflare Workers Builds. Push only when the owner asks or has said to.
- **Commits:** no Claude trailer and no `Co-Authored-By` line; the code is Abdulrahman's. Make logical commits (code, then regenerated data, then docs), and stage files by path, never `git add -A` when other sessions may have work in the tree.
- **Parallel sessions are normal here.** The owner often runs several at once in the same folder. Run `git status` before editing and before committing. Never stash, reset, checkout, clean or rewrite history while the tree has changes you didn't make. If files change under you, stop and say so. For larger parallel work, use a worktree.
- **Data integrity:** publish what the source publishes (no suppression). "Suppressed" and "no data" are never 0. No fallback to another year, and no trend line across a comparability break. Outliers are flagged, never trimmed. Every number carries its year and source.
- **Public text is for outsiders.** Never mention internal files, phases or sessions on the site. Describe data so a reader can fetch it themselves.
- `raw/` and the hand-downloaded budget export stay local, with no cloud storage. `site/chicago.css` is vendored from `../politics` and overwritten on build.
- Check UI work in a browser, at 360px and in both themes, and say plainly what you didn't check.

## How the owner works

These patterns come from the sessions so far. Update the list when you learn something new.

- **He wants a recommendation, not a menu.** For judgment calls he often says "you propose" or "it's up to you". Make the call, state it in one line with the reason, and record it in DECISIONS.md as *Delegated*.
- **"Do all of them" is common.** When you list next steps, order them so they can all run in one pass. Ask before only the destructive or outward-facing ones.
- **He explicitly approves destructive or public steps**: force-pushes, making the repo public, deploys, sending email. Ask once, clearly. After a yes, act without hedging.
- **He likes subagents and names the model.** Sonnet for lookups and web checks, Opus for hard proposals or hand matching. Run them in the background and keep working.
- **He favors transparency over caution.** Publish what's published, show honest caveats, ask the source directly. Guessing an email address is acceptable to him.
- **Cost-averse infrastructure:** static, free tiers, nothing that bills later.
- **Messages are often dictated and terse**, so read for intent. For example, "fix the texts" meant fix the tests. If the intent is still ambiguous and the action is cheap to redo, pick the likeliest reading and say so.
- **He asks "did you document it?"** Document as you go: PIPELINE.md for process, NOTES.md for detailed caveats, METHODOLOGY.md for what readers see, DECISIONS.md for choices, WORKLOG.md for the session.
- **"Check status and propose next steps"** expects a status table (done, open, blocked), problems found, and an ordered list of steps.

## Work log protocol

The point is that any future session can pick up cold. Treat this as part of the task, not an afterthought.

**At the start of a session:** the SessionStart hook prints `tools/logs.py brief` (open threads, the latest three sessions, a one-line index of active decisions). Pull full entries only when they're relevant (`tools/logs.py decisions D-0xx`, `tools/logs.py worklog <id>`) instead of reading DECISIONS.md or WORKLOG.md whole. If the SessionStart hook reports sessions missing from the log, add entries for the finished ones: `python3 tools/session_digest.py <id>` replays a session's prompts, commits and reports. Leave sessions marked "maybe active" alone unless they've clearly ended.

**Before you finish**, whenever the session changed files, made commits or settled anything, do the following:

1. **Add an entry to WORKLOG.md** directly under the line `---` that follows Open threads, so entries stay newest first. Re-read the file just before editing, because other sessions write to it too. Use this format:

   ```
   ## YYYY-MM-DD HH:MM–HH:MM · Short title · `<first 8 chars of session id>`

   **Asked:** what the owner wanted, in his terms (quote key phrases).
   **Done:** what exists now that didn't before. Include numbers you measured.
   **Obstacles:** what got in the way and how it was resolved (or not). Skip it if there were none.
   **Decisions:** D-0xx ids, or one-liners for small calls.
   **Commits:** `hash` subject · `hash` subject. Write "none" if there were none, and say where uncommitted work stands.
   ```

   Use local time (America/Chicago). Your session id is the name of the newest transcript in `~/.claude/projects/<repo path with / replaced by ->/`; running `session_digest.py` lists it as "maybe active".
2. **Tie commits to the work:** commit first, then put the resulting hashes in the entry. If you commit after writing the entry, update its **Commits** line. Committing WORKLOG.md with the session's last docs commit is fine.
3. **Record decisions:** anything a later session might otherwise re-argue goes in DECISIONS.md as the next D-0xx (`tools/logs.py decisions --next`), in the entry format at the top of that file: short title, date, status, who, tags, where, decision, why. Reverse a decision with a new entry that supersedes the old one.
   Outreach emails go in emails.md with **Sent:**, **Status:** and **Related:** lines; update the status when a reply comes. `python3 -m unittest tests.test_logs` checks all three formats.
4. **Update Open threads:** add what you left open and remove what you closed.
5. **Update this file** if you learned a durable fact about the project or how the owner works.

Keep entries factual and short. A dozen lines is plenty. Never paste secrets, credentials or private correspondence into these files: the repo is public.
