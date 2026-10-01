# Decisions

Settled choices, so nobody has to re-argue them. Each one gives the call, why, who made it, and where (the session id in [WORKLOG.md](WORKLOG.md)). User-facing caveats that follow from these choices live in [NOTES.md](NOTES.md), and the detailed method lives in the documents linked from each entry.

**Owner** means Abdulrahman decided. **Delegated** means he told the agent to make the call. **Agent** means an agent decided within an instruction and nobody objected. To reverse a decision, add a new entry with `Supersedes: D-0xx`, and change the old one's status to `Superseded by D-0xx`. Don't edit history otherwise.

**Format** (parsed by `tools/logs.py` and checked by `tests/test_logs.py`; keep it exact). Entries are in ID order. Each one is:

```
## D-0xx · Short title (one line, under about 70 characters)

- **Date:** YYYY-MM-DD
- **Status:** Active | Superseded by D-0xx
- **Supersedes:** D-0xx            (only when it does)
- **Who:** Owner | Delegated | Agent | ... (free text after the first word)
- **Tags:** comma-separated, from the existing set where possible
- **Where:** session ids and linked documents

**Decision:** ...

**Why:** ...
```

Skim instead of reading the whole file: `python3 tools/logs.py decisions` (index), `... decisions D-004 D-010` (full entries), `... decisions --tag budget`, `... decisions --grep crosswalk`, `... decisions --next` (next free ID).

## D-001 · Roster backbone is the CPS 20th-day file

- **Date:** 2026-09-30
- **Status:** Active
- **Who:** Owner
- **Tags:** data, roster
- **Where:** `589a4476`

**Decision:** **The roster backbone is the CPS 20th-day file for SY2026-27** (dated 2026-09-21, 639 schools). The Data Portal profile (SY2024-25) is not used.

**Why:** It's newer than anything on the portal. Outcomes and spending use the latest ISBE year (SY2024-25), labeled.

## D-002 · Spending shows ISBE per-pupil and the CPS school budget

- **Date:** 2026-09-30
- **Status:** Active
- **Who:** Owner + agent
- **Tags:** data, budget
- **Where:** `589a4476`, `3413053b`

**Decision:** **Spending shows two figures.** The comparable one is ISBE per-pupil (FY2025). The CPS school budget comes from the BI dashboard's "Download Data" line-item export, which the owner downloads by hand once a year. Budget units join to schools through the city profile's `finance_id` (`U` + id), which covers 637 of 639 schools.

**Why:** The public CPS budget files have no dollar totals or IDs. The dashboard requires a sign-in, so the build can't fetch it.

## D-003 · Grade 11 test is one series with no trend across the break

- **Date:** 2026-09-30
- **Status:** Active
- **Who:** Owner (adopted the Opus proposal)
- **Tags:** data, assessment, comparability
- **Where:** `589a4476`, [hs-assessment-proposal.md](hs-assessment-proposal.md)

**Decision:** **The grade 11 test is one series, "SAT through 2024, ACT from 2025",** with no trend line, delta or cross-year rank across the 2024→2025 break. Elementary IAR gets the same treatment because of the 2025 cut-score change.

**Why:** No year has both tests, and ISBE lowered cut scores without re-scoring earlier years.

## D-004 · Optional score-vs-benchmark toggle, labeled estimate

- **Date:** 2026-09-30
- **Status:** Active
- **Who:** Owner idea, agent method
- **Tags:** data, assessment, ui
- **Where:** `589a4476`, `3413053b`, [hs-score-benchmark-method.md](hs-score-benchmark-method.md)

**Decision:** **An optional "Score vs national benchmark (estimate)" toggle** shows the mean score minus the ACT benchmark (ELA 20, math 22). SAT years are converted with the official concordance and badged "est.". It ships only if the Spearman rank correlation across the break is at least 0.85; the actual values are 0.909 and 0.913.

**Why:** The owner wanted comparability across the break. Recomputing proficiency is impossible without student-level scores. ELA uses 20 because Illinois takes the ACT with Writing; this is pending ISBE confirmation.

## D-005 · CPS↔ISBE crosswalk with a confidence column

- **Date:** 2026-09-30
- **Status:** Active
- **Who:** Delegated
- **Tags:** data, crosswalk
- **Where:** `589a4476`, `3413053b`, [crosswalk_notes.md](crosswalk_notes.md)

