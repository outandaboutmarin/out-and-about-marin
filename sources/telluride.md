# Sweep sources: Telluride+

<!-- FIXED FORMAT, checked by check_docs.py. This file lists SOURCES ONLY: where to look and how to read each one.
     Every rule (ages, holidays, notes, duplicates, Spanish, cadence, the workbook layout) lives in CLAUDE.md,
     section "Weekly sweep", and applies to every region identically. Do not add rules here. -->

| Field | Value |
|---|---|
| Region key | `telluride` |
| `county` value on records | `Telluride+` |
| Sweep window | today through about 7 weeks ahead (first sweep: Oct 10 to Nov 30, 2026) |
| Review workbook | `Dropbox\01. Out AND About Files\Telluride\Sweeps\telluride_sweep_YYYY-MM-DD_review.xlsx` (renamed `…_review_APPROVED.xlsx` by the partner when reviewed; setup in `Telluride\PARTNER_SETUP.md`) |
| Source count | 10 |

All times are Mountain Time. Region facts (location groups, decisions) are in CLAUDE.md, "Regions".


## Sources

### Libraries (all read with plain fetches; no Chrome needed as of 2026-10-10)

1. **Wilkinson Public Library, Telluride** (LibCal). The page shows about 10 events; read the **iCal feed** `telluridelibrary.libcal.com/ical_subscribe.php?src=p&cid=19928`, which has every event. Times are **UTC**: subtract 6 h before Nov 1 and 7 h after. Open the file with `newline=''` and unfold continuation lines, or the descriptions come out cut short.
2. **Lone Cone Library, Norwood**: `lonecone.librarycalendar.com/events/list?page=0..8` (mixes room bookings with programs; the yoga classes are outside instructors' bookings) plus `lcld.specialdistrict.org/ongoing-programs`. The weekly update is a Canva embed and cannot be read as text.
3. **Ridgway Library**: `ridgwaylibrary.specialdistrict.org/calendar` and `?month=YYYY-MM` (titles only), plus each program page for times.
4. **Ouray Public Library**: `ouray.colibraries.org/lib-cal/` (use its own next-month link, which carries a `cid`). Monthly toddler storytime is sign-up by email.
5. **Montrose Regional Library**: one WordPress events API, `montroselibrary.org/wp-json/tribe/events/v1/events?start_date=&end_date=&per_page=50&page=N`. The main branch is **closed Saturdays**.
6. **Naturita Community Library (MRLD branch)**: same WordPress events API as source 5; Naturita events carry the `Naturita` category.
7. **MRLD Outreach / Bookmobile**: same API as source 5, category `Outreach/Bookmobile` (Olathe Town Park 1st & 3rd Wed, Northbrook Villas Park 1st & 3rd Thu, 3:15–4:15 PM, Sep–Dec).
8. **Dolores Public Library**: `doloreslibrary.specialdistrict.org/calendar?month=YYYY-MM` plus the monthly newsletter, whose program flyers are **images** (read them as images).
9. **Rico Public Library**: no web presence (open item 66e, ask Lee).

### Event sources

10. **Visit Telluride (Telluride Tourism Board) — Festivals & Events calendar** (added 2026-10-17 at Alexandra's request): `telluride.com/festivals-events/events/` (the Events tab; the Festivals tab, `/festivals-events/festivals/`, is a subset of it). **The list is built by script, so a plain fetch shows an empty "Showing 0 of 0" list.** Open it in the in-app browser and read the page's own data (the Vue component's `items` array: title, `attrs.dates`, type, category, area, url; 68 items through Sep 2027 on 2026-10-17). Then fetch each event page in the window (`telluride.com/event/<slug>/`, plain fetch works) for time, venue, address (the Get Directions link) and the organiser's own link under "Learn More"; use that link as `website` where there is one. Category ids: 1076 Kids, 1081 Theatre, 1073 Film, 1078 Live Music, 1074 Fundraiser, 50191 Holidays, 1079 Local Government. Much of it is adult or evening (bars, concerts, talks); Alexandra expects Telluride content to skew more adult. Library events listed here (Wilkinson) duplicate sources 1-9: dedupe by venue. First pass: workbook `Telluride\Sweeps	elluride_sweep_2026-10-17_review.xlsx`, ids 1679-1694.

## Not yet verified

The event sources in `Dropbox\01. Out AND About Files\Telluride\Telluride_Region_Research_v2.xlsx`
(Event Sources and Attestation Log tabs: markets, community calendars, arts venues, schools, government, community orgs,
including Lee's 18) are NOT yet in the sweep. Move each one up into "Sources" only after its live page has been read
and its fetch method written down, in the same numbered format.
