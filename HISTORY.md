# Out AND About: history and incident log

Moved out of CLAUDE.md on 2026-10-10 so the rulebook stays readable. **Nothing here is a current rule**; every rule it
produced is written in CLAUDE.md, usually with a one-line reason. Read this when you need the full story behind a rule.

## Known documentation-drift items (found 2026-07, not yet acted on)

- `location_group` values have drifted from what old docs claimed (see schema table above) — always check live values, don't hardcode a list.
- `type` includes both legacy `Music` and current `Music and Movies` — new entries should use `Music and Movies`.
- Napa-area events exist with no documented sweep process (see Napa note above) — flagged to Alexandra, awaiting direction.
- **Bollywood Beats Dance Party** (Mill Valley Library, `millvalleylibrary.libcal.com/event/16544594`): WebFetch on this page reported additional dates (Jul 2/9/16/23/30) beyond the visible June 25 date, attributed to an "expandable date list." Alexandra checked the page directly and does not see those additional dates. Do not propose any Bollywood Beats date beyond the one already in the DB (id 149, June 25) unless Alexandra can independently confirm a specific new date from the source herself.
- **Two Monthly events are currently invisible for want of an ordinal phrase (found 2026-07-29, NOT yet fixed — needs Alexandra's approval).** Both violate data-quality rule 9 and therefore render nowhere:
  - **id 586 Corte Madera Town Center Summer Music Series** — `cadence: Monthly`, `day: Thursday`, notes say only "Next date: Aug 6, 2026." Aug 6 is a real future Thursday, so this is live user-facing loss. Cleanest fix is a dated One-off for Aug 6 rather than forcing an ordinal.
  - ~~**id 588 Movies on the Green — Mill Valley**~~ — **RESOLVED 2026-07-29**, see the `/outdoor-movies` entry below. (My initial guess that it carried 2023 dates was wrong; they were 2017 dates.)
  - **id 31 Belvedere-Tiburon Family Storytime** is the same failure but honestly unfixable: it is genuinely "bi-monthly on select Sundays" with no published dates. It stays invisible until the library publishes dates. Leaving it flagged `UNPREDICTABLE` is the correct state, not a bug to fix.
- **`season_start`/`season_end` month-name format is VALID — do not "fix" it.** Nine active records (ids 71–76, 508, 509, 534) store bare month names like `"May"`/`"October"` instead of `MM/DD`. `parseSeasonDate()` in `index.html` (~line 3178) explicitly handles both forms, mapping a month name to the 1st (start) or last day (end) of that month in the viewed year. These records render correctly. Prefer `MM/DD` for new entries, but a validator flagging the month-name records as malformed is producing false positives.
- **NEVER USE `ronniesawesomelist.com/outdoor-movies` — it serves 2017 content (proven 2026-07-29).** This single URL injected multiple bad records into the DB, all with confidently-worded notes claiming they had been verified:
  - **id 588** was entered as "Movies on the Green — Mill Valley", Monthly/Friday/Dusk, with notes listing "Jul 7, Aug 4, Sep 8, Oct 6" — **all four are 2017 Fridays**. The real event is the City of Mill Valley's **"Movies in the Park"**, on **2nd Tuesdays** at dusk (~7 PM), Jun 2 – Oct 13 2026. Rebuilt as per-film One-off records (588 Finding Nemo Aug 11 at the **Community Center Lawn** — the only 2026 date not at Old Mill Park — plus Monsters University Sep 8 and Pirates of the Caribbean Oct 13 at Old Mill Park).
  - **id 587** was entered as "Movies on the Green — Larkspur", Weekly/**Wednesday**/Dusk at Marin Country Mart, with a note justifying itself as "distinct from the existing Friday Movie Nights at the Mart (ID 433) — different day of week." The Wednesday was fabricated; the Mart series is Fridays 6 PM. Deleted.
  - **Where the wrong names came from**: **Novato** genuinely calls its series "Movies on the Green" (Civic Green, 901 Sherman Ave) and "Movies at the Pocket Park." The stale page applied Novato's series name to Mill Valley and Larkspur.
  - **ids 589, 590, 591 still carry this source** and are flagged in-record as unverified. They are probably real Novato events but their dates, times and names are all untrustworthy. Verify against novato.gov (novatofun@novato.org) before trusting. Not deleted, because the underlying events likely exist.
- **Stale-year re-dating defeats weekday-vs-date validation — check the source's printed year, not just internal consistency.** id 450 "Movies in the Park: Luca" was stored as `2026-08-01` / `Saturday`. marinarts.org confirms the screening was **Friday, August 1 2025**. Whoever entered it kept the month and day, bumped the year, and re-derived the weekday to match 2026 — so `day` and `event_date` agreed perfectly and no consistency check could catch it. Deleted 2026-07-29. When a source omits the year, weekday alignment proves the year (see the Slide Ranch note); when a source *states* a year, read it.
- **`marincountrymart.com/movie-night` publishes its schedule ONLY as a PNG** (`MCM_MovieNightWebSchedule_2026.png`) with no text equivalent, so WebFetch returns navigation chrome and no dates. The lineup must come from a screenshot or a secondary source. Full 2026 series read off the graphic 2026-07-29: 20 Fridays, Jun 19 – Oct 30, 6 PM under the big tent, confirming id 433's existing `06/19`–`10/30` season bounds. Correct title is **"Movie Nights at the Mart"**.
- **Movie series are stored as per-film One-off records elsewhere in the DB** (Mill Valley Summer Movie Series ids 150/154/158/161/166/170; San Rafael Movies in the Park ids 451–454; Mill Valley Movies in the Park ids 588/788/789), because families choose by film title. id 433 (Marin Country Mart) is the one exception, deliberately left as a single Weekly record with the full lineup in its description — splitting it into 14 remaining per-film records is an open option for Alexandra, not an oversight.
- **Creekside Unplugged (Tam Valley Cabin) has phantom calendar repeats.** `marinmommies.com` per-day pages render "Creekside Fridays" on Jul 31, Aug 14 and Aug 28 — these are NOT real events. The authoritative lineup is six dates only: Jun 19, Jul 10, Jul 24, Aug 7, Aug 21, Sep 4 (ids 304–309). Do not propose the phantom dates.
- **Slide Ranch and touristclubsf.org publish dates with NO year.** Always confirm the year by weekday alignment before entering (e.g. "Aug 29, Saturday" is 2026; Aug 29 2025 was a Friday). Slide Ranch became a source in sweep 5 (2026-07-29) and runs Family Farm Days roughly monthly — worth converting to a recurring series if the pattern holds.
- **Marin Mommies weekend roundup post is a REQUIRED primary source (corrected 2026-07-23).** Earlier documentation told sweeps to AVOID the "Weekend Family Fun for [dates]" blog-post URLs (over-correcting for a past stale-cache incident) and use only the per-day `/calendar/` pages. This caused real misses: the Jul 24–26 2026 roundup post listed Cricket & the Wren Circus (Sausalito), Lucky Break concert (Corte Madera), a China Camp Junior Ranger Nature Ramble, and an Inflatable Pool Obstacle Course (Novato) — none of which were on the per-day calendar pages or in the DB. The curated roundup contains editorially-selected events the raw calendar never shows. Verify the printed year on the roundup page first (the slug-cache staleness risk is real, so gate on year before trusting it). Never revert to avoiding these pages. **Scope corrected 2026-08-09** — see the two Marin Mommies entries in the sweep procedure ("Weekly sweep"): source #1 is the curated roundup for the **upcoming weekend only** (the posts publish ~2 days ahead, so asking for "every weekend in the window" guaranteed 404s), and source #2 is the per-day calendar for **all 14 days**, mandatory. The two no longer overlap. Also: **Marin Mommies' day-of-week labels are unreliable** — it labelled five Slide Ranch Family Farm Days as Thursday/Friday when all five are Saturdays. Always re-derive the weekday from the date.

---

---

## State of play — last updated 2026-08-21

Where a new session should pick up.

### What happened 2026-08-20 → 2026-08-21 (two sweeps + a public-data incident)

**Marin Weekly Sweep, window Aug 21 – Oct 4.** All 42 sources fetched. 28 verified-clean candidates added as ids 863–887 (`570b50b`), plus 8 corrections, 5 of which were live-wrong records. Review file: `daily_sweep_2026-08-20_review.xlsx`.

**That sweep initially proposed 9 duplicates** — a 24% false-new rate, which Alexandra caught in review and called unacceptable work product. The cause was structural, not carelessness: `find_event()` is a *substring* matcher and was the only candidate-stage tool, while `check_duplicates.py` only audits records already in the file. Nine real programs were re-proposed under slightly different wording (Friday **Night**/Nights on Main, Wiggles **and**/& Wonder, Corte Madera **Town Center** Farmers, Fairfax **Community** Farmers, Storytime in the Park **(with Riva)**, 2nd Saturdays **Family** Storytime, **Marin MOCA**/MarinMOCA, Bookworms **by Gordon Korman**, and "Encanto", which was one week's edition of id 46's rotating theme). Fixed by **rule 18** and `check_duplicates.py --venue`; those nine ids are now a regression suite inside `--self-test`. **Do not dedup by name.**

**Napa sweep, window Aug 22 – Oct 4.** 24 sources. 16 events added as ids 888–903 (`1d0e200`), 4 corrections, plus Salvia (id 904, `7325b1a`) and the Lincoln Ave monthly series (ids 905–907, `cfeec4c`). Review file: `napa_sweep_2026-08-21_review.xlsx`. Logged in the Weekly Sweep Log tab of `Napa_Live_Music_Tracker_v2.xlsx`.

**⚠ THE INCIDENT — internal notes were public, on 109 records.** Alexandra spotted the amber box on id 530's detail screen and asked why the public was seeing our maintenance log. `notes` renders verbatim; it always has. See **rule 19**, which is now the most important rule in this file for anyone running a sweep. `check_duplicates.py --notes-lint` was added the same day. **RESOLVED 2026-08-21 in `e451268`** — she chose the structural fix, `internal_notes` was added, and all 109 records were migrated with rendered dates provably unchanged (open items 36 and 40, both now closed). Every new record written from here must still pass the lint.

**Two source corrections found by Alexandra, not by us:**
- **Lincoln Avenue Brewery** was reported "down two sweeps." It was not. Our checklist pointed at `lincolnavebrewerycalistoga.com`, a **dead domain returning HTTP 521**; the real site is `lincolnavenuebrewery.com`. Separately id 530 had `day: "Varies"`, which matches no weekday, so the record had **never rendered since it was created**. Both fixed. **Lesson: when a venue reads as "down", verify the URL itself before recording the venue as down** — and when a record reads as present-but-invisible, check `day` is a real weekday name.
- **Farmstead / Long Meadow Ranch** had ZERO records despite being a documented venue. Alexandra supplied `https://www.longmeadowranch.com/things-to-do/seasonal-events/`, which is the authoritative calendar and is now in the Napa checklist. It resolved a Sep 18 anomaly (a Live Fire chef dinner, not Locals Night) and surfaced Sep 23 Locals Night.
- **`https://www.sthelena.com/events/` added as a Napa source** at Alexandra's request. Note the music-category URL redirects to `/events/` — link to `/events/` directly.

**Self-inflicted parser traps hit AGAIN this stretch — all three are in the rules, and I still walked into them:**
- **Rule 9a, twice.** Writing "the THIRD Saturday" inside a *prose* note on id 208 made `parseOccurrenceRule()` return `{nths:[2,3]}` and generate a phantom Sep 19 that duplicated id 870. The parser scans the **entire** notes string and does not care about grammar. `/\blast\b/` is tested **first** and short-circuits everything else.
- **`parseSkipDates` prose trap.** Writing "add skip: 2026-09-18 here" as a *reminder to myself* suppressed that date immediately — the regex matches anywhere in the string, including inside a sentence about what someone should do later.
- Both traps are the same shape as rule 19: **`notes` is not scratch space.** It is parsed by three separate mechanisms and rendered to the public. Treat every character in it as load-bearing.

**A tooling blind spot worth knowing.** The COLLISION scan compared raw time strings, so `"12:30 PM – 2:00 PM"` never matched `"12:30 PM"` and real double-bookings were invisible. Fixed with `_start_time()` normalization, which immediately surfaced two live Larkspur collisions (resolved in `bf69112`, `6c039eb`). If a scan reports clean, confirm it is capable of reporting dirty — `--self-test` is 33 checks for exactly this reason.

**Still open going into the next sweep:**
- ~~109 records with leaking notes~~ — **done 2026-08-21**, see rule 19 and `e451268`.
- **Oct 4 LMR Jazz Orchestra** at Farmstead — **declined 2026-08-21.** Not added, and not to be re-proposed; it stays on Long Meadow Ranch's page, so treat it as deliberately declined (open item 38).
- **Hydro Bar & Grill (Calistoga)** — genuinely down, HTTP 500, verified. Passed this month; retry next Napa sweep.
- Item 26 (San Anselmo Imagination Park address, 535 vs 541 conflict), item 30 (Sep 1 seasonal flip verification), item 32 (first real scraper findings notification, ~Aug 27 with the Corte Madera reopening).


**Health**: `events.json` is 305 events / max id 850, all committed and pushed. Live site is current — GitHub Pages deploys straight off `main`, so **committing `events.json` IS publishing**; there is no build step and no staging. Verify locally before pushing, not after. **One known user-facing problem**: 39 *non-library* expired one-offs are still rendering (see open item 1 below) — found during the library audit but left alone, since batch deletions need Alexandra's sign-off and they're outside that audit's scope.

**Last sweep: 2026-08-13**, window Aug 14 – Sep 30. All 25 event sources fetched; libraries (26–41) and the Learning Bus skipped at Alexandra's direction, since the 16-branch library audit had just covered them. 22 candidates proposed, 13 approved, 12 added (ids 839–850) — one approval was conditional and turned out to be a duplicate of an existing Seasonal record. Review file: `daily_sweep_2026-08-13_review.xlsx`. **Four standing scope rules came out of it and are now written into the sweep procedure ("Weekly sweep")** (venue drop-ins, Sweetwater filter, stewardship work-parties, Marin Magazine slug reuse) — those questions should not need re-asking.

**COMPLETE — open item 28, the library audit.** All 16 branches read for Aug 13 – Sep 20 across **124 library-hosted records** (not just the 94 typed `Library`), reviewed by Alexandra, and applied. Deliverable was `OAA maintence and content/library_audit_2026-08-13_review.xlsx` (four sheets, including the new **Record Fixes** type); working notes and the per-branch live inventory are in `library_audit_2026-08-12_progress.md`. "Processing an approved sweep" now knows how to read a Record Fixes sheet.

Shipped across `0870cab`, `a018e5e`, `3ee9645`: 21 expired one-offs deleted; **four duplicate pairs removed** (766/799, 767/800, 768/801, 34/627 — every one rendering the same event twice publicly, see rule 13); ids 42/43's conflicting `Reopens` dates fixed (**second occurrence of the rule 9b bug after id 8 — it recurs, check every sweep**); 2 CANCELED events deleted; 9 recurring records retired; Novato's real resume dates applied (Sep 1/Sep 2, not the Aug 19 we'd assumed); organizations normalized 28 → 17 values; 32 Spanish names written.

**A real frontend bug surfaced while verifying**: `shouldShowEvent()` had no `Inactive` branch, so retiring a record did nothing and 11 records rendered that shouldn't have — one of them Inactive since 2026-07-29. Fixed in `3ee9645`; see the `status` row in the schema table.

**Two near-misses worth remembering**, both caught by the guards rather than by reading: an approved "new" candidate (In Harmony) was already held as id 36 — missed at audit time because its `organization` is the performer and its `venue` is a park, so it sat outside a library-scoped record set. And a note written *about* id 36 contained the word "second", which `parseOccurrenceRule()` lifted out of plain prose and turned into `{nths:[2,3]}` — rule 9a, walked into while documenting rule 9a.

**The biggest single finding is methodological**: three "known-flaky" library sources were never flaky — they were being fetched the wrong way, and every past sweep using those routes was under-reporting without any attestation revealing it. All three are now fixed in the sweep procedure ("Weekly sweep") (sources 26, 37, 39, plus the MCFL block). One prescribed instruction was actively harmful and has been deleted — see the Mill Valley note in source 37.

**Closed this stretch** (open items 2, 3, 4, 6, 9, 10, 11, 13, 14, 16, 18, 25): the swim directory table redesign; the Napa music process integration + its first sweep; the expired-event purge (730 → 335 records, One-off only, recurring templates preserved); several fabricated/stale event records deleted or corrected.

**Open items still live** — full list in `OAA maintence and content/open_items.md`:
- **1** — **daily.yml scraper FIXED 2026-08-13** (`3c98d25`), after ~110 green runs that committed nothing since May 8. Proven on manual run #127: first bot commit in 98 days, 48 expired one-offs purged. A second, older bug was found and fixed the same day (`15c3418`): the seasonal flip had **never** worked for any record — see rule 16. **Still to verify:** the 6 AM *scheduled* run (the manual one skips the weekly-sweep steps, which are gated on the cron trigger), and the Sep 1 seasonal flips, which will be the first time that code path has ever run successfully. Notification design is deliberately deferred until the scheduled run shows how noisy the library hash check really is.
- **5** — verify two Bolinas + one Inverness library programs. **Sharpened 2026-08-12**: Bolinas is absent from MCFL's bibliocommons calendar system entirely, so ids 175/176 cannot be verified online at all — the phone check is the only route. Inverness shows **no** children's programming in the Aug 13 – Sep 20 window, so id 284 is likely defunct.
- **7** — **effectively answered 2026-08-12, pending write-up.** Novato has reopened and *is* running children's programming, but later than assumed: Stories & Rhyme Wiggle Time resumes **Sep 1** (not Aug 19), Música y Movimiento **Sep 2**. ids 11/12 still sit `Temp. closed` and id 486 (the temporary Pioneer Park listing) should retire. Queued in the audit workbook.
- **8** — Corte Madera reopening **Sep 3 confirmed** from the branch page 2026-08-12 ("closed July 6 through September 2. Reopening September 3, 2026"). Still re-check after that date for new fall programming. **Two specific things to do on that visit** (Alexandra's ask, 2026-08-13): (a) **id 43** ("Read to a Dog with Stinson") is `Monthly` with **no ordinal phrase**, so per rule 9 it renders nowhere — the rule was deliberately not invented, because the branch was closed and had no live instance to infer from. Once reopened it will publish real dates; capture the actual monthly rule then. (b) Confirm id 8 (Family Storytime) actually resumes — it did **not** appear on the live calendar for Sep 3–20 as of 2026-08-13.
- **12** — **on hold**: Learning Bus still running but with no firm timeline; the program told Alexandra 2026-08-12 to expect a resumption sometime in September. Nothing to do until a September PDF posts at marinlibrary.org/learning-bus/.
- **17, 19–24, 26–28** — preschool/daycare DB, Rebecca's feedback (her mobile card report is now shipped), marketing items, the San Anselmo address fix scheduled for late August, the analytics work (item 27, mostly shipped), the library audit (28), and **24 (users-table lockdown)**, which is a real security item: the site still talks to Supabase `users` with the public key, so phone numbers and hashed PINs are readable by anyone holding it. Full checklist in `table_lockdown_checklist.md`. Deferred, not started.

**Known-flaky sweep sources** (all failed or partially failed on the 2026-08-06 sweep and will likely recur):
- Mill Valley Community Center — CivicEngage grid returns nothing for the window; needs browser paging.
- Belvedere-Tiburon Library — `/events` renders only ~6 of 25 pages.
- Mill Valley Library libcal — renders empty, unresolved across several sweeps.
- SRPL monthly newsletter PDF — served corrupted/binary; the `/events/` HTML is the reliable surface instead.
- Sausalito city + library need the **Chrome browser** workaround (Akamai). This works reliably — use it, don't retry WebFetch.
- **SOLVED 2026-08-12 — the 10 MCFL branches.** They were never "flaky" so much as fetched the wrong way: the per-branch `/locations/XX/` pages only list the next few days, so any multi-week sweep window using them alone was structurally under-reporting and no attestation would reveal it. Use `marinlibrary.bibliocommons.com/v2/events?startDate=…&endDate=…` paged with `&page=N` — one surface, every branch, and the **only** place CANCELED events are marked. Written up as a shortcut block at the top of the sweep procedure ("Weekly sweep")'s Libraries section. Keep `/locations/XX/` only for a branch's own closure notice.
- **SOLVED 2026-08-13 — Belvedere-Tiburon, Mill Valley, SRPL, Sausalito.** Same story as MCFL: not flaky, just fetched wrong. Belvedere-Tiburon accepts a date range as URL params (`/events?start=&end=`), cutting 25 pages to 7 with plain WebFetch. Mill Valley's libcal renders fully in the **browser** at `…/calendar?…&t=m`. SRPL needs the month-nav URL for anything past the current month. Sausalito's month URL is directly addressable (`/-curm-M/-cury-YYYY`). All four rewritten in the sweep procedure ("Weekly sweep") sources 26, 37, 39, 40.
- **⚠ REMOVED 2026-08-13 — the Mill Valley `site:…libcal.com` search-around.** This was a *prescribed* step in the sweep procedure ("Weekly sweep") and it returned **2023-dated events mixed with current ones**. Do not reinstate it under any circumstance; it is the same stale-content failure class that produced the fabricated Novato movie records.
- **Larkspur — CORRECTED, this entry was wrong.** It said "fully UNREACHABLE" and it is not. The site **moved**: use `larkspur.ca.gov/296/Larkspur-Library` and `/718/Programs`, plus `calendar.aspx?...&CID=24` (CID 24 is the library — read it off the "Select a Calendar" list, do not guess). the sweep procedure ("Weekly sweep") source 41 has the working routes and has been right about this since 2026-08-13, while this list stayed stale — **when the two disagree, trust the sweep procedure ("Weekly sweep"), it is closer to the fetch.** The real limitation is narrower: the library posts essentially nothing to its city calendar, so its ~6 records cannot be verified against dated listings and the phone (415-927-5005) is the only route for that. Its Programs page does confirm id 15 ("Story Time takes place on Fridays at 10 AM").

**Deliberately declined, do not silently redo**: Alexandra passed on backfilling the Marin Mommies 14-day gap from the 2026-08-06 sweep (Aug 10–19 went uncovered because only 5 out-of-range days were fetched), and on re-paging Belvedere-Tiburon. Both are known and accepted, not oversights to fix unprompted.

**Declined 2026-08-28, and these three WILL come back round — do not re-propose them without asking:**
- **Sweetwater's Moonalice Sunday Matinee.** This is the one to watch, because it is a *standing monthly slot* — Nov 8 and Dec 6 are already on Sweetwater's calendar and more will follow. It passes the source #5 filter cleanly (free/matinee, All Ages, 1 pm), and id 704 holds the Sep 6 edition, so it looks approvable every single sweep. It is not. Ask before proposing another one.
- **"Movies at Marin City Library" screenings.** The Sep 17 edition (*Michael*, the Michael Jackson biopic) was declined because MCFL categorises it for **Adults**. The series itself is ongoing, so the rule to apply is: check the audience MCFL assigns each film rather than assuming a library film night is a family film night.
- **Musical Yoga with JAMaROO Kids at Larkspur Library.** Appears on Marin Mommies but on none of Larkspur's own pages, and its one listed date had already passed by the time it was reviewed. Not added, and the offer to phone the branch (415-927-5005) to find out whether it is a real series was declined too.

The shape worth noticing: all three cleared the mechanical filters and were still wrong for the site. **A candidate passing the source's own filter is not the same as belonging here**, and that judgement is hers, not the checklist's.

**Working rhythm**: she runs the sweep on command, usually Wednesday or Thursday. Ad-hoc event batches arrive between sweeps (Instagram screenshots, links, plain text) — research each, dedup, and present for review before writing. She reviews in Excel and hands it back.

---

---

## Napa: older corrections (moved 2026-10-10)

Original introduction to the Napa section (superseded: Napa now follows the shared sweep procedure):

Covers live music in **Calistoga, St. Helena, and Yountville**, surfaced on the webapp via the 🍇 Napa County toggle on the Profile screen. This is entirely separate from the Marin Weekly Sweep above — different sources, different ID range, different cadence. Source of this section: `napa_music_process.md` (Alexandra, originally dated 2026-06-27), integrated here 2026-08-05. The full source tracker lives at `OAA maintence and content/Napa_Live_Music_Tracker_v2.xlsx` (4 tabs: Napa Live Music Tracker, Venues Reference, Weekly Sweep Log, Sources) — read it before making changes, same as `events.json`.

**Process**: same shape as the Marin sweep — fetch every source, **dedupe by VENUE using `check_duplicates.py --venue "<venue>"` (rule 18), never by event name**, draft new candidates matching the schema, log the sweep in the Weekly Sweep Log tab of `Napa_Live_Music_Tracker_v2.xlsx`, and present the list to Alexandra for Approve/Skip before touching `events.json` or pushing anything live. Never delete a Napa event without her explicit approval.

> ⚠️ **Corrected 2026-08-21.** This paragraph told sweeps to dedupe on *"name + venue + date"* until that date, which is precisely the instruction that let **nine already-existing events** through as "new" on the 2026-08-20 Marin sweep. Name-based dedup is defeated by a plural, an ampersand, a parenthesis or an inserted word. **Napa is more exposed to this than Marin, not less**, because wine-country venue names share generic tokens — Ballentine, Romeo and Markham all matched Merryvale on the single word "Vineyards" until the GENERIC token set was extended. Use `--venue`, read the whole returned list, and match on **day + time + cadence**.

> ⚠️ **Also new 2026-08-21: `notes` is public (rule 19).** Napa records are as exposed as Marin ones — several currently publish sourcing commentary naming Alexandra. Run `check_duplicates.py --notes-lint --all` before committing any Napa sweep.

---

## Older "What changed" logs (moved 2026-10-10)

## What changed late 2026-10-09: the Telluride+ region went live

- **160 Telluride-region library events** (ids 1450–1609) from 8 libraries, reviewed by Alexandra in a workbook and a sandbox mockup first. See "Telluride+ region" above.
- **`index.html`:** third Region button (⛰️ Telluride); `regionOf()` drives the feed, Location menu, Featured carousel, search and Coming Up; ads are Marin-only; "· MT" in the Telluride week bar; the Sep 1 Napa-music carousel rule is retired.
- `check_duplicates.py` shows 5 COLLISION findings at Wilkinson and Montrose that are different programs in different rooms; each carries a dated CHECKED note in `internal_notes`.

## What changed 2026-10-06 to 2026-10-09, in one pass

- **Weekly sweep (Oct 9 to Nov 30) applied:** 44 events added (ids 1384–1427) plus record fixes; holidays rely on the
  app's holiday banner (no skips); confirmed closures get a dated `ALERT[YYYY-MM-DD]:`, and one record can now carry
  several dated ALERTs (rule 17).
- **Many events added from screenshots and links**, with duplicates retired (Makers Market 1217 → kept 470; the weekly
  Cinelounge movie 736 retired). MVFF family screenings added.
- **FIT4MOM Marin went live:** Featured ad `fit4mom-marin` in `ads.json` and Stroller Strides partner events
  1445–1449 (ages "Prenatal & postpartum moms; 0-5 yrs"). The ad renderer gained optional fields (tile_icon, logo_wide,
  hours_label, blank address, contact, code-less offers, cta, facebook) and partner events can carry a `logo`.
- **Tides shown +1.07 ft** (`TIDE_ADJUST_FT`) with a bilingual note under the table.
- **Kid-Friendly Dining table:** 4 restaurants added (see the Resources section above).
- **Instagram moved to Metricool** (brand 7335950). Approved PNGs are staged in this repo under `ig/` so Metricool can
  fetch them by URL. Three series are scheduled: weekly event posts, "Weekly Wednesday Hot Tip!" (item 61, to Dec 2)
  and "Tag Out and About" Tuesdays 2nd/4th (item 62, to Dec 8).
- **Partner ad mockups** in `templates/` (Social Klub, FIT4MOM, GG Mahjong, plus `templates/assets/` logos) are now
  committed.

## What changed 2026-09-10, in one pass

- **Weekly sweep run, applied and pushed — all 44 sources checked**, which took two sessions: the
  first covered 21 and honestly attested the other 18 as not reached rather than presenting a
  partial sweep as complete. **41 events added**, plus 3 from Instagram flyers and 3 existing
  records enriched from organisers' own flyers instead of being duplicated.
- **The sweep's biggest finding was a hole in the checklist, not in the data.** the sweep procedure ("Weekly sweep") source
  41 said Larkspur Library "posts essentially NOTHING", verified three ways in August. True of its
  **city** calendar; false of the venue — the library runs a **LibCal on a different host** that no
  sweep had ever fetched, found only because Marin Mommies linked one of its event pages. One pass
  produced four candidates, a cancelled storytime and the id 15 defect behind new rule 24. The
  route is now in `sources/marin.md` source 41, and the general rule — **"this venue publishes nothing"
  is a claim about a ROUTE, not about a venue** — is in the Weekly Sweep section above.
- **`check_duplicates.py` caught a collision introduced in the same batch that created it** (ids
  1108/1111, Inverness). Worth noting because three of this project's four historic duplicate pairs
  were introduced by exactly this step — adding a dated one-off on top of a recurring record. Run
  it after every batch write, not just before a commit.
- **Rules 24 and 25 added.** 24: one slot shared by two named programmes, where a `Weekly` record
  over-advertises and **no scan fires unless the other programme is also a record**. 25: what to do
  when an organisation's own two channels contradict each other, which is not the same problem as
  an unreliable third party.
- **Two documentation corrections, and they were the same error in two places.** `CLAUDE.md` and
  `open_items.md` both described `build_dashboard.py`'s old curated-`ITEMS` design and a `--check`
  guard that no longer exists — the script now parses `open_items.md` directly and takes no
  arguments, so a command line carrying `--check` looks like it verified something and did not.
  CLAUDE.md was fixed first and `open_items.md` was missed, then caught the same day. **One fact
  written down twice will be corrected once.**
- **The dashboard's own header was stale all day**, reading 2026-09-09 while the file was edited
  four times. Nothing computes that date; it is prose in `open_items.md` and the page prints it
  verbatim. Alexandra caught it on the published page. That file now carries an explicit
  update-it-in-the-same-edit warning.

## What changed 2026-09-07 to 2026-09-09, in one pass

- **Instagram went from designed to running.** Both Business Suite composers — feed carousel and
  Story — were driven end to end for real, and five of the six assets for the week of Sep 11 are
  scheduled. `render_slides.py` renders any size, so the square carousel slides and the 9:16 Story
  frames come from the same approved HTML.
  ⚠ **Moved 2026-10-03:** the Instagram mockups and rendered PNGs no longer live in this repo's
  `templates/` and `slides/`. They are in the Dropbox project folder, `OAA marketing\Instagram templates\`
  and `OAA marketing\Instagram slides\` (Alexandra's request). Run `render_slides.py` from here with full paths.
  Partner ad mockups stay in `templates/`. Path map: `social_media_and_marketing.md`, "Where the Instagram files live".
  ⚠ **Changed 2026-10-09: Instagram posts are scheduled through Metricool, not Business Suite** (procedure in
  `social_media_and_marketing.md` section 3e). Metricool fetches images by public URL, so approved PNGs are staged in this
  repo under `ig/<folder>/` and served from outandaboutmarin.com/ig/; `ig/README.md` lists each folder and when to delete it.
- **⚠ "We're having trouble completing your request" CAN MEAN IT WORKED.** Two of the three
  carousels showed that error on a hung spinner and **both had scheduled successfully**. Retrying
  would have double-posted. **On any error or hang from a Business Suite composer, check the
  Planner before touching anything.**
- **A stale event was published for a day.** Id 788, a Mill Valley movie night, was live and
  cancelled; it now carries an `ALERT[2026-09-08]:` banner. Auditing its source found a **2017
  article still being scraped as current** — `/outdoor-movies` on Ronnie's Awesome List, now
  flagged in `sources/marin.md` source 11. Id 789 was retired in the same pass.
- **Rules 21, 22 and 23 added.** 21: correcting `time` is not the whole job, because `description`
  repeats the hours and nothing checks they agree. 22: `cost: "Free"` must mean free to a family
  who walks up. 23: **never write a file in place** — temp file, verify the round-trip, back up,
  then `os.replace`. Rule 23 exists because `open_items.md` was truncated to zero bytes on
  2026-09-07 and only recovered from another session's transcript log.
- **The duplicate scans now skip retired one-offs** (item 45), which they never had, though they
  had always skipped retired *recurring* records. 87 → 92 self-tests.
- **`build_dashboard.py` is a real file in the repo.** It had been described in CLAUDE.md as a
  scratchpad script for weeks; when it was finally looked for it **did not exist**, and every
  "show me the dashboard" had been a hand-rebuild. It had a `--check` guard, tested in both drift
  directions before being trusted. **That guard is gone as of 2026-09-10** — the script now parses
  `open_items.md` directly, so there are no longer two copies for it to compare.

## What changed since 2026-08-21, in one pass

- **The `notes` leak is fixed properly.** `internal_notes` exists, is never rendered and never parsed, and all 158 leaking records across two waves were migrated with rendered dates provably unchanged. See rule 19 — including **wave 2**, which existed because the first lint tested `_KEEP` before `_INTERNAL` and so could not see a leak fused to a control pattern.
- **The 2026-08-27 sweep is applied**: 32 events added, 6 record fixes, and a live duplicate (ids 310/854, Concerts in the Plaza) removed.
- **`Fitness` is in use.** It had been fully wired in `index.html` with zero records for months. The hikes now carry it, and it was added to `elig()` AND `score()` — see the type row in the schema table for why both were needed.
- **Napa music is out of the Featured carousel**, and the carousel deliberately ignores the county toggle — see the Featured strip section, that is a recorded decision, not a bug.
- **A type-vocabulary check now runs with every `check_duplicates.py`**, after id 493 sat live with `type: "Music"` — unfilterable, unstyled, and ineligible for the strip, raising nothing anywhere.

---

## Marin source-count history (moved 2026-10-10)

**Scope**: 31 distinct event sources + 16 libraries + the Learning Bus PDF = **48 total** (47 until the Town of Fairfax baby/toddler/preschool programs page was added as source #48 on 2026-10-05; 46 until the Barnes & Noble Corte Madera store calendar was added as source #47 on 2026-10-02 — it 403s headless, browser only; 45 until The Social Klub, a paying sponsor, was added as source #46 on 2026-10-01 — its events always go in as PARTNER records; 44 until the Mill Valley Briefing was added as source #45 on 2026-09-28; was 42; **this line went stale — it still said 42 after source 43 was added on 2026-09-01, and was corrected on 2026-09-02 when 44 was added**). (Numbering in the sweep procedure ("Weekly sweep") is contiguous 1–45 — it previously restarted at 24 for the libraries, so "#24" named two different sources; fixed 2026-08-09. **Sources 43 and 44 are event sources but sit at the END of the list on purpose**: inserting them in sequence would renumber all sixteen libraries and the Learning Bus, and every past sweep's Attestation Log keys its rows off these numbers. The number is a stable identifier, not a running order.) Full list with fetch method lives in the commands themselves (kept there so the checklist and the fetch logic don't drift apart) — this doc just states the ground rules:

Attestation-sheet wording before 2026-10-10: one row per source (**all 48** — the two halves of this sentence used to disagree, reading "all 43" and "the checklist is 42 items"; both are now 48 (47 until the Fairfax programs page was added 2026-10-05, 46 until Barnes & Noble Corte Madera was added 2026-10-02, 45 until The Social Klub was added 2026-10-01, 44 until the Mill Valley Briefing was added 2026-09-28); this line said 38 until 2026-08-27 and a stale count here invites an under-attested sweep)

---

## 2026-10-10: docs restructured into one rulebook

Alexandra wanted the Telluride sweep run by a partner, and asked for **one set of rules for every region**: "I want the
settings to stay consistent between all the apps... how the age categories work, how we treat holidays... No deviating."
A separate Telluride MD file was rejected for that reason; separate *source* lists were acceptable if their structure is
identical. She then asked why CLAUDE.md, run-sweep.md and process-sweep.md could not be one file. The split was only
historical (they began as slash commands, which never registered because sessions do not start in the repo), so they
were merged, with the dated narrative moved here to keep the rulebook readable.

**What was done (commit `f310731`):** sections moved verbatim by script, not retyped; new text only for the Regions
table, the region-neutral procedure wording ("the reviewer", `<repo>` paths) and the source-file headers. Napa's source
paragraph was rewritten as 30 numbered entries. A line-by-line audit of all 1,477 old lines found two real drops, both
restored ("then stop; do not touch `events.json` until approval" and the original Napa intro, now here). `check_docs.py`
added with a self-test. Partner path: Claude Chat online was considered first, then Claude Code on the web; both were
set aside because neither can see Dropbox, in favour of the partner running her own desktop Claude Code on the shared
Dropbox folder.

**Same night, later: Git dropped from the partner setup.** Alexandra asked why the partner needed Git and Python just to
run a sweep. Git was only there to copy and refresh the rulebook and tools, and the repo is public, so her Claude now
downloads 8 files with `curl` at the start of every sweep (`CLAUDE.md`, `check_duplicates.py`, `check_docs.py`,
`events_io.py`, `events.json`, `sources/marin.md`, `napa.md`, `telluride.md`) into `C:\Users\<her user>\OAA-rules`, outside
Dropbox. Python stays: the duplicate checker, the lints, the iCal/API sources and the `.xlsx` workbook all need it (plus
`openpyxl`). Tested on Alexandra's machine the same night: all 8 downloads arrived, `check_docs.py` passed and
`check_duplicates.py --venue` ran from the plain folder. Caveat kept on the setup page: if her Claude Code needs Git for
its own command line on Windows, it is a one-time install and nothing else changes. Commit `f3abd07`.

**Later still: a shorter partner prompt and a completion check.** Alexandra pointed out that her own prompts are five or
six sentences and asked why the partner's was so long. It repeated half of CLAUDE.md. The partner-specific steps moved
into a CLAUDE.md subsection ("Telluride partner sweep") and the prompt shrank to five sentences that download CLAUDE.md
and point there. Asked whether duplicates, Chrome escalation, full-page reading and the per-source completion record
were all covered, the check found them all in the shared procedure, plus two gaps, both fixed: tier 3 needs the Claude in
Chrome extension on the partner's machine (now on her setup page), and **nothing verified the Attestation Log at
processing time** (the processing notes literally said it needed no action), so a sweep that skipped sources would have
passed straight through. `check_docs.py --attestation` now checks it at both ends. Its first run flagged "Every Marin
item already in DB" as banned; the banned phrase was narrowed to the rule's actual wording, "recurring already in DB".
Also caught before shipping: the first-run download needed `curl --create-dirs`, since `OAA-rules` does not exist yet.

**Last change of the night: dates in the partner prompt.** Alexandra asked for a sentence where the partner writes today's
date and the period the sweep should cover (xx/xx/xxxx - xx/xx/xxxx). Added as the prompt's first sentence; the setup page
tells her to fill both in (usually today through about 7 weeks ahead) and CLAUDE.md "Telluride partner sweep" step 2 now
takes the window from them instead of a fixed "today + 7 weeks". Commit `9701bb0`.

## 2026-10-11: partner sweep test run (in Claude Chat, by mistake)

Alexandra dry-ran the partner prompt in a Claude Chat project instead of Claude Code. Chat reported five issues. Its
cloud workspace downloaded the rulebook fine (one HTTP 429 from GitHub, fixed by a retry) but could not reach the
library feeds (network allowlist) or her Dropbox, and its only fetch for those feeds summarizes, which can silently
drop events. She confirmed the partner will use her own Claude Code desktop, where none of that applies (this machine
read every feed directly on 2026-10-09). Fixes kept for Claude Code: download retries, a clearer `check_docs.py`
message, neutral command wording, a "use the prompt as written, in Claude Code" note on the setup page, and a new
every-region rule that feeds must be read raw and in full, with unreadable ones attested INCOMPLETE rather than
skipped or passed off as checked. The test was still worth it: the raw-feed rule closes a gap that applied to Marin too.

## 2026-10-14: Marin weekly sweep (Oct 14 - Dec 1)

Alexandra asked for the sweep as "Thursday 8/27"; the system date was Wednesday Oct 14, and the Marin Mommies roundup
(posted Oct 14 for Oct 16-18) confirmed it, so the window was today plus seven weeks and the date went to the top of the
Questions tab. She confirmed it. All 48 sources were read in full; the attestation check passed 48/48.

**What the sweep found:** 29 candidates and 15 questions. She approved 26 rows (27 records once dated series were split),
skipped six, and answered every question "follow your recommendation" except three: the Nicasio movie night and the Elf
Hunt went to the open items list to watch, and the Social Klub free play sponsored by the Yes on Measure X campaign was
kept, to be highlighted on Instagram. Committed as `8f4ba49`.

**Lessons, each now in `sources/marin.md`:**
- **A month grid can be incomplete without being blocked.** Sausalito's revize calendar showed "+2 more" on busy days,
  so its page text silently dropped events; the list view (`view=list`) prints them all. Same failure class as the
  stripped Akamai page, with a different cause.
- **Raw feeds exist for two more sources:** Marin Humane's WordPress events API, and MCFL's `gateway.bibliocommons.com`
  JSON (594 events in six pages, with cancellations and audiences as fields). Both make the raw-feed rule easy to meet.
- **The in-app browser was refused on Barnes & Noble**; real Chrome read it. The store calendar no longer shows per-day
  counts, so each day was opened in turn. It also found the LEGO build's real time (5 PM, not 7 PM).
- **Third-party listings were wrong twice in one sweep:** Marin Mommies listed a Monday Graveyard Stroll (the Parks
  page shows only Sunday, now wait-listed) and put the Hauke pop-up storytime on Thursdays. Checking the organiser
  caught both, which is the rule working.
- **Venues stop programmes without saying so:** the Village's Acoustic Weekends, Larkspur's Games morning, Mahjong at
  the Mart and one Slide Ranch farm day had simply vanished from their own pages, and were retired on that basis.

## 2026-10-16/17: phone sessions, search order, and one review template for every region

**Phone (cloud) sessions.** Alexandra started working from her phone in Claude Code on the web. Reading the repo worked
but every push failed (403) until the **Claude GitHub App was installed on the repo**; reconnecting GitHub in claude.ai
settings alone did not fix it. Phone sessions also need the "OAA - Full" environment for website access. The rules are in
CLAUDE.md, "Phone / cloud sessions". Because the phone and the nightly bot push to `main`, desktop sessions now **pull at
start** through a SessionStart hook (20-second limit, `--ff-only`, so it never merges or overwrites). The leftover
phone-session branch was deleted once everything on it was in `main`.

**Search order.** Results came back in database order, so the newest event sat at the bottom. They now sort by the next
date, soonest first, then start time; events with no upcoming date go last; "and", "&" and "+" match each other. Testing it
turned up a second bug, fixed in the same change: **search was showing retired records**, the same gap the Featured strip
had until Oct 13. Lesson for local testing: the `oaa-local` preview stops at the sign-up screen unless a profile is saved
in that localhost tab, which is why Alexandra first could not try it.

**Village records.** Asked to end-date the Village's weekly mahjong and storytime, the database turned out to have no
mahjong record at all, and the storytime was a Seasonal record (Jul 31 - Sep 25) that would have come back every summer.
Both became dated one-offs. A Seasonal record is the wrong shape for a series that will not recur next year.

**Telluride source #10.** The Visit Telluride calendar was the first new Telluride event source. Its list is built by
script, so a plain fetch shows "Showing 0 of 0"; the events were read from the page's own data in a browser. Alexandra
asked for a review workbook before anything was added (rather than adding straight from a chat list), approved all 16
events, and noted that Telluride content will skew more adult.

**One review template.** She asked for a tab listing the sources the content came from, as part of the template for
every region. The old procedure and the format section described two different column sets; there is now one
definition (four sheets: Weekly Sweep with a Source # column, Questions, Sources Used, Attestation Log), and
`check_docs.py --attestation` enforces the Sources Used sheet (`--partial` for a one-source review). Napa keeps its extra
line in the live-music tracker on purpose.

## 2026-10-21: three sponsor prospects in one evening (JCC, Kitsch + Sync, The Cave)

Alexandra spent the evening on sponsorship: the Osher Marin JCC, Kitsch + Sync in Novato and The Cave in Corte Madera,
each with listing mockups and, for Kitsch + Sync, a Featured carousel ad. Three things worth keeping:

- **Build from what is already live.** For the JCC, a logo download was stopped and the answer was "there are already
  live JCC events in the app": the JymBabies mockup was drawn from the live record, which also exposed two errors in
  it (wrong end time, wrong price on the San Rafael card).
- **Two versions of every mockup.** One with notes for her review, one clean to send to the vendor. Asked what the
  difference was, so the file names now say it: `mockup` vs `(for <vendor>)`.
- **Logos go into the shared assets folder only when she asks.** Mockups first load the logo from the vendor's site;
  she then asked to save each one, so both Kitsch + Sync logos and The Cave's are now in `assets/`.

## 2026-10-22: Marin sweep, and one listing for irregular dates

The Oct 22 sweep (all 49 sources, Oct 22 - Dec 3) produced 41 new records. Two things worth keeping. First, a duplicate
almost went out: San Rafael's Day of the Dead was already in the database as "San Rafael Day of the Dead Celebration"
(1642), and name searches for "muertos" missed it; the venue check (rule 18) caught it before the workbook was sent. The
venue check is the one that matters. Second, Alexandra asked for the Mill Valley ShaBabies to be one recurring listing
rather than seven one-offs, although its dates follow no ordinal. The app has no "list of dates" field, so it became a
Weekly record with seasons split at New Year and the other Fridays skipped, with `expires` so it does not return next
year: the Pavilion Playgroup shape, now written down as the pattern.

## 2026-10-22 (evening): Kitsch + Sync goes live, and a sponsor cap nobody knew about

Kitsch + Sync signed a 3-month Featured sponsorship. The same evening their flyers became 8 partner events (after four
rounds of mockup edits: titles, "Food/PlayZone passes for sale", Families, Community Event) and their Featured ad went
live. Three things worth keeping:

- **The strip could only ever show two sponsors.** `withAds()` sliced `activeAds` to 2, a limit written when there was
  one sponsor. The third ad loaded without error and simply never appeared; it was caught only because the ad was
  previewed locally before pushing. Now `MAX_FEAT_ADS = 9` (Alexandra). Lesson: preview a new sponsor on the real page,
  not just the mockup, because a silent cap looks exactly like "nothing to show".
- **`socials.facebook` needs a page slug.** Their Facebook page is a `/people/<name>/<number>/` URL, and the Follow
  button took the first path segment, so 8 live listings showed a button reading "people" until it was removed.
- **A hand-typed "Coming up" list on an ad page goes stale.** It was built from code-less offers, then removed at
  Alexandra's request; an automatic version (reading the sponsor's partner events) was offered and not taken.

The same day, a backspace byte landed in a CLAUDE.md path again (a `\b` inside a Python string written through a shell
heredoc), the trap the rulebook already describes. Caught by `cat -A` and fixed in `97314e7`. Write doc edits from a
script file, or check for control bytes before committing.

## 2026-10-24: a cloud-drafted post meets a changed offset

The king tide post was drafted on the phone on Oct 23/24 with the tide table's +1.07 ft adjustment. The same day another
phone session raised the adjustment to +1.25 ft, so by the time the post reached the desktop its closure windows were
15-35 minutes short of what the web app's own table implied. Caught only because the windows were recomputed from
`tides.json` before scheduling rather than taken from the handoff. Recomputing also exposed a rounding mismatch: the
app's `toFixed(1)` shows 7.25 as 7.3, Python's `round()` gave 7.2. **A handoff's numbers are a snapshot; re-derive them
from the current data before publishing.**

The phone inbox worked as designed for its first real batch, with one snag: it proposed item 74 for Golden Gate
Gymnastics after another session had already taken 74. Item numbers are not reserved across sessions.

Also: Alexandra asked that public copy never say "every family event", because the web app leaves out many paid events.

## 2026-10-29: the Marin sweep read twice, and a Pittsburgh brewery in the Napa list

Alexandra asked for the weekly sweep (Oct 29 - Dec 15), stepped away, and on her return asked one question before
reviewing: had every MD file been read, and the process followed exactly? The honest answer was no. The MD files had
been skimmed, several pages keyword-searched rather than read, the ten MCFL branch pages skipped, and the `--venue`
lists filtered instead of read whole. She said to read everything in full and update the workbook. The second pass
changed the result in four ways: two "new" candidates were already records (South Novato Ingrid Dec 23/30, 1627/1628),
a real event had been missed (Novato's Skeleton Scavenger Hunt, filtered out because it started before the window), a
"new" San Anselmo Crafternoon was its own record's themed edition (rule 27) and exposed 45's wrong rule, and 626 turned
out to duplicate 1157. **The shortcuts were exactly where the errors were.** The sweep was processed the same day
(34 records, 25 fixes, `14dc088`), after the Record Fixes column came back blank twice: the saved file did not yet hold
her answers.

The Napa sweep the same evening read all 30 sources in full and turned up the bigger problem: the Lincoln Avenue
Brewery URL that the 2026-08-21 sweep had "corrected" to `lincolnavenuebrewery.com` belongs to a brewery in Bellevue,
Pennsylvania. Three Monthly records (905-907) and the Saturday time on 530 had come from it, and had sat live for two
months. Nothing checks that a venue's website is in the venue's town; reading the footer would have. Calistoga's LAB
runs a GoDaddy site under its BBQ business (LocalQ 707). Alexandra also asked why Napa took so much longer than Marin:
Marin's biggest sources are raw feeds, while Napa's are script-built lists behind "Load more" buttons, each event on
its own page.

## 2026-10-29 (evening): a hashtag rule read two ways, and files nobody meant to move

Alexandra asked that every Instagram post carry "only 3 hashtags in the comments". That was read as the first comment:
templates, docs and memory were changed, and the Halloween post was edited minutes before it published to put its tags in
the first comment. An hour later, looking at a mockup, she asked for the hashtags "back within the slide", meaning the
caption. The second change was asked about first (caption, on the image, or both), which settled it in one exchange. **An
instruction about where something goes, given in a word or two, is worth one question before it is applied everywhere.**

While looking at the SMMC folder she found a `Downloads` folder of tax returns and lab results inside `OAA marketing\SMMC
Add`. The file times told the story: the review packet was moved into a new folder at 3:00:25 PM on Oct 25, and 21 seconds
later the first 57 files of her Downloads folder, in alphabetical order, landed beside it within two seconds, the signature
of a drag that was cancelled partway. The session logs showed no Claude command touching that folder. Windows records only
the account as owner, and Claude runs under the same account, so **the logs, not the file owner, are what clear or implicate
a session.** It also produced a filing rule: Sponsorship is money in (advertisers), marketing is money out (SMMC).

Two build traps from the same evening are in `social_media_and_marketing.md`: padding on a `.slide` shrinks every `cqw`
unit inside it, and `render_slides.py` names files from card labels, so a relabelled card leaves its old PNG behind.
