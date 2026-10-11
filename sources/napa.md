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
3. **Visit Calistoga: events calendar** — `visitcalistoga.com/events-calendar/` (catch-all).
4. **St. Helena Summer Concert Series** — `cityofsthelena.gov/517/2026-St-Helena-Summer-Concerts-Series` (summer only; 404s out of season).
5. **sthelena.com events** — `sthelena.com/events/` (catch-all). **Use this URL, not the music-category one:** `/events/category/st-helena-events/music/` just redirects to `/events/` (confirmed 2026-08-21). Large list (255 entries in Aug 2026) behind a "Load more" button that adds about 6 at a time, so reaching six weeks out takes about 20 clicks in the browser; WebFetch only sees the first 6. Worth it: on 2026-08-21 it produced 5 of 8 candidates and confirmed Merryvale's 1st/3rd-Friday pattern when merryvale.com rendered empty. Also the working route for Merryvale and Clif Family dates.
6. **Yountville Music in the Park** — `townofyountville.gov/648/Music-in-the-Park` (summer only; the domain moved from .com to .gov; town events: `townofyountville.gov/241/Events`).
7. **The Kitchen at Priest Ranch** — `thekitchenatpr.com/events/`.
8. **Farmstead at Long Meadow Ranch** — `longmeadowranch.com/farmstead-locals-night/` and `longmeadowranch.com/things-to-do/seasonal-events/` (the authoritative calendar, supplied by Alexandra 2026-08-21).
9. **The Saint Napa Valley** — `thesaintnapavalley.com/events` (**21+ only**).
10. **Calistoga Inn & Brewery** — `calistogainn.com/restaurant`.
11. **Buster's Southern BBQ** — `busterssouthernbbq.com/`.
12. **Hydro Bar & Grill** — `hydrogrillnapavalley.com/` (HTTP 500 for three sweeps as of 2026-09-26).
13. **Lincoln Avenue Brewery (the LAB)** — `lincolnavenuebrewery.com/`. **URL corrected 2026-08-21:** the old `lincolnavebrewerycalistoga.com` is a dead domain (HTTP 521) and made the venue read as "blocked" for two sweeps. The real site publishes: Saturday "Lincoln Avenue Live!" 7–10 PM, Jam Night 1st/3rd Thursdays, Don Cameron Acoustic 3rd Friday, Mark Shuttleworth Acoustic last Wednesday, Trivia Tuesdays (ids 530, 905–907).
14. **Pacífico Restaurante Mexicano** — `pacificomexicanrestaurant.com/`.
15. **Picayune Cellars** — `picayunecellars.com/`.
16. **Sam's Social Club at Indian Springs** — `indianspringscalistoga.com/samssocialclub`.
17. **Fleetwood at Calistoga Motor Lodge** — `fleetwoodcalistoga.com/`.
18. **Girard Winery** — `girardwinery.com/events/` (select Saturdays only).
19. **RO Restaurant & Lounge** — `rorestaurantandlounge.com/`.
20. **Bardessono** — `bardessono.com/dining.htm`. Monitor only, for a Lucy music announcement (see Reference: excluded venues).
21. **Visit Napa Valley outdoor concerts guide** — `visitnapavalley.com/blog/post/outdoor-concerts-in-the-napa-valley/` (season overview; a guide, not a venue).
22. **Brannan Center** — `brannancenter.org/events` (added 2026-09-26). 1407 3rd St, Calistoga: concerts and the Kids Rock U music class. The listing renders fully in the browser; each event page gives the real start time and member price (sthelena.com mirrors it but shows pre-concert-talk times).
23. **Clif Family Winery** — 709 Main St, St. Helena; Wednesday street food with patio music 4–7 PM. Its own site timed out and 404'd on 2026-09-26, so use its sthelena.com listings (source 5).
24. **Ronnie's Awesome List** — `ronniesawesomelist.com/theawesomelist` (the old `/ronnies-awesome-list` URL 404s since Sep 2026).
25. **Merryvale Vineyards** — `merryvale.com/events/`. **JS-rendered; needs real Chrome (tier 3).** Rendered EMPTY on 2026-09-06 and 2026-09-26; Merryvale posts its Music on the Terrace dates to sthelena.com (source 5), so use those. Phone 877-887-7763.

### Monthly (not every sweep)

26. **Napa Valley Vintners** — `napavintners.com/events/index.asp` (renders blank even in the browser as of 2026-09-26).
27. **Festival Napa Valley** — `festivalnapavalley.org/calendar/` (filter to admission-free; was still showing fall 2025 on 2026-09-26).
28. **Bandsintown: Calistoga** — `bandsintown.com/c/calistoga-ca`.
29. **Bandsintown: Yountville** — `bandsintown.com/c/yountville-ca`.
30. **Yountville special events** — `yountville.com/events/special-events/`.

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
