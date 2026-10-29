# Sweep sources: Napa

<!-- FIXED FORMAT, checked by check_docs.py. This file lists SOURCES ONLY: where to look and how to read each one.
     Every rule (ages, holidays, notes, duplicates, Spanish, cadence, the workbook layout) lives in CLAUDE.md,
     section "Weekly sweep", and applies to every region identically. Do not add rules here. -->

| Field | Value |
|---|---|
| Region key | `napa` |
| `county` value on records | `Napa` |
| Sweep window | 8 weeks ahead of today |
| Review workbook | `Dropbox\01. Out AND About Files\OAA maintence and content\napa_sweep_YYYY-MM-DD_review.xlsx`; also log the sweep in the Weekly Sweep Log tab of `Napa_Live_Music_Tracker_v2.xlsx` (same folder; read its Sweep Learnings tab first) |
| Source count | 30 |


## Sources

### Every sweep

1. **Calistoga Depot Distillery / Depot Live** — `calistogadepot.com/distillery/events`. Added 2026-08-12. The recurring Fri/Sat 6–9 PM and Sun 5–8 PM nights are held as two Weekly records, so this fetch is for the dated performer lineup and any change to the recurring nights or a new season. Do not re-add the weekly nights as one-offs.
2. **Visit Calistoga: Concerts in the Park** — `visitcalistoga.com/concerts-in-the-park/` (summer series; 404s out of season).
3. **Visit Calistoga: events calendar** — `visitcalistoga.com/events-calendar/` (catch-all). **Built by script (MEC plugin): read it in the in-app browser and click `.mec-load-more-button` until the list passes the window end** (10 clicks reached Dec 19 on 2026-10-29); each item's `visitcalistoga.com/events/<slug>/` page reads with a plain fetch and gives time, price and organiser. Also carries Calistoga town events (Halloween Parade, Lighted Tractor Parade at `/lighted-tractor-parade/`), The Village Calistoga kids' nights, and LAB and Clif listings.
4. **St. Helena Summer Concert Series** — `cityofsthelena.gov/517/2026-St-Helena-Summer-Concerts-Series` (summer only; 404s out of season).
5. **sthelena.com events** — `sthelena.com/events/` (catch-all). **Use this URL, not the music-category one:** `/events/category/st-helena-events/music/` just redirects to `/events/` (confirmed 2026-08-21). Large list (255 entries in Aug 2026) behind a "Load more" button that adds about 6 at a time, so reaching six weeks out takes about 20 clicks in the browser; WebFetch only sees the first 6. **2026-10-29: the button is `.wpgb-load-more` ("LOAD MORE (N)"); click it in batches of about 8 per browser call (one long loop times out), ~25 clicks to reach mid-December, ~150 items.** Event pages (`sthelena.com/event/<slug>/`) read with a plain fetch and give the organiser and street location. Worth it: on 2026-08-21 it produced 5 of 8 candidates and confirmed Merryvale's 1st/3rd-Friday pattern when merryvale.com rendered empty. Also the working route for Merryvale and Clif Family dates.
6. **Yountville Music in the Park** — `townofyountville.gov/648/Music-in-the-Park` (summer only; the domain moved from .com to .gov; town events: `townofyountville.gov/241/Events`, which on 2026-10-29 held only art calls; the Town's own events, such as the Town & Tree Lighting, appear on the Chamber calendar in source 30).
7. **The Kitchen at Priest Ranch** — `thekitchenatpr.com/events/`. The page's Upcoming Events list is often empty; **read the raw WordPress API `thekitchenatpr.com/wp-json/wp/v2/event?per_page=30`** (titles and dates in each post) and `/calendar/`.
8. **Farmstead at Long Meadow Ranch** — `longmeadowranch.com/farmstead-locals-night/` and `longmeadowranch.com/things-to-do/seasonal-events/` (the authoritative calendar, supplied by Alexandra 2026-08-21).
9. **The Saint Napa Valley** — `thesaintnapavalley.com/events` (**21+ only**).
10. **Calistoga Inn & Brewery** — `calistogainn.com/restaurant`.
11. **Buster's Southern BBQ** — `busterssouthernbbq.com/`.
12. **Hydro Bar & Grill** — `hydrogrillnapavalley.com/`. **Back up on 2026-10-29** (HTTP 500 for three sweeps before). Its "This Week: Live Entertainment" block is filled by script: read it in the in-app browser (`#events-grid`, or `window.HYDRO_SITE.events`). On 2026-10-29: Tue Open Mic 6 PM, Sat Monflower Jazz Duo 6 PM, Sun The Tritones 6 PM.
13. **Lincoln Avenue Brewery (the LAB), Calistoga** — `localq707atthelab.godaddysites.com/` and `/hours-and-events` (LocalQ 707 at the LAB, 1473 B Lincoln Ave, 707-403-5028). **URL corrected 2026-10-29:** the URL used from 2026-08-21, `lincolnavenuebrewery.com`, is a DIFFERENT brewery in Bellevue (Pittsburgh), Pennsylvania; check the address on any venue site before trusting it. The Calistoga LAB lists Monday Bingo Night, Friday Karaoke Night (7 PM, all ages, free, per Visit Calistoga) and Saturday Live Music; it does not list the Jam Night, Don Cameron, Mark Shuttleworth or Trivia Tuesdays that came from the Pennsylvania site (ids 905-907, retirement proposed in the 2026-10-29 workbook). Visit Calistoga (source 3) also lists its karaoke.
14. **Pacífico Restaurante Mexicano** — `pacificomexicanrestaurant.com/`.
15. **Picayune Cellars** — `picayunecellars.com/`.
16. **Sam's Social Club at Indian Springs** — `indianspringscalistoga.com/samssocialclub` (plain fetch 403s; the in-app browser reads it).
17. **Fleetwood at Calistoga Motor Lodge** — `fleetwoodcalistoga.com/` (a plain fetch returns an empty shell; use the in-app browser. `/events` is private events only).
18. **Girard Winery** — `girardwinery.com/events/` (select Saturdays only).
19. **RO Restaurant & Lounge** — `rorestaurantandlounge.com/`.
20. **Bardessono** — `bardessono.com/dining.htm`. Monitor only, for a Lucy music announcement (see Reference: excluded venues).
21. **Visit Napa Valley outdoor concerts guide** — `visitnapavalley.com/blog/post/outdoor-concerts-in-the-napa-valley/` (season overview; a guide, not a venue).
22. **Brannan Center** — `brannancenter.org/events` (added 2026-09-26). 1407 3rd St, Calistoga: concerts and the Kids Rock U music class. The listing renders fully in the browser; each event page gives the real start time and member price (sthelena.com mirrors it but shows pre-concert-talk times).
23. **Clif Family Winery** — 709 Main St, St. Helena; Wednesday street food with patio music 4–7 PM. Its own site timed out and 404'd on 2026-09-26, so use its sthelena.com listings (source 5).
24. **Ronnie's Awesome List** — `ronniesawesomelist.com/theawesomelist` (the old `/ronnies-awesome-list` URL 404s since Sep 2026).
25. **Merryvale Vineyards** — `merryvale.com/events/`. **JS-rendered; needs real Chrome (tier 3).** Rendered EMPTY on 2026-09-06 and 2026-09-26; Merryvale posts its Music on the Terrace dates to sthelena.com (source 5), so use those. Phone 877-887-7763. **2026-10-29: real Chrome read it fine** (holiday dinner and 2027 trivia only).

### Monthly (not every sweep)

26. **Napa Valley Vintners** — `napavintners.com/events/index.asp` (renders blank in the in-app browser; **real Chrome gets HTTP 403 "Access denied" as of 2026-10-29**, so attest it as blocked after all three tiers).
27. **Festival Napa Valley** — `festivalnapavalley.org/calendar/` (filter to admission-free; was still showing fall 2025 on 2026-09-26).
28. **Bandsintown: Calistoga** — `bandsintown.com/c/calistoga-ca`.
29. **Bandsintown: Yountville** — `bandsintown.com/c/yountville-ca`.
30. **Yountville special events** — `yountville.com/events/special-events/`. **The real calendar is `web.yountville.com/events`** (a month grid built by script: read it in the in-app browser, step with the `.fc-next-button`, and read each event's details from the page text, which carries start, end, address and description). It lists the Town of Yountville's events (Halloween Block Party, Town & Tree Lighting, Visits with Santa, Holiday Sing Along) and many Napa-city resort events (Meritage, Carneros) that are outside the three towns.

## Retired or seasonal

- **Dead as of 2026-09-26:** the Napa Valley Register community-calendar article (now redirects to the news homepage).
- **Seasonal:** sources 2, 4 and 6 are summer park series and 404 out of season.

## Reference

**Known venues and recurring series** (as of 2026-06-27; re-verify each sweep, especially "check site"/TBA rows):

*Calistoga* — Pioneer Park "Concerts in the Park" (Thu, Jun 18–Aug 20, 6:30–8:30 PM, free); Calistoga Inn & Brewery (Fri/Sat 6–9 PM, May–Oct); Buster's Southern BBQ (Sun 3–6 PM); Lincoln Avenue Brewery / the LAB (see source 13); Cami Art + Wine (Sat/Sun 3–5 PM); Hydro Bar & Grill (Sun 6–9 PM, The Tritones); Pacífico Restaurante Mexicano (Fri steel drums 5:30 PM + DJ 10 PM / Sat acoustic 5:30 PM); Picayune Cellars (Fri 6–8 PM); Sam's Social Club at Indian Springs (Sun 10 AM–1 PM brunch); Fleetwood at Calistoga Motor Lodge (Thu 5–7 PM, May–Oct); Girard Winery (select Saturdays only; confirmed 2026: Jul 25, Aug 29, Sep 26, 12–2 PM); Calistoga Depot Distillery / "Depot Live" (1458 Lincoln Ave, 707-963-6925; Fri 6–9 PM, Sat 6–9 PM, Sun 5–8 PM).

*St. Helena* — Lyman Park "Summer Concert Series" (Wed, Jun 17–Aug 12, 6–8 PM, free); The Saint Napa Valley (Tue "Bluesy Tuesday" 3–9 PM / Fri 8–11 PM, 21+); Farmstead at Long Meadow Ranch (Wed 4–7 PM, seasonal Jun–Sep); Merryvale Vineyards (1st & 3rd Fridays, May–Sep, 5–7 PM).

*Yountville* — Veterans Memorial Park "Music in the Park" (select Sundays, 5–7 PM, free); Napa Valley Vine Trail Rest Stop "Music Moves You!" (one-off dates via festivalnapavalley.org); Kitchen at Priest Ranch "Thursday Night Live" (select Thursdays, Jul–Sep, 6–9 PM); RO Restaurant & Lounge (Fri 6:30–9:30 PM).

**Paused pending a phone check (open item 38):** six weekly records rested only on Visit Calistoga's June 2022 "hot spots" guide and are `Temp. paused`: Picayune 511, Cami 529, Pacífico 531/532, Sam's 533, Hydro 510 (Buster's 509 and Fleetwood 534 were already paused).

**Excluded venues (do not add without a fresh confirmation call):** Freemark Abbey Winery (piano music only in old travel guides; 707-302-3717) and Lucy Restaurant & Bar at Bardessono (third-party mentions only, not on lucyyountville.com or bardessono.com; 707-204-6030).
