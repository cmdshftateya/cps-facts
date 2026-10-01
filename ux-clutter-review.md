# Clutter and overload review: map page

2026-10-01, session `8bd56763`. This review covers how the map page presents information and where it overloads the reader. I checked the map, legend, table, school panel, Settings menu, and the Data and Methodology pages in headless Chromium at 1440px and 360px, in both themes. I didn't check a real phone or a screen reader.

## Before and after

| | Before | After |
|---|---|---|
| Cluster circles at full-city view (1440×900) | 134 (110 of them "2") | 57; later superseded, since `main` removed clustering (D-025) |
| School panel height, Ariel (elementary) | 3,486 px | 2,130 px (−39%) |
| School panel height, Amundsen HS | not measured | 2,583 px |
| Year badges in the panel | one per tile (about 30) | one per section, plus a badge on each tile whose year differs |
| Year badge in the table | on every row | in the column header, plus a badge on rows that differ |
| Floating Settings button | covered the panel and the table's last column | sits in the header |

## Findings, worst first

1. **Cluster circles were the loudest thing on the map.** Markers merged when they were within 15 px of each other, which is about twice a marker's width. Most "clusters" were two schools that didn't overlap at all, drawn as numbered circles with a dark outline. About 130 of them outweighed the 500 colored squares they sat on. **Fixed:** markers merge only when they actually overlap (9 px), the circles are smaller, and the outline matches the page color. *Superseded:* another session removed clustering altogether (D-025), and that version is what shipped.
2. **Every panel tile repeated the same metadata:** a year badge, "City median", a sparkline and a year-range caption under the sparkline. Across about 30 tiles that added up to roughly 120 small labels, most of them identical. **Fixed:** each section heading states its year once ("DEMOGRAPHICS SY26-27"), and a tile gets a badge only when its year differs from that. The range caption moved into the sparkline's tooltip.
3. **Secondary measures each got a full tile.** These were five race and ethnicity shares, five spending-detail figures, four 5Essentials levels and two ACT averages. **Fixed:** each group is now one compact table with School, Median and a small trend line. The headline measures (enrollment, low income, EL, IEP, test scores, attendance, per-pupil spending) keep their tiles.
4. **Panel tiles turned black on hover.** The vendored `chicago.css` gives `.cell` a hover inversion and a 10 px flex gap. The panel reused that class name, so moving the mouse down the panel flashed each tile black, and on a phone a tapped tile stayed black. **Fixed:** the panel uses its own `.tile` class.
5. **The source list was a 12-item paragraph at the foot of every panel.** **Fixed:** it's folded into "Sources (12)". The dagger notes and the "suppressed / no data" note stay visible.
6. **The floating Settings button covered content.** On desktop it sat over the panel's tiles and the table's last column. **Fixed:** it moved into the header next to Map/Table. On phones the menu still opens as a bottom sheet.
7. **The legend had a separate year line ("SY26-27") and always showed a "No data" key.** **Fixed:** the year sits next to the title, and the "No data" key appears only when a visible school has no data.
8. **Header and sidebar noise.** The header said "639 of 639 schools" when nothing was filtered, and "Reset filters" showed even with no filters set. **Fixed:** the header reads "639 schools" until a filter applies, and Reset appears only when a filter is set. On phones the "Roster … data built …" line is hidden, so the header is 130 px tall instead of about 155 px.

## Second pass, done after the owner said "go"

| | Before | After |
|---|---|---|
| Sidebar | Search, Color by, then four filter dropdowns, a checkbox and Reset, always open | Search and Color by; filters fold under "Filters", which shows "· N on" when any are set and opens itself when a link carries filters |
| Color by menu | Full labels, cut off at 260px ("Low income / economically disa…") | Short names ("Low income"). The full label stays in the legend, the table header and the option's tooltip |
| Governance shapes | Hollow charter squares and diamonds in every view, with a shape key in every legend | Shapes only when coloring by school type (D-029). The legend draws each type with its shape, and clusters in that view fill by type |
| School panel | The measure you were looking at was somewhere among about 30 tiles | It opens with a highlighted line: the measure, its year, the school's value and the city median |
| Data and sources page (1280px) | 7,185 px | 1,851 px. Each source is a one-line summary (title and publisher) that opens for detail. The 54-row field table sits behind "Show all 54 values" |

I also fixed a stray apostrophe on the Data page ("'In schools.csv").

## Still open

- **Real-phone check** of all of the above. Only emulated viewports were checked.
- **Phone map density:** at 360px most markers overlap, so markers pile up until you zoom. Opening phones in table view (the current default under 760px) is the right answer, so I left it alone.
