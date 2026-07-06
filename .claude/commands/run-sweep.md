Run the full Out AND About Marin Weekly Sweep: check every source below for new/changed family events in Marin County, dedupe against `events.json`, and produce a review file for Alexandra.

Read `CLAUDE.md` first for the event schema, data quality rules, and dedup rules — apply them throughout.

## Process

1. **Load `events.json`** (via `events_io.py` — `load_events()`) so you have the current dataset to dedupe against.
2. **Go through every source below, in order.** For each one:
   - Fetch the URL using the method specified — a web search snippet alone is NOT sufficient, you must fetch the actual live page/calendar and read every current/upcoming event off it. If a source is marked with a workaround (JS-rendered, robots-blocked, etc.), use that workaround — do not stop at "JS-rendered, no list."
   - Compare every candidate event (name + date + venue) against `events.json` using `find_event()` in `events_io.py` before treating it as new. Skip anything already present under any status.
   - Record: source name, URL fetched, method used, # of current items reviewed, newest item date seen, and the result (candidates found, or "none — fetched live list, N items reviewed").
   - Do NOT report a source as done from assumption. If you could not complete a source, say so explicitly rather than silently skipping it.
3. **If you cannot complete all sources in one session**, tell Alexandra upfront before starting, rather than silently presenting a partial sweep as complete.
4. **Build the review workbook** with two sheets:
   - **Sheet 1 "Attestation Log"**: one row per source (all 37) — columns: Source | Category (Event Source / Library / Learning Bus) | URL Fetched | Method | Result | # Current Items Reviewed | Newest Item Date Seen.
   - **Sheet 2 "Weekly Sweep"**: one row per genuinely new candidate — columns: Decision (blank, for Alexandra to fill Approve/Skip) | Event Name | Date | Day | Time | Venue | Town | Description | Source URL | Notes | Type | Location Filter | Ages | Cost | Indoor/Outdoor | Cadence. Flag anything genuinely uncertain with "⚠ POSSIBLE DUPE" in Notes rather than silently including or excluding it.
