# Outreach emails (sent)

The questions sent to data publishers, and whether they've been answered. The letters below keep the placeholder recipient and signature they were drafted with.

**Format** (parsed by `tools/logs.py outreach`, checked by `tests/test_logs.py`): each email is a `## N. Recipient: topic` heading followed by these lines, then the letter.

```
**Sent:** YYYY-MM-DD HH:MM to `address`   (or "not sent")
**Status:** Awaiting reply | Answered YYYY-MM-DD | Bounced | No reply, closed
**Related:** D-0xx, NOTES.md caveat N   (what to update when the answer comes)
```

## 1. CPS budget office: Catalyst Maria

**Sent:** 2026-10-01 09:59 to `financedep@cps.edu`
**Status:** Awaiting reply
**Related:** D-008, NOTES.md caveat 20
**To:** [CPS Office of Budget / Finance contact]
**Subject:** Question on FY27 budget unit U66433 (Catalyst Maria)

Hello,

I'm building a public, sourced reference page of Chicago school facts from CPS's published data, and I have a question about the FY27 budget export.

Budget unit U66433 (Catalyst Maria) shows about $22.1 million. CPS lists two Catalyst Maria schools in the SY2026-27 20th-day file: CATALYST - MARIA (ID 400115, 564 students) and CATALYST MARIA HS (ID 400182, 541 students). Only the first has a budget unit of its own.

Does U66433 cover both campuses (about 1,105 students combined)? If so, I will show a combined per-pupil figure (about $20,000) on both schools and label it. If it covers only 400115, please tell me where the high school's budget sits.

Thank you,
[Name]

## 2. CPS data office: Low Income and IEP labels

**Sent:** 2026-10-01 09:59 to `accountability@cps.edu` (a guessed address; watch for a bounce)
**Status:** Awaiting reply
**Related:** NOTES.md caveat 3
**To:** [CPS Office of Student Information / data contact]
**Subject:** Question on the SY2026-27 20th-day demographics file

Hello,

Between the SY2025-26 and SY2026-27 20th-day demographics files, the columns changed from "Economically Disadvantaged" to "Low Income" and from "Students with Disabilities" to "Students with IEPs". The district share fell from 71.8% to 68.9%.

1. Did the source data, the matching process (direct certification, SNAP/TANF, Medicaid, homeless, foster, migrant flags) or the 185% poverty-line criterion change, or only the label?
2. Is "Students with IEPs" counted the same way as "Students with Disabilities"?
3. Chalkbeat reported that CPS expects some demographic figures to be updated as schools finish their data. Is the SY2026-27 file preliminary, and when will it be revised?

I'm asking so I don't show year-over-year changes that are really definition changes. Until I hear back I will not compare these two measures across the two years.

Thank you,
[Name]

## 3. ISBE Report Card team: per-pupil year and ACT "ELA"

**Sent:** 2026-10-01 09:59 to `reportcard@isbe.net`
**Status:** Awaiting reply
**Related:** D-004, NOTES.md caveats 4 and 18
**To:** [ISBE Illinois Report Card contact]
**Subject:** Two data questions on the 2025 Report Card public data set

Hello,

1. **Per-pupil expenditure year.** In the 2025 Report Card file, the Finance sheet's per-pupil expenditures use a school enrollment that matches the district's SY2024-25 enrollment. Can you confirm they are FY2025 expenditures (July 2024 to June 2025)?
2. **ACT "ELA".** In the ACT sheet, "ACT ELA Average Score - Grade 11" and "ACT ELA Proficiency Rate Grade 11 - Total": is the ELA score the ACT ELA score (the average of English, reading and writing), not the English subscore?
3. **ACT growth.** How was the 2025 grade 11 growth percentile computed across the move from PSAT 10 to ACT?

Thank you,
[Name]
