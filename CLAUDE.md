# Out AND About Marin

Bilingual (English/Spanish) family events webapp for Marin County, CA. Shows recurring and one-off events for families with young children — library storytimes, music, outdoor programs, rec events, cultural festivals, etc.

- **Live URL**: outandaboutmarin.com
- **Repo**: github.com/outandaboutmarin/out-and-about-marin (this repo — work directly here, it's the single working copy)
- **Owner**: Alexandra ("Alexandra" or "she/her" below) — full decision authority over tech and content.

This file is the living source of truth for how the app is built and maintained. It replaces a versioned Excel workbook (`daily_process_v1` through `v52`) that used to be re-uploaded to a fresh Claude Chat session every time. **Edit this file in place going forward — don't create versioned copies.** Git history is the version trail.

## Where things live — read this first in a new session

Claude Code sessions for this project run with the working directory set to **`C:\Users\AWalter\Documents\2. Claude-Work\PROJECTS\OAA Marin`** — *not* the repo. This is deliberate and has been the setup since the project moved out of Claude Chat on 2026-07-02. **Don't treat it as misconfiguration and don't propose restarting the session inside the repo folder** (asked and settled 2026-08-09).

| What | Where |
|---|---|
| **The repo** — `index.html`, `events.json`, this file, `scraper.py`, `swim_vendors.json`, `.claude/commands/` | `C:\Users\AWalter\Desktop\out-and-about-marin` — the single local clone. Reach it by **absolute path**. |
| **Working files** — `open_items.md`, sweep review workbooks, the Napa and swim trackers, process docs | `…\PROJECTS\OAA Marin\OAA maintence and content\` — inside the session's working directory. Never committed to the repo. |
| Session transcripts + auto-loaded memory | `C:\Users\AWalter\.claude\projects\C--Users-AWalter-Documents-2--Claude-Work-PROJECTS-OAA-Marin\` |

Three consequences of this split. All are normal; none need fixing:

- **This file does not auto-load.** Because the working directory isn't the repo, `CLAUDE.md` is not injected into context at session start. **Read it from the Desktop path as the first action in a new session.** What *does* auto-load is `memory/MEMORY.md` in the path above, which carries a pointer here.
- **`/run-sweep` and `/process-sweep` are not available as slash commands.** They live in the repo's `.claude/commands/` and only register when the repo is the working directory. Every sweep to date has been run by **reading `C:\Users\AWalter\Desktop\out-and-about-marin\.claude\commands\run-sweep.md` as a file and following it** — likewise `process-sweep.md`. That is the established method, not a workaround.
- **`Glob` and `Grep` have failed in at least one session** on this machine (`Executable not found in $PATH`, 2026-08-09). If they error, fall back to PowerShell `Get-ChildItem -Recurse` and `Select-String -LiteralPath` — both work fine. Don't conclude a file is missing on the strength of a failed Glob.

## Tech stack

- **Frontend**: `index.html` — single-page vanilla JS app, no framework, no build step. Hosted on GitHub Pages via custom domain (`CNAME`).
- **Data**: `events.json` — see schema below. This is the single source of truth for event content.
- **Scraper**: `scraper.py` — run daily by GitHub Actions (`.github/workflows/daily.yml`, 6 AM PT). Does three things only: (1) removes expired one-off events, (2) flips `Seasonal` events between `Active`/`Seasonal - Inactive` based on today's date vs. `season_start`/`season_end`, (3) hash-checks library pages for changes and writes `scraper_log.txt` + `library_page_hashes.json`. **It does not discover new events.**
- **`library_review.py`**: also invoked by `daily.yml` with `--weekly-sweep` / `--monthly-audit` flags on a cron. Its automated fetch/keyword-match logic does **not** produce usable event data (output is things like date="TBD", time="See website") — the real sweep work happens live, via Claude fetching and reading each source's page directly (see "Weekly Sweep" below). Confirmed with Alexandra (2026-07) that this automation should be **left running as-is for now** even though it's largely vestigial — don't touch `daily.yml` or these flags without asking first.
- **Backend**: Supabase (users/events/feedback tables) + Twilio Verify (SMS PIN reset). **Out of scope** for Claude Code work right now — Alexandra will explicitly bring this in scope later if needed. Don't touch Supabase, Edge Functions, or auth code unless asked.

## Git workflow

- Work happens directly in this repo — no more copying files in/out of chat.
- **Routine changes** (adding events from a sweep, fixing a field, flipping a status, updating a reopening date): commit and push directly. Use a short, present-tense commit summary (e.g. "Add 12 events from Jul 2 sweep", matching the existing commit style — see `git log`).
- **Bigger/riskier changes** (schema changes to `events.json`, major `index.html` rewrites or new features, batch deletions, edits to `scraper.py`/`library_review.py`/`daily.yml` logic): stop and confirm with Alexandra before pushing.
- Always check `git status`/`git pull` state before starting work — this repo should stay the only local clone. A second stale clone under the Documents project folder was emptied 2026-07; the now-empty `…\PROJECTS\OAA Marin\out-and-about-marin\` folder is its leftover husk. It contains nothing and is not a git repo — **ignore it, and never write repo files there.**

## `events.json` schema

File is a JSON object, **not** a flat array:
```json
{ "last_updated": "YYYY-MM-DD", "events": [ {...}, {...} ] }
```
Always load/save through the pattern in `scraper.py` (`load_existing_events()` / `save_events()` — reuse `events_io.py`, see below) rather than hand-editing JSON text. The file has Spanish-accented characters — always read/write with `encoding="utf-8"` or you'll corrupt them (confirmed failure mode: default Windows `cp1252` encoding mangles é/í/ñ etc.).

As of 2026-08-09: **366 events, max ID 832.** Next new event gets the next ID via `next_id()` (max existing ID + 1) — this is a single global sequence shared by Marin and Napa records, don't hand-roll a per-county counter. (Was 505 events / max 565 on 2026-07-02; the count dropped because 395 expired records were purged 2026-08-04 — see State of play.)

**Fields on every event** (confirmed against actual `index.html` usage, not just assumed from old docs):

| Field | Notes |
|---|---|
| `id` | integer, unique |
| `organization`, `venue` | text |
| `event_name`, `event_name_es` | **both required on every event** |
| `type` | one of: `Library`, `Kids Programs`, `Community Event`, `Farmers Market`, `Festival`, `Music and Movies`. (`Music` also appears on some older records — `Music and Movies` is the current type, renamed from `Music` in 2026; use `Music and Movies` for new outdoor concert series / movie screening entries.) |
| `day` | full English day name, e.g. `"Monday"`. Multi-day recurring: slash-separated, e.g. `"Tuesday/Thursday"`. |
| `time` | 12-hour format, e.g. `"10:30 AM"` or `"2 PM"`. Parsed client-side with `/(\d+)(?::(\d+))? ?(AM|PM)/i` — unparseable times silently sort last. |
| `time_of_day` | `Morning` / `Afternoon` / `Evening` |
| `town` | town name |
| `address` | full street address |
| `ages` | free text, e.g. `"0-12 months"`, `"All ages"`, `"5-12 yrs"` |
| `cost` | free text: `"Free"`, `"Paid"`, `"$10 drop-in"`, etc. |
| `indoor_outdoor` | `Indoor` / `Outdoor` / `Both` — present on every record but **not currently read by `index.html`**. Keep filling it in for consistency/future use, don't skip it. |
| `active_sedentary` | `Active` / `Sedentary` — same status: present on every record, not currently read by the frontend. Keep filling in. |
| `cadence` | one of: `Weekly`, `Bi-weekly`, `Monthly`, `One-off`, `Seasonal` |
| `season_start`, `season_end` | **Seasonal only.** `MM/DD` with slashes — e.g. `"06/01"`. Never dashes; the date parser fails on dashes. |
| `event_date` | **One-off only.** ISO `YYYY-MM-DD`. |
| `expires` | **One-off only** (Seasonal/recurring leave blank). ISO `YYYY-MM-DD`. Event is removed by the daily scraper once this date passes. **Multi-day festival rule**: when a multi-day event has separate daily entries, set `expires` on ALL entries to the LAST day of the event, not each entry's own date — otherwise earlier days disappear from the app mid-festival. |
| `status` | `Active`, `Temp. closed`, or `Temp. paused` (`Inactive`/`Seasonal - Inactive` are also written by the scraper for seasonal events). **`Temp. paused`** (added 2026-08-05) is for a venue that still exists but has suspended a recurring program with no announced resume date — it renders an amber "Temporarily Paused" badge and the event stays visible, unlike `Temp. closed`, which can hide the event entirely when a reopening date is >30 days out. First use: id 509 (Buster's Southern BBQ, Napa) after the venue posted that live music was paused. Frontend pieces: `.tag-paused` CSS, `getPausedLabel()`, an `isPaused` branch in `cardHTML()`, and a `shouldShowEvent()` case returning `'badge'`. |
| `featured` | boolean. `true` adds a manual scoring boost in the homepage Featured strip (~120 events currently featured). |
| `description`, `description_es` | **both required on every event** |
| `registration` | free text, e.g. `"Not required"` |
| `website` | source URL |
| `notes` | free text. Special parsed patterns: nth-weekday rules (e.g. `"2nd and 4th Saturdays of each month"`), reopening dates matched via regex `Reopen(?:ing|s)\s+([A-Z][a-z]+\s+\d{1,2}(?:,\s*\d{4})?)` (e.g. `"Reopens June 11"`) which drives the "Closed · Reopens {date}" badge, the literal word `UNPREDICTABLE` (see Data Quality Rules below), and an `ALERT: <text>` prefix (added 2026-08-05) which renders `<text>` as a **red banner on the event card itself** plus red styling on the detail screen, for schedule-affecting callouts like cancellations or seasonal breaks that need to be visible in the feed without opening the event. Terminate it with ` \| ` if other notes follow; `getAlertNote()` reads up to the first `\|`. |
| `location_group` | **Do not assume the old fixed list from prior docs — it's drifted.** Live values as of 2026-07: `Mill Valley`, `Tiburon/Belvedere`, `San Rafael`, `Novato`, `San Anselmo`, `Larkspur/Greenbrae` (not `Larkspur`), `Corte Madera`, `Fairfax`, `Sausalito/Marin City` (not `Sausalito`), `West Marin`, `Nicasio/San Geronimo`, `Virtual`, plus Napa-area values (`Calistoga`, `St. Helena`, `Yountville` — see Napa note below). When adding a new event, match an existing value exactly — check current values in the file rather than trusting a hardcoded list here, since this has changed before. **Never use `"Marin County"`** — see rule 8 below (removed 2026-07-19; the 8 events that had it were reassigned to their real town's `location_group`). |
| `county` | Only set on the Napa-area events (`"Napa"`). Leave blank for Marin events (implicit default). See the Napa County Music section below for its own separate sweep process. |

**Napa scope note**: `events.json` contains events in Calistoga, St. Helena, and Yountville tagged `county: "Napa"`, surfaced on the webapp via the 🍇 Napa County toggle on the Profile screen. This is a **separate process from the 37-source Marin Weekly Sweep below** — see "Napa County Music" section further down. Resolved 2026-08-05 (open item 18): the process was undocumented here until Alexandra supplied `napa_music_process.md` (originally maintained June 2026) — now integrated below.

## Data quality rules

Always follow these when adding or editing events — they exist because of specific past mistakes:

1. **Fetch the live source page before adding/updating anything** — never assume a schedule from memory or a stale doc. A `web_search` snippet is only good enough to *locate* the right URL, never as proof an event/schedule is correct.
2. **One-off dates vs. recurring rule**: if the source lists specific dates ("May 22, Jun 26, Jul 17"), add each as a separate `One-off` event with `event_date` set. If the source says "every 2nd Sunday" / "3rd Friday", add as `Monthly` cadence with the ordinal rule captured in `notes`. Never invent a `Monthly` cadence entry without one of these two things confirmed.
3. **`UNPREDICTABLE` flag**: if a recurring event has no fixed nth-weekday rule and no published dates, add the literal word `UNPREDICTABLE` to `notes`. The frontend is expected to treat this as "hide from feed until dates confirmed" — check the source each sweep and convert to dated one-offs once published.
4. **Multi-day festival `expires` rule** — see `expires` field note above.
5. **Every new event needs BOTH `event_name_es` and `description_es`** filled in with real Spanish translations, plus a correct `location_group` matching an existing value.
6. **Dedup before adding**: search `events.json` by name + venue + town (and check `organization`/`description` for partial matches) before proposing any candidate as new. Never propose an event that's already present under any `status`.
7. **Recurring programs are added once.** Don't re-add a storytime/class every sweep — only add a *new dated one-off instance* if the recurring program is already in the DB and the source publishes a specific date for a special/guest edition.
8. **Never assign `location_group: "Marin County"`.** Every event must map to an actual city/town value (see the live-values list above) — the county-level catch-all was removed 2026-07-19 per Alexandra. If a new town doesn't cleanly match an existing `location_group` grouping (e.g. a one-off rural West Marin preserve), pick the closest existing town/grouping value rather than falling back to a county-wide bucket.
9. **Never rewrite a `Monthly` event's `notes` without preserving its ordinal phrase.** For `cadence: Monthly` events, `index.html`'s `parseOccurrenceRule()` reads the ordinal wording out of the free-text `notes` field (e.g. `"Second Saturday of each month"`, `"1st and 3rd Wednesdays"`, `"Last Friday"`) to decide which calendar date the event lands on. If that phrase is edited away, the rule returns `null` and **the event silently vanishes from the feed entirely** — no error, it just stops rendering. Confirmed failure 2026-07-29: rewriting Marin Hiking Moms' (id 255) notes dropped "Second Saturday of each month" and the event disappeared. When a specific announced date differs from the ordinal rule (these community groups often shift week to week), add that date as a **separate `One-off` entry** rather than bending the recurring record — one-offs render off `event_date` and don't depend on notes parsing.

   **9a. `parseOccurrenceRule()` scans the ENTIRE notes string — including prose that is only *describing* a rule.** Confirmed 2026-08-06 while correcting Battery Townsley (id 114) from "first Sunday" to "second Saturday": the replacement note explained the fix as *"previously stored as 'first Sunday', which was wrong"*, and the parser picked up that stray "first" and returned `{nths:[1,2]}`, so the event began matching BOTH the 1st and 2nd Saturday. **Never mention a superseded ordinal inside a corrected note.** Say "the earlier stored rule named the wrong weekday and week-of-month" instead of naming it. After any edit to a `Monthly` event's notes, verify with `parseOccurrenceRule(e.notes)` in the browser console and confirm it returns exactly the intended `{nth: N}`.

   **9b. The reopening-date regex takes the FIRST match, so conflicting `Reopens …` strings render the wrong badge.** Confirmed 2026-08-06 on id 8 (Corte Madera Family Storytime), whose notes had accreted three closure statements across successive sweeps — "Reopens Aug 25", "Reopens Sep 3" and an older May–Jul closure. The badge showed **Aug 25**, which was wrong and user-facing. When a closure date changes, **replace** the old sentence rather than appending a new one; a notes field should never contain two reopening dates.
11. **Teen-only events**: do not add events that are explicitly restricted to teens only (e.g. "Teens 13-18 only", "Grades 9-12"). If an event reads as borderline or could plausibly work for a broader family/all-ages audience even though it's teen-flavored or teen-skewed, don't silently exclude it either — include it as a candidate in the Weekly Sweep review file so Alexandra can decide. Resolved 2026-08-04 (open item 11).
12. **`location_group` renames need a `LOCATION_ALIAS_MAP` entry in `index.html`.** Users' saved "My default filters" store raw `location_group` strings — if a value is ever renamed or merged (e.g. `Larkspur`→`Larkspur/Greenbrae`, `Sausalito`/`Marin City`→`Sausalito/Marin City`, `Tiburon`→`Tiburon/Belvedere`), anyone who saved defaults under the old name silently loses that town from both the checkbox display and actual event filtering — no error, just quietly fewer results. `loadDefaultFilters()` (~line 4025) auto-heals this via `LOCATION_ALIAS_MAP`, mapping old value(s) to current ones and persisting the fix back to the user's record on their next visit. **Any time a `location_group` value changes, add an entry to that map in the same commit**, or affected users will silently lose coverage for that town with no visible error.

## Weekly Sweep — the core recurring exercise

Alexandra runs this **on command**, in chat, not on a schedule — she says something like "run the sweep" and it happens in that session. It is the main thing this whole doc exists to support.

**The two command files**: `run-sweep.md` (fetch everything, build a review file) and `process-sweep.md` (apply her Approve/Skip decisions back to `events.json`), both in the repo's `.claude/commands/`. As noted in "Where things live" above, these do **not** register as `/`-commands in a normal session — read the relevant file from its absolute Desktop path and follow it top to bottom.

**Scope**: 20 distinct event sources + 16 libraries + the Learning Bus PDF = 37 total. Full list with fetch method lives in the commands themselves (kept there so the checklist and the fetch logic don't drift apart) — this doc just states the ground rules:

- **"Fetch, don't snippet"**: a source only counts as checked once its actual live list/calendar page has been fetched and every current/upcoming event read off it. A search snippet is only for *locating* the fetch URL.
- Several sources are JS-rendered or robots-blocked and need specific workarounds (documented in `/run-sweep`) — e.g. Sausalito's Granicus month-grid (`sausalitolibrary.org/kids/library-calendar`, paged via the "Next Month >" link), Mill Valley Library's `site:millvalleylibrary.libcal.com/event` search-around, Marin County Parks via `onetam.org/calendar` (not the JS Trumba widget), CivicEngage town calendars via `calendar.aspx?CID=NN`. Don't fall back to "JS-rendered, no list" as an acceptable result — there's a documented workaround for every source.
- **Akamai/bot-management blocks** (confirmed 2026-07 on both sausalito.gov and sausalitolibrary.org — same underlying Granicus calendar, both 403 any WebFetch/curl request regardless of headers): use the Chrome browser tools (`navigate` + `get_page_text` + `find`) instead of WebFetch — a real rendered browser session passes through fine since this is fingerprint/behavior-based blocking, not a header check. Requires the Claude in Chrome extension to be connected for that session; if it's not connected, report the source as blocked via attestation rather than retrying WebFetch (it will just 403 again).
- **Attestation**: every sweep must show, per source, the URL actually fetched and what was found ("3 candidates: ...", or "none — fetched live list, N items reviewed"). Banned as a result: "recurring already in DB" (that's not a reason to skip — one-off guest performers/specials show up on library calendars constantly), "not reached this pass", "UNVERIFIED — didn't get to it". This exists because of repeated real misses: Sausalito (6 summer guest-performer one-offs missed), Mill Valley Library (recurring-storytime assumption masked new one-offs), San Anselmo (NorCal Bats missed via wrong search surface).
- Review candidates go into a local Excel file (not committed to this repo) with a Decision column — Alexandra fills Approve/Skip and hands it back for `/process-sweep`. Saved to `OAA maintence and content/` in her Documents project folder, following the existing naming convention `daily_sweep_YYYY-MM-DD_review.xlsx`.

## Ad-hoc event requests (outside the Weekly Sweep)

Separate from the recurring Weekly Sweep: Alexandra sometimes hands over a curated batch of specific events to add — from Instagram screenshots, a link, or just plain text ("Marin Moms' hike — Sept 12, 8:30 AM, King Mountain"). This is a different workflow:

- **Research each one before drafting it**: fetch any URL given (same "never assume, always verify" principle as rule 1). For screenshot-sourced events with no link, extract everything decipherable from the image itself — venue, date, time, cost — and flag anything illegible or ambiguous rather than guessing at it.
- **Dedup check**: before treating anything as new, keyword-search `events.json` across `event_name` + `venue` + `organization` + `notes` for plausible matches — not just an exact-name check. A recurring series can already be in the DB under a different phrasing (e.g. "Marin Hiking Moms" vs. "Marin Moms' hike"), and a one-off date can collide with an existing recurring record's computed next-occurrence date. This is the concrete method for existing rule 6, below.
- **When she asks to see them before posting**: draft full bilingual records matching the schema and present them as a list for her Approve/Skip — same shape as a sweep review, just for a handful of events instead of 37 sources. Don't write to `events.json` or push until she confirms, even though this isn't a schema/logic change (the kind of edit rule normally gates on) — the review-first ask itself is what gates it here.

## Napa County Music — separate sweep process

Covers live music in **Calistoga, St. Helena, and Yountville**, surfaced on the webapp via the 🍇 Napa County toggle on the Profile screen. This is entirely separate from the Marin Weekly Sweep above — different sources, different ID range, different cadence. Source of this section: `napa_music_process.md` (Alexandra, originally dated 2026-06-27), integrated here 2026-08-05. The full source tracker lives at `OAA maintence and content/Napa_Live_Music_Tracker_v2.xlsx` (4 tabs: Napa Live Music Tracker, Venues Reference, Weekly Sweep Log, Sources) — read it before making changes, same as `events.json`.

**Schema specifics for Napa events** (on top of the standard schema above):
- `county`: always `"Napa"`.
- `id`: Napa IDs start at 500. As of 2026-08-05, current max is **547** (26 live events: 15 Calistoga, 8 St. Helena, 3 Yountville) — new events increment from **548**. Napa IDs share the same global sequence as Marin events in practice (`next_id()` in `events_io.py` already handles this correctly by taking the max across all events) — don't hand-roll a separate Napa-only counter.
- `type`: always `"Music and Movies"` for Napa music events (not the legacy `"Music"` value).
- `location_group`: must exactly match the town — `"Calistoga"`, `"St. Helena"`, or `"Yountville"`.
- `cadence`: `"One-off"` for dated events, `"Weekly"` for recurring venue nights.
- `event_date`/`expires`: for one-offs, both must be set to the *same* `YYYY-MM-DD` — a range will make the event display on every day in between. For `Weekly` recurring venues, leave both blank.
- `featured`: `true` only for marquee events (park-series openers, major one-offs); default `false`.

**Venues & known recurring series** (as of 2026-06-27 — reverify schedules each sweep, especially "check site"/TBA rows):

*Calistoga* — Pioneer Park "Concerts in the Park" (Thu, Jun 18–Aug 20, 6:30–8:30 PM, free, visitcalistoga.com/concerts-in-the-park); Calistoga Inn & Brewery (Fri/Sat 6–9 PM, May–Oct); Buster's Southern BBQ (Sun 3–6 PM); Cami Art + Wine (Sat/Sun 3–5 PM); Hydro Bar & Grill (Sun 6–9 PM, The Tritones); Lincoln Avenue Brewery/LAB (varies); Pacífico Restaurante Mexicano (Fri steel drums 5:30 PM + DJ 10 PM / Sat acoustic 5:30 PM); Picayune Cellars (Fri 6–8 PM); Sam's Social Club at Indian Springs (Sun 10 AM–1 PM brunch); Fleetwood at Calistoga Motor Lodge (Thu 5–7 PM, May–Oct); Girard Winery (select Saturdays only — confirmed 2026: Jul 25, Aug 29, Sep 26, 12–2 PM).

*St. Helena* — Lyman Park "Summer Concert Series" (Wed, Jun 17–Aug 12, 6–8 PM, free, cityofsthelena.gov/517); The Saint Napa Valley (Tue "Bluesy Tuesday" 3–9 PM / Fri 8–11 PM — **21+ only**); Farmstead at Long Meadow Ranch (Wed 4–7 PM, seasonal Jun–Sep); Merryvale Vineyards (1st & 3rd Fridays, May–Sep, 5–7 PM — **JS-rendered site, will not fetch programmatically; use the Chrome browser tools or call 877-887-7763**).

*Yountville* — Veterans Memorial Park "Music in the Park" (select Sundays, 5–7 PM, free, townofyountville.com/648); Napa Valley Vine Trail Rest Stop "Music Moves You!" (one-off dates via festivalnapavalley.org); Kitchen at Priest Ranch "Thursday Night Live" (select Thursdays, Jul–Sep, 6–9 PM); RO Restaurant & Lounge (Fri 6:30–9:30 PM).

**Excluded — do not add without a fresh confirmation call**: Freemark Abbey Winery (piano music only referenced in old travel guides, not on their current site — 707-302-3717) and Lucy Restaurant & Bar at Bardessono (mentioned in third-party sources only, not confirmed on lucyyountville.com or bardessono.com — 707-204-6030). Re-verify before ever adding either.

**Sweep source checklist** — fetch every sweep, 8 weeks ahead of today, same "fetch don't snippet" and attestation rules as the Marin sweep:

Every sweep: visitcalistoga.com/concerts-in-the-park/, visitcalistoga.com/events-calendar/ (catch-all), cityofsthelena.gov/517/2026-St-Helena-Summer-Concerts-Series, sthelena.com/events/category/st-helena-events/music/ (catch-all), townofyountville.com/648/Music-in-the-Park, thekitchenatpr.com/events/, longmeadowranch.com/farmstead-locals-night/, thesaintnapavalley.com/events, calistogainn.com/restaurant, busterssouthernbbq.com/, hydrogrillnapavalley.com/, lincolnavebrewerycalistoga.com/, pacificomexicanrestaurant.com/, picayunecellars.com/, indianspringscalistoga.com/samssocialclub, fleetwoodcalistoga.com/, girardwinery.com/events/, rorestaurantandlounge.com/, bardessono.com/dining.htm (monitor for a Lucy music announcement — see Excluded above), visitnapavalley.com/blog/post/outdoor-concerts-in-the-napa-valley/ (season overview), napavalleyregister.com/news/community-calendar-napa-valley-events/ (local paper), ronniesawesomelist.com/ronnies-awesome-list. **JS-rendered, needs the Chrome browser tools**: merryvale.com/events/.

Monthly (not every sweep): napavintners.com/events/index.asp, festivalnapavalley.org/calendar/ (filter to admission-free), bandsintown.com/c/calistoga-ca, bandsintown.com/c/yountville-ca, yountville.com/events/special-events/.

**Process**: same shape as the Marin sweep — fetch every source, dedupe against `events.json` (name + venue + date, same as rule 6 above), draft new candidates matching the schema, log the sweep in the Weekly Sweep Log tab of `Napa_Live_Music_Tracker_v2.xlsx`, and present the list to Alexandra for Approve/Skip before touching `events.json` or pushing anything live. Never delete a Napa event without her explicit approval.

## Swim Lesson Directory (second dataset — not events)

A separate reference dataset reachable from the Resources screen. **Not part of `events.json` and not touched by any sweep.**

- **Data**: `swim_vendors.json` (21 Marin swim-lesson providers). Built from `Marin_Swim_Lesson_Vendor_Dashboard_v4.xlsx` (in `OAA maintence and content/`) by the converter `swim_vendors_io.py`.
- **Corrections go in the converter, not the JSON.** `swim_vendors_io.py` holds an `OVERRIDES` dict keyed by vendor slug; a correction added there survives re-running the converter, whereas hand-editing `swim_vendors.json` is silently wiped on the next run. Example: `strawberry-recreation-district` carries `hoursSeason_override`.
- **`towns` (plural) is what the UI reads** for display and filtering — not the raw `town` field. Populate both.
- **UI** (in `index.html`, `#swimScreen`): a table, not cards. There is **no detail/drill-down screen** — a `#swimDetailScreen` existed and was deleted 2026-08-03. If you reintroduce one, note that `showScreen()` once kept a hard reference to it that threw on *every* screen change after deletion.
- Features: sortable + resizable + wrap-text columns, a frozen Vendor Name column, dropdown filters (town / class type / facility type / indoor-outdoor / age), drag-to-reorder columns with a "Default order" reset, and a user-added custom column. Column order and custom columns persist in `localStorage` under the `oaam_swim_*` keys (`oaam_swim_col_order`, `oaam_swim_custom_cols`, `oaam_swim_custom_data`), matching the existing `oaam_*` convention (`oaam_user`, `oaam_lang`, `oaam_county`).
- The page carries a "not mobile friendly, best on a computer" note by design — desktop-first was Alexandra's explicit call.
- **CSS trap worth remembering**: a container with `overflow-x:auto` computes `overflow-y:auto` too, which makes it the containing block for `position:sticky` and silently kills page-level sticky headers. The table's sticky header works because `.swim-table-scroll` is a height-bounded box with `thead` sticky at `top:0` *inside* it.
- `Swim_Dashboard_Integration_Spec.md` describes the original card-based design and is **superseded** — the header says so.

## Open Items tracker (Alexandra's to-do list)

- **Source of truth**: `OAA maintence and content/open_items.md` (her Documents project folder, **not** this repo). Grouped Infrastructure / Data Quality / Marketing, with a "Recently closed" section kept for reference. Edit it directly when she says to add, update, or close an item.
- **"Show me the dashboard" / "open the open items list"** means render it as a formatted page. The generator is a scratchpad script (`build_dashboard.py`) that emits a self-contained HTML file published as an Artifact. Statuses: `open`, `waiting`, `scheduled`, `low`, `hold`.
- **Keep the two in sync in the same edit.** They have drifted before (item 25 stayed open in the dashboard after being closed in the markdown). Closing an item means: remove from the open list in `open_items.md`, add a line to "Recently closed", remove the `dict(n=…)` from `build_dashboard.py`'s `ITEMS`, append to its `CLOSED`, regenerate, and republish the Artifact.
- Items resolved by a **policy decision** should be encoded where the policy actually executes — e.g. item 9 (stale Megan Schoenbohm source) and item 10 (add Slide Ranch) were both written into `/run-sweep`'s source list so they enforce themselves every sweep, not just sit in a tracker.

## Sweep review workbook format

The file handed to Alexandra each sweep (`daily_sweep_YYYY-MM-DD_review.xlsx`, saved to `OAA maintence and content/`, never committed) now carries **three** sheets, in this order:

1. **Weekly Sweep** — one row per new candidate, `Decision` column blank for her Approve/Skip. Flag genuine uncertainty with `⚠ POSSIBLE DUPE` in Notes rather than silently including or dropping it.
2. **Questions** — anything needing her judgement, with columns: `#`, Category, Question, What I Found, My Recommendation, Affects, and a shaded **YOUR ANSWER** column. Added 2026-08-06 at her request; it works well and should be kept. Give a real recommendation in every row, not just the question.
3. **Attestation Log** — one row per source, all 40.

She fills `Decision` and `YOUR ANSWER` and hands it back for `/process-sweep`. Note she may also **append her own rows** to the Weekly Sweep sheet with extra asks (she added two on 2026-08-06 pointing at a Slide Ranch page and asking for a closer re-read of a roundup) — always read past the last candidate row.

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
- **Marin Mommies weekend roundup post is a REQUIRED primary source (corrected 2026-07-23).** Earlier documentation told sweeps to AVOID the "Weekend Family Fun for [dates]" blog-post URLs (over-correcting for a past stale-cache incident) and use only the per-day `/calendar/` pages. This caused real misses: the Jul 24–26 2026 roundup post listed Cricket & the Wren Circus (Sausalito), Lucky Break concert (Corte Madera), a China Camp Junior Ranger Nature Ramble, and an Inflatable Pool Obstacle Course (Novato) — none of which were on the per-day calendar pages or in the DB. The curated roundup contains editorially-selected events the raw calendar never shows. Verify the printed year on the roundup page first (the slug-cache staleness risk is real, so gate on year before trusting it). Never revert to avoiding these pages. **Scope corrected 2026-08-09** — see the two Marin Mommies entries in `/run-sweep`: source #1 is the curated roundup for the **upcoming weekend only** (the posts publish ~2 days ahead, so asking for "every weekend in the window" guaranteed 404s), and source #2 is the per-day calendar for **all 14 days**, mandatory. The two no longer overlap. Also: **Marin Mommies' day-of-week labels are unreliable** — it labelled five Slide Ranch Family Farm Days as Thursday/Friday when all five are Saturdays. Always re-derive the weekday from the date.

---

## State of play — last updated 2026-08-09

Where a new session should pick up.

**Health**: `events.json` is 366 events / max id 832, all committed and pushed (`main` clean as of the last commit). Live site is current. No known user-facing breakage.

**Closed this stretch** (open items 2, 3, 4, 6, 9, 10, 11, 13, 14, 16, 18, 25): the swim directory table redesign; the Napa music process integration + its first sweep; the expired-event purge (730 → 335 records, One-off only, recurring templates preserved); several fabricated/stale event records deleted or corrected.

**Open items still live** — full list in `OAA maintence and content/open_items.md`, 8 open:
- **1** — daily.yml scraper silently broken since May 8 (~110 "successful" runs, zero commits; a swallowed `git stash pop` conflict). Fix is drafted but **not pushed** — her standing rule is to see the diff first.
- **5** — verify two Bolinas + one Inverness library programs (needs phone calls; both branches showed near-zero events again this sweep, so the records may be dead).
- **7** — Novato library reopened Aug 19 but published **zero** children's programming; re-check.
- **8** — Corte Madera library reopens **Sep 3**, no September programs published yet. Re-check after that date. Related: id 8's notes were just cleaned (see rule 9b).
- **12** — **on hold**: Learning Bus has published no schedule since June. Alexandra texted (415) 497-1666 on 2026-08-04 and is awaiting a reply. Nothing to do until she hears back.
- **17, 19–24** — preschool/daycare DB, Rebecca's feedback, marketing items, and **24 (users-table lockdown)**, which is a real security item: the site still talks to Supabase `users` with the public key, so phone numbers and hashed PINs are readable by anyone holding it. Full checklist in `table_lockdown_checklist.md`. Deferred, not started.

**Known-flaky sweep sources** (all failed or partially failed on the 2026-08-06 sweep and will likely recur):
- Mill Valley Community Center — CivicEngage grid returns nothing for the window; needs browser paging.
- Belvedere-Tiburon Library — `/events` renders only ~6 of 25 pages.
- Mill Valley Library libcal — renders empty, unresolved across several sweeps.
- SRPL monthly newsletter PDF — served corrupted/binary; the `/events/` HTML is the reliable surface instead.
- Sausalito city + library need the **Chrome browser** workaround (Akamai). This works reliably — use it, don't retry WebFetch.

**Deliberately declined, do not silently redo**: Alexandra passed on backfilling the Marin Mommies 14-day gap from the 2026-08-06 sweep (Aug 10–19 went uncovered because only 5 out-of-range days were fetched), and on re-paging Belvedere-Tiburon. Both are known and accepted, not oversights to fix unprompted.

**Working rhythm**: she runs the sweep on command, usually Wednesday or Thursday. Ad-hoc event batches arrive between sweeps (Instagram screenshots, links, plain text) — research each, dedup, and present for review before writing. She reviews in Excel and hands it back.
