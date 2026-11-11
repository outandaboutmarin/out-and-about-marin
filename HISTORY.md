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

## 2026-11-02: a tide table that was right in one column and wrong in the other

Alexandra said the Resources tide table didn't look right and asked for proof. NOAA's predictions were downloaded again
and laid beside `tides.json` and the live page. Every time and every high/low matched, but the heights didn't: the
generator had rounded NOAA's three decimals to one before saving, and the page then added the adjustment and rounded
again. With +1.50 ft the double rounding was harmless; with Lucky Drive's new +1.65 ft it moved 19 of 38 cells by
0.1 ft, and one 7.0 ft flood high showed as an unshaded 6.9. **Store the source's full precision and round once, at
display.** The proof she asked for was a plain table (NOAA value, plus the adjustment, the shown value) for two weeks,
which made the fix easy to trust.

## "What changed" logs and health snapshots, 2026-10-10 to 2026-11-07 (moved 2026-11-11)

Moved word for word from CLAUDE.md on 2026-11-11 to shorten the rulebook. Newest first, as they stood there.

### Health snapshots (START HERE, as of 2026-11-11)

**Health 2026-10-29 (end of day, after the Napa sweep)**: `events.json` is **644 events, max id 1853**; notes-lint and bilingual-lint clean; self-test 92/92; `check_docs.py` clean; duplicate scan 6 findings, all known (1643/1710/1778/1818 four Día de los Muertos in four towns, 1716/1717, 1156/1158, 1770/1771, 1723/1724, 1729 vs 286). **Health 2026-10-29 (after the Marin sweep)**: `events.json` is **601 events, max id 1810**; notes-lint and bilingual-lint clean; self-test 92/92 (the id 45 fixture now expects 3rd Wednesday; 1368 carries the last-weekday case); duplicate scan 6 findings, all known (1643/1710/1778 three Día de los Muertos in three towns, 1716/1717, 1156/1158, 1770/1771, 1723/1724, 1729 vs 286). **Health 2026-10-24**: `events.json` is **642 events, max id 1772**; notes-lint and bilingual-lint clean; duplicate scan 7 findings, all known (1770/1771 Sunday Football is a New-Year split pair like 1716/1717 and 1723/1724). **Health 2026-10-22 (end of day)**: `events.json` is **666 events, max id 1764**; notes-lint and bilingual-lint clean; duplicate scan 6 findings (the same ones reviewed after the sweep); self-test 91/91; `check_docs.py` clean. **Health 2026-10-22 (after the sweep)**: `events.json` is **658 events, max id 1756**; notes-lint and bilingual-lint clean; duplicate scan 6 findings, all reviewed (two genuinely separate same-afternoon library programs, three New-Year split pairs, 1643/1710). **Health 2026-10-21**: `events.json` is **628 events, max id 1711**; notes-lint and bilingual-lint clean; duplicate scan 3 findings; `check_docs.py` clean. **Health 2026-10-17 (end of day)**: `events.json` is **659 events, max id 1694**; notes-lint and bilingual-lint clean; duplicate scan 3 known findings. **Health 2026-10-16**: `events.json` is **640 events, max id 1666**; notes-lint and bilingual-lint clean; duplicate scan 3 known findings (1156/1158 and two Telluride room collisions); `check_docs.py` clean with **Marin at 49 sources**. **Health 2026-10-15**: `events.json` is **645 events, max id 1661**; notes-lint and bilingual-lint clean; duplicate scan 3 findings, all known (1156/1158 and two Telluride room collisions; the others dropped off as their dates passed). **Health 2026-10-14** (after the Oct 14 sweep): `events.json` is **664 events, max id 1650**; notes-lint and bilingual-lint clean; duplicate scan 6 findings, all known (1156/1158 and the 5 Telluride room collisions). **Health** (re-run and verified late 2026-10-10 from the NEW repo path `C:\Users\AWalter\Code\out-and-about-marin`): `events.json` is **665 events, max id 1614** (Marin 462, Telluride+ 160, Napa 43); self-test 91/91, notes-lint and bilingual-lint clean; duplicate scan 7 findings, all documented (1156/1158, the 5 Telluride room collisions, and 1612 vs 56, the deliberate Megan listing). Late 2026-10-09: **670 events, max id 1609**; self-test 91/91, notes-lint and bilingual-lint clean; duplicate scan shows 1156/1158 plus the 5 documented Telluride room collisions. (Earlier the same day: **510 events,
max id 1449**, all committed and pushed, level with `origin/main`.
`check_duplicates.py --self-test` is **91/91**; `--notes-lint --all` and `--bilingual-lint` are
clean; the duplicate scans show only the known, legitimate finding: the Pavilion Play Group's two
season halves 1156/1158 (the Southern Marin open houses 1153–1155 dropped off after their Oct 4 date). (464 events / max 1383 on 2026-10-06; 466 events / max 1350 on 2026-10-02 — the drop is the daily purge of past one-offs; 440 events /
max 1145 on 2026-09-10; 406 events / max 1097 on 2026-09-09. The count moves both
ways — the daily job purges expired one-offs, so a fall is the system working. **Re-run the scans
rather than trusting this sentence**; a hard-coded count in prose goes stale silently, and this
line has been wrong before.) GitHub Pages deploys off `main`, so **committing `events.json` IS
publishing** — there is no staging.

## What changed 2026-11-06/07, in one pass

- **Instagram rule (open item 15, Alexandra 2026-11-06):** every post now goes to her as slides + caption + **a funny, witty first
  comment ending in a brief question**, all approved together; the comment goes in Metricool `firstCommentText` and posts
  automatically. Hashtags stay as the caption's last line. First used on the Sat Nov 7 / Sun Nov 8 posts (new Metricool ids
  419514903 / 419515063). Spec in `social_media_and_marketing.md` (rule 12, Template A standard, section 3e).
- **Events added:** Craft Time with Tia at the Cabin, Tam Valley (1955 Nov 18, $15; 1956 Dec 16 save-the-date); TCSD Speaker
  Series on groundwater and sea-level rise (1957, Nov 17) and Breakfast with Santa (1958, Dec 12, times assumed from 2025);
  the six 2027 Marin repair fairs (1959-1964, Reuse Alliance). **Venue note:** the Cabin is 60 Tennessee Valley Rd; the Tam
  Valley Community Center is 203 Marin Ave. TCSD Game Night (Nov 24) and Mahj, Mingle & Jingle (Dec 2) wait for details
  (open item 58 zzd; Alexandra: wait for TCSD).
