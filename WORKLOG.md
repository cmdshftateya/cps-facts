# Work log

One entry per working session (a Claude Code conversation, or a stretch of work done by hand). This file records what each session set out to do, what it got done, what got in the way, what was decided, and which commits it produced. `git log` says *what* changed; this says *why*, and what it cost to get there. Durable decisions also go in [DECISIONS.md](DECISIONS.md). How to write an entry: [AGENTS.md](AGENTS.md#work-log-protocol).

Newest first. Times are America/Chicago. The 8-character id is the Claude Code session id (transcripts live in `~/.claude/projects/`; `python3 tools/session_digest.py <id>` replays one). Hashes are current ones: the history rewrite on 2026-10-01 changed every hash from before 10:16, so hashes quoted inside old transcripts no longer exist.

The format is parsed by `tools/logs.py` and checked by `tests/test_logs.py`: entry headings are exactly `## <when> · <title> · \`<8-char id>\``, each field starts a line with `**Asked:**`, `**Done:**`, `**Obstacles:**`, `**Decisions:**` or `**Commits:**`, and each open thread is one line, `- **Label:** text`. Skim instead of reading it all: `python3 tools/logs.py worklog` (index), `... worklog <id>` (one entry), `... worklog --grep stash`, `... threads`.

## Open threads

Carried forward until closed. Update this list in every entry that opens or closes one.

- **Outreach replies pending:** sent 2026-10-01 09:59 (`python3 tools/logs.py outreach`): CPS finance (`financedep@cps.edu`) on the Catalyst Maria budget unit; CPS accountability (`accountability@cps.edu`, a guessed address, so watch for a bounce) on the low-income/IEP relabel; ISBE (`reportcard@isbe.net`) on the per-pupil fiscal year and the ACT "ELA" column. Record answers in NOTES.md and DECISIONS.md.
- **2026 Illinois Report Card:** expected late October 2026; re-run `build.py`, re-audit the crosswalk and break flags, and move "latest" years forward.
- **FY27 budget label:** the board apparently approved the budget on 2026-07-30. Nobody has compared the approved book to the "proposed" export the site uses.
- **Cross-link from the politics board guide:** the edit to `../politics/chicago-school-board-2026-guide.html` is uncommitted in that repo.
- **For the owner to confirm on the Data page:** the budget-export steps ("Interactive Reports", then "Download Data") and the Data Portal titles for the boundary datasets, which were written from memory.
- **Share button on a real phone:** check the snapshot in iOS Safari's share sheet (iMessage, Instagram) and Android Chrome; only the no-share-sheet fallback was tried, in the desktop browser pane.
- **Check a shared school link after deploy:** paste one `/s/<id>/` link into iMessage, WhatsApp and Slack, and run it through the Facebook Sharing Debugger so cached previews refresh.
- **Real-phone check of the map UI:** Settings sheet, school panel, report card, long-press on a marker. Only checked in emulated 360–375px viewports. Not checked: actual print output of the report card (print CSS written, preview not available in the browser pane).

---
## 2026-10-01 17:05–17:25 · Fun logo that resets the map · `970a2ff2`

**Asked:** "Improve the top right logo": "a creative and fun logo", and clicking it "should reset the map to the default view".
**Done:** The header wordmark (top left; the only logo) is now an inline SVG mark, the flag star in a graduation cap between two blue bars, plus "CPS Facts" with "Facts" in red. Hover swings the tassel; a click tosses the cap, spins the star, animates the map back to the full city and resets metric, filters, search, open school and view (Settings kept). Checked in the browser pane at 1280px and 360px, light and dark, mid-animation; console clean; `tests.test_gates tests.test_published` pass.
**Obstacles:** `chicago.css` styles every `a` with an underline and a blue hover fill; overridden for `#home`.
**Decisions:** D-033.
**Follow-up (10-02):** owner disliked the wordmark font (same Helvetica Condensed as the ChiElections masthead, but small and loosely spaced); from four options side by side he picked Barlow Condensed Black. Bars shortened to just wider than the star and thickened, star points poking out. Rechecked at 360px and in both themes. Then the nav sat about 7px below the wordmark (the header aligned on the icon's bottom edge); the wordmark now sets the baseline.
**Commits:** `2d13bce` logo and reset · `d90fcce` docs · `0024c79` font and bars · `a5beac3` docs · `672d0da` baseline fix. Not pushed.

## 2026-10-01 15:40–16:20 · Share snapshot button · `ba5e68c6`

**Asked:** A share in the school panel that makes a snapshot of "the most important metrics" and opens the share sheet "to imessage etc, with a text summary img and link". First try (a 4:3 table of six numbers) "kinda sucks"; wanted "a mini map card and measure card", "quick fire", the "cute little icon", not overwhelming, "good for Instagram"; rebase on main first.
**Done:** Rebased on main (per-school link cards). Share button next to Report card: a 1080×1440 PNG drawn on a canvas when the panel opens (badge, name, location star on the city outline, students, spending per student, ELA proficiency, chronic absenteeism, each with year and city median), passed to `navigator.share` with a one-line summary and `/s/<id>/`; download plus clipboard where there is no share sheet. Barlow fonts served from `site/fonts/` (about 340 KB, loaded only for sharing). Checked in the browser pane: elementary, high school with a long name, a suppressed value, 375px in dark mode, and the fallback (image saved; clipboard blocked in the pane). `tests.test_published` passes.
**Obstacles:** No `.venv` in this worktree, so `build_site.py` and `tests.test_gates` weren't run; fonts copied by hand (same files the build copies). The pane has no Web Share, so the real share sheet is untested.
**Decisions:** D-032.
**Commits:** `1519566` share button and fonts · `8e35cb7` docs; pushed to `main` on the owner's "push it to main".

## 2026-10-01 14:55–15:35 · Per-school link previews · `5b9f1914`

**Asked:** When sharing a school's page, a rich link preview "customized for each school", "easily readable", maybe an icon "semi-randomly related to the school's name"; "propose something smart". Approved the proposal: "AMAZING yes please".
**Done:** Found the real blocker: school links are `/#school=ID` and preview bots drop the fragment, so every school showed `og.png`. New `pipeline/share.py` (called by `build_site.py`, or alone with `python -m pipeline.share`) writes `site/s/<id>/index.html` (own title, description, og/twitter tags, JS redirect to the map) and a 1200×630 `card.png` for all 639 schools: name badge (hashed star colour and pattern plus initials), location star on the city outline, students, low income, and graduation or attendance with school years. Pillow plus vendored Barlow (OFL); about 44 KB per card, 28 MB total, 25–30 s on 4 cores; unchanged cards are not rewritten (re-run touched 0 files). The map now shows `/s/<id>/` in the address bar while a school is open; the report card links there too. Two new tests in `test_published` (every school has a page and card, every number has a year, suppressed and no data never become 0). Checked in Chromium: `/s/<id>/` lands on the right school, reload, Esc back to `/`, old `#school=` links, nav links and back button, 360px in both themes (no horizontal scroll), the no-JS page and its tags.
**Obstacles:** The cloud container's network policy blocks schools.ateya.org, so the live pages weren't fetched after deploy. No `raw/` in the cloud container, so `build_site.py` itself wasn't run; the generator ran from the committed `site/data/schools.json`, which is the same input. Not checked: a real share on a phone or in Slack/iMessage, which needs a deploy.
**Decisions:** D-031 (first numbered D-029; renumbered after merging main, where another session took D-029 and D-030).
**Commits:** `42ec73f` per-school share pages and cards (code) · `25c8deb` generated pages and cards for 639 schools · `bfa4fda` docs · `f03ec77` merge of main (D-029 renumbered to D-031), pushed to `main` on the owner's "yes merge it" · `f0a85a7` fix: CI installs no packages, so `pipeline/share.py` imports Pillow only inside the drawing functions (the first deploy's test run failed on `import PIL`).


## 2026-10-01 14:05–15:50 · Clutter and overload review of the map page · `8bd56763`

**Asked:** "conduct a usability review with a focus on presentation of information and figure out how to reduce the amount of visual clutter and overload", then "go" on the five recommendations, then "gogogo but rebase with master first" and "push it to main".
**Done:** Review in [ux-clutter-review.md](ux-clutter-review.md). School panel: section-level year with badges only where a year differs, compact row tables for race, spending detail, 5Essentials and ACT averages, no range caption under sparklines, sources in a disclosure, and a highlighted line for the colored-by measure at the top (Ariel: 3,486 to 2,130 px). Panel tiles renamed `.tile`, because the vendored `.cell` hover inverted them to black. Settings moved from a floating button into the header. Filters fold under a "Filters" disclosure with an active count. Color by menu uses short names. Governance shapes show only when coloring by type (REQUIREMENTS.md updated). Legend year sits beside the title. Table year moved to the column header. On the Data page, sources and the field table sit under disclosures (7,185 to 1,851 px). Checked at 1440px and 360px in both themes: no JS errors, no horizontal overflow. `tests.test_published` passes. Not checked on a real phone or with a screen reader.
**Obstacles:** `main` moved mid-session: `8369c217` removed clustering and added the report card, and used D-025 to D-027. On rebase, my cluster tweaks were dropped in favor of D-025, and my decisions became D-028 and D-029; after `31c35177` claimed D-028 and restructured the logs, they became D-029 and D-030. `build_site.py` imports `pyshp`, which isn't installed here, so `data.html` was regenerated by calling `downloads()` with a stub module, after confirming an unchanged run reproduced the file byte for byte.
**Decisions:** D-029, D-030.
**Commits:** `35d6f88` map page clutter cuts · `93f4146` filters disclosure, short labels, shapes by type, panel focus · `64535f4` Data page disclosures · `3d4bf8b` and `aa67660` review doc, decisions, requirements · this docs commit. Rebased onto `2da9909`, then merged `origin/main` (the logs restructure; a second rebase was blocked by the session's permission check) and pushed to `main` (deploys).

## 2026-10-01 15:04–15:10 · Machine-readable decisions, work log and outreach log · `31c35177`

**Asked:** Make the decision file "machine readable so you can programmatically skim it instead of having to load in all the context"; then "same for the worklog" and "any other logs as well".
**Done:** DECISIONS.md went from one wide table to one `## D-0xx · Title` section per decision, each with a new short title and tags plus Date, Status, Supersedes, Who and Where fields (content unchanged). Open-thread bullets in WORKLOG.md now all read `- **Label:** text`; emails.md gained Sent, Status and Related lines per email. New `tools/logs.py` (stdlib only): `brief` (default), `decisions` (index, ids, `--tag`, `--grep`, `--active`, `--tags`, `--next`), `worklog` (index, id prefix, `--grep`, `--decision`, `-n`), `threads`, `outreach`, all with `--json`. The brief is about 4 KB versus about 35 KB for reading DECISIONS.md and WORKLOG.md whole. New `tests/test_logs.py` (8 tests) checks all three formats; the SessionStart hook now also prints the brief. AGENTS.md points to the tool.
**Decisions:** D-028.
**Commits:** `a0b81a8` logs tool, format tests, SessionStart brief · `3763ee5` structured decisions, threads and outreach log · `7cce101` log entry. Merged with `origin/main` (renumbered this decision from D-025 to D-028 and converted main's new D-025 to D-027 to the section format), then pushed to `main`.

## 2026-10-01 14:05–14:50 · GitHub issues #1–#3: jitter, contrast, report card · `8369c217`

**Asked:** "correct all github issues and close them". Mid-session: holding down on a marker "makes a very big ugly circle".
**Done:** #2: removed clustering (it regrouped every zoom frame); all 639 schools always drawn, markers near-constant screen size, non-scaling strokes. #3: new `site/sequential.css` ramp, every step ≥3:1 vs page (was 2.54 dark / 1.87 light at the low end); halo selection ring; stronger `--mark` with underline; tinted selected row. Long-press: no tap highlight or callout on the map, focus stroke no longer scales with zoom. #1: printable report card per school (`#school=ID&card=1`): hero numbers, every panel value with year, city range strip and median, caveats, sources. Checked dark and light at desktop, report card at 360px (no horizontal scroll). Tests pass.
**Obstacles:** none. Print output itself not previewed.
**Decisions:** D-025, D-026, D-027.
**Commits:** `274ec22` map markers, contrast, report card.

## 2026-10-01 13:32–13:40 · Data page: drop filename labels · `255a5c46`

**Asked:** "remove the .csv for the data.html page". Clarified: remove the filename line (e.g. `schools.csv`) under each download link, keep every file.
**Done:** `build_site.py` no longer prints `<code>name</code>` under the 8 download links; `site/data.html` rebuilt. `tests.test_published` passes; checked at 360px (no horizontal scroll), light theme only.
**Obstacles:** `raw/` isn't in worktrees; linked the main checkout's raw files temporarily to run `build_site.py`, then removed the links.
**Commits:** `2b8e637` Data page: drop filename labels under download links. Merged to `main` and pushed (deploys).

## 2026-10-01 10:48–13:35 · Site usability review fixes, short Methodology page · `60a708a1`

**Asked:** Fix the usability issues an outside review found: the draft-looking Methodology page, overlapping map markers, the buried grade 11 benchmark view, and a list of smaller polish items. Then "reword" the budget-dashboard line, "rewrite the methodology page for readers and be brief", and "commit this and push it and respect the new work log instructions".
**Done:** Markers within about 15 screen px merge into numbered circles filled with the group's average color; click or Enter zooms in (1024 to 256 viewBox width in a test; 149 clusters down to 19). The grade 11 benchmark is now two Color by entries plus a "% proficient | Vs. college-ready" toggle under Color by, replacing the Settings dropdown (old `s_g11` links still work). It and the enrollment change share a generalized diverging scale; the benchmark bins are −9, −5, −1, +1, +5, +9 points. Also: marker-size legend, shape key hidden in subdistrict shading, spending split into two Color by options (old `s_spend` links still work), a labeled Settings button, accurate empty-data messages, plain-language scale text, "5Essentials" everywhere. Checked at 375px: no horizontal overflow; the Settings button covered the school panel, so it hides while a panel is open on small screens. New `METHODOLOGY.md` (about 650 words, six sections) now feeds the Methodology page; `NOTES.md` stays as the detailed record. Merged `origin/main` (work log, resizable columns, Data and sources page) and re-checked the merged map.
**Obstacles:** The full site build needs `pyshp`, which isn't installed here, so `methodology.html` was regenerated by calling `methodology()` directly. The merge conflicted in `NOTES.md` (took main's version), `build_site.py` (took main's `_inline`, which no longer auto-links repo files) and `site/methodology.html` (regenerated). Main's rule that public text never cites internal files meant the new page links the downloadable lookup table on the Data and sources page, and keeps only the two public GitHub method documents. The browser pane is shared with other sessions, and its tab was navigated away mid-test several times.
**Decisions:** D-024 (Methodology page comes from `METHODOLOGY.md`, superseding D-020). Smaller calls: the benchmark toggle sits under Color by, not next to Map/Table, because it applies to only two metrics; clusters keep the data color instead of a neutral fill.
**Commits:** `bd3cd00` map clustering, benchmark metrics, legends, spending options, Settings label · `bf0656b` Methodology page rewrite · `1406c9a` merge of `origin/main`. Pushed to the branch `claude/school-search-review-be40f8`, not to `main`.

## 2026-10-01 10:51–11:02 · Work log, decision register, agent instructions · `630ea84d`

**Asked:** Start a work log covering every past conversation (timestamps, accomplishments, obstacles, decisions), and set up agent instructions so the log, commits and decisions stay current automatically. Document the owner's working and decision style too.
**Done:** Read all 11 earlier transcripts for this repo, plus one in another repo that linked here. Wrote this file, [DECISIONS.md](DECISIONS.md), [AGENTS.md](AGENTS.md) (agent instructions, working style, log protocol) and `CLAUDE.md` (imports AGENTS.md). Added `tools/session_digest.py`, which lists sessions, flags the ones missing from this log, and replays one session's prompts, commits and reports. Added a SessionStart hook in `.claude/settings.json` that runs the digest, so each new session is told which sessions still need entries.
**Obstacles:** Hashes quoted in transcripts before the history rewrite are stale. The digest matches commits by subject to recover the current hashes. The requirements draft (v0.1–v0.3) existed before the first transcript, and its origin isn't in any Claude Code session.
**Decisions:** D-022, D-023.
**Commits:** `2d71f60` work log, decision register and agent instructions (this entry's hash line added in the follow-up commit).

## 2026-10-01 10:34–10:52 · Launch polish, public repo, sources described for outsiders · `0b9d5d09`

**Asked:** Check status and propose next steps, then "do all of them", and make the GitHub repo public so people can file issues. Later: drop the draft banner, make the side columns resizable, and describe the data so a reader can find it themselves instead of through internal references.
**Done:** Added the downloads page (`data.html`, `site/downloads/`), OG/Twitter tags, a social image and favicons (`tools/make_og.py`), README, MIT license, issue templates, and "Report an issue" links. Fixed the header at 360px. CI now runs `test_published` on every push, and `test_gates` skips without `raw/`. Made the repo public and lifted `noindex`. Then removed the WIP banner, added drag- and keyboard-resizable side columns (widths saved per browser, map keeps at least 320px), and rewrote the Data and Methodology pages around public sources: publisher, dataset, exact sheet and column headers, and how to retrieve each one (`sources_catalog.py`).
**Obstacles:** Workers Builds didn't deploy the push (the second time this happened), so the session deployed by hand. The owner then said auto-deploy on push to `main` is set up and not to worry about it. The politics cross-link lives in another repo, so it was left uncommitted there.
**Decisions:** D-017, D-018.
**Commits:** `a127ebe` downloads, social preview, icons, issue links, README, license, CI, lift noindex · `c975812` resizable columns, drop WIP banner, sources documented with links and field names.

## 2026-10-01 10:25–10:34 · Status check, table view, docs cleanup · `e9f8a576`

**Asked:** Status and next steps, then: resolve the NOTES conflict, update PIPELINE.md, fix the tests, build the table view, and push. Also: "the site still won't open."
**Done:** Resolved the leftover conflict markers in NOTES.md (caveats 17–18; the later ACT "ELA" text won). Made `tests/test_gates.py` a real unittest. Built the Map/Table toggle: sortable, shares the map's filters, blanks sort last, row click opens the panel, table is the default under 760px, `#v=table`. Documented deploy and DNS troubleshooting.
**Obstacles:** Conflict markers had been committed in `7dea61e` during the parallel-session collision. The test file collected zero tests because it was a script with no test class. The push didn't trigger Workers Builds, so the session deployed by hand with `npx wrangler deploy`. "Site won't open" turned out to be the home router (192.168.1.1) caching NXDOMAIN from before the custom domain existed; 1.1.1.1 and 8.8.8.8 resolved fine.
**Commits:** `1199b3f` table view, NOTES conflict, discoverable tests, docs · `d25f295` deploy and DNS troubleshooting.

## 2026-10-01 09:53–10:26 · Commits, private remote, history rewrite, first deploy · `cdd059c7`

**Asked:** Commit all work logically, create a remote and push. Then: don't make it public, don't push the CSV, and work out what belongs in the repo for a serverless static site that is updated with data occasionally ("go ahead and change everything"; no cloud storage, since it could cost money). Run the filter-branch and force-push. Delete the backup branch, install nvm and Node 22, and deploy. Then document the deploy and set up Cloudflare Workers Builds.
**Done:** Split commits into code, data and docs. Created the private repo `cmdshftateya/cps-facts`. Stopped tracking the 75 MB `Budget_Book_FY27.csv`, then removed it from all history with filter-branch and a force-push. Committed `build_site.py`, the methodology page and `wrangler.jsonc`, and retired the synthetic fixture. Installed nvm and Node 22 under `~/.nvm` without touching the system Node. First `wrangler deploy` went to schools.ateya.org. Connected Workers Builds; the owner authorized the GitHub app. Documented the update and deploy routine in PIPELINE.md.
**Obstacles:** The permission classifier blocked the first history rewrite as destructive, so the session asked the owner and got explicit approval. `filter-branch` needs a clean tree, and the session stashed while another session was editing the same files. The stash pop half-failed and left NOTES.md with conflict markers. Everything was preserved on `backup/pre-filter-stash` (later deleted on request) and the session stopped instead of guessing. The owner cleaned up and the rewrite ran on a clean `main`. Wrangler needs Node 22 and the machine had 18.12.1. The new domain didn't resolve locally because of cached negative DNS, even though Cloudflare served 200.
**Decisions:** D-012, D-013, D-014, D-015.
**Commits:** `23985f2` demographics as published, shared Catalyst Maria budget · `7b22527` regenerate data · `597edd2` Phase 1 docs · `968d20b` stop tracking the budget export · `e10c8cb` site build, methodology page, deploy config · `def375a` remove fixture · `9efe521` ignore `.wrangler/` · `b5dc43c` deploy docs · `f8adc5e` auto-deploy docs (also the commit that proved Workers Builds fired).

## 2026-10-01 10:03–10:05 · WIP readiness check · `270ad70a`

**Asked:** "Are we ready to upload a WIP to schools.ateya.org?", then do everything except the deploy.
**Done:** Answered yes, with guardrails: commit first, add a WIP banner and `noindex`, write the deploy config, and run the tests. Ran the gate tests (all fire). Added the banner and `noindex`, extended `build_site.py` to generate `methodology.html` from NOTES.md, and wrote `wrangler.jsonc`. These landed in `e10c8cb` and `7dea61e` through the other sessions.
**Obstacles:** The working tree changed underneath it mid-task (the stash for the history rewrite in `cdd059c7`), so it stopped without restoring or committing anything.

## 2026-10-01 10:03–10:04 · Map pan and zoom · `731daf38`

**Asked:** The map can't pan or zoom.
**Done:** Wheel and trackpad zoom toward the cursor (up to 40×), drag to pan without triggering clicks, pinch on touch, double-click to zoom, and +/−/reset buttons. The buttons moved to the top-right because they covered the legend. Markers scale with zoom.
**Obstacles:** None in the session itself. The edit was caught in the stash during the history rewrite and reached `main` in `7dea61e` when the Phase 1 session rebuilt `site/index.html` from the stash.
**Decisions:** Markers grow with zoom (unconfirmed; see Open threads).

## 2026-10-01 09:51 · Prior-art check · `06705eb3`

**Asked:** Does something like this already exist? Are we replicating it?
**Done:** Answered from knowledge, without a web search. The overlapping tools are the Illinois Report Card, CPS School Profiles, the CPS budget portal, the Chicago Data Portal, GreatSchools/Niche, Urban Institute/NCES and one-off newsroom maps. None is a district-wide map that pairs sourced, dated numbers with budget, crosswalk and comparability caveats. The project's real value is the CPS↔ISBE crosswalk, the budget aggregation and the caveats. Offered a web search; it wasn't taken up.

## 2026-09-30 21:46 · Git setup · `ac83c76c`

**Asked:** Set up git.
**Done:** `git init`, a `.gitignore` (venv, caches, `raw/*` except `raw/MANIFEST.json`), and the initial commit.
**Obstacles:** The root-level 75 MB `Budget_Book_FY27.csv` went into this first commit. It was removed from history on 2026-10-01 (see `cdd059c7`).
**Commits:** `c9a8390` initial commit (originally `558f8f7`).

## 2026-09-30 21:38 – 2026-10-01 09:59 · Phase 2: map and school panel · `81bc3b29`

**Asked:** Start Phase 2 (color-by, filters, search, school panel) before Phase 1 is finished. The next morning: Phase 1 is done, so finish Phase 2.
**Done:** The first night built `site/index.html` against a synthetic fixture with a written `SCHEMA.md` contract. In the morning it moved to the real data. `build_site.py` projects lat/lon and simplifies subdistrict and community-area outlines into `site/data/schools.json`. The page has 25 color-by options, filters, search (name, ID, address, neighborhood, RCDTS), a panel with medians, sparklines, year badges, grade bars, funding sources and flags, and a settings menu (comparison set, spending figure, year policy, subdistrict shading, size by enrollment, theme) kept in the URL hash and localStorage. Display rules: no fallback year, no trend line across a break, "suppressed" is never 0. Checked mobile and dark mode. Retired the fixture.
**Obstacles:** The fixture shape didn't match the real data (lat/lon versus x/y, per-year values, a metric registry). The simplifier collapsed closed rings to two points, which made every outline empty; fixed by splitting each ring at its farthest point. An `srs`/`srcs` typo broke the panel. JavaScript ordered grade "K" last.
**Decisions:** D-019. Left four items open: the grade 11 toggle, the enrollment diverging palette, the minimum-n rule, and the table and methodology pages.
**Commits:** none directly. The work landed in `e10c8cb`, `def375a` and `7dea61e`.

## 2026-09-30 21:37 – 2026-10-01 10:18 · Phase 1: data pipeline · `3413053b`

**Asked:** Build the normalized `schools.json`, CSVs and a validation report. After review: Catalyst Maria ("you propose, do the best thing"), stop suppressing demographics ("if they publish it, we should publish it"), and the crosswalk call is up to the session. Then: propose a solution for per-pupil spending, send a Sonnet subagent after the disability-label change, look into the ACT "ELA" column, Urban Prep Bronzeville and the roster facts, reconcile the budget, and draft emails. Then send them through Gmail ("I guess emails all the time"). Then finish the Grade 11 toggle, commit, and build the enrollment-change diverging palette.
**Done:** Built `build.py` (fetch, normalize, validate, write) with a cached `raw/`, a manifest of URLs, dates and sha256 hashes, and 11 gate tests that corrupt the data in memory. 639 schools pass. Fixed the budget fund file (two schools missing, about $37M; school total corrected to $5.38B). Added `lineage.csv` for the six charter conversions. Research results: the ISBE per-pupil figure is FY2025, matched by its enrollment denominator; the low-income/IEP change looks label-only (Sonnet agent); the ACT "ELA" column is the ELA score, so the benchmark is 20; Urban Prep was renewed through 2026-27 as one school; Virtual Academy is open but counted at home schools; ChiArts' real budget unit is `U47141`; the YCCS budget sits in one network unit. The export's $10.11B matches the published FY27 budget. Sent three emails. Built the `g11_*_gap` metrics (SAT years through the official concordance; Spearman 0.909/0.913 against the 0.85 ship bar) and the Settings toggle. Built the diverging palette (`site/diverging.css`, `tools/diverging_palette.mjs`), checked with the dataviz validator.
**Obstacles:** Hit the session limit at 21:47 and resumed at 09:42. The first build failed validation on 5Essentials level 0, which turned out to mean "not rated". Another session's stash silently reverted four pipeline files; they were re-applied. `site/index.html` changed while being read, and port 8765 belonged to another session's server, so the session used a different port. The real Phase 2 page was recovered from `backup/pre-filter-stash` (`cabeb8d`) before the toggle was added. WebFetch couldn't read the PDFs, so it parsed them with pypdf. Claude declined to guess email addresses until the owner insisted.
**Decisions:** D-004, D-008, D-009, D-010, D-011, D-016.
**Commits:** `ae907fd` grade 11 benchmark metrics · `650587f` regenerate data · `7dea61e` Grade 11 toggle, ACT ELA decision, outreach emails (also carried pan/zoom, banner and `noindex`) · `feab014` enrollment-change diverging palette.

## 2026-09-30 19:23–21:37 · Phase 0: source audit · `589a4476`

**Asked:** Confirm datasets, years, field names and join coverage, with `sources.md` as the output. On review: send a background agent to hand-match schools, an Opus agent for the SAT/ACT comparability problem, and a Sonnet agent to check the charter conversions online; try the BI portal; the session can do the hand review itself. Then the owner proposed a "computed proficiency" toggle, and exported the budget themselves.
**Done:** Downloaded and measured every source and wrote `sources.md`. Four agents ran in the background: the crosswalk (639 IDs, 613 matched to ISBE, no duplicates; `crosswalk.csv` and `crosswalk_notes.md`), `hs-assessment-proposal.md`, `charter-conversions.md` and `bi-portal.md`. Found the enacted subdistrict shapefile and checked it visually against the official PDF. All 645 schools fall in exactly one subdistrict. REQUIREMENTS.md moved to v0.4. Started NOTES.md as the plain-language basis for the methodology page. Wrote `hs-score-benchmark-method.md`. Turned the owner's budget export into `budget_units.csv` and `budget_unit_funds.csv`, matched to 637 of 639 schools through `finance_id`.
**Obstacles:** No official CPS↔ISBE ID crosswalk exists; two old portal datasets cover 81% and hand matching did the rest. The public CPS budget files have no dollar totals and no school IDs. The Board of Elections site blocks scripted downloads and only publishes PDFs. SAT was replaced by ACT, and the 2025 cut scores were lowered, so there are two breaks at once. The proficiency toggle as proposed was impossible because there are no student-level scores; it became a mean score versus the ACT benchmark instead. The BI portal's public link embeds a guest password, and Claude won't authenticate with it even when the owner says it's fine. The owner exported the data instead. The budget book PDF has no school breakdown. The export CSV is Latin-1, not UTF-8.
**Decisions:** D-001 through D-007.
**Commits:** none. Git didn't exist yet; the work entered `c9a8390`.

## Before the first session (by 2026-09-30 19:23)

REQUIREMENTS.md (draft v0.3: goal, scope, phases 0–4, the vendored "Chicago School" theme from `../politics`) existed before any Claude Code session in this repo. Its origin isn't in a transcript.