**Decision:** **The CPS↔ISBE crosswalk** combines legacy portal IDs with an agent's hand matching, recorded in a `confidence` column. A low-confidence match carrying ISBE data fails the build; medium matches ship with a flag.

**Why:** No official crosswalk exists.

## D-006 · Subdistricts from the Senate redistricting shapefile

- **Date:** 2026-09-30
- **Status:** Active
- **Who:** Agent
- **Tags:** data, geo
- **Where:** `589a4476`

**Decision:** **Subdistricts come from `ERSB_20_Sub_District_Map_FA1_SB_15`** on the Illinois Senate redistricting site, with labels 1a–10b.

**Why:** The Board of Elections publishes only PDFs and blocks scripts. This shapefile matched the official map visually.

## D-007 · Lineage follows charter conversions, not closures

- **Date:** 2026-09-30
- **Status:** Active
- **Who:** Agent
- **Tags:** data, roster, crosswalk
- **Where:** `589a4476`, [charter-conversions.md](charter-conversions.md)

**Decision:** **Lineage follows charter conversions but not closures.** The five Acero campuses and ChiArts carry their history from the old charter ID and use the old coordinates, flagged. EPIC and the ASPIRA high schools drop off.

**Why:** Same buildings, new IDs. Closed schools have no SY2026-27 presence.

## D-008 · Catalyst Maria: ISBE on one campus, shared per-pupil budget

- **Date:** 2026-10-01
- **Status:** Active
- **Who:** Delegated ("you propose, do the best thing")
- **Tags:** data, budget, crosswalk
- **Where:** `3413053b`

**Decision:** **Catalyst Maria** (400115/400182): ISBE values go on 400115 only. Per-pupil budget uses the combined enrollment, shown on both campuses and labeled. The budget total stays on 400115.

**Why:** One ISBE row and one budget unit cover both campuses. This avoids double counting and keeps the per-pupil figure meaningful. CPS was emailed to confirm.

## D-009 · No suppression of anything CPS publishes

- **Date:** 2026-10-01
- **Status:** Active
- **Who:** Owner
- **Tags:** data, display
- **Where:** `3413053b`

**Decision:** **No suppression of anything CPS publishes.** Schools under 30 students get a `low_n` label only, and medians include them.

**Why:** "If they publish it, we should publish it."

## D-010 · Edge rules for $0, not rated, `*` and outliers

- **Date:** 2026-10-01
- **Status:** Active
- **Who:** Agent
- **Tags:** data, display, validation
- **Where:** `3413053b`, [PIPELINE.md](PIPELINE.md)

**Decision:** **Edge rules:** a $0 budget unit is no data. YCCS campus per-pupil is withheld because the budget sits in one network unit. 5Essentials level 0 means not rated. ISBE `*` where the grade level doesn't apply means no data, not suppressed. Outliers are flagged, never trimmed. "Suppressed" is never shown as 0.

**Why:** Each fixes a real misread found during validation.

## D-011 · Ask the source directly by email

- **Date:** 2026-10-01
- **Status:** Active
- **Who:** Owner
- **Tags:** process, outreach
- **Where:** `3413053b`, [emails.md](emails.md)

**Decision:** **Ask the source directly.** Open data questions go by email to CPS and ISBE from the owner's Gmail, signed Abdulrahman Ateya. Guessing an address is acceptable.

**Why:** The owner guesses addresses routinely, and a bounce is cheap.

## D-012 · Static site only, no server or database

- **Date:** 2026-10-01
- **Status:** Active
- **Who:** Owner
- **Tags:** infra
- **Where:** `cdd059c7`

**Decision:** **Static site only:** no server and no database. A Cloudflare Worker serves `site/` as static assets at schools.ateya.org. The built data is committed. `raw/` stays on the owner's machine, with no cloud storage.

**Why:** Cheap, simple and reviewable as diffs. Storage could cost money later.

## D-013 · Budget export removed from git history

- **Date:** 2026-10-01
- **Status:** Active
- **Who:** Owner (explicit approval for the destructive step)
- **Tags:** infra, git
- **Where:** `cdd059c7`

**Decision:** **The 75 MB budget export was removed from all git history** (filter-branch plus force-push). Only the small derived CSVs are tracked.

**Why:** It bloated every clone and was a duplicate of `raw/`.

## D-014 · Deploys via Cloudflare Workers Builds on push to main

- **Date:** 2026-10-01
- **Status:** Active
- **Who:** Owner
- **Tags:** infra, deploy
- **Where:** `cdd059c7`, `0b9d5d09`

