# Out AND About Marin

Bilingual (English/Spanish) family events webapp for Marin County, CA. Shows recurring and one-off events for families with young children — library storytimes, music, outdoor programs, rec events, cultural festivals, etc.

- **Live URL**: outandaboutmarin.com
- **Repo**: github.com/outandaboutmarin/out-and-about-marin (this repo — work directly here, it's the single working copy)
- **Owner**: Alexandra ("Alexandra" or "she/her" below) — full decision authority over tech and content.

This file is the living source of truth for how the app is built and maintained. It replaces a versioned Excel workbook (`daily_process_v1` through `v52`) that used to be re-uploaded to a fresh Claude Chat session every time. **Edit this file in place going forward — don't create versioned copies.** Git history is the version trail.

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
- Always check `git status`/`git pull` state before starting work — this repo should stay the only local clone (a second stale clone under a Documents project folder was deleted 2026-07).

## `events.json` schema

File is a JSON object, **not** a flat array:
```json
{ "last_updated": "YYYY-MM-DD", "events": [ {...}, {...} ] }
```
Always load/save through the pattern in `scraper.py` (`load_existing_events()` / `save_events()` — reuse `events_io.py`, see below) rather than hand-editing JSON text. The file has Spanish-accented characters — always read/write with `encoding="utf-8"` or you'll corrupt them (confirmed failure mode: default Windows `cp1252` encoding mangles é/í/ñ etc.).

As of 2026-07-02: 505 events, max ID 565. Next new event gets the next ID (max existing ID + 1).

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
| `status` | `Active` or `Temp. closed` (confirmed current live values — `Inactive`/`Seasonal - Inactive` also used by the scraper for seasonal events). |
| `featured` | boolean. `true` adds a manual scoring boost in the homepage Featured strip (~120 events currently featured). |
| `description`, `description_es` | **both required on every event** |
| `registration` | free text, e.g. `"Not required"` |
| `website` | source URL |
| `notes` | free text. Special parsed patterns: nth-weekday rules (e.g. `"2nd and 4th Saturdays of each month"`), reopening dates matched via regex `Reopen(?:ing|s)\s+([A-Z][a-z]+\s+\d{1,2}(?:,\s*\d{4})?)` (e.g. `"Reopens June 11"`) which drives the "Closed · Reopens {date}" badge, and the literal word `UNPREDICTABLE` (see Data Quality Rules below). |
| `location_group` | **Do not assume the old fixed list from prior docs — it's drifted.** Live values as of 2026-07: `Mill Valley`, `Tiburon/Belvedere`, `San Rafael`, `Novato`, `San Anselmo`, `Larkspur/Greenbrae` (not `Larkspur`), `Corte Madera`, `Fairfax`, `Sausalito/Marin City` (not `Sausalito`), `West Marin`, `Nicasio/San Geronimo`, `Virtual`, plus Napa-area values (`Calistoga`, `St. Helena`, `Yountville` — see Napa note below). When adding a new event, match an existing value exactly — check current values in the file rather than trusting a hardcoded list here, since this has changed before. **Never use `"Marin County"`** — see rule 8 below (removed 2026-07-19; the 8 events that had it were reassigned to their real town's `location_group`). |
| `county` | Only set on the Napa-area events (`"Napa"`). Not documented anywhere in the historical process docs — see Napa note below. Leave blank for Marin events (implicit default). |

**⚠️ Napa scope note**: `events.json` contains events in Calistoga, St. Helena, and Yountville tagged `county: "Napa"`. There is no documented Napa sweep process anywhere in the historical Excel docs — everything below (the 37-source Weekly Sweep) is Marin-only. Until Alexandra says otherwise, treat Napa events as out of scope for the sweep — don't go looking for new Napa events, just don't break the existing ones.

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
9. **`location_group` renames need a `LOCATION_ALIAS_MAP` entry in `index.html`.** Users' saved "My default filters" store raw `location_group` strings — if a value is ever renamed or merged (e.g. `Larkspur`→`Larkspur/Greenbrae`, `Sausalito`/`Marin City`→`Sausalito/Marin City`, `Tiburon`→`Tiburon/Belvedere`), anyone who saved defaults under the old name silently loses that town from both the checkbox display and actual event filtering — no error, just quietly fewer results. `loadDefaultFilters()` (~line 4025) auto-heals this via `LOCATION_ALIAS_MAP`, mapping old value(s) to current ones and persisting the fix back to the user's record on their next visit. **Any time a `location_group` value changes, add an entry to that map in the same commit**, or affected users will silently lose coverage for that town with no visible error.