- **Sweep sources:** #20 The Phoenix now reads its non-profit book sale page too (sales = Community Events, held while "Date
  TBD"); **#51 Reuse Alliance** added (Marin repair fairs via `/events?format=json`). Source count 51.
- **Phone inbox applied twice** (item 58 zzc to-confirms; Kitsch + Sync hours in the Resources spreadsheet) and emptied.

## What changed 2026-11-04 (evening), in one pass

- **Instagram week of Nov 5 scheduled in Metricool** (Template A, `build_week_of_nov5.py`): Thu Nov 5 5 PM (417346028), Sat Nov 7
  7 AM (417346062), Sun Nov 8 5 PM (417346082); images staged at `ig/week_of_nov5/` (commit 0eee3b8), delete after Nov 8. Details in
  `social_media_and_marketing.md`, "The week of Nov 5".
- **New sponsor: Metta Mama Yoga Studio**, 3-month Featured + 8 weekly partner classes. Mockups approved and with Metta; nothing in
  `ads.json` or `events.json` yet. Waiting on Metta's feedback and start date (open item 21 has the full spec: times, $35/class,
  code `kidsyoga50`, @mettamamamarin, links to mettayogastudio.com/mama).
- **Open items:** 78 is now the flood Instagram template (sources copied to `OAA marketing\Instagram templates\Tide flooding	emplates\`);
  79 SMMC paid and submitted, posts run Dec 3; 59 gained to do 3, a Monday GA4 email (81 merged in).

## What changed 2026-11-04 (Marin sweep), in one pass

- **Sweep Nov 5 to Jan 10** (`daily_sweep_2026-11-04_review.xlsx`): 48 of 50 sources read; #9 Enjoy Mill Valley (Cloudflare check)
  and #47 Barnes & Noble (page renders only its shell) could not be read: open item 83 has alternatives. 83 candidate rows, 67
  approved; **70 events added, ids 1873-1942** (incl. the November Learning Bus, Holiday Light Spectacular film nights, Friends of
  China Camp walks, Marin Humane adoption Saturdays) and **18 record fixes** (ALERTs, skips, 985 to 3rd Friday, 1410 Puzzle Swap to
  Monthly, Carol-oke and French Market times). Commit 37f27e6.
- **New raw routes** written into `sources/marin.md`: LibCal JSON per day (#37, #41), tribe/events feeds (#4 Strawberry, #6 JCC),
  Ronnie's Awesome List JSON (#11), OneTam paged to the end (#13).
- **Rule 9a bit again:** "For 3rd to 5th graders" in a Monthly note made the parser read 2nd/3rd/5th Fridays (id 1892); caught by
  checking the parsed rule before committing. Keep ordinal-looking words out of Monthly notes.
- Health 2026-11-04: **634 events, max id 1942**; notes-lint and bilingual-lint clean; self-test 92/92; duplicate scan 8 findings,
  all explained (the 5 known, 1416/1941 and 1417/1942 New-Year split pairs, 1932 vs 3 two programmes in one BelTib slot).

## What changed 2026-11-02 to 11-04, in one pass

- **Tide table audit (Resources).** NOAA's predictions were re-downloaded and compared cell by cell: times and order
  matched, but `tides.json` stored heights pre-rounded to 0.1 ft, so adding +1.65 ft put 19 of 38 Lucky Drive cells
  0.1 ft off. Fixed: `generate_tides.py` keeps NOAA's 3 decimals (tides.json regenerated) and the page rounds with
  `_tideShown()` in whole thousandths, half up. Checked against exact arithmetic on all 11,284 tides for 2026-27.
- **Adjustments now per station** (`TIDE_ADJUST_BY_STATION`): Tam Junction +1.80 ft, Corte Madera / Lucky Drive +2.20 ft,
  Hwy 37 and Bolinas +1.50 (`TIDE_ADJUST_FT`). Footnote under the table says so in both languages. Red shading still
  starts at 7.0 ft shown. Commits 0e2548e, d243499, abba742.
- **Tide flooding Instagram post** "The tides are back!" (Wed Nov 4 to 11, six slides) scheduled Tue Nov 3, 5 PM
  (415760200); details and the slide method (cutoffs 7.0 / 7.3 ft, closures +90 min at the end, footnote) are in
  `social_media_and_marketing.md`, "Tide flooding post, Nov 3 2026". Flood Watch on Resources reuses four of the slides
  through Nov 11 (ebe3b64).
- **SMMC (item 79):** short link `smmc/index.html` committed and live (7614402); Dec 3, 5 PM confirmed with the collaborator
  tag and a Story link sticker; final files (graphic, caption, email, `post_mockup_dec3.png`) in `final_for_smmc_dec3\`.
- **Resources tab:** Flood Watch has arrow buttons and clickable dots on computers, hidden on touch screens (f392261); the
  Choose your own adventure card title is now "Too wet for the park? Too wild for the living room? Choose your own
  adventure...before your kiddo chooses one for you :-/" with a Spanish version (86d55b1).
- **Choose your own adventure:** the Bay Model Visitor Center (Sausalito, free, Tue to Sat) added: spreadsheet row 18 plus
  its `days`/`hoursEs`/`agesEs` in `adventure_io.py`; 23 places (68a3f3e). Its website blocks plain fetches (403); read
  it in a browser.
- **Phone sessions** (Nov 3-4) added 15 events, ids 1858-1872, straight to events.json; phone inbox empty.
- Health 2026-11-04: 564 events, max id 1872; self-test 92/92; `check_docs.py` clean; duplicate scan 5 findings, all
  known (1729 vs 286 among them).

## What changed 2026-10-28 to 2026-10-31 (phone sessions), in one pass

- **Events added from screenshots and links:** Social Klub partner events Meet Lulu Bird! (1773, Nov 3) and hiccapop Play
  Lab (1774, Nov 23, a disclosed product-feedback session), plus 1745 (Your Body After 40) corrected to 6-8 PM; Election
  Night Distraction / Hamilton Movie (1775, Marin City Library, Nov 3, title as Alexandra gave it); ¡Noche de Baile! (1776,
  Dance Palace, Oct 30; cost "Free entry; food & drinks for sale" assumed); Mill Valley City Hall Historic Plaque Unveiling
  (1854, Nov 2); Free Halloween Face Painting (1855/1856, Bahia park, Novato, Oct 30-31, from a neighbor's Nextdoor post);
  Bike Fest Marin City (1857, St. Andrew Presbyterian, Oct 31). Gingerbread House Decorating Party (100) cost now
  "$65 + fees ($71.21 on Eventbrite)". **Ids are reused:** `next_id()` is max + 1, so after the nightly purge removes
  the highest id, the next record takes its number (1773 was briefly an Art Barn event that expired). Search
  `internal_notes` dates, not ids, when tracing a record's history.
- **Passed:** the Get Ready for Super El Niño talks at Belvedere-Tiburon Library (all three dates had already
  happened). The **Napa sweep** was deferred from the phone and run on the desktop (see the Oct 29 entries).
- **Instagram, Sat Oct 31 post (Metricool 411930560, was 410788148):** slide 1 and the caption's first line now read
  "Need a break from Marinoween-Mania?" (Alexandra). The slide was edited in a cloud session without the Dropbox builder by
  overlaying one line on the existing PNG in headless Chromium (Playfair Display italic 71.6px, matched to the original
  pixel box); it is `ig/week_of_oct29/sat-1-marinoween.png`. **Trick worth keeping:** when GitHub Pages is slow to deploy,
  Metricool accepts the `raw.githubusercontent.com/<owner>/<repo>/<commit>/<path>` URL and copies the image into its own
  storage; download Metricool's copy afterwards and compare it to the file.
- **Instagram auto-DM to new followers (research only, nothing set up):** Metricool Flows has no new-follower trigger. The
  only approved route is ManyChat's "Follow to DM" (Pro, about $15/month), which Meta grants account by account and
  likely not below about 1,000 followers (the account had 256 on Oct 26); tools that scrape followers or log in with
  the password break Instagram's terms. Instagram's official follower list comes only from "Download your information".
  Open item 82 (via the phone inbox).
- Health 2026-10-31: 634 events, max id 1857; self-test 92/92; `check_docs.py` clean; duplicate scan the same 6 known
  findings.

## What changed 2026-10-29 (evening), in one pass

- **Instagram:** a one-off **Halloween weekend carousel** (30 Marin events, Halloween plus Día de los Muertos; builder
  `OAA marketing\Instagram templates\Halloween weekend\build_halloween_weekend.py`) published Thu Oct 29, 8:15 PM via
  Metricool (410775552). Then the **Sat Oct 31 7 AM** and **Sun Nov 1 5 PM** posts, with no Halloween content, were scheduled
  (410788148, 410788157; `build_week_of_oct29.py`). Details in `social_media_and_marketing.md`.
- **Hashtag rule (caption rule 12):** every Instagram post ends its caption with **exactly 3 hashtags**, no first comment.
  Alexandra first said "only 3 hashtags in the comments", which was read as the first comment and applied; she then asked
  for them back in the caption. The Halloween post went out with them in the first comment. Earlier-scheduled Hot Tips and Tag
  posts keep their ~10 caption hashtags (her call). **When a short instruction about placement is ambiguous, ask.**
- **Open items:** 56 (Choose your own adventure) closed; 59 retitled **Google Analytics ToDos** (two GA4 settings for her);
  new **80** Stack Sorted / Supplement Mgmt Business (own section; secure website domain); new **81** weekly Monday GA
  analysis email (not started); 77 gained Sausalito Library; 38 and the CLAUDE.md pick-up list now record the processed
  Napa sweep (`806f476`).
- **Folders:** `OAA Sponsorship and Partners` is for advertisers who pay her; `OAA marketing` is for placements she pays
  for. The SMMC post files moved to `OAA marketing\SMMC Add\SMMC social post\`. A stray partial copy of her Downloads folder
  (57 personal files) inside `SMMC Add` was traced to File Explorer on Oct 25, 3:00 PM (no Claude session touched it) and
  was gone by the time deletion was approved.
- Health unchanged: 644 events, max id 1853; duplicate scan the same 6 known findings; `check_docs.py` clean.

## What changed 2026-10-25 to 2026-10-29, in one pass

- **Oct 25-26 (app):** Choose your own adventure "Museum" became **Museum/Attraction** (TrainTown and Snoopy's Home Ice moved in, `a2b317b`); garbled Spanish accents fixed (`0ca438a`); **Self Serve Resources** links under the tide table (Manzanita webcam, WET tide app, King Tide Alert; `966882c`, enlarged in `fb02be1`); **bolder sponsor tiles** in the Featured carousel (3px outline, glow and tint in the sponsor's colour, `f240cb8`); CYOA header row locked while scrolling (`ab25352`). Open items 78 (flood resources post) and 79 (SMMC $250 sponsored post, waiting on SMMC to confirm 1080x1080 vs 1080x1350).
- **Marin weekly sweep, Oct 29 - Dec 15** (`daily_sweep_2026-10-29_review.xlsx`, 50 sources). Alexandra asked whether the MD files had been read and the process followed exactly; it had not, fully (MD files skimmed, some pages keyword-searched, library branch pages skipped, venue lists filtered). **A second pass re-read everything in full** and changed the result: two candidates were already in the DB (South Novato Ingrid Dec 23/30 = 1627/1628) and came out; one was missed (Novato's Skeleton Scavenger Hunt, because the MCFL feed carries multi-day events that START before the window, so filter on end date, not start date); San Anselmo Crafternoon's Nov 18 theme was its own slot (rule 27), so 45 was fixed to "Third Wednesday" instead; 626 (Fairfax parents' group) was a duplicate of 1157 after moving back to the Pavilion; the rule 24 reverse check found library dates with no session. **Lesson: the full read is not optional, and it is where the errors are.**
- **Processed the same day** (`14dc088`): **34 records added (ids 1777-1810)**, including Fairfax House by the Park as four dated one-offs (irregular 3rd/4th Fridays), Sausalito Books by the Bay storytime Weekly, Christmas Ceramics (Social Klub partner), Ukulele Jam Nov 20 (985's moved session). **25 record fixes:** 1193 and 626 retired; cancellation ALERTs on 58, 717, 1173; skips on 1108, 815, 985, 180, 1649; 1767 moved to Fri Dec 11 5-7 PM, $55; 1326 10:30; 45 third Wednesday; "No session listed" ALERTs (Alexandra's choice) on 838, 11, 876, 176, 175, 1182, 46. Library-event `website`s now use each event's own `marinlibrary.bibliocommons.com/v2/events/<id>` page, not the generic list (link rule). **The Record Fixes Decision column came back blank twice; Alexandra filled it on the third read.** Re-read the saved file after she says it is updated: Excel may still hold unsaved edits.
- **Napa weekly sweep, Oct 30 - Dec 15** (`napa_sweep_2026-10-29_review.xlsx`, 30 sources, attestation complete; **processed the same day, `79fec3a`**: Alexandra approved all 32 rows, so 43 records were added, ids 1811-1853, plus 5 fixes: 905-907 retired, 530 re-sourced, Hydro 510 Active again; both town farmers markets, Tuba Christmas Dec 19 and a new location group `Napa` for Napa-city events added at her request). 32 rows: for the first time **non-music family events** (Calistoga Halloween Parade, Lighted Tractor Parade, Merry & Bright Night; Yountville Town & Tree Lighting, Visits with Santa, Holiday Sing Along; St. Helena Día de los Muertos, Wine Barrel Tree Lighting, Old Mill Holidays; The Village Calistoga kids' nights), plus four Brannan concerts, two Clif Sip & Support dates, and weekly LAB Karaoke and Hydro Open Mic / Monflower Jazz Duo. **Findings:** the LAB source is a Pittsburgh brewery (Napa specifics); **Hydro's site is back** (Tritones Sundays 6 PM; propose 510 Active); Napa Vintners is blocked in all three tiers. New fetch routes are in `sources/napa.md`. Alexandra asked why Napa took far longer than Marin: Marin has raw feeds (MCFL, Marin Humane), while Napa's sources are script-built lists that need browser "Load more" clicks and one event page per item.
- **Housekeeping:** `check_duplicates.py --self-test` fixture for id 45 updated (now 3rd Wednesday; 1368 covers "last"). The Social Klub ad was checked against its site (matches; the site adds members-only 7-9 AM hours and "Saturday times may shift for private parties"; Alexandra: no change).

## What changed 2026-10-23/24, in one pass

- **Phone sessions, Oct 23** (pulled at start): the tide table's adjustment went from +1.07 to **+1.25 ft** (`2575516`);
  Free Story Time at Milkweed (1768); Kitsch + Sync Candy Comedown Playdate (1769, Nov 1, 9-11:30 AM) and **Sunday
  Football @ Kitsch + Sync** (1770/1771, split at New Year, to Jan 10); Bingo and Trivia reservations by email
  (info@kitschandsync.com, preferred not required); MarinHealth Mothers Support Group, online Thursdays (1772).
- **Phone inbox applied** (Oct 24): open item 75 (Context Transfer skill), 58zq address, 58zm closed, Kitsch + Sync notes
  in item 21. A Golden Gate Gymnastics item was added as 76 and then deleted by Alexandra ("this isn't correct"). The
  inbox had numbered it 74, which "Beyond Marin" already held: **check the highest item number in `open_items.md`
  before numbering a new one.**
- **King tide flood post** (Oct 25-30), drafted in a cloud session (`OAA maintence and content\HANDOFF_king_tide_post.md`)
  and finished here: times recomputed at the new +1.25 ft, a new slide 4 ("Want more *resources?*"), end slide reworded
  to "Family events in Marin, all in one place." (never "every" event), scheduled in Metricool for Sat Oct 24, 4 PM
  (id 405268548). Slide sources are untracked in `templates/tide_flood_*_oct25.html`.
- **Flood Watch on Resources** (`ecda119`, build 2026-10-24.1): slides 1-3 as a swipeable strip at the top of Resources,
  hiding itself after Oct 30 (`data-until`). See the Resources section.
- **Tide heights must round like the app.** `_tideCell()` uses `toFixed(1)`, which rounds the exact value half up (7.25
  shows as 7.3); Python's `round()` rounds half to even (7.2). Anything printed from `tides.json` for the public (slides,
  captions) must use Decimal ROUND_HALF_UP to match the table.
- **Choose your own adventure Phase 1A** (`452d48b`, build 2026-10-24.3): Cost column (sorts and filters on the lowest dollar amount in the cost text, bands in `ADV_COST_BANDS`), the table scrolls sideways inside `.adv-scroll` with a sticky Place column, and `adventure_io.py` writes every location group as `Marin/<group>` so Phase 2 can add `Sonoma/...`.
- **Choose your own adventure, same day:** open gym audit (`da04cb4`; Flying Dutchman toddler + all-ages in one row with Fri, Gravity Vault's age rule in its hours) and a "Days, Hours & Age" column (`4bf1532`, build 2026-10-24.4) showing `ages` / `agesEs` at the top of each cell. Spanish ages live in `adventure_io.py` `AGES_ES`; the sheet has English only.
- **Choose your own adventure, San Francisco (`a99bc24`, build 2026-10-24.5):** `adventure_io.py` now also reads the "Beyond Marin" sheet, keeping only rows whose Region is "San Francisco" (Sonoma stays out). Those rows name their category in a "Category" column (must be a CATEGORY_ES key; "Zoo" added) and get their location from `SF_AREA` ("San Francisco/<area>"). Put the child price first in a cost cell: the cost filter reads the first $ amount, and "Free" counts as 0.
- **Choose your own adventure, Sonoma (`c042d93`, 2026-10-25):** the Region filter was replaced by `BEYOND_LOCATION` (slug to "<Region>/<area>"): only Beyond Marin rows listed there are published, and `region` is the part before the slash. Five Sonoma places added; new categories "Ice skating" and "Rides & play park". **Excel COM from PowerShell 5.1:** a .ps1 with Spanish text must be saved as UTF-8 *with BOM*, or accents land in the sheet garbled ("bahÃ­a"); check with `grep -c "Ã" adventure.json`.
- Health: 642 events, max id 1772; notes-lint and bilingual-lint clean; duplicate scan 7 findings, all known (1770/1771 is
  a new New-Year split pair).

## What changed 2026-10-22, in one pass

- **Kitsch + Sync signed a 3-month Featured sponsorship (Leadsheet start 10/22/2026).** Live the same day (`5322dd0`,
  `4c6ac8d`): Featured ad `kitsch-sync` in `ads.json` (Oct 22, 2026 - Jan 21, 2027; bright yellow `#FFD200` tile border,
  logo `assets/ads/kitsch_sync_logo.png` + tile icon `kitsch_sync_mark.png`), 8 partner events from their flyers (ids
  1757-1764: Halloween week Oct 27-31, Dine & Donate Nov 4-6; ages Families, type Community Event, cost "Food/PlayZone
  passes for sale"), and the Oct 23 movie night (1748) made a partner record. Held: Candy Comedown Playdate (no time);
  left out: Football Is On.
- **Every Kitsch + Sync listing's public note ends "Socks required in the play zone."** (`493e413`; 1748 already had it).
- **Record fixes found while picking Instagram posts** (`e994fdc`): 476 Ross Valley Farm Walk (ends 1 PM; 2026 dates to Dec 27) and 1125 Evening at Roy's Redwoods (adults, registration required, 3:30-6:30 PM, event page as website).
- **Instagram week of Oct 22 scheduled in Metricool** (Thu 403646200, Sat 403646224, Sun 403646242); images staged at `ig/week_of_oct22/` (`91c65c0`).
- **Up to 9 sponsor tiles** (`MAX_FEAT_ADS`, build 2026-10-22.1). `withAds()` had a fixed cap of 2, so a third
  Featured sponsor got no tile and nothing said so. The strip stays at 12 cards; each ad takes an event's slot.
- **An ad page cannot list a sponsor's events.** A hand-typed "Coming up" list (code-less `offers`) was tried and
  removed at Alexandra's request because it goes stale. Making it automatic (read the sponsor's partner events) was
  offered and not taken.