**Decision:** **Deploys go through Cloudflare Workers Builds on push to `main`**, not GitHub Actions. Locally, Node 22 comes from nvm in `~/.nvm`, and the system Node is left alone.

**Why:** No Cloudflare token stored in GitHub. A push to `main` is a production deploy.

## D-015 · Commit hygiene: logical commits, no Claude trailer

- **Date:** 2026-10-01
- **Status:** Active
- **Who:** Owner
- **Tags:** process, git
- **Where:** `cdd059c7`, `~/.claude/CLAUDE.md`

**Decision:** **Commit hygiene:** logical commits (code, then data, then docs), and no Claude trailer or co-author line.

**Why:** The code is Abdulrahman's (global CLAUDE.md). Small commits keep the data diffs reviewable.

## D-016 · Enrollment-change palette: 7 fixed zero-centered bins

- **Date:** 2026-10-01
- **Status:** Active
- **Who:** Agent
- **Tags:** ui, design
- **Where:** `3413053b`

**Decision:** **The enrollment-change palette has 7 fixed, zero-centered bins** (≤−20, −10, −3, flat, +3, +10, ≥+20%): terra cotta for decline, gray for flat, lake blue for growth. It lives in `site/diverging.css`, separate from the vendored `chicago.css`.

**Why:** Fixed bins keep the middle meaning "no change", even though the data skews toward decline. `chicago.css` is overwritten on build.

## D-017 · Public repo with issues on, MIT for code

- **Date:** 2026-10-01
- **Status:** Active
- **Who:** Owner
- **Tags:** infra, public
- **Where:** `0b9d5d09`

**Decision:** **The repo is public with issues on.** MIT covers the code only. `noindex` is lifted and the WIP banner removed.

**Why:** People should be able to report data errors.

## D-018 · Public pages describe data by its public source

- **Date:** 2026-10-01
- **Status:** Active
- **Who:** Owner
- **Tags:** public, docs
- **Where:** `0b9d5d09`, `sources_catalog.py`

**Decision:** **Public pages describe data by its public source**: publisher, dataset, link, exact sheet and column headers, and how to get it. They never cite internal files, phases or "the owner exported".

**Why:** A reader must be able to reproduce any number on their own.

## D-019 · Phase 2 started early against a synthetic fixture

- **Date:** 2026-09-30
- **Status:** Active
- **Who:** Owner
- **Tags:** process
- **Where:** `81bc3b29`

**Decision:** **Phase 2 started before Phase 1 was done**, against a synthetic fixture, and the fixture was retired once real data existed.

**Why:** The owner wanted parallel progress.

## D-020 · Methodology page generated from NOTES.md

- **Date:** 2026-10-01
- **Status:** Superseded by D-024
- **Who:** Agent (per requirements)
- **Tags:** docs, public
- **Where:** `270ad70a`

**Decision:** **The methodology page is generated from NOTES.md** by `build_site.py`.

**Why:** One source of truth for caveats.

## D-021 · Not a duplicate of an existing tool

- **Date:** 2026-10-01
- **Status:** Active
- **Who:** Agent assessment
- **Tags:** scope
- **Where:** `06705eb3`

**Decision:** **This isn't a duplicate of an existing tool.** Its value is the crosswalk, the budget aggregation and honest caveats on one district-wide map.

**Why:** Prior-art check, from knowledge only, without a web search.

## D-022 · Every session gets a work-log entry

- **Date:** 2026-10-01
- **Status:** Active
- **Who:** Owner
- **Tags:** process, docs
- **Where:** `630ea84d`

**Decision:** **Every session gets a work-log entry tied to its commits.** Durable decisions go here, and AGENTS.md is the single instruction file; CLAUDE.md imports it. A SessionStart hook lists sessions that still need an entry.

**Why:** Agents start cold. A written history of what, why and what went wrong speeds up every later session.

## D-023 · Parallel sessions never touch each other's work

- **Date:** 2026-10-01
- **Status:** Active
- **Who:** Agent (from the incident)
- **Tags:** process, git
- **Where:** `cdd059c7`, `3413053b`, `270ad70a`

**Decision:** **Parallel sessions must not touch each other's uncommitted work**: no stash, reset, checkout or filter-branch on a dirty tree. Use worktrees for parallel work.

**Why:** This caused reverted edits, a half-restored tree and committed conflict markers on 2026-10-01.

## D-024 · Methodology page generated from a short METHODOLOGY.md