## Weekly Sweep — the core recurring exercise

Alexandra runs this **on command**, in chat, not on a schedule — she says something like "run the sweep" and it happens in that session. It is the main thing this whole doc exists to support.

**Slash commands**: `/run-sweep` (fetch everything, build a review file) and `/process-sweep` (apply her Approve/Skip decisions back to `events.json`). See `.claude/commands/`.

**Scope**: 20 distinct event sources + 16 libraries + the Learning Bus PDF = 37 total. Full list with fetch method lives in the commands themselves (kept there so the checklist and the fetch logic don't drift apart) — this doc just states the ground rules:

- **"Fetch, don't snippet"**: a source only counts as checked once its actual live list/calendar page has been fetched and every current/upcoming event read off it. A search snippet is only for *locating* the fetch URL.
- Several sources are JS-rendered or robots-blocked and need specific workarounds (documented in `/run-sweep`) — e.g. Sausalito's Granicus month-grid (`sausalitolibrary.org/kids/library-calendar`, paged via the "Next Month >" link), Mill Valley Library's `site:millvalleylibrary.libcal.com/event` search-around, Marin County Parks via `onetam.org/calendar` (not the JS Trumba widget), CivicEngage town calendars via `calendar.aspx?CID=NN`. Don't fall back to "JS-rendered, no list" as an acceptable result — there's a documented workaround for every source.
- **Akamai/bot-management blocks** (confirmed 2026-07 on both sausalito.gov and sausalitolibrary.org — same underlying Granicus calendar, both 403 any WebFetch/curl request regardless of headers): use the Chrome browser tools (`navigate` + `get_page_text` + `find`) instead of WebFetch — a real rendered browser session passes through fine since this is fingerprint/behavior-based blocking, not a header check. Requires the Claude in Chrome extension to be connected for that session; if it's not connected, report the source as blocked via attestation rather than retrying WebFetch (it will just 403 again).
- **Attestation**: every sweep must show, per source, the URL actually fetched and what was found ("3 candidates: ...", or "none — fetched live list, N items reviewed"). Banned as a result: "recurring already in DB" (that's not a reason to skip — one-off guest performers/specials show up on library calendars constantly), "not reached this pass", "UNVERIFIED — didn't get to it". This exists because of repeated real misses: Sausalito (6 summer guest-performer one-offs missed), Mill Valley Library (recurring-storytime assumption masked new one-offs), San Anselmo (NorCal Bats missed via wrong search surface).
- Review candidates go into a local Excel file (not committed to this repo) with a Decision column — Alexandra fills Approve/Skip and hands it back for `/process-sweep`. Saved to `OAA maintence and content/` in her Documents project folder, following the existing naming convention `daily_sweep_YYYY-MM-DD_review.xlsx`.

## Known documentation-drift items (found 2026-07, not yet acted on)

- `location_group` values have drifted from what old docs claimed (see schema table above) — always check live values, don't hardcode a list.
- `type` includes both legacy `Music` and current `Music and Movies` — new entries should use `Music and Movies`.
- Napa-area events exist with no documented sweep process (see Napa note above) — flagged to Alexandra, awaiting direction.
- **Bollywood Beats Dance Party** (Mill Valley Library, `millvalleylibrary.libcal.com/event/16544594`): WebFetch on this page reported additional dates (Jul 2/9/16/23/30) beyond the visible June 25 date, attributed to an "expandable date list." Alexandra checked the page directly and does not see those additional dates. Do not propose any Bollywood Beats date beyond the one already in the DB (id 149, June 25) unless Alexandra can independently confirm a specific new date from the source herself.
- **Marin Mommies weekend roundup post is a REQUIRED primary source (corrected 2026-07-23).** Earlier documentation told sweeps to AVOID the "Weekend Family Fun for [dates]" blog-post URLs (over-correcting for a past stale-cache incident) and use only the per-day `/calendar/` pages. This caused real misses: the Jul 24–26 2026 roundup post listed Cricket & the Wren Circus (Sausalito), Lucky Break concert (Corte Madera), a China Camp Junior Ranger Nature Ramble, and an Inflatable Pool Obstacle Course (Novato) — none of which were on the per-day calendar pages or in the DB. The curated roundup contains editorially-selected events the raw calendar never shows. Fix applied in `/run-sweep` source #1: fetch the weekend roundup for every weekend in the window AND the per-day pages, using both; verify the printed year on each roundup page first (the slug-cache staleness risk is real, so gate on year before trusting it). Never revert to avoiding these pages.