- **`socials.facebook` needs a page slug.** A full `/people/<name>/<number>/` URL makes the Follow button read
  "people" (`index.html` takes the first path segment as the label). Kitsch + Sync has no slug, so their records carry
  Instagram only.
- **Instagram: Template A is the weekly standard** from the week of Oct 22, built with
  `OAA marketing\Instagram templates\Template A - Thu Sat Sun posts\build_week_of_oct22.py` (see
  `social_media_and_marketing.md`, "Template A standard").

- **Marin weekly sweep, Oct 22 - Dec 3** (workbook `daily_sweep_2026-10-22_review.xlsx`; all 49 sources, Ronnie's
  skipped at Alexandra's instruction). **41 records added (ids 1716-1756)**, among them: Mill Valley Shabbat ShaBabies
  (1716/1717), Marin Humane adoption events, Elf Hunt (1723/1724), Civic Center kids' movies, Fairfax DrawBridge, BelTib
  Afterschool Lounge, Tween D&D (Monthly, 1737), Village Santa photos and Pet Nights, Social Klub and Golden Gate Mahjong
  partner events, Kitsch + Sync movie night, Marinwood Night Camp (4 dates), and four December events found past the
  window (Rock and Roll Playhouse, Holiday Craft Fair, Menorah Lighting, JCC Chanukah). Record fixes applied: skips on 46,
  ALERTs on 815 and 861, 776 retired, San Anselmo storytimes (21/33/82) move to Council Chambers Nov-Mar, 1696 links to
  goldengatemahjong.com/play. The Record Fixes tab came back blank; Alexandra then said "apply all 11", and all 11 went
  live in `41e8f96` (cancellation ALERTs on 48/837, 1177 and 1313 retired, Winterfest and Winter Wonderland times,
  Gingerbread venue, Lego Saturdays Weekly, Larkspur storytime 10:30 AM, Social Klub free play 1-3 PM).
- **Golden Gate Mahjong titles end "w/ GG Mahjong"** (Spanish "con GG Mahjong"), ids 1696 and 1747 (`a3d65ab`); both link
  to goldengatemahjong.com/play. Search is region-scoped: a visitor whose last-tapped region is Telluride will not find
  Marin events until they switch back.
- **Pattern for a recurring program with irregular dates** (Alexandra asked for one recurring listing, not one-offs):
  Weekly on its weekday with `season_start`/`season_end`, **split at New Year (seasons do not wrap the year)**, every
  non-session date as `skip:`, and `expires` on the last date so the season does not come back next year. Same shape as
  Pavilion Playgroup (1156/1158). Used for ShaBabies Mill Valley, the Elf Hunt and Village Santa photos (daily: `day` lists
  all seven weekdays).
- **San Rafael Public Library moved to sanrafael.gov/events** (source #39 updated). Sausalito list views read fine in the
  in-app browser (sources #8/#40 noted).
- **Sponsorship (Oct 21-22):** Advertising Partners Upload now has `Kitsch + Sync` (Featured) and `The Cave` (Community)
  tabs; `Marin JCC` marked prospect; the Leadsheet lists all three as "(prospect)" with no live date.

## What changed 2026-10-21, in one pass

- **Phone sessions synced** (Oct 18-21, 25 commits by the phone and the nightly bot; listed in the repo log).
- **Three new sponsor prospects, mockups only; nothing about them is in `events.json` or `ads.json`.** All files are in
  `OAA Sponsorship and Partners\`, each vendor in its own subfolder, built in the app's own CSS and rendered with Edge
  headless. Each listing comes in two versions: `... mockup.png` has the review notes for Alexandra, and
  `... (for <vendor>).png` has no notes and is the one to send.
  - **Osher Marin JCC** (`JCC/`): JymBabies Mill Valley as a partner listing, built from the live record (id 59) with
    the JCC logo. The `Marin JCC` tab of `Advertising Partners Upload.xlsx` holds the 6 recurring JBaby programs plus
    the 2 ad hoc ones (Tot Pool Parties, Family Connections); Side by Side is left out (a pre-registered course). The tab
    was written via Excel COM, with time cells set to text (`NumberFormat '@'`) so "10:30 AM" is not converted.
    **Live-record fixes still owed:** 59's description says "Runs until 12:00 PM" (ends 11:00) and lacks the waiver
    note; 58's card shows $15 (now $20).
  - **Kitsch + Sync** (`Kitsch + Sync/`, family restaurant and play space, 1757 Grant Ave, Novato): Halloween Movie Night
    (The Haunted Mansion, Fri Oct 23, 5:00-6:30 PM, $18 with play and popcorn) as a partner listing, plus a **Featured
    carousel ad** modelled on the Social Klub ad, with a "Coming up" list of their events in place of offer codes.
    Their site sits behind a Cloudflare check: read it in the in-app browser.
  - **The Cave** (`The Cave/`, gymnastics, parkour and CrossFit; 412 Tamal Plaza, Corte Madera, and 25 Dodie St, San
    Rafael): three separate listings, Kids' Night Out (Halloween Night, Sat Oct 24, 4:30-9 PM, ages 5-12, $75.25 early
    bird / $86.20), Ninja Night (Sat Nov 14, 4:30-8:30 PM, ages 5-12, $99) and Sunday Open Gym (9-11 AM, ages 6+).
    inthecave.com reads fine with a plain fetch.
- **Logos saved to the shared `assets/` folder, at Alexandra's request:** `kitsch_sync_logo_long.png`,
  `kitsch_sync_logo_stacked.png` (their site serves WebP; converted to PNG) and `the_cave_logo.png`. The JCC logo
  (`marin_jcc_logo.png`) was copied there from the repo. The OAA logo was copied to
  `OAA marketing\Instagram templates\assets\`.

## What changed 2026-10-16/17, in one pass

- **Review workbook template standardised, with a new "Sources Used" tab** (Alexandra, Oct 17). Every region (Marin,
  Napa, Telluride) now uses the same four sheets and columns: Weekly Sweep (now with a `Source #` column), Questions,
  **Sources Used** (each source that produced a candidate, with the events it gave), Attestation Log. See "Review
  workbook format". `check_docs.py --attestation` now checks the Sources Used sheet too (`--partial` for a one-source
  review); self-test 12/12.
- **Telluride source #10, Visit Telluride's Festivals & Events calendar** (`4e1fa44`): first pass approved in full, 16
  events (ids 1679-1694: Pumpkins & Peaks, Adventures in Acting, Mountain Sprouts party, Mountainfilm for Locals, KOTO Ski
  Swap x3, Young Frankenstein x3, Lamplight Cemetery Tour x2, Ski Resort Opening Day, Freeski Film Night, gondola notice).
  Alexandra: Telluride content will skew more adult. The page must be read in a browser (see `sources/telluride.md`).
- **Housekeeping, later on Oct 17:** the leftover phone-session branch `claude/push-events-marin-app-cz0p19` was deleted
  from GitHub (everything on it was already in `main`; only `main` and `lockdown-edge-functions` remain). In open items:
  the GitHub / cloud-session issue is **closed** (Alexandra confirmed phone sessions read, commit and push); new **item 73,
  "Apply for the Anthropic startup program"** (name only so far); and Telluride items **66-70 merged into item 66**
  (entries 66a-66e; numbers 67-70 retired).
- **The Telluride partner is now named: Lee Shea** (Alexandra, Oct 17; "Lee Shea" is her first name, so use both words, corrected Oct 20), in this file, item 72 and `Telluride\PARTNER_SETUP.md`.
  The section title "Telluride partner sweep" is unchanged on purpose: Lee Shea's start-up prompt names it.
- **Search results now run soonest first** (`970fb94`, build 2026-10-17.1, tried locally by Alexandra first).
  `searchEvents()` sorts by next occurrence date (new helper `getNextOccurrenceDate()`, also used by
  `getNextOccurrenceLabel()`), then start time, then name; events with no upcoming date go last. "and", "&" and "+"
  now match each other. Search also skips retired (Inactive) records, which it had been showing (the same
  `shouldShowEvent` fix the Featured strip got on Oct 13). **To try a change locally**: the `oaa-local` preview needs a
  saved profile, or the app stops at sign-up; set `localStorage.oaam_user` in that localhost tab only.
- **Also added:** Pottery Barn Kids Halloween Craft Event, Sat Oct 24, 10 AM (id 1676, `af602a6`). The pull hook's
  time limit is 20 seconds (Alexandra).
- **First phone (cloud) sessions** (Oct 16-17). Events added from the phone: **1667** Coffee + Community @ Creekside Bakery
  with The Local Hype Girl (Wed Oct 21, 10-11:30 AM, Novato; retitled once; street address and audience still open, item
  58zq); **1668/1669** Marin Ski & Snowboard Swap (Sat Oct 17 / Sun Oct 18, 10 AM-4 PM at Alexandra's instruction though
  the flyer says 9-4, Demosport, 1101 Francisco Blvd. E, San Rafael; "Free entry" and indoors approved assumptions);
  **1670** Black Canyon Model Garden Railroad Open Day (Sat Oct 17, 10 AM-3 PM, 35 Bradcliff Court, San Rafael, from
  bsrr.net). New CLAUDE.md section **"Phone / cloud sessions (Claude Code on the web)"** explains how they work.
- **Phone sessions can now push to GitHub.** Reconnecting GitHub in claude.ai settings did not fix it; **installing the
  Claude GitHub App on the repo did.** (Details in the Phone / cloud sessions section.)
- **Desktop sessions now pull first, automatically:** a SessionStart hook in the Dropbox project folder's
  `.claude/settings.json` runs `git -C "C:\Users\AWalter\Code\out-and-about-marin" pull --ff-only` when a session starts.
  It never merges or overwrites: if the local repo has its own commits or conflicting edits, the pull just stops and
  says so, and the session carries on. Remove the hook from that file to turn it off.
- **The Village at Corte Madera** (`448f182`): Pottery Barn Kids storytime ends Oct 31 and the Mahjong Social (Thursdays,
  11-1) ends Oct 29. Both are now dated one-offs (1671-1674); seasonal 750 retired so it does not return next summer. There
  was no Village mahjong record before.
- **The Social Klub refreshed** (`448f182`): new The Awakening Breathwork (Oct 29, 1675, Grown-Ups Only!); 1334 now
  7-8:30 PM, $35 / $60 for two; 1648 (Sausalito Thrive free play) now says it includes a presentation and Q&A and that
  booking is for Sausalito voters.

## What changed 2026-10-16, in one pass

- **5 events added** (ids 1662–1666, `1787396`): Trick or Treating with Horses at Halleck Creek Ranch (Sat Oct 24, 4-7 PM,
  RockRose Ranch, 3311 Nicasio Valley Rd; flyer from Instagram, confirmed on halleckcreekranch.org/events); Citrine free
  community class, Guided Hypnosis & Sound (Thu Oct 22, 6:30 PM, Larkspur, Grown-Ups Only!, from its Momence page, read in
  the in-app browser while Chrome was disconnected); Katie Mae's free Zoom parent sessions (Coaching Conversations Oct 20
  and Nov 17, Conscious Parenting Lab Nov 12; type Community Event, `Virtual`).
- **New Marin source 49: Katie Mae, withkatiemae.com/events** (Alexandra: "free events from here and add to source list").
  Free events only; the $35 workshops are left out. `sources/marin.md` Source count is now **49**, so the next Marin
  sweep workbook needs 49 Attestation Log rows or `check_docs.py --attestation` will fail.

## What changed 2026-10-15, in one pass

- **11 events added from Alexandra's screenshots** (ids 1651–1661, `7718b72`): Pini Kid's Club Halloween sun catchers
  (Oct 17, San Marin store; the flyer graphic said Sept 17, the caption Oct 17, caption used), Free Art Lessons / ArtBridge
  kickoff with CoachArt (Oct 17, MV Community Center, ages 6-15), Sing! Marin World Singing Day (Oct 17, Marin Country
  Mart), Michaels Halloween Fest (Oct 17, San Rafael, the only Marin Michaels; national promo, "call ahead" in notes),
  thRED TENT pop-up sale (Oct 18, Green Door Design, Community Event), Sound Bath with Blue Muse Healing (Oct 22, Church
  of Our Saviour, Grown-Ups Only!, time TBA), Jewelry Pop Up Fundraiser for Fire Foundation (Oct 25, Lumber Yard, title
  as the maker asked), Witch's Brews and Stews (Oct 31, Toby's Feed Barn, WMI PTSA), Bolinas Winter Faire x3 (Dec 11-13,
  all expire Dec 13; Santa Sunday Dec 13 2-4 PM in the Dec 13 record).