- **Date:** 2026-10-01
- **Status:** Active
- **Supersedes:** D-020
- **Who:** Owner (asked for a brief rewrite for readers)
- **Tags:** docs, public
- **Where:** `60a708a1`

**Decision:** **The Methodology page is generated from a short `METHODOLOGY.md`, not NOTES.md.** NOTES.md stays as the detailed record.

**Why:** The 24-item caveat list read as working notes; readers need about one screen per topic.

## D-025 · Map draws every school, no marker clustering

- **Date:** 2026-10-01
- **Status:** Active
- **Who:** Owner (issue) + agent method
- **Tags:** ui, map
- **Where:** `8369c217`

**Decision:** **The map draws every school; no marker clustering.** Markers hold about the same screen size (growing as zoom^0.25), so zooming in separates overlapping schools. Supersedes the clustering and "markers grow as you zoom in" calls in `60a708a1`.

**Why:** Clusters regrouped on every zoom frame and the map jittered (GitHub issue #2: "just render all datapoints"). Map-unit markers never separated when zoomed.

## D-026 · Sequential ramp overridden for 3:1 contrast

- **Date:** 2026-10-01
- **Status:** Active
- **Who:** Agent
- **Tags:** ui, design, accessibility
- **Where:** `8369c217`

**Decision:** **The map's sequential ramp is overridden in `site/sequential.css`**, generated by `tools/diverging_palette.mjs`, with every step at least 3:1 against `--page` in both themes. The search highlight and selected row are raised too. `chicago.css` stays untouched.

**Why:** The vendored ramp's lowest steps were 2.5:1 (dark) and 1.9:1 (light) against the map, and the dark-mode selection ring vanished on pale fills (issue #3).

## D-027 · Printable school report card inside the map page

- **Date:** 2026-10-01
- **Status:** Active
- **Who:** Agent
- **Tags:** ui, print
- **Where:** `8369c217`

**Decision:** **The school report card is a printable sheet inside the map page** (button in the profile, link `#school=ID&card=1`), printed or saved as PDF through the browser. It's light "paper" in both themes and shows only what the panel shows, with years, medians, caveats and sources.

**Why:** Static site, no PDF library. Reusing the panel's values keeps one source of truth (issue #1).

## D-028 · Logs are structured markdown, skimmed with tools/logs.py

- **Date:** 2026-10-01
- **Status:** Active
- **Who:** Owner (asked for it); agent chose the format
- **Tags:** process, docs
- **Where:** `31c35177`

**Decision:** **DECISIONS.md, WORKLOG.md and emails.md stay markdown but follow a strict, documented entry format** (one `## D-0xx · Title` section per decision with Date, Status, Supersedes, Who, Tags and Where fields; the existing work-log headings and fields; Sent, Status and Related lines per email). `tools/logs.py` parses them into an index, single entries, filters and JSON, and `tests/test_logs.py` fails when a file drifts. The SessionStart hook prints `tools/logs.py brief`.

**Why:** Agents should skim the index and pull only the entries they need instead of loading every log into context. Markdown with fixed fields keeps the files readable on GitHub and diffable, with no second source of truth to keep in sync (a YAML or JSON source would need a generated markdown copy).

## D-029 · Each school has a share page with its own preview card

- **Date:** 2026-10-01
- **Status:** Active
- **Who:** Owner asked for per-school previews; agent proposed the design and he approved it
- **Tags:** ui, sharing
- **Where:** `5b9f1914`

**Decision:** **Every school gets a static page at `/s/<id>/` with its own Open Graph and Twitter tags and a 1200×630 card, generated at build time.** The page redirects browsers to `/#school=<id>`, and the map shows the selected school as `/s/<id>/` in the address bar (report card: `/s/<id>/#card=1`; old `#school=` links still work). The card shows the school name, a badge made from its name (six-point star, initials, colour and pattern hashed from id and name; this encodes no data), a star at its location on the city outline, and three numbers with school years: students, low income, and 4-year graduation (high and combined schools) or attendance (elementary). Suppressed and missing values are spelled out, never shown as 0.

**Why:** Preview bots never see a URL's `#` fragment, so every school link showed the same site image. Static pages keep the site free and serverless (a Worker drawing images on request was the alternative). The location star tells a Chicago reader the most at a glance; the name badge makes each card recognizable; three numbers stay legible at thumbnail size. About 28 MB of PNGs, rewritten only when pixels change.