5. **Save the workbook** to `C:\Users\AWalter\Documents\2. Claude-Work\PROJECTS\OAA Marin\OAA maintence and content\daily_sweep_YYYY-MM-DD_review.xlsx` (today's date). Do not save it inside this repo, and do not commit/push it.
6. **Summarize in chat**: how many sources were fully checked, how many candidates were found, any sources you couldn't complete, and where the review file is. Tell Alexandra to fill in the Decision column and let you know when it's ready for `/process-sweep`.

## Source checklist (37 total: 20 event sources + 16 libraries + Learning Bus)

Napa-area events (Calistoga, St. Helena, Yountville) are NOT part of this checklist — Marin-only, per CLAUDE.md.

### Event sources (20)

1. **Marin Mommies — Weekend Post** (marinmommies.com) — Do NOT use the "Weekend Family Fun for [dates]" blog-post URLs — confirmed (2026-07) to serve stale content cached by URL slug regardless of actual year (e.g. a "July 8-10" slug returned 2022 content, a "July 11-13" slug returned 2025 content). Instead fetch the per-day pages directly: marinmommies.com/calendar/YYYY-MM-DD for the upcoming Friday, Saturday, and Sunday — these are live and reliably dated. Supplement with per-town web searches (Tiburon, Mill Valley, San Rafael, Novato, Fairfax, Sausalito, San Anselmo, Larkspur, Ross) as a cross-check only, not as the primary fetch. Confirm specifics via per-event pages at marinmommies.com/calendar/[event-slug] (these ARE fetchable and reliable). Cross-check day-of-week labels against a real calendar — the site has mislabeled days before.
2. **Marin Mommies — 14-day Calendar** — fetch marinmommies.com/calendar/YYYY-MM-DD for today + next 13 days.
3. **Marin Mommies — General Calendar** — fetch marinmommies.com/calendar directly, scan for anything not caught by #1/#2.
4. **Strawberry Recreation District** — fetch strawberry.marin.org/events-page/ directly.
5. **Sweetwater Music Hall** — fetch sweetwatermusichall.org/events/ directly, filter for family/all-ages/daytime shows.
6. **Osher Marin JCC** — fetch marinjcc.org/programs/ directly, look for Tot Pool Party, JymBabies, Shabbat ShaBabies dates.
7. **Mill Valley Community Center** — fetch millvalleylibrary.org/calendar.aspx?CID=23 (CivicEngage month grid — page via grid arrows) AND scan event detail pages. The /289/Special-Events page is a stub, do NOT rely on it alone.
8. **Sausalito City Events** — **RESOLVED 2026-07**: the whole sausalito.gov domain sits behind an Akamai bot-management WAF that 403s any WebFetch/curl request regardless of headers — this is fingerprint/behavior-based, not fixable by URL or header changes. Use the Chrome browser tools instead (`navigate` + `get_page_text`) — a real browser session passes through fine. Correct URL is sausalito.gov/our-city/local-events/city-calendar (NOT /our-city/calendar-of-events, which 404s). The homepage itself also shows a live preview widget of upcoming events if you need a quick check. Note: this calendar is shared with Sausalito Public Library (#38 below) — same Granicus-powered event system, same event list appears on both sites.
9. **Enjoy Mill Valley** — fetch enjoymillvalley.com directly.
10. **Marin Country Mart** — fetch marincountrymart.com/events directly.
11. **Ronnie's Awesome List** — fetch the current Marin kids roundup page, plus ronniesawesomelist.com/free-music-marin and /outdoor-movies. Newsletter drops Thursdays — check on Friday sweeps.
12. **Bay Area Kid Fun** — fetch bayareakidfun.com/family-friendly-events-in-the-bay-area/, filter to Marin towns only.
13. **Marin County Parks** — the parks.marincounty.org calendar is JS/Trumba and won't fetch directly. PRIMARY: fetch onetam.org/calendar (page 1) and onetam.org/calendar?page=1 (page 2) — server-rendered, reliably returns full Marin County Parks event list. Filter for family/ranger/nature programs.
14. **Marin Humane Society** — fetch marinhumane.org/events/ directly, look for Woofstock and family/adoption events.
15. **MALT (Marin Agricultural Land Trust)** — malt.org/malt_events/ is confirmed (2026-07) broken (404) — fetch malt.org/events/ instead. Note: as of 2026-07 this page was serving stale/prior-year content — verify dates carefully before treating anything as current, and flag to Alexandra if it's still stale next sweep.
16. **Megan Schoenbohm — Upcoming Shows** — fetch musictimewithmegan.com/copy-of-classes directly (page titled "UPCOMING SHOWS"). Marin venues only: Marin Country Mart (Larkspur), Pelican Inn (Muir Beach), Novato Farmers Market. Do NOT add Bon Air entries — removed at Alexandra's direction. Confirmed (2026-07) this page appears stale/unmaintained (still showing prior-year dates) — verify the year on any date found before reporting a candidate; flag to Alexandra if still stale.
17. **The Redwoods Senior Living Center** — no online calendar. Manually managed (Oldies Music, Wednesdays, ID 188). No fetch needed unless Alexandra reports a schedule change.
18. **Goodie's Kids Club (Goodman Building Supply)** — fetch goodmanbuildingsupply.net/goodies-kids-club/ directly. Date/theme posted ~2 weeks ahead each month; add the next session as a dated one-off if missing.
19. **Marin Hiking Moms — Monthly Hike** — WhatsApp/Instagram only, no fetchable page. Confirm location is still King Mountain Loop Trail if Alexandra flags a change; otherwise no action needed.
20. **The Phoenix Used Bookshop** — fetch phoenixusedbookshop.com directly; check Instagram @phoenixusedbookshop if no events page exists yet.
21. **The Village at Corte Madera — Acoustic Weekends** — fetch villageatcortemadera.com/Events directly; confirm the recurring Sat/Sun series is still running and note any schedule changes (IDs 474/475 already cover the recurring slots — only add new entries for a specific named performer/special event).
22. **Ross Valley Farm Walk** — no public website, sourced via Nextdoor Tamalpais Valley group. Confirm each summer sweep whether it's still running (Jun–Aug only) — no fetch route, flag to Alexandra if status is unclear.
23. **San Rafael Library & Recreation — Annual Summer Programs PDF** — fetch srpubliclibrary.org/events/ to find the current summer PDF link, then fetch the PDF with text extraction. Once per summer (June), not every sweep. Read all 3 locations (Downtown, Northgate, Al Boro CC).

(Note: list above has 23 numbered entries because the historical Excel's "20" count folds a few multi-part sources together — treat each numbered line as one checklist item; that's the working granularity.)

### Libraries (16) — every sweep, no exceptions, even though programs are "recurring/already in DB" — one-off guest performers and specials show up on these calendars constantly

24. **Belvedere-Tiburon Library** — fetch beltiblibrary.org/kids/summer-reading (dated summer-performer lineup, best single page) AND beltiblibrary.org/events (paginated year-round list, page forward as needed). The Communico calendar and Eventbrite org page are JS-rendered — don't use those.
25. **MCFL — Civic Center** (San Rafael) — fetch marinlibrary.org/locations/mc/. **CORRECTED 2026-07**: `/mb/` (previously documented here) actually resolves to Bolinas, not Civic Center — verified via marinlibrary.bibliocommons.com/v2/locations.
26. **MCFL — Corte Madera** — fetch marinlibrary.org/locations/mm/. Check closure status (2nd Refresh closure Jul 6–Sep 2, 2026 — reopens Sep 3). During this closure, some programs relocate to Corte Madera Community Center (offsite) — check for relocated/temporary listings, not just a closure notice.
27. **MCFL — Fairfax** — fetch marinlibrary.org/locations/mf/.
28. **MCFL — Marin City** — fetch marinlibrary.org/locations/ma/. **CORRECTED 2026-07**: `/mc/` (previously documented here) actually resolves to Civic Center, not Marin City — verified via marinlibrary.bibliocommons.com/v2/locations.
29. **MCFL — Novato** — fetch marinlibrary.org/locations/mn/. Check closure status (closed Jun 17–Aug 18, 2026, reopens Aug 19). Note: Novato Library's page also lists Bookmobile curbside visits during this closure — Alexandra has said Bookmobile stops are explicitly out of scope for this site (Learning Bus only), so exclude any Bookmobile items even if they appear on this page.
30. **MCFL — South Novato** — fetch marinlibrary.org/locations/mh/. **CORRECTED 2026-07**: this is a genuinely distinct branch page, NOT the same page as Novato as previously documented — verified via marinlibrary.bibliocommons.com/v2/locations and branch address confirmation.
31. **MCFL — Point Reyes** — fetch marinlibrary.org/locations/mp/.
32. **MCFL — Bolinas** — fetch marinlibrary.org/locations/mb/ directly (see corrected slug note on #25 above — this is the real Bolinas page); check marinlibrary.bibliocommons.com series URLs for existing program IDs (175/176) as a supplement. Very small branch.
33. **MCFL — Inverness** — fetch marinlibrary.org/locations/mi/ (very small branch, check manually).
34. **MCFL — Stinson Beach** — fetch marinlibrary.org/locations/ms/ (very small branch, check manually).
35. **Mill Valley Public Library** — libcal calendar is JS and looks empty on direct fetch. Run the full `site:millvalleylibrary.libcal.com/event [program type] 2026` search-around AND fetch millvalleylibrary.org homepage (lists featured specials by date), then fetch each individual event page found. Resolve every homepage teaser to a concrete event before closing this row. Do NOT rely on the iCal feed — it goes stale.
36. **San Anselmo Library** — fetch sananselmo.gov/Calendar.aspx?CID=22 (CivicEngage month grid — page via grid arrows, this is the library calendar and lists one-off programs). Use /624/Storytime-Programs only to confirm recurring storytimes. Do NOT attest from a generic web search — it surfaces town-wide events, not the library's own calendar (root cause of a past miss).
37. **SRPL (San Rafael Public Library — Downtown/Northgate/Pickleweed/Al Boro)** — fetch srpubliclibrary.org/events/ (JS tag-cloud, but links the current monthly newsletter PDF — read that; it's text-readable and covers ~1 month).
38. **Sausalito Public Library** — **RESOLVED 2026-07**: same Akamai WAF block as source #8 above (whole sausalitolibrary.org domain 403s WebFetch/curl regardless of headers). Use the Chrome browser tools instead (`navigate` + `get_page_text`) — confirmed working: sausalitolibrary.org/kids/library-calendar renders the current month correctly through a real browser session. To page forward, use `find` to locate the "Next Month >" link and navigate to its href (or click it) — do this repeatedly to step through each month in the sweep window; you cannot jump directly to a future month. Capture "KIDS SUMMER READING EVENT" one-offs. Do NOT use the /kids-teens/summer-reading-2026 page (image-only) or the old /kids/children-s-programs path (stale cache) — confirmation-only, not the fetch route. Do NOT substitute a web-search-located event page as a workaround even now that the direct route works — one such page found via search was dated 2024 despite appearing in a fresh search, a stale-content trap. If the Chrome extension isn't connected in a given session, report this source as blocked via attestation rather than falling back to WebFetch (which will just 403 again).
39. **Larkspur Library** — cityoflarkspur.org bot-blocks fetches; ci.larkspur.ca.us serves a stale cache. Workaround: confirm any Larkspur special via a second current-year source (Ronnie's / Marin Mommies) before adding, cross-check the weekday actually matches the current year, else skip. Flag to Alexandra for a manual check if anything looks off.

### Learning Bus (1)

40. **MCFL Learning Bus** — fetch marinlibrary.org/learning-bus/ to check for a new month's PDF. If found, fetch the PDF with text extraction, parse every stop (date, location, address, town, time), and add each as a dated one-off event. Old months auto-expire via the daily scraper.

## After the sweep

Tell Alexandra where the review file is and wait for her to fill it in. Do not touch `events.json` until she gives you the completed file and asks for `/process-sweep`.