- **Updated 1160 Downtown Getdown** (Oct 17): ends 6:00 PM, not 6:30; band Danny's Live Dead. **Not added:** the Play-Well
  Haunted House LEGO workshop, already id 1215.
- **Assumptions to confirm** (in open items 58zp): Pini Kid's Club cost set to Free (not stated); Sound Bath time and price
  unknown; Michaels details not confirmed by the San Rafael store.

## What changed 2026-10-14, in one pass

- **Marin weekly sweep, Oct 14 - Dec 1** (workbook `daily_sweep_2026-10-14_review.xlsx`, attestation 48/48). Alexandra's
  decisions applied in `8f4ba49`: **27 events added** (ids 1624–1650: Marin Girls Chorus, Indigenous Storytelling x2, South
  Novato Ingrid Dec 23/30, Belvedere-Tiburon crafts / Sewing Bee / THE HANGOUT x4, Larkspur Chess Club x3, San Rafael extra
  Sing-Along and Books Beyond Borders, San Anselmo Read to a Dog Nov 4 and Seed Fair, Summit Sips hike, San Rafael Day of
  the Dead, Bolinas Día de los Muertos, Veterans Day program, Pink Halloween Tea, JCC Shabbat Shmooze (monthly) and
  Festival of Lights, Social Klub free play, Mill Valley Panel to Panel). **Record fixes:** 980 D&D Fairfax made Monthly
  (3rd Wed); 1156/1158 playgroup no-class skips; 829 retired, 830 retitled Thankful Bellies; 1124 wait-list note; 1419 time
  5 PM; 951 time 6-7:30 PM; 474/475, 707, 129 retired (no longer listed); Dec cancellation ALERTs on 6 and 7.
