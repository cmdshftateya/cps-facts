# CPS FY27 BI Portal (Interactive Reports) investigation

Date: 2026-09-30

## Decision: NOT verified usable; automated fetch not recommended. Manual export by the owner is the only possible path, and it needs a decision from the owner about the guest login.

## What I found

1. The href on both https://www.cps.edu/about/finance/budget/budget-2027/ and /more-information-2027/ is:
   `https://biportal.cps.edu/analytics/saw.dll?Portal&PortalPath=%2Fshared%2FCPS%20FY27%20Budget%2F_portal%2FChicago%20Public%20Schools%20FY27%20Budget%20Interactive%20Reports&NQUser=<guest user>&NQPassword=<guest password>`
   The public CPS page itself embeds a shared guest username and password (a "cpsbiguest" account) as NQUser / NQPassword query parameters. Same pattern on the FY26 page (`CPS FY26 Budget` portal path). I am not reproducing the password here; read it from the page HTML (view-source of the budget-2027 page, search "biportal").
2. Anonymous access does NOT work. Requesting the portal URL without NQUser/NQPassword:
   - with a generic UA: "Your browser is not supported by Oracle BI Presentation Services" stub (Oracle BIEE, UA-gated);
   - with a Chrome UA: HTTP 200 "Oracle Business Intelligence Sign In" page (User ID / Password form).
   So the dashboard only loads through the guest credentials CPS puts in the link.
3. I stopped there. Using the NQUser/NQPassword in the URL is authenticating with a password, which I was told not to do. I did not open the dashboard, so I could NOT confirm: which dashboard pages exist, whether total dollars per school are shown, whether a school ID column exists, whether sample schools show totals, or whether export works. Anything about contents below is unverified.
4. Terms of use: I did not find terms on the portal sign-in page. No robots.txt on biportal.cps.edu (404). Not reviewed beyond that; the owner should check the cps.edu terms/footer.
5. School profile pages: https://www.cps.edu/schools/profiles/ and a sample profile (https://www.cps.edu/schools/profiles/609678/ returned 200) contain no budget figures in the HTML text; the only "budget" text is the site nav link. (JS-rendered content not checked; the /schools/school-profiles/ path 404s.)

## Likely behavior (unverified, based on how OBIEE works generally)

- OBIEE answers can usually be exported via the dashboard "Export" link (CSV/Excel/PDF) or by `saw.dll?Go&Action=Download&Format=csv&path=...` URLs, but these require an authenticated session cookie (ECID/ORA_BIPS_NQID) obtained after the guest login. A build script would need to log in with the guest account, hold cookies and handle expiring session tokens. This is fragile and uses the shared credential programmatically, so I do not recommend it for automation.
- Many CPS budget dashboards are school-level (by fund/position/expense category), so a total per school is plausible, but I could not confirm it or the presence of a school ID (likely a unit/school number if present).

## Steps for the project owner to try (manual export)

1. Open the "INTERACTIVE REPORTS 2027" link from https://www.cps.edu/about/finance/budget/budget-2027/ in a normal desktop Chrome/Edge/Firefox (Oracle BI rejects unusual user agents). The link logs in as the public guest automatically.
2. Review each dashboard tab; find the school-level view with budget dollars (by fund / expense category / position). Note whether a school ID/unit number column is present.
3. Filter to one school-level view with all schools (clear filters, set Fiscal Year 2027), expand to the full table.
4. Use the "Export" link under the table (Excel or Data > CSV). Save to cps-facts/data/raw/.
5. Verify: 3 sample schools (a neighborhood school, a selective/magnet, an Alt-Spec/charter-managed), column list, and that totals reconcile to the xlsx FTE counts.
6. Record the export date; the dashboard is not versioned.

## Fallback recommendation

- Treat portal data as a one-time manual snapshot checked into the repo (CSV), not a build-time fetch.
- If it lacks school IDs, join by normalized school name to the xlsx/CPS school list and flag unmatched.
- If nothing usable: keep staffing FTEs + per-pupil components from the xlsx, and estimate nothing; show "total dollars not published at school level in open data" rather than computing a figure. Alternatively file a CPS FOIA request for the school-level FY27 budget table with school IDs.
