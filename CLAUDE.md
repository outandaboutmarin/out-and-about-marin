# Out AND About Marin

Bilingual (English/Spanish) family events webapp for Marin County, CA. Shows recurring and one-off events for families with young children — library storytimes, music, outdoor programs, rec events, cultural festivals, etc.

- **Live URL**: outandaboutmarin.com
- **Repo**: github.com/outandaboutmarin/out-and-about-marin (this repo — work directly here, it's the single working copy)
- **Owner**: Alexandra ("Alexandra" or "she/her" below) — full decision authority over tech and content.

This file is the living source of truth for how the app is built and maintained. It replaces a versioned Excel workbook (`daily_process_v1` through `v52`) that used to be re-uploaded to a fresh Claude Chat session every time. **Edit this file in place going forward — don't create versioned copies.** Git history is the version trail.

## Where things live — read this first in a new session

Claude Code sessions for this project run with the working directory set to **`C:\Users\AWalter\Documents\2. Claude-Work\PROJECTS\OAA Marin`** — *not* the repo. This is deliberate and has been the setup since the project moved out of Claude Chat on 2026-07-02. **Don't treat it as misconfiguration and don't propose restarting the session inside the repo folder** (asked and settled 2026-08-12).

| What | Where |
|---|---|
| **The repo** — `index.html`, `events.json`, this file, `scraper.py`, `swim_vendors.json`, `.claude/commands/` | `C:\Users\AWalter\Desktop\out-and-about-marin` — the single local clone. Reach it by **absolute path**. |
| **Working files** — `open_items.md`, sweep review workbooks, the Napa and swim trackers, process docs | `…\PROJECTS\OAA Marin\OAA maintence and content\` — inside the session's working directory. Never committed to the repo. |
| Session transcripts + auto-loaded memory | `C:\Users\AWalter\.claude\projects\C--Users-AWalter-Documents-2--Claude-Work-PROJECTS-OAA-Marin\` |

**Run the duplicate checker at the start of a session, and again after any batch write:**

```
python C:\Users\AWalter\Desktop\out-and-about-marin\check_duplicates.py
```

Exits 0 when clean, 1 when it finds something (so it scripts). `--self-test` verifies its logic still matches `index.html`; `--all` adds the low-signal findings it suppresses by default. Written 2026-08-13 after **five** duplicate pairs were found live in two days — see rule 13 and the script's own header for what each of its four scans catches and which real pair motivated it.

Three consequences of this split. All are normal; none need fixing:

- **This file does not auto-load.** Because the working directory isn't the repo, `CLAUDE.md` is not injected into context at session start. **Read it from the Desktop path as the first action in a new session.** What *does* auto-load is `memory/MEMORY.md` in the path above, which carries a pointer here.
- **`/run-sweep` and `/process-sweep` are not available as slash commands.** They live in the repo's `.claude/commands/` and only register when the repo is the working directory. Every sweep to date has been run by **reading `C:\Users\AWalter\Desktop\out-and-about-marin\.claude\commands\run-sweep.md` as a file and following it** — likewise `process-sweep.md`. That is the established method, not a workaround.
- **`Glob` and `Grep` have failed in at least one session** on this machine (`Executable not found in $PATH`, 2026-08-12). If they error, fall back to PowerShell `Get-ChildItem -Recurse` and `Select-String -LiteralPath` — both work fine. Don't conclude a file is missing on the strength of a failed Glob.

## Tech stack

- **Frontend**: `index.html` — single-page vanilla JS app, no framework, no build step. Hosted on GitHub Pages via custom domain (`CNAME`).
- **Data**: `events.json` — see schema below. This is the single source of truth for event content.
- **Scraper**: `scraper.py` — run daily by GitHub Actions (`.github/workflows/daily.yml`, 6 AM PT). **Despite the name it discovers NO events** — it is a nightly janitor. Four jobs: (1) removes expired one-off events, (2) flips `Seasonal` events between `Active`/`Seasonal - Inactive` based on today vs. `season_start`/`season_end` (see rule 16 — this had *never* worked until 2026-08-13), (3) hash-checks library pages and writes `library_page_hashes.json`, (4) writes `scraper_log.txt` plus `scraper_findings.json`, flagging reopenings coming up and `UNPREDICTABLE` events still missing dates. (Reopenings were printed to the console and nowhere else until 2026-08-15 — never added to `issues`, so they never reached the log either.)
  **Both automated jobs were dead for months and were fixed 2026-08-13.** The workflow reported success ~110 times since May 8 while committing nothing: `actions/checkout` gives a clean tree, so its `git stash`/`pull`/`stash pop` dance only ever held the scraper's own output, and when the pull brought down commits touching `events.json` the pop conflicted, `|| true` swallowed it, and the run still went green. Fixed in `3c98d25` — commit first, then rebase and push, with no `|| true` on the critical path. That commit also added a **liveness check** (the run now fails if `scraper_log.txt` isn't dated today, so a silent Python failure can't look like a quiet day), a non-blocking nightly `check_duplicates.py` scan, and a `concurrency` group because both crons fire at 13:00 UTC on the 1st. First green run purged 48 expired one-offs.
  **`scraper.py` / `daily.yml` logic edits need Alexandra's sign-off — show the diff first.** The hash check (job 3) is **settled noise, resolved 2026-08-15**: it MD5s the whole raw page, so any rotating banner counts. Across two scheduled runs against a *fresh* baseline it flagged **11 of 16** and **13 of 16** pages — the 15-of-16 on its first run back was not a stale-baseline artifact. It stays in `scraper_log.txt` for the weekly sweep to skim, and is **deliberately excluded from notifications**; see "How the scraper reaches you" below.

  **How the scraper reaches you (open item 31, built 2026-08-15).** Two channels, and the split matters:
  - **Failure** → GitHub's own email to the repo owner, confirmed switched on 2026-08-15. Combined with the liveness check, a silent breakage can no longer masquerade as a quiet day. Nothing in our code handles this; don't rebuild it.
  - **Findings** → one **rolling GitHub Issue**, assigned to Alexandra, labelled `scraper-findings`. Created when findings appear, edited *only when they change*, closed automatically when they clear. Three design points that are load-bearing:
    1. **One rolling issue, never one per run.** A fresh issue each morning for the same unchanged finding is ~30 emails a month, gets filtered within a week, and then hides the rare finding that matters.
    2. **Assigned, not merely opened.** GitHub's default notification setting is "Participating and @mentions", which does *not* email you about an issue a bot opened on a repo you only own. Assignment is what makes it arrive. Drop the `--assignee` and the whole feature silently stops working.
    3. **The change signature ignores countdowns.** `write_findings()` gives each finding a `key` separate from its display `text`, stripping `(in N day(s))`. Without that, a reopening counting down 7→6→5 looks like new news every morning — the exact daily-email problem the design exists to prevent.

    What qualifies: reopenings inside 7 days, `UNPREDICTABLE` events still missing one-off dates, and `check_duplicates.py` findings. What doesn't: page-change flags. `scraper_findings.json`, `duplicate_report.txt` and `issue_body.md` are per-run scratch and gitignored.
- **`library_review.py`**: also invoked by `daily.yml` with `--weekly-sweep` / `--monthly-audit` flags on a cron. Its automated fetch/keyword-match logic does **not** produce usable event data (output is things like date="TBD", time="See website") — the real sweep work happens live, via Claude fetching and reading each source's page directly (see "Weekly Sweep" below). Confirmed with Alexandra (2026-07) that this automation should be **left running as-is for now** even though it's largely vestigial — don't touch `daily.yml` or these flags without asking first.
- **Backend**: Supabase (users/events/feedback tables) + Twilio Verify (SMS PIN reset). **Out of scope** for Claude Code work right now — Alexandra will explicitly bring this in scope later if needed. Don't touch Supabase, Edge Functions, or auth code unless asked.

## Git workflow

- Work happens directly in this repo — no more copying files in/out of chat.
- **Routine changes** (adding events from a sweep, fixing a field, flipping a status, updating a reopening date): commit and push directly. Use a short, present-tense commit summary (e.g. "Add 12 events from Jul 2 sweep", matching the existing commit style — see `git log`).
- **Bigger/riskier changes** (schema changes to `events.json`, major `index.html` rewrites or new features, batch deletions, edits to `scraper.py`/`library_review.py`/`daily.yml` logic): stop and confirm with Alexandra before pushing.
- Always check `git status`/`git pull` state before starting work — the Desktop path is and should stay the **only** local clone. A second clone once lived at `…\PROJECTS\OAA Marin\out-and-about-marin\`; its contents were deleted 2026-07 and the leftover empty folder was removed 2026-08-12. **Never clone or copy repo files into the Documents project folder** — that folder is for working files only (see "Where things live"). Two clones with the same name is how edits get made to the wrong copy.

## `events.json` schema

File is a JSON object, **not** a flat array:
```json
{ "last_updated": "YYYY-MM-DD", "events": [ {...}, {...} ] }
```
Always load/save through the pattern in `scraper.py` (`load_existing_events()` / `save_events()` — reuse `events_io.py`, see below) rather than hand-editing JSON text. The file has Spanish-accented characters — always read/write with `encoding="utf-8"` or you'll corrupt them (confirmed failure mode: default Windows `cp1252` encoding mangles é/í/ñ etc.).

As of 2026-08-21: **330 events, max ID 907.** Next new event gets the next ID via `next_id()` (max existing ID + 1) — this is a single global sequence shared by Marin and Napa records, don't hand-roll a per-county counter. (Was 505 events / max 565 on 2026-07-02; 366 on 2026-08-09; 341 after the library audit; 353 after the Aug 13 sweep. The drop to 305 on 2026-08-14 was the **first automated purge in 98 days** — 48 expired one-offs cleared by the newly-repaired `daily.yml`. Expiry is automatic again; it should no longer need purging by hand. See State of play.)

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
| `season_start`, `season_end` | **Seasonal only.** `MM/DD` with slashes — e.g. `"06/01"`. **Never dashes** — `index.html` builds `new Date(s + '/' + year)`, which dashes break. A bare month name (`"May"`, `"October"`) is also valid and resolves to the first day of that month for a start and the last day for an end. **TWO parsers must agree on this field**: `parseSeasonDate()` in `index.html` (~line 3549) and `parse_season_date()` in `scraper.py`. They disagreed silently until 2026-08-13 — see the seasonal note below. Change one, change both. |
| `event_date` | **One-off only.** ISO `YYYY-MM-DD`. |
| `expires` | **One-off only** (Seasonal/recurring leave blank). ISO `YYYY-MM-DD`. Event is removed by the daily scraper once this date passes. **Multi-day festival rule**: when a multi-day event has separate daily entries, set `expires` on ALL entries to the LAST day of the event, not each entry's own date — otherwise earlier days disappear from the app mid-festival. |
| `status` | `Active`, `Inactive`, `Seasonal - Inactive`, `Temp. closed`, or `Temp. paused`. **`Inactive` is how you retire a record without deleting it** — `shouldShowEvent()` returns `'hide'` for it. That only became true 2026-08-13: before, the function had no `Inactive` branch, its catch-all returned `'show'`, and 11 retired records were rendering anyway — one of them marked Inactive on 2026-07-29 and visible for two weeks. Prefer `Inactive` over deletion so the record survives for reference; delete only when the source says an event is CANCELED. **`Seasonal - Inactive` is deliberately NOT hidden by `shouldShowEvent()`** — see the seasonal note below; it is written by `scraper.py` from *today's* date, while season visibility is owned by the week-aware filter in `getFilteredEvents()`. Hiding on the status too would make a not-yet-started season invisible even in its own week. Also `Active`, `Temp. closed`, or `Temp. paused` (`Inactive`/`Seasonal - Inactive` are also written by the scraper for seasonal events). **`Temp. paused`** (added 2026-08-05) is for a venue that still exists but has suspended a recurring program with no announced resume date — it renders an amber "Temporarily Paused" badge and the event stays visible, unlike `Temp. closed`, which can hide the event entirely when a reopening date is >30 days out. First use: id 509 (Buster's Southern BBQ, Napa) after the venue posted that live music was paused. Frontend pieces: `.tag-paused` CSS, `getPausedLabel()`, an `isPaused` branch in `cardHTML()`, and a `shouldShowEvent()` case returning `'badge'`. |
| `featured` | boolean. `true` adds a manual scoring boost in the homepage Featured strip (~120 events currently featured) — see "Homepage Featured strip" below for the full eligibility rules, which as of 2026-08-13 exclude all recurring events (one narrow exception) and evening music concerts. |
| `description`, `description_es` | **both required on every event** |
| `registration` | free text, e.g. `"Not required"` |
| `website` | source URL |
| `notes` | **PUBLIC — renders verbatim in an amber callout box on the event detail screen. Never put maintenance/provenance commentary here; see rule 19, and lint with `check_duplicates.py --notes-lint` before committing.** Free text. Special parsed patterns: nth-weekday rules (e.g. `"2nd and 4th Saturdays of each month"`), reopening dates matched via regex `Reopen(?:ing|s)\s+([A-Z][a-z]+\s+\d{1,2}(?:,\s*\d{4})?)` (e.g. `"Reopens June 11"`) which drives the "Closed · Reopens {date}" badge, the literal word `UNPREDICTABLE` (see Data Quality Rules below), and an `ALERT: <text>` prefix (added 2026-08-05) which renders `<text>` as a **red banner on the event card itself** plus red styling on the detail screen, for schedule-affecting callouts like cancellations or seasonal breaks that need to be visible in the feed without opening the event. Terminate it with ` \| ` if other notes follow; `getAlertNote()` reads up to the first `\|`. **Scope a one-date alert as `ALERT[YYYY-MM-DD]: <text>`** (added 2026-08-15) — see rule 17. |
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
13. **Duplicate records are the recurring failure mode of this dataset. Dedup on a NORMALIZED key, never on exact strings.** `find_event()` matches on name substring + venue + town and **never compares `event_date`**, so a "corrected" one-off that lands on a date another record already covers passes it silently. Four live duplicate pairs were found in a single audit (2026-08-12/13), each rendering the same event twice on the public site:
    - **766/799 and 767/800** — the 2026-08-04 "Music with Arlette" fix retired ids 600/601 (impossible Aug 1/Aug 8 dates) and added 799–801 with the correct Aug 19/26 dates, without noticing 766/767 already held exactly those dates. Doubled for eight days.
    - **768/801** — same program, Aug 29, 2:00 PM, same location, but stored as `"Music with Arlette"` @ `"San Rafael Downtown Library"` vs `"Music with Arlette | Música con Arlette"` @ `"San Rafael Public Library - Downtown"`. **Different name AND different venue string.**
    - **34/627** — Sausalito's 2nd-Saturday storytime under two names, identical day/time/venue/cadence. Doubled on *every* second Saturday.

    - **572/573 vs 74** — the San Rafael Summer Market. id 74 is `Monthly`/2nd Friday and its notes already listed the real dates; 572 and 573 were dated one-offs sitting on two of them, with a wrong time. Both those dates rendered twice.

    **Don't hand-roll these checks — run `python check_duplicates.py`** (repo root). It does all four scans, including the one no string comparison can do: a `One-off` landing on a date a recurring record *computes*. That last scan needs the app's occurrence logic, so the script ports `parseOccurrenceRule` / `parseSkipDates` / `doesEventOccurOnDate` from `index.html` — **if you change that logic, change the port too**, and run `--self-test`, which asserts the two still agree.

    For reference, the keys it uses: exact `(event_name, venue, event_date)` catches 766/799 but sails straight past 768/801; the normalized `(event_date, time, town, name-prefix)` key catches that one; `(day, time, venue, cadence)` **plus a matching occurrence rule** catches 34/627 without flagging legitimate same-slot pairs like San Anselmo's 3rd-Wednesday and last-Wednesday programs. Same-venue/same-date/same-**time** is the shape every real collision had — differing times are almost always two separate programs and are suppressed unless you pass `--all`.

    **When a one-off legitimately replaces a recurring occurrence** (a themed storytime standing in for the regular one), don't delete either — add `skip: YYYY-MM-DD` to the recurring record's notes. `parseSkipDates()` reads it and drops just that date.

    When two records do collide, keep the one with the better content and **merge the other's provenance into it** rather than deleting information: 766/767 had the fuller bilingual descriptions and correct `type`; 799/800 carried the newer verification note; 627 had the continuation confirmation that 34 lacked.
14. **Never trust a fetched page's day-of-week label — always re-derive the weekday from the date.** This was previously documented only for Marin Mommies, but it is not source-specific: on 2026-08-12 WebFetch labelled the same date (Aug 13 2026, a **Thursday**) as "Tuesday" on one library page and "Wednesday" on another. The summarising layer invents weekdays that were never on the page. A wrong `day` value puts a recurring event on the wrong weekday in the feed, and for `Monthly` records feeds `parseOccurrenceRule()` a wrong answer. Compute it: `datetime.date.fromisoformat(d).strftime('%A')`.

15. **A `notes` sentence describing WHEN something happens is documentation, not logic — the app never reads it.** Exactly five things gate whether a recurring record renders on a given date: `cadence`, an ordinal phrase (rule 9), a `skip: YYYY-MM-DD` entry, `season_start`/`season_end`, and `status`. Nothing else. Confirmed 2026-08-13: id 11 (Novato "Stories & Rhyme Wiggle Time") carried the note *"This Tuesday session resumes 2026-09-01"* while being `cadence: Weekly` and `status: Active` — so it rendered on Aug 18 and Aug 25, two weeks before the date its own note claimed, because the sentence is invisible to `doesEventOccurOnDate()`. **Whenever you write "resumes on X" / "returns in the fall" / "last session is Y" into a note, encode it too** — `skip:` for a handful of dates, `season_start`/`season_end` for a run, `status` for an indefinite pause. Otherwise the note reassures the next reader while the site keeps showing the event. This is the mirror image of rule 9a: there, prose is read when you don't want it to be; here, prose is *not* read when you assume it is.

    **The seasonal-handoff pattern needs BOTH halves.** When a program temporarily moves venue and then moves back, two records cover one slot at different times, and each needs its own guard. Novato's storytime ran at Pioneer Park during the branch closure (id 486) then returned to the branch (id 11): correct rendering required `season_end: 08/31` on the temporary record **and** `skip: 2026-08-18` / `skip: 2026-08-25` on the permanent one. Fix only one side and you get a gap (both suppressed) or a double-booking (both firing at the same time on the same day at different venues — which the duplicate checker's venue-keyed scans will NOT catch, since the venues genuinely differ).

16. **Seasonal events have TWO independent mechanisms, and they own different things. Don't collapse them.**
    - **`scraper.py` → the `status` field.** Nightly it compares *today* against `season_start`/`season_end` and writes `Active` or `Seasonal - Inactive`. This is a record-keeping signal about the present moment.
    - **`index.html` → visibility.** `getFilteredEvents()` (~line 3547) compares the season against the **week being viewed**, not today. That is what lets a user page forward into an upcoming season and see what's coming.

    **`shouldShowEvent()` must NOT hide `Seasonal - Inactive`.** Doing so overrides the week-aware filter with a today-based one and makes a not-yet-started season invisible even in its own week. Confirmed 2026-08-13 with id 493 (West End Block Party, season `08/21`–`10/16`): on Aug 13 the scraper correctly marks it `Seasonal - Inactive` because the season hasn't begun, while the week-aware filter correctly shows it in the week of Aug 17–23. Hiding on status would have removed it from the site until Aug 21. `shouldShowEvent()` owns **retirement**; the week-aware filter owns **seasons**.

    **The two date parsers must agree.** Until 2026-08-13 they didn't: `scraper.py` built `date.fromisoformat(f"{year}-{season_start}")`, which for the documented `"06/01"` produces `"2026-06/01"` — invalid ISO. The `ValueError` was swallowed by a bare `except (ValueError, KeyError): pass`, so **every one of the 12 Seasonal records was skipped in silence and no seasonal event had ever been flipped.** It stayed invisible for months precisely because `index.html` parsed the same values correctly, so the site *looked* right. Fixed in `15c3418` by porting the frontend's logic into `parse_season_date()`; unparseable seasons now print a loud named warning instead of vanishing. **If you change season parsing in either file, change it in both, and re-check that a bare month name and a year-wrapping season (`"11/01"`–`"02/28"`) both still work.**

17. **An `ALERT:` about ONE date on a recurring record must be written `ALERT[YYYY-MM-DD]:`, or it shows on every occurrence.**

    `getAlertNote()` matches the `ALERT` marker anywhere in `notes` and returns the text; nothing about the plain form is date-aware. On a `Weekly` record that means the banner renders on **every** occurrence forever. A note reading "No session September 22" therefore sits on every Tuesday from the day it's written, telling families the event is cancelled on dates it is actually running — the opposite of the intended message.

    Found 2026-08-15 immediately after adding exactly such a note to id 6 (Preschool & Family Storytime, Weekly Tuesday, cancelled only on Sep 22 when the bilingual storytime replaces it). Fixed by adding the optional scope marker:

    - `ALERT[2026-09-22]: <text>` — shows **only** on that date.
    - `ALERT: <text>` — shows on **every** occurrence. Correct for genuinely open-ended callouts, e.g. "on break for all of August", and the reason the bare form still works.

    Choose by asking *does this apply to one date or to an ongoing state?* Single date → always bracket it. `cardHTML()` and `openDetail()` each pass the date of the occurrence they're drawing; `localDateStr()` builds it from local calendar fields, deliberately not `toISOString()`, which converts to UTC first and names the following day when the Date carries an evening time.

    Two records already had this defect and were corrected the same day: **id 16** (Labor Day, → `ALERT[2026-09-07]`). Verify a scoped alert after writing it — evaluate `getAlertNote(e, '<date>')` across several occurrence dates and confirm exactly one says SHOWS.

18. **Dedup a sweep candidate by VENUE, never by event name. Run `check_duplicates.py --venue "<venue>"` and read the whole list.**

    **This is not advice, it is the required step.** The 2026-08-20 sweep proposed 37 candidates and **nine were already in `events.json`** — a 24% false-new rate on the sweep's single most important job. Alexandra caught it, not the process.

    Every one of the nine failed the same way: dedup by **event-name substring**. Source pages and stored records name the same program differently, and a substring search sees no match:

    | Proposed from the source | Already stored as | id |
    |---|---|---|
    | Friday **Night** on Main | Friday **Nights** on Main | 459 |
    | Wiggles **and** Wonder Storytime | Wiggles **&** Wonder Storytime | 10 |
    | Corte Madera Farmers Market | Corte Madera **Town Center** Farmers Market | 69 |
    | Fairfax Farmers Market | Fairfax **Community** Farmers Market | 71 |
    | Storytime in the Park **with Riva** | Storytime in the Park **(with Riva)** | 28 |
    | 2nd Saturdays Storytime & Art | 2nd Saturdays **Family** Storytime & Art | 627 |
    | **Marin MOCA** Free Family Day | **MarinMOCA** Free Family Day | 209 |
    | Bookworms Book Club | Bookworms Book Club **by Gordon Korman** | 685 |

    A plural, an ampersand, a parenthesis, two inserted words, a removed space, an author suffix. **Name matching cannot survive any of these, and there is no wording discipline that fixes it** — the library writes the title, not us.

    **Why the existing tools did not catch it — this is the structural gap, and it is worth understanding rather than just obeying:**
    - `events_io.find_event()` is the only candidate-stage check, and its own docstring calls itself a *"loose dedup lookup … name (case-insensitive substring)"*. It is a **substring matcher**. It was never capable of this and should never be the last word.
    - `check_duplicates.py`'s four scans audit `events.json` for duplicates **already inside it**. A candidate that has not been added yet is invisible to all four. Rule 13 and that script protect the file *after* a bad add; they do nothing to prevent one.

    So the correct unit of comparison is the **venue**, not the title. A venue name is short, stable, and doesn't get editorialised. Before proposing anything:

    ```
    python C:\Users\AWalter\Desktop\out-and-about-marin\check_duplicates.py --venue "Marin City Library"
    ```

    It prints **every** record at that venue/town with day, time, cadence and status. Read the whole list and match on **day + time + cadence**, never on the name. That check surfaced all nine misses immediately. It matches on **token overlap, not substring** — because venue words get reordered too ("Town Center Corte Madera" vs the stored "Corte Madera Town Center" share every token and no useful substring, and that reordering hid id 69 even on the first version of this scan).

    The nine ids above are wired into `--self-test` as a **regression suite**. If a future change to the matching stops surfacing any of them, the self-test fails.

    **Three further traps this episode exposed:**
    - **A retired record is still a duplicate.** ids 175/176 read as "new" because they were `Inactive`. `--venue` deliberately lists every status — dedup against the *record*, not against what's currently visible.
    - **Not every collision is a name collision.** "Wednesday Kids' Movie: Encanto" wasn't a near-miss on any title; it was one week's edition of id 46, whose notes say it is a single weekly slot with a rotating theme. **Read the matched record's `notes` before concluding it's a different program.**
    - **Verify the incumbent actually renders before dismissing a candidate.** Checking id 209 (MarinMOCA) confirmed it correctly renders Sep 13 — but the same check on id 208 (Goodie's Kids' Club) found it renders Sep 12 while the real session is Sep 19. A duplicate check is also a free correctness check on the record you're matching against; use it.

19. **`notes` IS PUBLIC. It renders verbatim on the event detail screen. Never write internal commentary into it.**

    Found 2026-08-21, and it is the single largest documentation failure in this file's history. Alexandra was looking at the live site, saw the amber callout box under ABOUT THIS EVENT on id 530, and asked why the public was being shown *"FIXED 2026-08-21. This record previously had day='Varies'… doesEventOccurOnDate() always returned False… NOTE the sweep checklist pointed at lincolnavebrewerycalistoga.com, a dead domain returning HTTP 521…"*. She was right, and the problem was never one record: **`check_duplicates.py --notes-lint` found 109 of 330 records carrying the same class of text.**

    **There is no internal field on an event.** `notes` looks like scratch space and has been used as scratch space by every sweep since ~2026-07, but `index.html` renders it in full inside a styled amber box. Sentences like "CONFIRMED 2026-08-13 against srpubliclibrary.org", "per Alexandra", "duplicate id 673 deleted 2026-07-29", "the audit window was too narrow to see it", "Marin Mommies listed it wrong" have been live on the public site for weeks. Some name Alexandra directly; some disparage a source by name; some expose our internal ids and filenames.

    **What `notes` may contain — nothing else:**
    - the ordinal recurrence phrase the parser needs (rule 9) — "Second Saturday of each month."
    - `ALERT:` / `ALERT[YYYY-MM-DD]:` banners (rule 17)
    - `skip: YYYY-MM-DD` entries
    - `Reopens <date>` / `UNPREDICTABLE` control words
    - short, genuinely public schedule or logistics prose a *parent reading the listing* would want: "Sign up at the children's desk the morning of the event." / "Moves indoors in bad weather." / "Cash or exact change only."

    **Where provenance goes instead: the git commit message.** That is the internal record — it is durable, timestamped, attributed, searchable with `git log -S`, and invisible to the public. Write the *why*, the source URL, the date verified, and the ids touched there, at whatever length is useful. Nothing is lost by keeping it out of `notes`.

    **Before every commit that touches `events.json`:**
    ```
    python check_duplicates.py --notes-lint          # count + ids
    python check_duplicates.py --notes-lint --all    # offending sentences, and what survives
    ```
    It exits non-zero when anything leaks, prints a `LEAK` line per offending sentence with the reason it fired, and a `KEEP` line showing the public remainder. The `KEEP` line is the draft of the corrected note — read it, don't apply it blindly, since the split is sentence-level and occasionally clips a legitimately public clause.

    **Test the phrasing this way:** would you be comfortable if this sentence were read aloud by the venue's owner, or by a parent deciding whether to attend? "Second Saturday of each month" passes. "Time re-confirmed by Alexandra 2026-08-13 — Marin Mommies lists it wrong" does not.

    Related: **open item 36** proposed adding a separate non-rendered `internal_notes` field, which would make this structurally impossible rather than merely against the rules. That is a schema change and needs Alexandra's sign-off. Until it exists, the rule above is the whole defence.

## Homepage Featured strip

The horizontal card row at the top of the homepage (`#featuredWrap` / `#featuredRow`). Selection logic is `selectFeatured()` in `index.html` (~line 3981) — a client-side scoring pass over `allEvents`, not a stored list. `featured: true` on a record does **not** put it in the strip by itself; it only adds a scoring boost (`+10` in `score()`) among records that are otherwise eligible, plus one specific reserved-slot exception (below).

**Eligibility (`elig()`), current rules as of 2026-08-13:**
- Type must be one of `Festival`, `Music and Movies`, `Community Event`, `Kids Programs`, `Library`. `Farmers Market` and anything named "Learning Bus" are always excluded.
- **No recurring events.** Only `cadence: 'One-off'` is eligible — `Weekly`, `Bi-weekly`, `Monthly`, and `Seasonal` are all excluded, with exactly one exception below. This replaced an older, narrower rule that only excluded `Weekly`/`Bi-weekly`/`Daily` **Library** records; that rule is now redundant and was removed since no recurring type qualifies anymore.
  - **The one exception**: a record with `featured: true` **and** `cadence: 'Monthly'` **and** `type: 'Kids Programs'` still qualifies — this is the existing reserved-slot mechanism (up to 2 slots, in `selectFeatured()`'s `pick()`) for marquee recurring storytimes. Confirmed 2026-08-13 by Alexandra to keep working exactly as before; everything else recurring is now out.
- **No evening music concerts.** A record is excluded if `type === 'Music and Movies'` **and** `time_of_day === 'Evening'` **and** the event name does not contain "movie" (case-insensitive). There is no schema field that separates concerts from movie screenings within this type — the name-substring check is the only signal, and it's clean in practice: every movie-night record in the dataset (`Movie Nights at the Mart`, `Movies in the Park: …`, `Dive in Movie Night`, `Outdoor Movie Night — …`) contains "movie", and no concert record does. **Evening movie nights stay eligible** — this rule targets concerts specifically, confirmed with Alexandra 2026-08-13. Non-evening concerts (morning/afternoon) are unaffected either way.

Everything else — the `BOOST`/`DEM` name-keyword lists, the reserved slots for Mill Valley/Sausalito Library one-offs (`isLibHi()`), the per-town cap of 3, the widening date window if fewer than 9 candidates are found — is unchanged.

## Weekly Sweep — the core recurring exercise

Alexandra runs this **on command**, in chat, not on a schedule — she says something like "run the sweep" and it happens in that session. It is the main thing this whole doc exists to support.

**The two command files**: `run-sweep.md` (fetch everything, build a review file) and `process-sweep.md` (apply her Approve/Skip decisions back to `events.json`), both in the repo's `.claude/commands/`. As noted in "Where things live" above, these do **not** register as `/`-commands in a normal session — read the relevant file from its absolute Desktop path and follow it top to bottom.

**Scope**: 25 distinct event sources + 16 libraries + the Learning Bus PDF = 42 total. (Numbering in `/run-sweep` is contiguous 1–42 as of 2026-08-09 — it previously restarted at 24 for the libraries, so "#24" named two different sources.) Full list with fetch method lives in the commands themselves (kept there so the checklist and the fetch logic don't drift apart) — this doc just states the ground rules:

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

*Calistoga* — Pioneer Park "Concerts in the Park" (Thu, Jun 18–Aug 20, 6:30–8:30 PM, free, visitcalistoga.com/concerts-in-the-park); Calistoga Inn & Brewery (Fri/Sat 6–9 PM, May–Oct); Buster's Southern BBQ (Sun 3–6 PM); Cami Art + Wine (Sat/Sun 3–5 PM); Hydro Bar & Grill (Sun 6–9 PM, The Tritones); Lincoln Avenue Brewery / the LAB (Sat “Lincoln Avenue Live!” 7–10 PM; Jam Night 1st & 3rd Thu; acoustic 3rd Fri and last Wed — schedule established 2026-08-21, previously recorded only as “varies”, which left id 530 unrenderable); Pacífico Restaurante Mexicano (Fri steel drums 5:30 PM + DJ 10 PM / Sat acoustic 5:30 PM); Picayune Cellars (Fri 6–8 PM); Sam's Social Club at Indian Springs (Sun 10 AM–1 PM brunch); Fleetwood at Calistoga Motor Lodge (Thu 5–7 PM, May–Oct); Girard Winery (select Saturdays only — confirmed 2026: Jul 25, Aug 29, Sep 26, 12–2 PM); **Calistoga Depot Distillery / "Depot Live"** (1458 Lincoln Ave, 707-963-6925 — Fri 6–9 PM, Sat 6–9 PM, Sun 5–8 PM, no season stated; added 2026-08-12).

*St. Helena* — Lyman Park "Summer Concert Series" (Wed, Jun 17–Aug 12, 6–8 PM, free, cityofsthelena.gov/517); The Saint Napa Valley (Tue "Bluesy Tuesday" 3–9 PM / Fri 8–11 PM — **21+ only**); Farmstead at Long Meadow Ranch (Wed 4–7 PM, seasonal Jun–Sep); Merryvale Vineyards (1st & 3rd Fridays, May–Sep, 5–7 PM — **JS-rendered site, will not fetch programmatically; use the Chrome browser tools or call 877-887-7763**).

*Yountville* — Veterans Memorial Park "Music in the Park" (select Sundays, 5–7 PM, free, townofyountville.com/648); Napa Valley Vine Trail Rest Stop "Music Moves You!" (one-off dates via festivalnapavalley.org); Kitchen at Priest Ranch "Thursday Night Live" (select Thursdays, Jul–Sep, 6–9 PM); RO Restaurant & Lounge (Fri 6:30–9:30 PM).

**Excluded — do not add without a fresh confirmation call**: Freemark Abbey Winery (piano music only referenced in old travel guides, not on their current site — 707-302-3717) and Lucy Restaurant & Bar at Bardessono (mentioned in third-party sources only, not confirmed on lucyyountville.com or bardessono.com — 707-204-6030). Re-verify before ever adding either.

**Sweep source checklist** — fetch every sweep, 8 weeks ahead of today, same "fetch don't snippet" and attestation rules as the Marin sweep:

Every sweep: calistogadepot.com/distillery/events (**Calistoga Depot Distillery / Depot Live** — added 2026-08-12; recurring Fri/Sat 6–9 PM and Sun 5–8 PM are held as two Weekly records, so what this fetch is *for* is the dated performer lineup and any change to the recurring nights or the addition of a season — do not re-add the weekly nights as one-offs), visitcalistoga.com/concerts-in-the-park/, visitcalistoga.com/events-calendar/ (catch-all), cityofsthelena.gov/517/2026-St-Helena-Summer-Concerts-Series, sthelena.com/**events/** (catch-all — **use this URL, not the music-category one**. The checklist previously said `/events/category/st-helena-events/music/`, which simply **redirects to `/events/`**: the category filter does not stick, so that URL was never actually filtering to music. Confirmed 2026-08-21. It is a large list — 255 entries in Aug 2026 — paginated behind a 'Load more' button that adds ~6 at a time, so reaching a date six weeks out takes ~20 clicks in the browser; WebFetch only ever sees the first 6. Worth the effort: on the 2026-08-21 sweep this single source produced 5 of 8 candidates and independently validated Merryvale's 1st/3rd-Friday pattern when merryvale.com itself rendered empty.), townofyountville.com/648/Music-in-the-Park, thekitchenatpr.com/events/, longmeadowranch.com/farmstead-locals-night/, thesaintnapavalley.com/events, calistogainn.com/restaurant, busterssouthernbbq.com/, hydrogrillnapavalley.com/, lincolnavenuebrewery.com/ (**URL corrected 2026-08-21** — the checklist previously said `lincolnavebrewerycalistoga.com`, a DEAD domain returning HTTP 521. That wrong URL made this venue report as “blocked” for two consecutive sweeps. The real site works fine and publishes a full schedule: Saturday “Lincoln Avenue Live!” 7–10 PM, Jam Night 1st/3rd Thursdays, Don Cameron Acoustic 3rd Friday, Mark Shuttleworth Acoustic last Wednesday, plus Trivia Tuesdays), pacificomexicanrestaurant.com/, picayunecellars.com/, indianspringscalistoga.com/samssocialclub, fleetwoodcalistoga.com/, girardwinery.com/events/, rorestaurantandlounge.com/, bardessono.com/dining.htm (monitor for a Lucy music announcement — see Excluded above), visitnapavalley.com/blog/post/outdoor-concerts-in-the-napa-valley/ (season overview), napavalleyregister.com/news/community-calendar-napa-valley-events/ (local paper), ronniesawesomelist.com/ronnies-awesome-list. **JS-rendered, needs the Chrome browser tools**: merryvale.com/events/.

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
3. **Attestation Log** — one row per source, all 42.

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

## State of play — last updated 2026-08-21

Where a new session should pick up.

### What happened 2026-08-20 → 2026-08-21 (two sweeps + a public-data incident)

**Marin Weekly Sweep, window Aug 21 – Oct 4.** All 42 sources fetched. 28 verified-clean candidates added as ids 863–887 (`570b50b`), plus 8 corrections, 5 of which were live-wrong records. Review file: `daily_sweep_2026-08-20_review.xlsx`.

**That sweep initially proposed 9 duplicates** — a 24% false-new rate, which Alexandra caught in review and called unacceptable work product. The cause was structural, not carelessness: `find_event()` is a *substring* matcher and was the only candidate-stage tool, while `check_duplicates.py` only audits records already in the file. Nine real programs were re-proposed under slightly different wording (Friday **Night**/Nights on Main, Wiggles **and**/& Wonder, Corte Madera **Town Center** Farmers, Fairfax **Community** Farmers, Storytime in the Park **(with Riva)**, 2nd Saturdays **Family** Storytime, **Marin MOCA**/MarinMOCA, Bookworms **by Gordon Korman**, and "Encanto", which was one week's edition of id 46's rotating theme). Fixed by **rule 18** and `check_duplicates.py --venue`; those nine ids are now a regression suite inside `--self-test`. **Do not dedup by name.**

**Napa sweep, window Aug 22 – Oct 4.** 24 sources. 16 events added as ids 888–903 (`1d0e200`), 4 corrections, plus Salvia (id 904, `7325b1a`) and the Lincoln Ave monthly series (ids 905–907, `cfeec4c`). Review file: `napa_sweep_2026-08-21_review.xlsx`. Logged in the Weekly Sweep Log tab of `Napa_Live_Music_Tracker_v2.xlsx`.

**⚠ THE INCIDENT — internal notes were public, on 109 records.** Alexandra spotted the amber box on id 530's detail screen and asked why the public was seeing our maintenance log. `notes` renders verbatim; it always has. See **rule 19**, which is now the most important rule in this file for anyone running a sweep. `check_duplicates.py --notes-lint` was added the same day. **109 of 330 records are still leaking and have NOT been cleaned** — cleaning them is a batch edit and needs Alexandra's sign-off (open item 38). Every new record written from here must pass the lint.

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
- **109 records with leaking notes** (open item 38) — needs Alexandra's approval to batch-clean.
- **Oct 4 LMR Jazz Orchestra** at Farmstead — in window, flagged, deliberately not added, awaiting her call.
- **Hydro Bar & Grill (Calistoga)** — genuinely down, HTTP 500, verified. Passed this month; retry next Napa sweep.
- Item 26 (San Anselmo Imagination Park address, 535 vs 541 conflict), item 30 (Sep 1 seasonal flip verification), item 32 (first real scraper findings notification, ~Aug 27 with the Corte Madera reopening).


**Health**: `events.json` is 305 events / max id 850, all committed and pushed. Live site is current — GitHub Pages deploys straight off `main`, so **committing `events.json` IS publishing**; there is no build step and no staging. Verify locally before pushing, not after. **One known user-facing problem**: 39 *non-library* expired one-offs are still rendering (see open item 1 below) — found during the library audit but left alone, since batch deletions need Alexandra's sign-off and they're outside that audit's scope.

**Last sweep: 2026-08-13**, window Aug 14 – Sep 30. All 25 event sources fetched; libraries (26–41) and the Learning Bus skipped at Alexandra's direction, since the 16-branch library audit had just covered them. 22 candidates proposed, 13 approved, 12 added (ids 839–850) — one approval was conditional and turned out to be a duplicate of an existing Seasonal record. Review file: `daily_sweep_2026-08-13_review.xlsx`. **Four standing scope rules came out of it and are now written into `/run-sweep`** (venue drop-ins, Sweetwater filter, stewardship work-parties, Marin Magazine slug reuse) — those questions should not need re-asking.

**COMPLETE — open item 28, the library audit.** All 16 branches read for Aug 13 – Sep 20 across **124 library-hosted records** (not just the 94 typed `Library`), reviewed by Alexandra, and applied. Deliverable was `OAA maintence and content/library_audit_2026-08-13_review.xlsx` (four sheets, including the new **Record Fixes** type); working notes and the per-branch live inventory are in `library_audit_2026-08-12_progress.md`. `/process-sweep` now knows how to read a Record Fixes sheet.

Shipped across `0870cab`, `a018e5e`, `3ee9645`: 21 expired one-offs deleted; **four duplicate pairs removed** (766/799, 767/800, 768/801, 34/627 — every one rendering the same event twice publicly, see rule 13); ids 42/43's conflicting `Reopens` dates fixed (**second occurrence of the rule 9b bug after id 8 — it recurs, check every sweep**); 2 CANCELED events deleted; 9 recurring records retired; Novato's real resume dates applied (Sep 1/Sep 2, not the Aug 19 we'd assumed); organizations normalized 28 → 17 values; 32 Spanish names written.

**A real frontend bug surfaced while verifying**: `shouldShowEvent()` had no `Inactive` branch, so retiring a record did nothing and 11 records rendered that shouldn't have — one of them Inactive since 2026-07-29. Fixed in `3ee9645`; see the `status` row in the schema table.

**Two near-misses worth remembering**, both caught by the guards rather than by reading: an approved "new" candidate (In Harmony) was already held as id 36 — missed at audit time because its `organization` is the performer and its `venue` is a park, so it sat outside a library-scoped record set. And a note written *about* id 36 contained the word "second", which `parseOccurrenceRule()` lifted out of plain prose and turned into `{nths:[2,3]}` — rule 9a, walked into while documenting rule 9a.

**The biggest single finding is methodological**: three "known-flaky" library sources were never flaky — they were being fetched the wrong way, and every past sweep using those routes was under-reporting without any attestation revealing it. All three are now fixed in `/run-sweep` (sources 26, 37, 39, plus the MCFL block). One prescribed instruction was actively harmful and has been deleted — see the Mill Valley note in source 37.

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
- **SOLVED 2026-08-12 — the 10 MCFL branches.** They were never "flaky" so much as fetched the wrong way: the per-branch `/locations/XX/` pages only list the next few days, so any multi-week sweep window using them alone was structurally under-reporting and no attestation would reveal it. Use `marinlibrary.bibliocommons.com/v2/events?startDate=…&endDate=…` paged with `&page=N` — one surface, every branch, and the **only** place CANCELED events are marked. Written up as a shortcut block at the top of `/run-sweep`'s Libraries section. Keep `/locations/XX/` only for a branch's own closure notice.
- **SOLVED 2026-08-13 — Belvedere-Tiburon, Mill Valley, SRPL, Sausalito.** Same story as MCFL: not flaky, just fetched wrong. Belvedere-Tiburon accepts a date range as URL params (`/events?start=&end=`), cutting 25 pages to 7 with plain WebFetch. Mill Valley's libcal renders fully in the **browser** at `…/calendar?…&t=m`. SRPL needs the month-nav URL for anything past the current month. Sausalito's month URL is directly addressable (`/-curm-M/-cury-YYYY`). All four rewritten in `/run-sweep` sources 26, 37, 39, 40.
- **⚠ REMOVED 2026-08-13 — the Mill Valley `site:…libcal.com` search-around.** This was a *prescribed* step in `/run-sweep` and it returned **2023-dated events mixed with current ones**. Do not reinstate it under any circumstance; it is the same stale-content failure class that produced the fabricated Novato movie records.
- **Larkspur is now fully UNREACHABLE** (2026-08-13): `cityoflarkspur.org/185/Library` 301s to `larkspur.ca.gov`, which 404s on both hosts. Reclassified as a manual/phone source. Its 6 records are unverified.

**Deliberately declined, do not silently redo**: Alexandra passed on backfilling the Marin Mommies 14-day gap from the 2026-08-06 sweep (Aug 10–19 went uncovered because only 5 out-of-range days were fetched), and on re-paging Belvedere-Tiburon. Both are known and accepted, not oversights to fix unprompted.

**Working rhythm**: she runs the sweep on command, usually Wednesday or Thursday. Ad-hoc event batches arrive between sweeps (Instagram screenshots, links, plain text) — research each, dedup, and present for review before writing. She reviews in Excel and hands it back.