- **Fetch routes learned, now written into `sources/marin.md`:** Sausalito city and library calendars must be read in
  **list view** (the month grid hides events behind "+2 more"); Marin Humane has a raw JSON events feed; MCFL's
  `gateway.bibliocommons.com` API is the raw route for all ten branches; Barnes & Noble needs real Chrome and a
  click on each day; FIT4MOM's schedule is a Glofox frame; Mill Valley's calendar IDs changed again (source 7).
- **Marin Mommies proved mostly a cross-check this week:** the roundup and all 14 days gave one new event; nearly
  everything else was already in the database. Two of its listings were wrong (a Monday Graveyard Stroll that does not
  exist; Hauke pop-up storytime shown on Thursdays), caught by checking the organiser.
- **Open items:** 58zm (Nicasio movie night, organiser unconfirmed), 58zn (Elf Hunt 2026 dates), 58zo (Instagram:
  highlight the Sausalito Thrive free play), 58m updated.

## What changed 2026-10-13, in one pass

- **Bug fix: the Featured carousel could show retired events** (e.g. id 789, a misdated movie night retired Sep 8). It now skips anything the main list hides. See the Featured strip section.

- **Featured carousel: 12 cards and a "Community Resources!" card** (Marin view) that opens the Resources tab at the top (`57f0796`, build 2026-10-13.1). See the Featured strip section.

- **Kids Eat Free listings removed from the event feed** (`4362c54`): ids 1118 (Hotboys), 1119 (Finnegan's),
  1356/1357 (Asian Box), 1369 (Amici's) set Inactive. The deals stay on the Resources dining table (starred rows);
  rule added to the dining section so a sweep does not re-add them.

## What changed 2026-10-12, in one pass

- **9 events added from screenshots and a link** (ids 1615–1623, commits `2e04846`, `3dc40b9`): Lair of the Dragon Queen
  haunted house (Stinson Beach, Oct 31), Move Better, Live Better (Mill Valley Downtown Plaza, Oct 15), Free estate planning
  talk / Numbered with the Saints (Church of Our Saviour, Nov 1, Grown-Ups Only!), Novato Mothers Club family hike (Nov 7,
  meeting place unknown: item 58zl), Walk: Mom Life on the Move Walk (Dr. Insomniac's, Nov 14), Blood Drive at the Bay Model
  (Nov 19, Grown-Ups Only!), and three Our Sisters Keeper December events in Marin City (wreath making Dec 14, pajama sip &
  paint brunch Dec 16, Christmas Eve toy drive; website = their Upcoming Events page, as Alexandra asked).
- **Not added because already covered:** Sausalito Art & Harbor Days Oct 24 (id 97, 4th Saturday) and the Marin Hiking Moms
  hike Nov 14 (id 255, 2nd Saturday). **Held:** Our Sisters Keeper's Dec 30 movie day (no time; public access unclear).
- **Undated organiser page:** Our Sisters Keeper lists dates with no year; held until Alexandra confirmed 2026 (the
  stale-year rule). Assumptions to verify are in each record's `internal_notes` (Stinson Beach Community Center address,
  the blood drive's sign-up site).
- **Retitled at Alexandra's request (`a6e6f41`):** "Walk: Mom Life on the Move Walk" and "Free estate planning talk /
  Numbered with the Saints" (cost now "Free (lunch included)" to match).
- Health: `events.json` 640 events, max id 1623; checks clean apart from the documented findings.

## What changed 2026-10-11, in one pass

- **Fixes from the 2026-10-11 test run** (report: `Downloads\telluride_partner_sweep_chat_test_2026-10-11.md`). Alexandra tested the partner prompt in **Claude Chat** by
  mistake; the partner uses **Claude Code** desktop (confirmed). Chat's cloud workspace cannot reach the library feeds or
  Dropbox, so those findings do not apply. Kept: retry each download up to 3 times, 30 s apart, before stopping (GitHub
  answered one 429); `check_docs.py` now says a missing region file probably means a failed download; neutral wording
  (`python`/`python3`, `/` or `\`, browsers named by what they are); setup page says use the prompt as written, in Claude
  Code. **New rule for every region: feeds (iCal, JSON APIs, long paged lists) must be read raw and in full; a
  summarizing fetch never counts, and an unreadable feed is attested INCOMPLETE while the sweep finishes** (Alexandra:
  record and finish).

**Older "What changed" logs, the 2026-08-21 state of play and the documentation-drift notes are in `HISTORY.md`.**
- **Sponsor Leadsheet** (night of 2026-10-10): new first tab `Leadsheet` in
  `OAA Sponsorship and Partners\Advertising Partners Upload.xlsx` listing sponsors that are live on the site:
  Golden Gate Mahjong (09/28/2026, Community), The Social Klub (09/30/2026, Community + Featured), FIT4MOM Marin
  (10/09/2026, Community + Featured). See "Where the non-repo files live".

## What changed 2026-10-10, in one pass

- **Colorado events seen in a Marin feed: not a data bug.** The live data and code were clean (0 Telluride records in the
  Marin view across 9 weeks). The cause was a tab still running the pre-Telluride page against the new `events.json`.
  **Fix shipped: auto-update** (`05dc754`). Open tabs read `version.json` when they return to the foreground (and every 30
  min) and reload once if `APP_BUILD` differs. **Run `python bump_build.py` after any `index.html` change** (Git workflow
  section). Region stays in localStorage: Alexandra wants returning visitors to reopen on the region they last chose, and
  first visits default to Marin. An attempt to reset everyone to Marin each visit was started and reverted at her request
  before shipping.
- **Kid-Friendly Dining table now 17 rows:** added Boudin (The Village, not Town Center as given), El Huarache Loco and
  Souvla (Marin Country Mart), Blue Barn Novato, Pond Farm; Gott's patios and parklet; Hook Fish Co. at Tam Jct.;
  **asterisk + footnote** on kids-eat-free restaurants (Resources section).
- **Events:** Peace, Love & Lullabies (Social Klub partner, Nov 28, id 1610), Belvedere Halloween Carnival (Oct 25, 1611),
  Music with Megan @ Marin Country Mart (Oct 10, 1612, a deliberate duplicate of the id 56 slot), Bay Club Free Tour Day
  (Oct 17 and 18, 1613/1614, Bay Club Marin, 10-4, other locations named in the description).
- **Naming rule:** every Megan Schoenbohm event is titled `Music with Megan @ <venue>` (ids 1353, 1382, 1383 renamed).
- **The Dropbox move** (night of 2026-10-10): see the top of "Where things live" and the full record in
  `OAA maintence and content\Dropbox_move_plan_2026-10-10.md`. 3,111 files checksum-verified; repo pushed from its new path.
- **Claude sidebar:** all OAA sessions are filed under a custom group "Out AND About" (new sessions must be filed by hand).
- **Metricool:** the first auto-publish (Sat Oct 10, 7 AM) went out as planned.
- **Docs restructured late 2026-10-10 (commit `f310731`, Alexandra):** one rulebook for every region. CLAUDE.md now holds
  every rule plus the single "Weekly sweep" procedure and "Processing an approved sweep" (merged from `run-sweep.md` and
  `process-sweep.md`, now two-line pointers). Region source lists are in `sources/marin.md` (49 since 2026-10-16), `sources/napa.md` (30,
  rewritten from one paragraph into a numbered list) and `sources/telluride.md` (9), all in one fixed header + numbered
  format that **`check_docs.py`** enforces (`--self-test` proves it catches 5 kinds of breakage). Dated stories moved to
  `HISTORY.md`. CLAUDE.md went from 180 KB to 152 KB; all 1,477 old lines were checked against the new files.
- **Telluride sweeps move to Alexandra's partner, Lee Shea:** her own Claude Code works in the shared Dropbox `Telluride` folder with
  fresh downloads of the rulebook, tools and event list each sweep (no Git), saves `Telluride\Sweeps\telluride_sweep_YYYY-MM-DD_review.xlsx`, and
  renames it `…_APPROVED.xlsx` after review. Only Alexandra's Claude Code processes and commits. Setup page:
  `Dropbox\01. Out AND About Files\Telluride\PARTNER_SETUP.md`. **Rule:** a region never gets its own rule; a rule that
  seems region-specific is changed in CLAUDE.md for everyone, with Alexandra's OK.
- **Partner sweep made self-contained, and a completion check added (late 2026-10-10):** her start-up prompt is now five
  sentences that download CLAUDE.md and point to the new subsection "Telluride partner sweep", which holds every
  partner-specific step (downloads, `OAA-rules` as `<repo>`, the Claude in Chrome extension for tier 3, save, stop).
  **New `check_docs.py --attestation <workbook>`** confirms one Attestation Log row per source in the region file, each with
  a Result and none banned; it runs at the end of every sweep (procedure step 5) and before processing (step 0), for
  every region. Self-test covers it; verified on the real Telluride (9/9) and Marin Oct 8 (48/48) workbooks.
- **Partner prompt carries the dates (Alexandra, late 2026-10-10):** she writes today's date and the sweep period
  ("Today's date is MM/DD/YYYY, and the sweep should cover MM/DD/YYYY - MM/DD/YYYY") as its first sentence; "Telluride
  partner sweep" step 2 takes the window from those dates and asks her if they are missing or look wrong. The full
  six-line prompt is on `Telluride\PARTNER_SETUP.md`; keep that page and this section in step.
