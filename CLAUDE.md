# Out AND About Marin

Bilingual (English/Spanish) family events webapp for Marin County, CA. Shows recurring and one-off events for families with young children — library storytimes, music, outdoor programs, rec events, cultural festivals, etc.

- **Live URL**: outandaboutmarin.com
- **Repo**: github.com/outandaboutmarin/out-and-about-marin (this repo — work directly here, it's the single working copy)
- **Owner**: Alexandra ("Alexandra" or "she/her" below) — full decision authority over tech and content.

This file is the living source of truth for how the app is built and maintained. It replaces a versioned Excel workbook (`daily_process_v1` through `v52`) that used to be re-uploaded to a fresh Claude Chat session every time. **Edit this file in place going forward — don't create versioned copies.** Git history is the version trail.

## Where things live — read this first in a new session

> **📱 Working directory `/home/user/out-and-about-marin` on Linux = a PHONE / CLOUD session.** The Windows paths
> below do not exist there. Read "Phone / cloud sessions" (directly after this section) and follow it instead.

> **⚠ MOVED 2026-10-10 (Alexandra).** The working files moved from `Documents\2. Claude-Work\PROJECTS\OAA Marin` to
> **`C:\Users\AWalter\Dropbox\01. Out AND About Files`** (same subfolders: `OAA maintence and content`, `OAA marketing`,
> `OAA Sponsorship and Partners`, `Telluride`, plus `Preschool Database`, `Archive\From Downloads`, and the empty `ABOUT ME`,
> `OUTPUTS`, `TEMPLATES`). The repo moved from the Desktop to **`C:\Users\AWalter\Code\out-and-about-marin`**, deliberately
> OUTSIDE Dropbox: Dropbox syncing a `.git` folder risks corruption, and GitHub is the repo's backup. Sessions now start in the
> Dropbox folder. The old folders were renamed `… (MOVED to Dropbox)` / `… (MOVED to Code)` and **deleted by Alexandra on 2026-10-24** (item 71, after a file-by-file check); never
> write to them. Inventory and plan: `OAA maintence and content\Dropbox_move_plan_2026-10-10.md`.

Claude Code sessions for this project run with the working directory set to **`C:\Users\AWalter\Dropbox\01. Out AND About Files`** — *not* the repo. This is deliberate (since 2026-07-02; the folder itself moved to Dropbox 2026-10-10). **Don't treat it as misconfiguration and don't propose restarting the session inside the repo folder** (asked and settled 2026-08-12).

| What | Where |
|---|---|
| **The repo** — `index.html`, `events.json`, this file, `HISTORY.md`, `sources/` (one sweep source list per region), `check_docs.py`, `scraper.py`, `swim_vendors.json` | `C:\Users\AWalter\Code\out-and-about-marin` — the single local clone. Reach it by **absolute path**. |
| **Working files** — `open_items.md`, sweep review workbooks, the Napa tracker, process docs | `…\PROJECTS\OAA Marin\OAA maintence and content\` — inside the session's working directory. Never committed to the repo. |
| **Resources-tab source spreadsheets** — swim directory and Choose your own adventure (since 2026-10-22) | `C:\Users\AWalter\Dropbox\01. Out AND About Files\Resources\`. Never committed to the repo. |
| Session transcripts + auto-loaded memory | `C:\Users\AWalter\.claude\projects\C--Users-AWalter-Dropbox-01--Out-AND-About-Files\` (before 2026-10-10: `C--Users-AWalter-Documents-2--Claude-Work-PROJECTS-OAA-Marin`, where the older transcripts still live) |

**Phone inbox: check it at the start of every desktop session** (added 2026-10-23, Alexandra). Phone/cloud sessions
cannot reach Dropbox, so they leave their to-dos for `open_items.md`, memory and other Dropbox files in
`C:\Users\AWalter\Code\out-and-about-marin\phone_inbox.md`. If its "Pending" list has entries: apply each one (skip any
the target already has; write `open_items.md` the safe way, rule 23), then empty the list, commit
("Apply phone inbox") and push, and tell Alexandra in one line what was applied. She should never have to relay these
herself. Event changes need no inbox entry: they arrive with the pull, and their reasons are in `internal_notes`.

**Run the duplicate checker at the start of a session, and again after any batch write:**

```
python C:\Users\AWalter\Code\out-and-about-marin\check_duplicates.py
```

Exits 0 when clean, 1 when it finds something (so it scripts). `--self-test` verifies its logic still matches `index.html`; `--all` adds the low-signal findings it suppresses by default. Written 2026-08-13 after **five** duplicate pairs were found live in two days — see rule 13 and the script's own header for what each of its **five** scans catches and which real pair motivated it. (Four until 2026-09-03, when SAME-NAME/DATE was added after a live duplicate slipped past the other four; it is stricter again since 2026-09-06, when `_norm()` learned to strip a leading article.)

Three consequences of this split. All are normal; none need fixing:

- **This file does not auto-load.** Because the working directory isn't the repo, `CLAUDE.md` is not injected into context at session start. **Read it from the repo path (`C:\Users\AWalter\Code\out-and-about-marin`) as the first action in a new session.** What *does* auto-load is `memory/MEMORY.md` in the path above, which carries a pointer here.
- **The sweep procedure is a section of this file, not a command file** (merged 2026-10-10 at Alexandra's request: one rulebook for every region). Read "Weekly sweep (one procedure for every region)" and "Processing an approved sweep" below; each region's sources are in `sources/<region>.md`. `.claude/commands/run-sweep.md` and `process-sweep.md` are now two-line pointers here. Dated stories behind the rules live in `HISTORY.md`.
- **`Glob` and `Grep` have failed in at least one session** on this machine (`Executable not found in $PATH`, 2026-08-12). If they error, fall back to PowerShell `Get-ChildItem -Recurse` and `Select-String -LiteralPath` — both work fine. Don't conclude a file is missing on the strength of a failed Glob.

## Phone / cloud sessions (Claude Code on the web) — added 2026-10-17

Alexandra works from her phone (claude.ai or the Claude app, the Code tab) in **cloud sessions**. **You are in one if
the working directory is `/home/user/out-and-about-marin` on Linux.** Everything else in this file applies; this
section says what is different. Alexandra asked for it here so she does not have to explain it at the start of every
phone session.

### Standing instructions for a cloud session (Alexandra, 2026-10-16/17)
- **Get the latest `main` before touching anything**: `git fetch origin main`, then
  `git checkout -B <session branch> origin/main`. The desktop and the nightly bot push to `main` too, and `next_id()`
  hands out a duplicate id from a stale copy.
- **Routine event changes go straight to `main`** once the checks pass: `python3 check_duplicates.py`,
  `--venue "<venue>"` for every new candidate (rule 18), `--notes-lint`, `--bilingual-lint`. Commit, then
  `git push origin HEAD:main`, then `git push origin HEAD:<session branch>` so the session branch matches (otherwise a
  stop-hook warning about "unpushed commits" keeps firing). Cloud sessions are given a `claude/…` branch by default;
  **this standing instruction is the permission to push to `main`.** App changes (`index.html`) still follow the
  normal Git workflow rules: show Alexandra first, and run `bump_build.py`.
- **Dropbox is unreachable.** `open_items.md`, the review workbooks and Claude's memory notes are not here. Do not try
  to update them, and do not hand Alexandra lines to paste: **write them into `phone_inbox.md`** (repo root, "Pending"
  list) and push it with the session's other commits. The desktop applies them (see "Phone inbox", Alexandra
  2026-10-23: she does not want to relay messages between sessions). The open-items dashboard page can be
  READ (Artifact `read`, URL in "Open Items tracker"), but never republish it from a cloud session: the desktop rebuilds
  it from `open_items.md` and would overwrite the edit.
- **Use `python3`**, not `python`.
- **Push in the same session.** After long idle gaps the cloud copy can be reset, and anything committed but not pushed
  is lost (a July 2026 event commit disappeared this way).

### GitHub access
- Through the **Claude GitHub App**, installed 2026-10-16 on the personal account `outandaboutmarin` for **this repo
  only**. Read and write on code, issues, pull requests, actions and workflows; **read-only administration, so a cloud
  session cannot delete branches** (403).
- The fix that made pushing work was **installing the app** (github.com/apps/claude/installations/select_target).
  Reconnecting GitHub under claude.ai → Customize → Connectors did NOT fix it. Symptom before: reading the repo worked,
  every push returned 403 ("Claude doesn't have GitHub access…").
- The desktop pushes with its own git credentials; the app does not affect it.

### Website access (network)
- **For phone sessions, use the "OAA - Full" environment** (created 2026-10-17, full website access). It is picked on
  the phone start screen: tap the cloud chip, choose "OAA - Full", then type the request. A session keeps the
  environment it started with; switching applies only to sessions started afterwards.
- The two cloud environments named **"Default"** are **limited ("trusted") network access**: outside websites return
  EGRESS_BLOCKED / 403 / DNS failure, and WebFetch fails. Do not use them. If a session finds outside sites blocked, it
  was probably started on a "Default"; tell Alexandra to start a new one on "OAA - Full".
- **Without full access, a cloud session cannot do a weekly sweep** ("fetch, don't snippet" cannot be met) and cannot
  check a flyer's web page. Single events from a screenshot or pasted text still work: the screenshot IS the source.
  Say plainly when a link could not be opened, and ask for a screenshot.
- **Even with full access there are no Chrome browser tools** (tier 3) in a cloud session. Sources that need real Chrome
  (Sausalito's calendars) get attested as blocked, naming the tiers tried.
- Headless Chromium IS available (Node `playwright`, run with `NODE_PATH=$(npm root -g)`) for testing `index.html`
  against the local `events.json`, e.g. calling `loadEvents()` then `searchEvents('coffee')`. Serve the repo with
  `python3 -m http.server` and block Supabase/analytics requests so a test never writes to production.

### What belongs on the computer instead
Weekly sweeps (unless the session is on "OAA - Full"; Chrome-only sources always), app changes Alexandra wants to try before
they go live, and anything in Dropbox (open items, workbooks, memory). When a phone session changes events, the next
desktop session must pull first; tell Alexandra which ids changed so she can mention them.

### Usage
Tell Alexandra to close the cloud tab when finished. A session left waiting on a plan-mode approval once produced dozens
of automatic "Continue from where you left off" retries that used up usage while nobody was there.

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
  **New tables need an explicit GRANT (Supabase change effective 2026-10-30, emailed to Alexandra; noted 2026-10-20).** From Oct 30, a table created in the `public` schema is no longer reachable through the Data API (supabase-js, PostgREST, GraphQL) until a `GRANT` is run for it; until then the API returns "permission denied", and Supabase says the error includes the statement to run. **Existing tables (`users`, `activity_log`, feedback, the `ad_metrics` view) keep their current grants and are not affected.** So any feature that adds a table (the Tide Pool Table, open item 33; the sponsored slot, open item 59) must include the GRANT step, run by Alexandra in the SQL Editor, granting only what the browser or Edge Function actually needs (`users` is deliberately locked to the Edge Functions; see open item 24). Check the permission-denied message for the exact statement before writing one by hand.

## Git workflow

- Work happens directly in this repo — no more copying files in/out of chat.
- **Routine changes** (adding events from a sweep, fixing a field, flipping a status, updating a reopening date): commit and push directly. Use a short, present-tense commit summary (e.g. "Add 12 events from Jul 2 sweep", matching the existing commit style — see `git log`).
- **Bigger/riskier changes** (schema changes to `events.json`, major `index.html` rewrites or new features, batch deletions, edits to `scraper.py`/`library_review.py`/`daily.yml` logic): stop and confirm with Alexandra before pushing.
- Always check `git status`/`git pull` state before starting work — the Code path (`C:\Users\AWalter\Code\out-and-about-marin`) is and should stay the **only** local clone. A second clone once lived at `…\PROJECTS\OAA Marin\out-and-about-marin\`; its contents were deleted 2026-07 and the leftover empty folder was removed 2026-08-12. **Never clone or copy repo files into the Dropbox project folder** — that folder is for working files only (see "Where things live"). Two clones with the same name is how edits get made to the wrong copy.

- **⚠ After ANY `index.html` change, run `python bump_build.py` before committing** (added 2026-10-10). It bumps `APP_BUILD` in
  `index.html` and `version.json` together. Open tabs and home-screen apps read `version.json` when they come back to the
  foreground (and every 30 min) and reload once if the build differs, so nobody keeps running old code against new data.
  Why it exists: on 2026-10-10 Colorado events showed in someone's Marin feed because their tab still ran the pre-Telluride
  page, which treats every non-Napa record as Marin, while fetching the new `events.json`. Forget the bump and stale tabs are
  not told to update. `events.json`-only commits need no bump (data is always fetched fresh). A reload keeps the visitor's
  region: `oaam_county` stays in localStorage, and new visitors default to Marin. Alexandra 2026-10-10: always reopen on the
  region the visitor last chose; never switch it because another region was updated.

## `events.json` schema

File is a JSON object, **not** a flat array:
```json
{ "last_updated": "YYYY-MM-DD", "events": [ {...}, {...} ] }
```
Always load/save through the pattern in `scraper.py` (`load_existing_events()` / `save_events()` — reuse `events_io.py`, see below) rather than hand-editing JSON text. The file has Spanish-accented characters — always read/write with `encoding="utf-8"` or you'll corrupt them (confirmed failure mode: default Windows `cp1252` encoding mangles é/í/ñ etc.).

As of 2026-10-16: **640 events, max ID 1666** (5 added; the daily purge removed past one-offs). As of 2026-10-15: **645 events, max ID 1661** (11 added from screenshots; the daily purge removed past one-offs). As of 2026-10-14: **664 events, max ID 1650** (27 added from the Oct 14 sweep, ids 1624–1650). As of 2026-10-09 (evening): **670 events, max ID 1609** (160 Telluride+ records, ids 1450–1609, added that day). Earlier on 2026-10-09: **510 events, max ID 1449.** Next new event gets the next ID via `next_id()` (max existing ID + 1) — this is a single global sequence shared by Marin and Napa records, don't hand-roll a per-county counter. (Was 507 events / max 1436 on 2026-10-08; 464 events / max 1383 on 2026-10-06; 450 events / max 1369 on 2026-10-05; 446 events / max 1354 on 2026-10-04; 466 events / max 1350 on 2026-10-02; 406 events / max 1097 on 2026-09-09; 330 events / max 907 on 2026-08-21; 505 events / max 565 on 2026-07-02; 366 on 2026-08-09; 341 after the library audit; 353 after the Aug 13 sweep. The drop to 305 on 2026-08-14 was the **first automated purge in 98 days** — 48 expired one-offs cleared by the newly-repaired `daily.yml`. Expiry is automatic again; it should no longer need purging by hand. See State of play.)

**Fields on every event** (confirmed against actual `index.html` usage, not just assumed from old docs):

| Field | Notes |
|---|---|
| `id` | integer, unique |
| `organization`, `venue` | text |
| `event_name`, `event_name_es` | **both required on every event** |
| `type` | one of: `Library`, `Kids Programs`, `Community Event`, `Farmers Market`, `Festival`, `Music and Movies`, `Fitness`, `Grown-Ups Only!`. **`Fitness` was missing from this list until 2026-08-28 and that was documentation drift, not an absence** — it has been fully wired in `index.html` all along (filter option with its own green dot, `tag-fitness` styling, the `--fitness-bg`/`--fitness-text` tokens, the Spanish label `Ejercicio`, and a card icon). It simply had ZERO records until Alexandra re-coded the hikes onto it. `Fitness` IS Featured-strip eligible as of 2026-08-28 — but only because `elig()` and `score()` were both updated in the same commit. **When adding a new type, remember it must be added in THREE places, not one**: the filter list, `elig()`, and `score()`'s weight map. Miss `elig()` and the type never reaches the strip; miss `score()` and it reaches the strip with the fall-through weight of 1 and loses every slot to a Community Event's 3 — eligible in theory, invisible in practice. `Fitness` is weighted 3, matching the `Community Event` value the hikes carried before they moved. **`Grown-Ups Only!` was added 2026-08-18 at Alexandra's request and is fully wired in `index.html` — filter dropdown (`{ value: 'Grown-Ups Only!', dot: '#1795A6' }`), `.tag-grownups` styling, `--grownups-bg`/`--grownups-text` tokens, and the Spanish label `¡Solo para Adultos!` in two places. ~~As of 2026-08-21 ZERO records use it~~ — FIRST RECORD ADDED 2026-09-06**: id 1094, a waterfront yoga flow at the DJs by the Bay festival, which Alexandra classed as grown-ups-only. **"Fully wired" above is also too strong, corrected 2026-09-06.** It is wired in the four places listed, but it is absent from BOTH Featured-strip gates: `elig()`'s closing type whitelist (~line 4112, `['Festival','Music and Movies','Community Event','Kids Programs','Library','Fitness']`) does not include it, and `score()`'s weight map omits it so it falls through to 1. **A `Grown-Ups Only!` record can therefore never reach the Featured strip — and that is the RIGHT behaviour, not a bug**, since the strip is family-facing and this type exists precisely to mark listings that are not. Do not "fix" it without asking. Same three-places trap as `Fitness` above, landing the other way up: there the omission was a defect, here it is the intent. Use it for adult-oriented listings (evening music, wine events, adults-only classes) rather than inventing a new type. (`Music` also appears on some older records — `Music and Movies` is the current type, renamed from `Music` in 2026; use `Music and Movies` for new outdoor concert series / movie screening entries.) |
| `day` | full English day name, e.g. `"Monday"`. Multi-day recurring: slash-separated, e.g. `"Tuesday/Thursday"`. |
| `time` | 12-hour format, e.g. `"10:30 AM"` or `"2 PM"`. Parsed client-side with `/(\d+)(?::(\d+))? ?(AM|PM)/i` — unparseable times silently sort last. |
| `time_of_day` | `Morning` / `Afternoon` / `Evening` |
| `town` | town name |
| `address` | full street address |
| `ages` | free text, e.g. `"0-12 months"`, `"All ages"`, `"5-12 yrs"`. **The age filter reads it as a range** (since 2026-10-05, open item 64: `parseAgeRange`/`ageChipsFor` in `index.html`). It understands `X-Y yrs`, `X-Y months`, mixed `6 months - 5 yrs`, `Grades K-2` / `3rd-5th grade` / `Grades K+`, `X+` / `X and up` / `X yrs and older`, `12 and under`, `Birth to age 5`, `Pregnancy to 3 yrs`, `Expecting and new parents`, `School age`, `Tweens`, `Teens`, `Kids`. An event shows under each chip it overlaps by 6+ months: Babies 0-12 mo, Toddlers 1-3, Preschool 3-5, Kids 5-12; an upper age is the END of the range, so `0-5 yrs` is not under Kids. `All ages` / `Families` map to Families only; `Adults`, `21+`, `Not listed` map to none. **Prefer those shapes for new records**; a phrasing it cannot read appears under no age chip. To check one: open index.html headless and call `ageChipsFor("<text>")`. |
| `cost` | free text: `"Free"`, `"Paid"`, `"$10 drop-in"`, etc. |
| `indoor_outdoor` | `Indoor` / `Outdoor` / `Both` — present on every record but **not currently read by `index.html`**. Keep filling it in for consistency/future use, don't skip it. |
| `active_sedentary` | `Active` / `Sedentary` — same status: present on every record, not currently read by the frontend. Keep filling in. |
| `cadence` | one of: `Weekly`, `Bi-weekly`, `Monthly`, `One-off`, `Seasonal` |
| `season_start`, `season_end` | **Seasonal only.** `MM/DD` with slashes — e.g. `"06/01"`. **Never dashes** — `index.html` builds `new Date(s + '/' + year)`, which dashes break. A bare month name (`"May"`, `"October"`) is also valid and resolves to the first day of that month for a start and the last day for an end. **TWO parsers must agree on this field**: `parseSeasonDate()` in `index.html` (~line 3549) and `parse_season_date()` in `scraper.py`. They disagreed silently until 2026-08-13 — see the seasonal note below. Change one, change both. |
| `event_date` | **One-off only.** ISO `YYYY-MM-DD`. |
| `expires` | **One-off only** (Seasonal/recurring leave blank). ISO `YYYY-MM-DD`. Event is removed by the daily scraper once this date passes. **Multi-day festival rule**: when a multi-day event has separate daily entries, set `expires` on ALL entries to the LAST day of the event, not each entry's own date — otherwise earlier days disappear from the app mid-festival. |
| `status` | `Active`, `Inactive`, `Seasonal - Inactive`, `Temp. closed`, or `Temp. paused`. **`Inactive` is how you retire a record without deleting it** — `shouldShowEvent()` returns `'hide'` for it. That only became true 2026-08-13: before, the function had no `Inactive` branch, its catch-all returned `'show'`, and 11 retired records were rendering anyway — one of them marked Inactive on 2026-07-29 and visible for two weeks. Prefer `Inactive` over deletion so the record survives for reference; delete only when the source says an event is CANCELED. **`Seasonal - Inactive` is deliberately NOT hidden by `shouldShowEvent()`** — see the seasonal note below; it is written by `scraper.py` from *today's* date, while season visibility is owned by the week-aware filter in `getFilteredEvents()`. Hiding on the status too would make a not-yet-started season invisible even in its own week. Also `Active`, `Temp. closed`, or `Temp. paused` (`Inactive`/`Seasonal - Inactive` are also written by the scraper for seasonal events). **`Temp. paused`** (added 2026-08-05) is for a venue that still exists but has suspended a recurring program with no announced resume date — it renders an amber "Temporarily Paused" badge and the event stays visible, unlike `Temp. closed`, which can hide the event entirely when a reopening date is >30 days out. First use: id 509 (Buster's Southern BBQ, Napa) after the venue posted that live music was paused. Frontend pieces: `.tag-paused` CSS, `getPausedLabel()`, an `isPaused` branch in `cardHTML()`, and a `shouldShowEvent()` case returning `'badge'`. |
| `featured` | boolean. `true` adds a manual scoring boost in the homepage Featured strip (~120 events currently featured) — see "Homepage Featured strip" below for the full eligibility rules, which as of 2026-08-13 exclude all recurring events (one narrow exception) and evening music concerts. |
| `no_feature` | **Optional, `true` only** (added 2026-10-19, Alexandra, first used on id 1331). Keeps the record out of the homepage Featured strip: `elig()` returns false before any other rule, including `pinned`. The record still shows in the event list, search and its own page. Omit it otherwise. |
| `description`, `description_es` | **both required on every event** |
| `registration` | free text, e.g. `"Not required"` |
| `website` | source URL |
| `notes` | **PUBLIC — renders verbatim in an amber callout box on the event detail screen. Maintenance/provenance commentary goes in `internal_notes` instead (added 2026-08-21); see rule 19, and lint with `check_duplicates.py --notes-lint` before committing.** Free text. Special parsed patterns: nth-weekday rules (e.g. `"2nd and 4th Saturdays of each month"`), reopening dates matched via regex `Reopen(?:ing|s)\s+([A-Z][a-z]+\s+\d{1,2}(?:,\s*\d{4})?)` (e.g. `"Reopens June 11"`) which drives the "Closed · Reopens {date}" badge, ~~the literal word `UNPREDICTABLE`~~ — **wrong, corrected 2026-08-21: that string appears NOWHERE in `index.html`.** What actually returns `{unpredictable:true}` is the words **`check` and `calendar` both present with no ordinal** (`index.html` ~3388). Writing UNPREDICTABLE in a note does nothing; writing "check the calendar" hides the record from the feed, and an `ALERT: <text>` prefix (added 2026-08-05) which renders `<text>` as a **red banner on the event card itself** plus red styling on the detail screen, for schedule-affecting callouts like cancellations or seasonal breaks that need to be visible in the feed without opening the event. Terminate it with ` \| ` if other notes follow; `getAlertNote()` reads up to the first `\|`. **Scope a one-date alert as `ALERT[YYYY-MM-DD]: <text>`** (added 2026-08-15) — see rule 17. |
| `internal_notes` | **INTERNAL — never rendered, never parsed.** Added 2026-08-21 as the structural fix for rule 19. Maintenance log, provenance, sourcing, corrections, open-item references, reasoning about the record — all of it belongs here. `index.html` reads only the fields it names, so this one is invisible to the public by construction rather than by discipline. Optional; omit it rather than writing an empty string. **The one hazard**: the five control patterns `notes` carries (nth-weekday rule, `skip:`, `Reopens`, `ALERT:`, `UNPREDICTABLE`) are inert in here. Moving one out of `notes` silently disables it — `check_duplicates.py --notes-lint` scans for exactly that and reports it as STRANDED. Explaining a control in `internal_notes` is fine and expected; *storing* it there is not. |
| `partner` | **Optional, `true` only** (added 2026-09-28, open item 59). Marks a paying partner's own event: PARTNER pill above the title on the list card (reuses `.featured-badge`) and a white pill beside the type badge on the event page; Spanish “Colaborador”. **It also adds the paid-listing disclosure at the foot of the event page** (“Sponsored listing. Out AND About Marin is paid to feature this local business.”, added 2026-09-28), so set it only for a vendor who pays. Omit it for everyone else. **`website` rule (Alexandra, 2026-10-01):** an event's Visit website normally goes straight to that event's own booking/registration page; the ONLY exception is a paying sponsor's own events, which link to the sponsor's events page (The Social Klub: thesocialklub.com/events-and-activities, plus "Hosted by The Social Klub." at the end of the description — see run-sweep source #46). It does NOT put the event in Featured; the sponsored slot is not built. |
| `contact` | **Optional object** (2026-09-28): `{name, phone, email, instagram, form_url}`, any subset. PUBLIC: renders under About as “Questions? Contact <name>” (when there is a phone or email) or “Questions? Message <name>”, then the links separated by ·. `name` falls back to `organization`. Instagram takes a handle or URL. Built with textContent, so no markup gets through. |
| `socials` | **Optional object** (2026-09-28): `{instagram, facebook}`. PUBLIC: a “Follow <organization>” row of buttons under Save/Calendar/Share. Instagram: handle or URL; Facebook: page slug or full URL. |
| `logo` | **Optional, partner records only** (added 2026-10-09, FIT4MOM at Hannah Austin's request): path to a wordmark image (e.g. `assets/ads/fit4mom_marin_logo.png`) shown in a white panel at the top of the event card when `partner: true`. Ignored on non-partner records. |
| `location_group` | **Do not assume the old fixed list from prior docs — it's drifted.** Live values as of **2026-10-06** (regrouped that day at Alexandra's request): `Mill Valley`, `Tiburon/Belvedere`, `San Rafael`, `Novato`, **`San Anselmo/Ross`** (towns San Anselmo and Ross), **`Larkspur/Greenbrae/Kentfield`** (towns Larkspur, Greenbrae, Kentfield), **`Corte Madera`** (stands alone), **`Fairfax`**, `Sausalito/Marin City` (not `Sausalito`), `West Marin`, `Nicasio/San Geronimo`, `Virtual`. **Retired 2026-10-06, never reuse:** `Ross Valley`, `Larkspur/Corte Madera`, `Larkspur/Greenbrae`, `San Anselmo` (all mapped in `LOCATION_ALIAS_MAP`). Rule of thumb: the group follows the record's `town`; one town, one group. The Location menu is built from the data (non-Inactive records only), so a stray value on any live record shows up in the menu, plus Napa-area values (`Calistoga`, `St. Helena`, `Yountville` — see Napa note below). When adding a new event, match an existing value exactly — check current values in the file rather than trusting a hardcoded list here, since this has changed before. **Never use `"Marin County"`** — see rule 8 below (removed 2026-07-19; the 8 events that had it were reassigned to their real town's `location_group`). |
| `county` | **The region key, not literally a county.** `"Napa"` for the three Napa towns, **`"Telluride+"`** for the Telluride region (added 2026-10-09; it spans San Miguel, Ouray, Montrose and Montezuma counties, hence the `+`, Alexandra's wording), blank for Marin (implicit default). `regionOf(e)` in `index.html` maps it to `marin` / `napa` / `telluride`. **Every region-aware check must go through `regionOf()`**, never `e.county !== 'Napa'`, which would count Telluride as Marin. See the Napa and Telluride+ sections. |

**Sponsored Featured ads live in `ads.json`, NOT in `events.json`** (added 2026-09-30, open item 59). An ad is a business, not an event, so keeping it out of `events.json` means it can never appear in a day list, search, saved hearts, `check_duplicates.py` or the scraper. `index.html` fetches `ads.json` in `loadAds()`; each entry with `active: true` and today inside `start`..`end` (YYYY-MM-DD, `end` = last day shown, either may be blank) takes one of the nine Featured slots (`withAds()`, at most `MAX_FEAT_ADS` = 9 ads since 2026-10-22; it was a fixed 2, which silently hid a third sponsor), rotates with the others, and opens `openAd(id)`, a separate `#adScreen`. Fields: `id` (used in the share link `?ad=<id>`), `name`, `logo` (path under `assets/ads/`), `color` / `color_ink` (tile border and kicker), `tile_meta`, `town`, `badge`, `subtitle`, `venue`, `address`, `address_note`, `phone`, `hours[]` ({days, time}), `hours_note`, `about`, `note`, `offers_label`, `offers[]` ({title, sub, code}), `offers_how`, `tags[]` ({text, class}), `website`, `website_label`, `instagram`, `internal_notes`. **Optional fields added 2026-10-09 for FIT4MOM** (all backward-compatible; the Social Klub ad uses none of them): `tile_icon` (a separate square image for the Featured tile when `logo` is a wordmark), `logo_wide: true` (wordmark sizing, 210px wide), `hours_label` (heading for the hours table, e.g. "Where & when"), **`address` may be blank** for a business with no single location (then no Where section and no Directions button; put the places in `hours[].time`), `contact` ({name, phone, email} → "Questions? Contact …" under About), offers **without a `code`** (no code row or Copy button), `cta` ({url, label} → the primary button, with Visit website demoted beside it) and `facebook` (page slug → a Follow button). Text fields are `{en, es}` pairs and are PUBLIC (since 2026-10-24 a blank line, `\n\n`, in `about` starts a new paragraph on the ad page: `#adBody .description-text` is `white-space: pre-line`); `internal_notes` is never rendered. **Codes are the sponsor's to create; never publish one Alexandra has not confirmed is live.** Taps log `ad_click` and Copy buttons log `ad_code_copy` to `activity_log` (with the ad id in `event_name`). **`activity_log` only accepts action types on a fixed list** (constraint `activity_log_action_type_check`); a value not on it is refused SILENTLY (the browser only `console.warn`s). The two ad types were added 2026-09-30 by Alexandra in the SQL Editor, after three test taps logged nothing. **Any new `logActivity('<type>')` needs its type added to that constraint first**: read the list, drop the constraint, re-add it with the new value (the DO block used that day rebuilds it from the current definition plus the new values). Read the metrics in Supabase: **Table Editor → `ad_metrics`**, a view Alexandra created 2026-09-30 (`security_invoker = true`, and `select` revoked from `anon`/`authenticated`, so the public key cannot read it; times shown in Pacific). The same two events also go to **GA4** as `ad_click` {ad_id, ad_name} and `ad_code_copy` {ad_id, promo_code} (no PII). Take an ad down by setting `active` to false or an `end` date.

**Telluride+ scope note** (added 2026-10-09): the third region. Records carry `county: "Telluride+"` and show only when the Profile **Region** toggle is on ⛰️ Telluride. Location groups: `Telluride`, `Mountain Village`, `Norwood`, `Ridgway`, `Ouray`, **`Montrose/Olathe`**, `West End` (Naturita, Nucla, Paradox), `Dolores`, plus `Virtual` for online talks. **All Telluride times are Mountain Time**; the week bar shows "· MT" in that view, and the `time` field stays plain ("10:30 AM"). Full process in the "Telluride+ region" section.

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

    **Don't hand-roll these checks — run `python check_duplicates.py`** (repo root). It does all **five** scans, including the one no string comparison can do: a `One-off` landing on a date a recurring record *computes*. That last scan needs the app's occurrence logic, so the script ports `parseOccurrenceRule` / `parseSkipDates` / `doesEventOccurOnDate` from `index.html` — **if you change that logic, change the port too**, and run `--self-test`, which asserts the two still agree.

    For reference, the keys it uses: exact `(event_name, venue, event_date)` catches 766/799 but sails straight past 768/801; the normalized `(event_date, time, town, name-prefix)` key catches that one; `(day, time, venue, cadence)` **plus a matching occurrence rule** catches 34/627 without flagging legitimate same-slot pairs like San Anselmo's 3rd-Wednesday and last-Wednesday programs. Same-venue/same-date/same-**time** is the shape every real collision had — differing times are almost always two separate programs and are suppressed unless you pass `--all`.

    **The scans only audit what can RENDER — retired records are skipped (changed 2026-09-07,
    open item 45).** `scan()` drops any record whose `status` is `Inactive` or
    `Seasonal - Inactive` from **both** its one-off and recurring lists, via one `_renders()`
    predicate. The audit exists to find events that double-book **on the live site**, and
    `shouldShowEvent()` hides those two statuses outright, so a retired record cannot double-book
    anything; counting it produces a finding no reader could ever have seen.

    **The history matters, because the trap it created is easy to re-create.** The filter had been
    on the `recurring` list since the file was written on 2026-08-13, and **never on `one_offs`**.
    Retire a dated one-off that a recurring record has superseded and it stayed a **permanent
    COLLISION finding** — it still lands on a date the recurring record generates, forever.
    `check_duplicates` then exits non-zero every night and feeds a standing `duplicates:present`
    flag to the daily notifier: precisely the cry-wolf failure that notifier exists to avoid. On
    2026-09-01 six records did this and the workaround was to **delete** them rather than retire
    them, losing the reference copies. **The tool was pushing us toward the worse of the two
    options** — which is the real reason this was worth fixing, more than the tidier report.
    Prefer `Inactive` over deletion for a superseded record; the scans will now stay quiet.

    **`Temp. closed` and `Temp. paused` are NOT retired.** Both still render, with a badge, so both
    still take part in every scan. A self-test asserts it.

    **What this deliberately does not touch: `--venue` / `venue_scan()` still lists every record
    whatever its status**, because rule 18 asks a different question — *"is this candidate already
    on file anywhere?"* — for which a retired record absolutely still counts. That is a separate
    function and a self-test pins it. `--all` also still shows everything. **Nothing protecting
    against ADDING a duplicate was weakened here**; only the render-time audit was scoped to what
    can actually render.

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

    ⚠ **A YEAR-WRAPPING SEASON DOES NOT ACTUALLY RENDER — found 2026-09-15, and the sentence above oversold it.** `parseSeasonDate()` resolves BOTH dates into the year of the week being viewed (`new Date(s + '/' + weekStart.getFullYear())`), so `"10/02"`–`"03/26"` becomes start Oct 2 / end Mar 26 **of the same year**, and the hide test `weekEnd < start || weekStart > end` is true for every week there is: the record is invisible all year, silently. The scraper's parser handles the wrap fine, which is exactly why this hides — `status` keeps flipping correctly while nothing renders. **Until the frontend is fixed, split a run that crosses the new year into two records** — `MM/DD`–`12/31` and `01/01`–`MM/DD` — cross-referenced in `internal_notes`; ids 1156 and 1158 (Fairfax Pavilion Play Group, Oct 2 2026 – Mar 26 2027) are the worked example. Check for the fault with: `season_start > season_end` as strings.

17. **An `ALERT:` about ONE date on a recurring record must be written `ALERT[YYYY-MM-DD]:`, or it shows on every occurrence.**

    `getAlertNote()` matches the `ALERT` marker anywhere in `notes` and returns the text; nothing about the plain form is date-aware. On a `Weekly` record that means the banner renders on **every** occurrence forever. A note reading "No session September 22" therefore sits on every Tuesday from the day it's written, telling families the event is cancelled on dates it is actually running — the opposite of the intended message.

    Found 2026-08-15 immediately after adding exactly such a note to id 6 (Preschool & Family Storytime, Weekly Tuesday, cancelled only on Sep 22 when the bilingual storytime replaces it). Fixed by adding the optional scope marker:

    - `ALERT[2026-09-22]: <text>` — shows **only** on that date.
    - Several dated alerts may sit on one record, separated by ` | ` (added 2026-10-08, id 24); `getAlertNote()` returns the one for the date being drawn.
    - `ALERT: <text>` — shows on **every** occurrence. Correct for genuinely open-ended callouts, e.g. "on break for all of August", and the reason the bare form still works.

    Choose by asking *does this apply to one date or to an ongoing state?* Single date → always bracket it. `cardHTML()` and `openDetail()` each pass the date of the occurrence they're drawing; `localDateStr()` builds it from local calendar fields, deliberately not `toISOString()`, which converts to UTC first and names the following day when the Date carries an evening time.

    Two records already had this defect and were corrected the same day: **id 16** (Labor Day, → `ALERT[2026-09-07]`). Verify a scoped alert after writing it — evaluate `getAlertNote(e, '<date>')` across several occurrence dates and confirm exactly one says SHOWS.

20. **`description_es` is public too, and an error only Spanish readers see stays hidden longest. Lint with `check_duplicates.py --bilingual-lint`.**

    Added 2026-09-03 after id 41 was found publishing **the wrong branch** to Spanish readers. Its venue had been corrected from South Novato to Corte Madera at some point; `description_es` still read *"en South Novato"*, so Spanish-speaking families were being sent to a different library in a different town. The English description named no town at all, so the two languages did not even agree with each other. It had been live for an unknown length of time.

    **Nothing could have caught it.** Every existing check compares a field to a field. This was *prose contradicting a field*, in one language only — and it survived precisely because nobody had reason to read the Spanish. The same record also carried "the 2nd, 4th, and 5th Wednesdays" in **both** descriptions while its `day` was Thursday.

    The lint reports four things: a `description_es` that is empty, or identical to the English; a **town named in exactly one language that no field on the record places it in**; and **prose naming weekdays when none of them is the record's own `day`**.

    **Both halves of the town rule are load-bearing, and the noisier versions were tried first.** "Flag any town in prose the record does not claim" gives 22 findings, nearly all legitimate — beneficiaries (*"proceeds to Muir Beach Volunteer Fire"*), donation drop-offs, second venues. "Flag any town the Spanish names that the English does not" gives 38, because naming the town in Spanish is simply this dataset's house style. Either would have been a cry-wolf tool, the failure closed item 31 was about. The conjunction scores **0 on live data** while still catching id 41. Likewise the weekday rule fires only when *no* named day matches: naming an extra day is normal ("Saturday and Sunday", a Friday-to-Saturday campout).

    **Do not "fix" a finding by editing the prose to match a wrong field** — check which one is actually right first. On id 41 the prose was wrong; on another record it may be the field.

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
    - `check_duplicates.py`'s five scans audit `events.json` for duplicates **already inside it**. A candidate that has not been added yet is invisible to all five. Rule 13 and that script protect the file *after* a bad add; they do nothing to prevent one.

    So the correct unit of comparison is the **venue**, not the title. A venue name is short, stable, and doesn't get editorialised. Before proposing anything:

    ```
    python C:\Users\AWalter\Code\out-and-about-marin\check_duplicates.py --venue "Marin City Library"
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

    **Where provenance goes instead: `internal_notes` on the record** (added 2026-08-21 — see the schema table). It is never rendered and never parsed, so it holds the maintenance log where it is most useful: attached to the record it describes. Write the *why*, the source URL, the date verified, and the ids touched there, at whatever length is useful. The git commit message remains the right place for cross-record reasoning about a batch.

    **Before every commit that touches `events.json`:**
    ```
    python check_duplicates.py --notes-lint          # count + ids
    python check_duplicates.py --notes-lint --all    # offending sentences, and what survives
    ```
    It exits non-zero when anything leaks, prints a `LEAK` line per offending sentence with the reason it fired, and a `KEEP` line showing the public remainder. The `KEEP` line is the draft of the corrected note — read it, don't apply it blindly, since the split is sentence-level and occasionally clips a legitimately public clause.

    **Test the phrasing this way:** would you be comfortable if this sentence were read aloud by the venue's owner, or by a parent deciding whether to attend? "Second Saturday of each month" passes. "Time re-confirmed by Alexandra 2026-08-13 — Marin Mommies lists it wrong" does not.

    **The migration — done 2026-08-21, at Alexandra's direction.** All 109 records were split: public text stayed in `notes`, commentary moved to `internal_notes`. Nothing was deleted. 71 split cleanly on the lint's own sentence boundaries, 31 had notes that were entirely internal and now carry no public note at all, and **7 needed hand-splitting** because a control pattern and a comment shared one sentence (ids 12, 25, 177, 208, 255, 859, 904).

    **The migration was verified by diffing what the site DERIVES from `notes`, not by reading the diff.** For all 330 records, before and after: the occurrence dates over a 365-day horizon, the parsed rule, the skip set, the `Reopens` date, the `ALERT` text, and the `UNPREDICTABLE` flag. **Rendered dates: identical, 6,786 before and after.** Five records' parsed *rule* changed (674, 675, 771, 773, 904) — all phantom rules that ordinal words in internal prose had produced by accident, on four One-off records (routed by `event_date` at every public call site) and one Weekly record (short-circuits before `parseOccurrenceRule()`). None was ever consulted. Rule 9a in reverse: the prose was creating rules nobody wanted.

    **WAVE 2, the same day — the first migration missed 49 more records, and Alexandra found one of them on the live site again.** She opened id 16 (Cuentos con Ritmo) and saw *"Venue label normalized 2026-07-29 (was 'Old Mill Park Amphitheater') to match the ~20 other Mill Valley records..."* still in the amber box, hours after the lint had reported itself clean. Two causes, both now fixed and both with regression tests:

    1. **The structural one, and the more serious.** `_KEEP` was tested **before** `_INTERNAL` and `continue`d, so any commentary fused into a sentence that also carried a control pattern — a `skip:`, an `ALERT:`, an ordinal, `Reopens` — **was never evaluated for leaks at all**. Thirteen records hid entirely behind that, including id 26, which published *"parseOccurrenceRule() returned null and the event rendered NOWHERE"* to the public because the sentence also contained the word UNPREDICTABLE. The lint now evaluates both and marks such a sentence **MIXED**: it stays in `notes` (the control is load-bearing) and is reported for a hand split.
    2. **Vocabulary.** "normalized", "converted", "approved", "reopened", "cost string shortened", "per libcal", "WebFetch", "the DB", and editorial instructions with no date at all (*"Retired rather than deleted: set status back to Active if it returns"*) all passed as public prose. Marker list widened; each shape now has a test.

    Wave 2 migrated 49 records, 19 of them hand-split. **Exactly one record's rendered dates changed — id 127, and it was a live bug.** "so the last actual Sunday is Sep 27" sat in its notes as ordinary prose, and `/\blast\b/` is tested first and short-circuits everything, so Saddle Up Sundays had been rendering **only the final Sunday of each month instead of every Sunday** — 12 dates where the source says 52. Rule 9a again, and the third time it has bitten in a week.

    **Two records were caught making past-tense claims about dates that have not happened.** id 8 and id 42 both carried *"Reopened 2026-09-03 as scheduled; confirmed..."* written on 2026-08-21. Both are flagged in `internal_notes` and left unverified rather than trusted; see open item 8.

    **Re-run that diff before any future batch edit to `notes`.** Reading a 109-record text diff cannot tell you whether a date moved; only expanding the occurrences can.

    Two things worth knowing about the field:
    - **A control pattern in `internal_notes` is a control that no longer fires.** The lint's second scan reports these as STRANDED. It flags only *lost* controls — one absent from `notes` and actually consulted for that cadence — because internal commentary quotes source text constantly, and a scan that cries wolf gets ignored.
    - **`--notes-lint` shipped 2026-08-21 with two dead regexes** — a literal backspace byte sat where the `\b` word boundaries belonged, so the `Reopens` and `UNPREDICTABLE` checks could never match anything. It ran, printed clean, and proved nothing. Fixed the same day and each pattern now has a self-test that asserts it can fire. This is the same lesson as the COLLISION time-string bug: **if a scan reports clean, confirm it is capable of reporting dirty.**

21. **Correcting `time` is not the whole job — `description` usually repeats the hours in prose,
    and nothing checks that the two agree.** Confirmed 2026-09-06 on id 871 (Show Your School
    Spirit, Corte Madera). Its `time` had been corrected on 2026-08-27 from `11:00 AM` to
    `12:00 PM – 3:00 PM` against the venue's own page — and both `description` and
    `description_es` were left reading *"11 AM-3 PM"*. The record sat that way for ten days,
    publicly, telling a reader to arrive an hour before the event started. **No scan catches
    this.** The five duplicate scans, `--notes-lint` and `--bilingual-lint` all passed on that
    record every single day, because none of them compares a time field with the prose around it.
    It was caught by eye.

    **So: whenever you change `time`, grep that record's `description`, `description_es` and
    `notes` for the old hours and fix every copy.** The same applies in reverse — a description
    that states hours is a claim about the same fact as `time`, and the two must never disagree.
    A cheap lint for this (find a time-like string in `description` and compare it to `time`)
    does not exist yet and would be worth writing.

22. **`cost: "Free"` must mean free to a family who walks up on the day. A waived admission fee
    is not the same thing as a free outing.** Confirmed 2026-09-06 on id 961 (Free Day at Muir
    Woods, Constitution Day). The record read `Free` and it was wrong in the way that costs a
    family money: the fee-free day waives the **$15 per-adult entrance fee only**. NPS states
    plainly that *"Parking/shuttle reservation fees are separate from entrance fees and are
    required for all vehicles and shuttle riders"*, and `gomuirwoods.com` prices them at **$10 per
    standard vehicle** or **$4 per adult round trip** on the shuttle. You cannot get in without
    one. A family reading `Free` would have driven up Highway 1 expecting to pay nothing.

    The field now reads `Free entry; $10 parking or $4 shuttle`, which means `index.html` tags it
    with `.tag-paid` and it drops out of the free filter — **that is the correct outcome, not a
    regression.** `cardHTML()` branches on `e.cost === 'Free'` exactly, so any string but that
    literal renders as paid.

    **This will recur.** Any venue that charges separately for admission and for parking, entry
    and booking, or the event and a required reservation, has the same shape: a national or state
    park on a fee-free day, a museum with a free-admission day but paid timed entry, a festival
    that is free to enter with a paid parking lot. **Ask what the family actually pays to be
    standing there**, and put that in `cost` — not the headline the venue is advertising.

23. **NEVER write in place. Write a temp file, verify it reads back, then replace — and copy the
    original aside first.** Opening a file for writing **truncates it instantly**, before a single
    byte of new content lands. If anything then fails, the old content is already gone and the new
    content never arrived.

    **This destroyed `open_items.md` on 2026-09-07.** A script read the file, built the new text in
    memory, opened the real file for writing, and died on the write with a `UnicodeEncodeError`:
    an emoji had been written as the escape `\ud83d\uddc2`, which is *half* of a character.
    Python holds a lone surrogate in memory quite happily and refuses to encode it to UTF-8. The
    file was left at **0 bytes**. Three weeks of an untracked, hand-maintained document, gone in
    the time it took to fail.

    **The pattern that would have made it a non-event:**

    ```python
    tmp = dest + ".tmp"
    with io.open(tmp, "w", encoding="utf-8", newline="\n") as f:
        f.write(new_text)
    assert io.open(tmp, encoding="utf-8").read() == new_text   # it round-tripped
    shutil.copy2(dest, dest + ".bak2")                          # keep the old one
    os.replace(tmp, dest)                                       # atomic swap
    ```

    A crash anywhere above the last line leaves the target untouched. **Use this for every write to
    a file that is not in git** — which, on this project, means everything in
    `OAA maintence and content/`.

    **Why it was unrecoverable, which is the part worth fixing at the source.** Those MD files are
    the only project records outside version control. File History has never been enabled on that
    machine, there were no volume shadow copies, and the folder sits outside OneDrive. The `.bak`
    beside it was three weeks stale. **A single bad write on an untracked file is permanent.**

    **How it was actually recovered, worth knowing for next time.** Claude Code logs every tool call
    and its full output to `~/.claude/projects/<project>/<session>.jsonl`. Another session had read
    the whole file earlier the same day, so a complete verbatim copy of all 200 lines was sitting in
    that log. `grep -l "<a distinctive phrase>" *.jsonl` found it; the Read tool's line-number
    prefixes (`1\t`, `2\t`, …) strip off with a one-line regex. **This is a real recovery route
    for any file a session has read, but do not treat it as a backup** — it depends entirely on
    somebody having happened to read the file, and on the log not having been rotated.

    **Two things the lint cannot check for you.** Build the replacement text with real characters
    (`"\U0001F5C2"` or the literal emoji), never a surrogate pair written by hand. And after any
    scripted edit to a hand-maintained document, assert on the result — length, line count, a few
    distinctive strings that must survive, and any that must be gone.

24. **ONE TIME SLOT, TWO NAMED PROGRAMMES — the alternation trap. A `Weekly` record over a shared
    slot silently over-advertises, and no scan will tell you.** Found twice on 2026-09-10, at two
    unrelated libraries, within an hour of each other.

    - **Larkspur, Fridays 10:00 AM.** id 15 (Storytime) was `Weekly`. The branch actually alternates
      that slot with **Cuentos con Ritmo**: Storytime on Oct 9, 23 and 30, Cuentos on Oct 2 and 16.
      id 15 generated all five, so the site advertised Storytime on **three Fridays it does not
      run** — two taken by the other programme and one cancelled outright.
    - **Inverness, Wednesdays 10:45 AM.** A new `Weekly` record ("Storytime is calling") and a new
      one-off ("Music & Movement with Colors of Spanish") landed on the same slot on Oct 14. Here
      `check_duplicates.py` **did** catch it — as a COLLISION — but only because the replacing
      programme had been entered as its own record in the same batch.

    **That difference is the whole lesson.** The collision scan compares records to records. When
    the other programme is in the database, it fires. When the other programme is only on the
    library's calendar and not in the database, **nothing fires at all** — the recurring record
    just quietly claims a slot it does not own. Larkspur was invisible for exactly that reason.

    **So: when reading any venue calendar, do not only look for events to ADD. Look at what occupies
    the slots your existing recurring records claim.** A week where the slot is filled by a
    different named programme is a `skip:` on your record, and it is the only signal you will get.

26. **A MONTH-GRID LISTING IS NOT A DATE. OPEN THE EVENT'S OWN PAGE.** Found 2026-09-24 and it
    nearly put a two-year-old event on the site. The Mill Valley Chamber's calendar rendered
    "Blessing of the Animals" inside its **October 2026** grid, on Oct 4 — a Sunday, so the
    weekday check (rule 14) passed cleanly. The event's own detail page on the same site read
    **"Sunday, October 6, 2024"**. Aggregator grids re-render undated or recurring entries into
    whatever month you are browsing, so the grid position carries no year at all.

    **The rule: a date is only as good as the deepest page you opened.** A month grid tells you an
    event exists; the detail page, or better the organiser's own bulletin or calendar, tells you
    when. Two events were held back on this basis the same day and one was then confirmed from a
    church bulletin PDF (id 1219) while the other stayed out. This is the same failure class as
    Ronnie's 2017 outdoor-movies page, except the stale content was wearing the current month's
    clothes.

27. **THE FEED MAY NAME THIS WEEK'S THEME AS IF IT WERE A NEW EVENT.** MCFL publishes its rotating
    afterschool slot as "Wednesday Kids' Club: Gaming Club", "… : Sugar Skull Mask Craft" and so
    on, and Mill Valley names the film in "Family Movie Day: Coco". Each reads as a distinct new
    programme and each is really one existing record — id 46, whose own description says *"the
    activity rotates each week between gaming on the Nintendo Switch, LEGO building, and crafts"*,
    and id 969's monthly Movie Days. Five such proposals reached the review workbook on 2026-09-24
    and were withdrawn only because `check_duplicates.py` flagged the COLLISION against the
    recurring record. **This is rule 18's dedup-by-venue check earning its keep: match on day +
    time + venue and READ the matched record's description before calling a theme a new event.**

    **Which way to resolve it matters.** If the theme is just this week's activity in the usual
    slot, the dated record is a duplicate and should be dropped. If a *different* programme
    genuinely displaces the usual one that week — a movie instead of the club, a visiting bat
    show — keep the special and add `skip: YYYY-MM-DD` to the recurring record, which is how
    id 46 now carries both Oct 7 and Oct 14.

28. **A LEGITIMATE SPANISH WORD CAN TRIP THE BILINGUAL LINT, AND THE FIX IS THE WORDING, NOT THE
    LINT.** `--bilingual-lint` flags a Marin town named in one language only, which is what caught
    a real bug in the past. On 2026-09-24 it fired on id 1214 (Shark Night, in Mill Valley)
    because **"tiburón" contains "Tiburon"** — the Spanish for shark is also the name of a town
    twelve miles away. The lint was right to fire: a Spanish reader seeing "Tiburon" on a Mill
    Valley card would be misled. Reworded to "grandes blancos", which is what Spanish actually
    calls great whites. **Never suppress a lint finding to make a commit pass — reword the copy.**

25. **WHEN AN ORGANISATION'S OWN TWO CHANNELS DISAGREE, THAT IS NOT A THIRD-PARTY PROBLEM AND THE
    USUAL RULE DOES NOT SETTLE IT.** "Fetch the source that owns the event" assumes the owner speaks
    with one voice. Twice on 2026-09-10 the owner did not:

    - **id 853, Spanish Sing-along at Northgate.** The record says 10:30 AM, sourced from the
      library's own **August Instagram flyer**. `srpubliclibrary.org` lists **10:00–10:30 AM** for
      every September and October date. Same library, two channels, a 30-minute gap. Unresolved as
      of this writing — open item 54.
    - **Bolinas Film Festival Kids Film Showcase.** The festival's **own Instagram** announced it
      for Fri Sep 11, 6–7 PM; the festival's **own website** lists no such event and shows a
      different pre-festival screening on Sep 12. Added anyway (id 1143), because the flyer was
      recent, came from the organiser's account, and named the festival's real venue and address
      exactly — it reads as a late addition the website has not caught up with.

    **How to decide, and what to record.** Prefer the channel that is **dated closest to the event**
    and most specific to it: a current-term calendar beats a month-old flyer; a this-week social
    post beats a season-overview page that predates it. Then **write which channel you took and
    why into `internal_notes`**, because the next person to look will find the same contradiction
    and needs to know it was seen rather than missed. When the two disagree on something a family
    acts on — a start time, a date — and neither is clearly fresher, **ask rather than pick.**


## Regions (Marin, Napa, Telluride+)

The app has three regions, chosen with the Profile **Region** toggle. Every record's region comes from its `county`
field via `regionOf()` (see the schema). **All rules in this file apply to every region**; the only region-specific
material is listed here and in `sources/<region>.md`.

| Region | `county` | Location groups | Sources | Notes |
|---|---|---|---|---|
| Marin | blank | see the schema's `location_group` row | `sources/marin.md` | default for first-time visitors |
| Napa | `Napa` | `Calistoga`, `St. Helena`, `Yountville` | `sources/napa.md` | live music; see Napa specifics below |
| Telluride+ | `Telluride+` | `Telluride`, `Mountain Village`, `Norwood`, `Ridgway`, `Ouray`, `Montrose/Olathe`, `West End`, `Dolores`, `Virtual` | `sources/telluride.md` | all times Mountain Time; swept by the partner |

### Napa specifics
**Schema specifics for Napa events** (on top of the standard schema above):
- `county`: always `"Napa"`.
- `id`: Napa IDs historically started at 500, but **they are not a reserved range and never were** — they come off the same global sequence as Marin. As of 2026-08-21 the highest Napa id is **907** and the file's max id is also **907**; the Aug 21 sweep's Napa records landed at 888–907, well past any "Napa block". Do not reason about a record's county from its id. Napa IDs share the same global sequence as Marin events in practice (`next_id()` in `events_io.py` already handles this correctly by taking the max across all events) — don't hand-roll a separate Napa-only counter.
- `type`: always `"Music and Movies"` for Napa music events (not the legacy `"Music"` value).
- `location_group`: must exactly match the town — `"Calistoga"`, `"St. Helena"`, or `"Yountville"`.
- `cadence`: `"One-off"` for dated events, `"Weekly"` for recurring venue nights, and **`"Monthly"` with an ordinal phrase in `notes`** for venue series that run on an nth-weekday rule. Monthly is NOT a Marin-only cadence — this doc said so until 2026-08-21 and it was wrong. Lincoln Avenue Brewery alone needs three of them: ids 905 (Jam Night, "First and third Thursdays"), 906 (Don Cameron Acoustic, "Third Friday") and 907 (Mark Shuttleworth Acoustic, "Last Wednesday"), alongside the Weekly Saturday id 530. **Rule 9a applies exactly as it does in Marin** — each record's `notes` must contain only its own ordinal words, `last` is tested first and short-circuits, and you must verify the rule parses to what you intended before committing.
- `event_date`/`expires`: for one-offs, both must be set to the *same* `YYYY-MM-DD` — a range will make the event display on every day in between. For `Weekly` recurring venues, leave both blank.
- `featured`: `true` only for marquee events (park-series openers, major one-offs); default `false`.

### Telluride+ specifics (added 2026-10-09)

Alexandra's request 2026-10-09: bring in the Telluride, CO area "similar to Napa, but a lot more events", with sourcing **standardised on the Marin process**. Libraries first; the other sources in `Telluride/Telluride_Region_Research_v2.xlsx` (markets, community calendars, arts venues, schools, towns, Lee Shea's 18 sources) are the next phase.

- **Files (Dropbox project folder, NOT the repo):** `Telluride\Telluride_Region_Research_v2.xlsx` (towns, every library, every source, attestation) and `Telluride\Telluride_library_sweep_2026-10-09_review.xlsx` (the first sweep: same three tabs as a Marin review, her decisions in it).
- **Sandbox first.** She asked for mockups before anything is committed: candidates go to a review workbook, approved rows become records in a sandbox JSON, and a local copy of the site (demo session, writes stubbed, a "MOCKUP" ribbon) is served for her to click through. Commit only on her explicit go. The first batch went live 2026-10-09 (ids 1450–1609).
- **Decisions (Alexandra 2026-10-09):** teen programs IN; adult programs IN as `Grown-Ups Only!` (`ages` "Adults" or "21+"); approved one-offs that repeat on a visible pattern become Weekly/Monthly records ("add the other events as recurring"), but a single date is not a pattern and a series that ends stays as one-offs; region-scoped carousel; Marin-only ads; header stays "Out AND About Marin" for now.
- **Open items:** 65 (umbrella), 66 (the five library questions, 66a-66e: Wilkinson Thursday 10:30 Storytime vs Books Alive, November dates not yet posted, Ridgway Tween Café time, Dolores Silly Stories times, Rico; items 67-70 merged in 2026-10-17), 72 (Lee Shea, the partner, sets up her Claude Code).
- **Sources:** `sources/telluride.md`: 10 sources since 2026-10-17 (the 9 libraries, plus #10, the Visit Telluride Festivals & Events calendar). The other v2 event sources are listed there as "Not yet verified"; add them one at a time, each with a one-source review workbook first.

## Homepage Featured strip

The horizontal card row at the top of the homepage (`#featuredWrap` / `#featuredRow`). Selection logic is `selectFeatured()` in `index.html` (~line 3981) — a client-side scoring pass over `allEvents`, not a stored list. `featured: true` on a record does **not** put it in the strip by itself; it only adds a scoring boost (`+10` in `score()`) among records that are otherwise eligible, plus one specific reserved-slot exception (below).

**Eligibility (`elig()`), current rules as of 2026-08-13:**
- Type must be one of `Festival`, `Music and Movies`, `Community Event`, `Kids Programs`, `Library`, `Fitness` (added 2026-08-28 with the hike re-code). `Farmers Market` and anything named "Learning Bus" are always excluded.
- **No recurring events.** Only `cadence: 'One-off'` is eligible — `Weekly`, `Bi-weekly`, `Monthly`, and `Seasonal` are all excluded, with exactly one exception below. This replaced an older, narrower rule that only excluded `Weekly`/`Bi-weekly`/`Daily` **Library** records; that rule is now redundant and was removed since no recurring type qualifies anymore.
  - **The one exception**: a record with `featured: true` **and** `cadence: 'Monthly'` **and** `type: 'Kids Programs'` still qualifies — this is the existing reserved-slot mechanism (up to 2 slots, in `selectFeatured()`'s `pick()`) for marquee recurring storytimes. Confirmed 2026-08-13 by Alexandra to keep working exactly as before; everything else recurring is now out.
- ~~**No Napa County music.**~~ **RETIRED 2026-10-09 (Alexandra, option A)**: the strip is now region-scoped (bullet below), so Napa music can only appear in the Napa view and the rule had nothing left to protect. Keeping it left the Napa carousel empty (every Napa record is music). Evening concerts are still excluded everywhere. Original text kept for history: Added 2026-09-01 at Alexandra's request, replacing an earlier “Marin only” understanding that was never actually implemented. `elig()` had **no county check whatsoever**, so Napa records could reach the strip for a Marin viewer regardless of the county toggle. All 36 Napa records are `Music and Movies`; the evening rule below already caught the evening ones, but nine **afternoon** winery sets were genuinely eligible. The rule is scoped to `county === 'Napa' && type === 'Music and Movies'` rather than to the whole county, so a future Napa festival or children's event can still feature.
- **⚠ SUPERSEDED 2026-10-09: the carousel NOW FOLLOWS THE REGION** (Alexandra: "the carousel should only show events tied to the specific region Marin/Napa/Telluride"). `elig()` opens with `if(regionOf(e)!==activeCounty)return false;`. **Sponsor ads (`ads.json`) show only in the Marin view** (`withAds()` returns none unless `activeCounty === 'marin'`; her words: "no Marin sponsors in Napa or Telluride"). Search (`searchEvents`) and Coming Up (`renderComingUp`) were scoped to the region in the same change. A future non-Marin sponsor will need a region field on the ad. Old text follows for history: **The carousel does NOT follow the county toggle, and that is a decision, not an oversight.** `selectFeatured()` never reads `activeCounty`, so a visitor who switches to 🍇 Napa sees a Napa event feed with a MARIN carousel above it. Raised with Alexandra 2026-09-01 and she chose to leave it: “fine while Napa is small and mostly winery music”. **Do not make the carousel county-aware, and do not harden the Napa rule into a whole-county block, without asking her.** Two things would change the calculus and are worth re-raising if either happens: Napa gaining non-music events, since the rule above names music only and a Napa festival WOULD then surface for a Marin viewer; or Napa growing enough One-off records to fill a strip of its own. Note also that “Marin” is not a stored value — `county` holds `Napa` or nothing, and Marin is inferred as `county !== 'Napa'` here and in `getFilteredEvents()`.
- **A `pinned: true` record was held at the FRONT of the strip, whatever its cadence (added 2026-09-03). SUPERSEDED 2026-09-13: it still qualifies whatever its cadence, but it no longer stays first — it rotates with the other cards (see the rotation bullet below).** `elig()` lets a pinned record through before the One-off check, `occ()` always reports it as occurring today, and `pick()` puts pins at the head of `reserved[]` — which is emptied into the strip *before* the scored loop runs, so position in `reserved` IS display order. A pin therefore beats a higher-scoring card: verified in-browser against the real `selectFeatured()`, the Imagination Library card (score 12) sits ahead of a marquee storytime scoring 13. The existing reserved slots still work and are counted relative to the pins (`nPins+2` libraries, `nPins+4` including storytimes), and with **zero** pins the ordering is unchanged — also verified. **Use it sparingly**: a pin costs one of the strip's nine slots every single day, permanently. First and only use is id 1082, Dolly Parton's Imagination Library, a standing sign-up programme with no date and no venue, which could never qualify any other way.
- ⚠ **The bullet above was itself mangled on first write (2026-09-03) and had to be repaired** — it was authored through `python -c "..."` in double quotes, so bash performed command substitution on every backtick and silently deleted `elig()`, `occ()`, `pick()`, `reserved[]` and the rest, leaving sentences like "A  record is held at the FRONT". It was committed and pushed in that state. **Author any text containing backticks with the Write tool, or a quoted heredoc (`<<'PY'`), never inside a double-quoted shell string.** This is the same class of failure as the heredoc backslash mangling already recorded in this file, and it has now happened twice.
- **The strip ROTATES — one slot every 5 minutes (added 2026-09-13, Alexandra).** selectFeatured() still decides WHICH nine cards appear, in the same fixed order as before; renderFeatured() then passes that list through rotateFeatured(), which shifts it by floor(Date.now() / FEAT_ROTATE_MS) mod n. The card in slot 2 moves to slot 1 and slot 1 goes to the end. **The offset comes from the wall clock, not the page load**, so every visitor sees the same order at the same moment and a reload does not reset it; over any 45 minutes each card holds every slot for exactly 5 minutes, so visibility is equal across a day. armFeatRotation() sets a timer for the next 5-minute boundary and re-renders; it **skips the move while the tab is hidden or the visitor has scrolled the strip** (scrollLeft greater than 4), retrying at the next boundary, so cards do not jump out from under a reader. A visibilitychange listener re-renders when the tab comes back. **Pinned cards rotate too** — equal visibility for all nine was the explicit ask, and it reverses holding the Imagination Library card first. To pin something back to slot 1, remove it from the list before rotating and put it back at the front. **Verification note:** the local copy only reaches the home screen after sign-in, so the test loaded events.json with fetch-then-text and JSON.parse (a direct r.json() on the 720 KB file kept failing in the in-app browser), then mocked Date.now in 5-minute steps; the live timer was confirmed by temporarily setting FEAT_ROTATE_MS to 10 seconds. The scroll-skip branch could not be exercised locally. Closed open item 52.
- **No evening music concerts.** A record is excluded if `type === 'Music and Movies'` **and** `time_of_day === 'Evening'` **and** the event name does not contain "movie" (case-insensitive). There is no schema field that separates concerts from movie screenings within this type — the name-substring check is the only signal, and it's clean in practice: every movie-night record in the dataset (`Movie Nights at the Mart`, `Movies in the Park: …`, `Dive in Movie Night`, `Outdoor Movie Night — …`) contains "movie", and no concert record does. **Evening movie nights stay eligible** — this rule targets concerts specifically, confirmed with Alexandra 2026-08-13. Non-evening concerts (morning/afternoon) are unaffected either way.

- **Retired records never feature (fixed 2026-10-13).** `elig()` now starts with `if(shouldShowEvent(e)==='hide')return false;`. Until then the strip never looked at `status`, so Inactive one-offs with a future date still featured: Alexandra spotted id 789 (Movies in the Park: Pirates of the Caribbean, retired Sep 8 as a misdated 2023 finale) on the strip on Oct 13. Six retired future one-offs were exposed. Verified by simulating five dates (none shown, strip still 12) and by switching the check off (789 reappeared).
- **12 cards, and a Community Resources card (Alexandra 2026-10-13).** `FEAT_SLOTS = 12` (was a literal 9 in three places). Sponsor ads (Marin only, up to 9 since 2026-10-22, `MAX_FEAT_ADS`; was 2) and the **Community Resources!** card (`withResourcesCard()`, Marin view only, since the Resources tab is Marin content) take slots from that total; events fill the rest, so Marin shows 9 events + 2 ads + 1 resources card. The card opens the Resources tab scrolled to the top (`openResourcesTop()`) and rotates like every other card. Napa or Telluride may show fewer than 12 when fewer events qualify. Write emoji in this file as the character itself or `\uXXXX\uXXXX`: `featEmoji()` uses `\U0001F...` escapes, which JavaScript does not understand (it is dead code, never called, so harmless).

Everything else — the `BOOST`/`DEM` name-keyword lists, the reserved slots for Mill Valley/Sausalito Library one-offs (`isLibHi()`), the per-town cap of 3, the widening date window if fewer than 9 candidates are found — is unchanged.

## Weekly sweep (one procedure for every region)

**Restructured 2026-10-10 at Alexandra's request:** one rulebook for every region. This section is the whole sweep
procedure for Marin, Napa and Telluride alike. **Only the source lists differ**, and they live in `sources/marin.md`,
`sources/napa.md` and `sources/telluride.md`, all in one fixed format that `check_docs.py` enforces. Ages, holidays,
cadence, `notes`, Spanish, duplicates and the workbook layout are written here once. **No region deviates; if a region
seems to need a different rule, change the rule here, for everyone, with Alexandra's OK.**

**Who runs what:** Alexandra runs the Marin and Napa sweeps. The **Telluride sweep is run by her partner, Lee Shea, on Lee Shea's own Claude Code**
on the partner's computer, following "Telluride partner sweep" below. The partner reviews the workbook; Alexandra's
Claude Code processes the approved file and commits. The partner never commits. Setup and her start-up prompt:
`Dropbox\01. Out AND About Files\Telluride\PARTNER_SETUP.md`.

### Starting a sweep
0. **Name the region** (`marin`, `napa` or `telluride`) and open `sources/<region>.md`. Run `python check_docs.py`; it must
   pass. On the partner's machine, do "Telluride partner sweep" step 1 first.

### Telluride partner sweep (runs on the partner's computer)
Her start-up prompt only downloads this file and points here, so **everything her Claude needs is in this subsection and
the shared procedure below**. Added 2026-10-10 (Alexandra); no Git, and her only installs are the Claude app and Python.
1. **Get the current rules and tools, every sweep, before anything else.** Download, overwriting old copies, into
   `C:\Users\<her Windows user>\OAA-rules` (outside Dropbox), keeping the `sources` subfolder:
   `CLAUDE.md`, `check_duplicates.py`, `check_docs.py`, `events_io.py`, `events.json`, `sources/marin.md`,
   `sources/napa.md`, `sources/telluride.md`, from `https://raw.githubusercontent.com/outandaboutmarin/out-and-about-marin/main/`
   with `curl -fsSL --create-dirs -o <file> <address>`. **If a download fails (GitHub sometimes answers "429 too many
   requests"), wait 30 seconds and retry, up to 3 tries per file**; stop and tell her only if a file still fails. First run
   only: `python -m pip install openpyxl`. Then `python check_docs.py` in `OAA-rules` must say "clean" (`python3` if
   `python` is not found; paths may use `/` or `\`).
2. **`<repo>` in this file means her `OAA-rules` folder.** Region **telluride**; sources `OAA-rules\sources\telluride.md`;
   window = **the dates in her prompt** (she writes today's date and the period to cover, MM/DD/YYYY - MM/DD/YYYY; if they are
   missing or look wrong, e.g. a start date in the past, ask her before sweeping; the usual period is today through about 7
   weeks ahead); all times Mountain Time.
3. **Run the shared procedure below in full**: every source, full pages, the escalation tiers, venue-based duplicate checks
   against the fresh `events.json`, and the Attestation Log. Tier 2 is **the Claude desktop app's built-in browser**; tier 3 is **real
   Chrome through the "Claude in Chrome" extension**, which must be installed and connected on her computer (tool names
   differ between setups; go by what the tool is, not its name). If it is not and a source still fails after tier 2, attest it as blocked,
   naming the tiers tried; never skip it.
4. **Save** the workbook to her `Telluride\Sweeps\` folder as `telluride_sweep_YYYY-MM-DD_review.xlsx`, run the completion
   check (procedure step 5), report (step 6), and **stop**.
5. **Never** edit `OAA-rules`, change `events.json`, commit, push or publish. She reviews and renames the file
   `…_review_APPROVED.xlsx`; Alexandra's Claude Code processes it.

### Procedure (every region)
1. **Load `events.json`** (via `events_io.py` — `load_events()`) so you have the current dataset to dedupe against.
2. **Go through every source in `sources/<region>.md`, in order.** For each one:
   - Fetch the URL using the method specified — a web search snippet alone is NOT sufficient, you must fetch the actual live page/calendar and read every current/upcoming event off it. If a source is marked with a workaround (JS-rendered, robots-blocked, etc.), use that workaround — do not stop at "JS-rendered, no list."

   - **WHEN A FETCH FAILS OR LOOKS EMPTY, ESCALATE THROUGH THESE THREE TIERS BEFORE REPORTING A SOURCE AS BLOCKED. Added 2026-09-03 at Alexandra's request.**

     1. **WebFetch** — the default. Fine for server-rendered pages.
        **⚠ FEEDS MUST BE READ RAW AND IN FULL (added 2026-10-11, every region).** WebFetch passes pages through a small
        summarizing model, which can silently drop events, cut descriptions and garble times. **For calendar feeds
        (iCal/.ics), data APIs (JSON, e.g. a WordPress events API) and long paged lists, a summarizing fetch never counts as
        checked.** Read them raw: a direct download in the shell (`curl` or Python), or the raw text from the in-app browser
        or Chrome, then parse it in Python. If no raw read is possible, finish the rest of the sweep and **attest that source
        as INCOMPLETE**, naming the method that was available (Alexandra, 2026-10-11: record and finish, don't stop). The
        completion check treats "incomplete" as an honest result, so the reviewer sees exactly what was not read.
     2. **The in-app preview browser** (`mcp__Claude_Browser__*`) — use for JS-rendered pages. It also lets you `fetch()` same-origin from inside the page and parse the HTML yourself, which is how all 16 MCFL pages and all 10 Belvedere-Tiburon pages get read in one pass.
     3. **REAL CHROME** (`mcp__claude-in-chrome__*`) — the user's actual browser, with its own fingerprint and logged-in sessions. **This is the last resort and it works when tier 2 does not.**

     **These are NOT the same browser, and the difference is not cosmetic.** Older wording in this file said "use the Chrome browser tools", which is ambiguous now that both exist — and on 2026-09-03 that ambiguity cost a whole source. Sources 8 and 40 were reported INCOMPLETE after tier 2 failed; the identical URLs returned full months on the first try in tier 3.

     **THE FAILURE MODE THAT MATTERS: a bot-management WAF may serve a STRIPPED PAGE RATHER THAN AN ERROR.** Sausalito's Akamai WAF returned HTTP 200 with the calendar's day-number grid intact and every event row silently removed. There was no 403, no exception, nothing to catch. It reads exactly like a genuinely empty calendar. **That is far more dangerous than an outright block**, because a sweep can attest "checked, no events found" in perfect good faith and be completely wrong — which is the same class of silent under-reporting as the per-branch MCFL pages and the 5-of-14 Marin Mommies episode.

     **So: an empty-looking calendar is a TRIGGER TO ESCALATE, never a result.** Before writing "no events" for any month, ask whether a venue that runs weekly storytimes plausibly has a blank month. If not, go to tier 3. Two other tells that you are being served a stripped page rather than a real one: same-origin `fetch()` from inside the page returns a JS-challenge or meta-refresh document instead of HTML, and navigation starts being refused after a handful of requests.

     Only after tier 3 also fails should a source be attested as blocked — and say which tiers you tried.
   - **Dedup by VENUE, not by name — this is mandatory, see rule 18 in `CLAUDE.md`.** For every candidate, run:

     ```
     python <repo>\check_duplicates.py --venue "<the candidate's venue>"
     ```

     Read the **whole** returned list and match on **day + time + cadence**. Do NOT dedup by event name, and do NOT treat `find_event()` as sufficient — it is a substring matcher and its own docstring says so. On 2026-08-20 name-based dedup let **nine already-existing events** through as "new" (a plural, an ampersand, a parenthesis, inserted words, a missing space). Two extra requirements that come out of the same episode: a record with `status: Inactive` is **still a duplicate** (`--venue` lists every status on purpose), and when a match comes back you must **read its `notes`** before deciding it's a different program — one of the nine was a single weekly slot with a rotating weekly theme, not a separate event.

   - **Write `notes` as PUBLIC text — it renders verbatim on the site. Mandatory, see rule 19 in `CLAUDE.md`.** There is no internal field on an event. Everything you put in `notes` appears in an amber callout box on the public event detail screen, which is how 109 records ended up publishing our maintenance log — including sentences naming Alexandra, citing internal ids, and criticising named sources. `notes` may contain **only**: the ordinal recurrence phrase the parser needs, `ALERT:` / `ALERT[YYYY-MM-DD]:`, `skip: YYYY-MM-DD`, `Reopens <date>`, `UNPREDICTABLE`, and short public logistics prose ("Sign up at the children's desk the morning of the event"). **Everything else — the URL you verified against, the date you checked it, what a source got wrong, why you chose a cadence, who told you — goes in the git commit message**, which is the durable internal record and is invisible to the public. Before committing:

     ```bash
     python <repo>\check_duplicates.py --notes-lint --all
     ```

     It exits non-zero on any leak, prints the offending sentence and why it fired, and prints the public remainder that would survive. Fix every leak you introduced. (Pre-existing leaks on records you did not touch are tracked as open item 38 and need Alexandra's sign-off to batch-clean — don't fold that into a sweep commit.)

   - **Never write a reminder-to-self into `notes` using a phrase the app parses.** Two live incidents on 2026-08-21, both self-inflicted while documenting the very rules they broke: the words "the THIRD Saturday" inside explanatory prose made `parseOccurrenceRule()` emit `{nths:[2,3]}` and generate a phantom occurrence that duplicated another record; and writing "add skip: 2026-09-18 here" as a to-do **immediately suppressed that date**, because `parseSkipDates()` matches anywhere in the string. `parseOccurrenceRule()` scans the entire notes field, ignores grammar, and tests `/\blast\b/` **first**, short-circuiting every other ordinal. After writing any `Monthly` record, verify the rule actually parses to what you intended before committing.

   - Record: source name, URL fetched, method used, # of current items reviewed, newest item date seen, and the result (candidates found, or "none — fetched live list, N items reviewed").
   - Do NOT report a source as done from assumption. If you could not complete a source, say so explicitly rather than silently skipping it.
3. **If you cannot complete all sources in one session**, tell the reviewer (Alexandra; the partner for Telluride) upfront before starting, rather than silently presenting a partial sweep as complete.
4. **Build the review workbook** exactly as "Review workbook format" below says: the same four sheets, in the same order,
   with the same columns, for Marin, Napa and Telluride alike. Do not drop, rename or reorder a column for one region.
5. **Save the workbook** to the path in the region file's header (`Review workbook`) (today's date). Do not save it inside this repo, and do not commit/push it. **Then run the completion check** (added 2026-10-10): `python <repo>\check_docs.py --attestation <workbook>`. It must say "complete": one Attestation Log row per source in the region file, every row with a Result, none banned. Fix the gaps (finish the source, or attest honestly why it could not be read) before reporting.
6. **Summarize in chat**: how many sources were fully checked, how many candidates were found, any sources you couldn't complete, and where the review file is. Tell the reviewer to fill in the Decision column and let you know when it is ready for "Processing an approved sweep" below.
7. **Then stop.** Do not touch `events.json` until the reviewer has filled in the workbook and someone asks for "Processing an approved sweep". `<repo>` above means the local copy of this repo: Alexandra's is `C:\Users\AWalter\Code\out-and-about-marin`; the partner's is her `OAA-rules` download folder.

### Ground rules (every region)

Alexandra runs this **on command**, in chat, not on a schedule — she says something like "run the sweep" and it happens in that session. It is the main thing this whole doc exists to support.

**History note:** until 2026-10-10 the procedure lived in two command files (`run-sweep.md`, `process-sweep.md`); they were merged here so every region follows one procedure.

- **"Fetch, don't snippet"**: a source only counts as checked once its actual live list/calendar page has been fetched and every current/upcoming event read off it. A search snippet is only for *locating* the fetch URL.
- **Pre-registered weekly classes are OUT of scope (settled 2026-09-03).** Alexandra's rule, in her words: *"we don't usually include pre-registered weekly classes on this app."* The test is whether a family can simply turn up. A drop-in session stays in scope even when it charges at the door — that is why the JCC's JymBabies and Tot Pool Parties qualify. A course you enrol in for a term does not, however family-shaped it looks: the JCC's Side by Side publishes a full schedule for ages 15–30 months and is still excluded, because it states *"we cannot accommodate drop-in attendance"* and costs $352 for eleven classes. This is the same boundary source #1's standing venue-drop-in exclusion draws from the commercial side, and it applies to every source.
- **Not every source is equally trustworthy on CADENCE, and one is known bad.** Source 44, the Novato Mothers Club community list, is hand-curated by a volunteer and is a **discovery source only**. On the day it was added (2026-09-02) it listed Books & Bubbles at Novato Library as "Every other Wednesday" — the exact error corrected in id 859 that same morning against the library's own Instagram, where the real rule is the 2nd, 4th and 5th Wednesdays. Take names, dates, venues and times from it as leads; confirm cadence at the venue before writing it to a record. It is still worth reading every sweep: it is the best Novato coverage on the list, and because it repeats programmes already in the database it doubles as a cross-check — a disagreement is a signal in one direction or the other.
- **Three fetch tiers, and the third one is a DIFFERENT browser (added 2026-09-03).** WebFetch → the in-app preview browser (`mcp__Claude_Browser__*`) → **real Chrome (`mcp__claude-in-chrome__*`)**. Older notes said "use the Chrome browser tools", which was unambiguous when only one browser existed and is not any more; on 2026-09-03 that ambiguity made sources 8 and 40 get reported INCOMPLETE when tier 3 read them perfectly. **The important part is the failure mode: a bot-management WAF can answer HTTP 200 with a stripped page rather than an error.** Sausalito's returned the calendar's day-number grid with every event row removed — no 403, no exception, indistinguishable from a genuinely empty month. That is worse than a hard block, because a sweep can attest "no events found" in good faith and be wrong, the same silent-under-reporting class as the per-branch MCFL pages. **Treat an implausibly empty calendar as a trigger to escalate, never as a result** — a branch running weekly storytimes does not have a blank month. Other tells: same-origin `fetch()` returning a JS-challenge/meta-refresh document instead of HTML, and navigation being refused after a few requests. Escalate to real Chrome for ANY source that fails or looks suspiciously empty, not just Sausalito.
- Several sources are JS-rendered or robots-blocked and need specific workarounds (documented in `sources/marin.md`) — e.g. Sausalito's Granicus month-grid (`sausalitolibrary.org/kids/library-calendar`, paged via the "Next Month >" link), Mill Valley Library's `site:millvalleylibrary.libcal.com/event` search-around, Marin County Parks via `onetam.org/calendar` (not the JS Trumba widget), CivicEngage town calendars via `calendar.aspx?CID=NN`. Don't fall back to "JS-rendered, no list" as an acceptable result — there's a documented workaround for every source.
- **Akamai/bot-management blocks** (confirmed 2026-07 on both sausalito.gov and sausalitolibrary.org — same underlying Granicus calendar, both 403 any WebFetch/curl request regardless of headers): use the Chrome browser tools (`navigate` + `get_page_text` + `find`) instead of WebFetch — a real rendered browser session passes through fine since this is fingerprint/behavior-based blocking, not a header check. Requires the Claude in Chrome extension to be connected for that session; if it's not connected, report the source as blocked via attestation rather than retrying WebFetch (it will just 403 again).
- **A venue's "events calendar" is not automatically the source of record for its recurring programs.** Added 2026-08-27 after the JCC miss. `marinjcc.org/events/` returned 13 items and **not one** of the JCC's six JBaby family programs; the sweep fetched it, found nothing, and reported "none new" while a brand-new fall program (MusicBabies, both sites) went unproposed. Alexandra caught it by asking. The old checklist wording — absence from that calendar is "weak evidence" — was too soft to stop it.

  **The test to apply**: if a venue is known to run recurring family programming and its calendar shows none of it, the calendar is the wrong surface, not proof the programming stopped. Go to the program pages. This is the same failure shape as the MCFL `/locations/XX/` pages (which only ever show the next few days) and the Mill Valley libcal empty render — a source that returns a clean, plausible, *incomplete* answer, which is far more dangerous than one that errors.

  **Term-based venues need the late-August and early-September sweeps to be extra thorough.** Anything running on a school-year term — the JCC, and likely any preschool/enrichment source added later — stops for the summer and restarts with dated fall sessions published weeks ahead on the program page and nowhere else. A session published as a range with a named exclusion ("Sep 14 – Nov 23, no class Sep 21") needs the exclusion encoded as `skip: 2026-09-21`, per rule 15.

- **⚠ "THIS VENUE PUBLISHES NOTHING" IS A CLAIM ABOUT A ROUTE, NOT ABOUT A VENUE. Added 2026-09-10, and it is the biggest single gap this checklist has had.**

  Source 41 (Larkspur Library) said the branch "posts essentially NOTHING to its city calendar", verified three ways in August, with the explicit instruction not to retire Larkspur records for calendar absence. **All of that was true and none of it was the whole picture.** The city calendar really is empty — re-verified for October on 2026-09-10. But the library runs a **full LibCal at `larkspurlibrary.libcal.com`** that no sweep had ever fetched, because no page this checklist named links to it. It was found only because Marin Mommies happened to link one of its event pages.

  **One pass produced**: four candidates no other source carried, a CANCELLED storytime, and the discovery that **id 15 was over-generating** — the Friday 10 AM slot alternates between Storytime and Cuentos con Ritmo, so the record had been advertising Storytime on Fridays it does not run.

  **The rule that follows, and it generalises past Larkspur:** when a source is written off as empty, record **which route was checked**, not that the venue is silent. Two questions close the gap cheaply — *does this venue plausibly run programming it is not showing me?* and *is there a calendar platform (LibCal, Communico, Bibliocommons, Granicus) behind the CMS page I am reading?* This is the same instinct as the JCC rule directly above — the calendar is the wrong surface — arriving from the opposite direction: there, the right surface existed on the same site; here, it was on a different host entirely.

- **A guide is not a venue (2026-09-26, from Napa).** Before adding a recurring venue night, find it on the VENUE's own channel and record the source's date. Six Napa weekly records had rested only on a June 2022 tourism guide and had to be paused.
- **Attestation**: every sweep must show, per source, the URL actually fetched and what was found ("3 candidates: ...", or "none — fetched live list, N items reviewed"). Banned as a result: "recurring already in DB" (that's not a reason to skip — one-off guest performers/specials show up on library calendars constantly), "not reached this pass", "UNVERIFIED — didn't get to it". This exists because of repeated real misses: Sausalito (6 summer guest-performer one-offs missed), Mill Valley Library (recurring-storytime assumption masked new one-offs), San Anselmo (NorCal Bats missed via wrong search surface).
- Review candidates go into a local Excel file (not committed to this repo) with a Decision column — Alexandra fills Approve/Skip and hands it back for "Processing an approved sweep". Saved to `OAA maintence and content/` in her Dropbox project folder, following the existing naming convention `daily_sweep_YYYY-MM-DD_review.xlsx`.

### Review workbook format (every region)

**One template for every region (standardised 2026-10-17, Alexandra).** The file handed to the reviewer each sweep
(named and saved as the region file's header says, never committed) carries **four** sheets, in this order, with these
exact columns. Marin, Napa and Telluride all use it, and so does a one-source review (e.g. trying out a new source).
(The one deliberate extra: a Napa sweep also logs a line in the Weekly Sweep Log tab of `Napa_Live_Music_Tracker_v2.xlsx`, as
`sources/napa.md` says. Alexandra kept it on 2026-10-17; it is an extra log, not a change to the workbook.)

1. **Weekly Sweep** — one row per new candidate (one row per date when an event runs on several days). Columns:
   `Decision` | Event Name | Date | Day | Time | Venue | Address | Town | Description | Source URL | Notes (public) | Type |
   Location Filter | Ages | Cost | Indoor/Outdoor | Cadence | **Source #** | For your review (internal).
   `Decision` is left blank for the reviewer (Approve/Skip). `Source #` is the source's number in `sources/<region>.md`
   (or "Ad hoc" for something Alexandra sent), and must match a row on the Sources Used sheet. `Notes (public)` follows
   rule 19 (it becomes public `notes`); everything internal goes in the last column. Flag genuine uncertainty with
   `⚠ POSSIBLE DUPE` in the internal column rather than silently including or dropping it.
2. **Questions** — anything needing the reviewer's judgement. Columns: `#` | Category | Question | What I Found |
   My Recommendation | Affects | **YOUR ANSWER** (shaded). Added 2026-08-06 at her request. Give a real recommendation in
   every row, not just the question.
3. **Sources Used** (added 2026-10-17, Alexandra) — one row per source that **produced at least one candidate** on the
   Weekly Sweep sheet, so the reviewer can see at a glance where the content came from. Columns: Source # | Source |
   URL(s) read | Candidates (count) | Candidate events (names) | Also checked (organiser pages read to confirm details).
   It complements the Attestation Log, which lists every source read, including the ones that produced nothing.
4. **Attestation Log** — one row per source in the region file (its header gives the count). Columns: `#` | Source |
   Category (Event Source / Library / Learning Bus) | URL Fetched | Method | Result | # Current Items Reviewed |
   Newest Item Date Seen.

`check_docs.py --attestation <workbook>` checks sheets 3 and 4 (a Sources Used sheet that names a source for every
candidate's `Source #`, and one Attestation Log row per source). For a one-source review add `--partial`, which skips the
per-source row count but still checks the Sources Used sheet. She fills `Decision` and `YOUR ANSWER` and hands it back
for "Processing an approved sweep". Note she may also **append her own rows** to the Weekly Sweep sheet with extra asks
(she added two on 2026-08-06 pointing at a Slide Ranch page and asking for a closer re-read of a roundup) — always read
past the last candidate row.

## Processing an approved sweep (every region)

Apply the approved Decision rows of a review workbook to `events.json`, then commit and push. Only Alexandra's own
Claude Code does this step (the repo at `C:\Users\AWalter\Code\out-and-about-marin`).

### Before you commit — `notes` is PUBLIC (rule 19)

This file is where Alexandra's Approve/Skip decisions get written into `events.json`, which
means it is where `notes` values get authored. **`notes` renders verbatim in an amber callout
box on the public event detail screen.** There is no internal field on an event.

On 2026-08-21 a scan found **109 of 330 records** publishing maintenance commentary — sentences
naming Alexandra, citing internal ids and filenames, and criticising named third-party sources.
That accumulated one sweep at a time, through this file.

When applying a decision, `notes` may contain **only**: the ordinal recurrence phrase the parser
needs, `ALERT:` / `ALERT[YYYY-MM-DD]:`, `skip: YYYY-MM-DD`, `Reopens <date>`, `UNPREDICTABLE`,
and short public logistics prose. **Everything else — the workbook row it came from, the source
URL, the date verified, who confirmed it, why a cadence was chosen — goes in the git commit
message.** Do not copy a review workbook's "Notes" or "Rationale" column into the record's
`notes` field; that column is internal by nature.

Required before committing:

```bash
python C:\Users\AWalter\Code\out-and-about-marin\check_duplicates.py --notes-lint --all
```

**Also run the bilingual lint before committing** (added 2026-09-03):

```bash
python C:\Users\AWalter\Code\out-and-about-marin\check_duplicates.py --bilingual-lint
```

`description_es` renders to the public exactly as `description` does. This lint catches a `description_es` that is empty, untranslated, names a town no field on the record places it in, or names a weekday that is not the record's `day`. It exists because id 41 spent an unknown period telling Spanish readers to go to **South Novato** when the event was in **Corte Madera** — see rule 20 in `CLAUDE.md`. Every event you write here has two descriptions, and this is the only check that reads the second one.

It exits non-zero on any leak, prints the offending sentence and why it fired, and prints the
public remainder that would survive. Fix every leak you introduce. Pre-existing leaks on records
you did not touch are open item 36 and need Alexandra's sign-off — do not fold that cleanup into
a sweep commit.


### Process

0. **Completion check first** (added 2026-10-10, Alexandra): `python check_docs.py --attestation <workbook>` must say "complete". If it does not, **stop**: tell Alexandra (and, for Telluride, the partner) exactly which sources are missing or carry a banned result, and write no events from that workbook unless Alexandra explicitly says to go ahead anyway.
1. **Locate the filled-in review file** at the path in the region file's header (`Review workbook`): the most recent one, unless Alexandra points at a specific file. For Telluride, process only a file the partner has renamed to end in `_APPROVED.xlsx`.
2. **Read the "Weekly Sweep" sheet.** For each row:
   - `Decision = Approve` → this event gets added.
   - `Decision = Skip` or blank → skip it, no action.
3. **For each approved row, build a full event object** per the schema in `CLAUDE.md`:
   - Assign the next `id` via `events_io.py`'s `next_id()`.
   - Map the review row's columns to event fields (Event Name → `event_name`, Venue → `venue`, Town → `town`, Type → `type`, etc.).
   - Write real Spanish translations for `event_name_es` and `description_es` — never leave these blank or copy the English text unchanged.
   - Set `location_group` to an existing value from the current dataset (check live values — don't assume the old fixed list).
   - Fill `indoor_outdoor` and `active_sedentary` even though the frontend doesn't currently read them (keep data consistent — see CLAUDE.md).
   - For `One-off` cadence: set `event_date` and `expires`. Apply the multi-day festival rule if relevant (all entries in a multi-day series get `expires` = the last day).
   - For `Seasonal` cadence: `season_start`/`season_end` in `MM/DD` format with slashes.
   - Before finalizing, run `find_event()` from `events_io.py` one more time as a final dedup check — the sweep file should already be deduped, but confirm nothing slipped through.
4. **If the workbook has a "Record Fixes" sheet, process it too** (added 2026-08-13, first used by the library audit). This sheet proposes changes to **existing** records rather than new events. Columns: `Decision` | `id` | `Branch` | `Field` | `Current Value` | `Proposed Value` | `Source URL` | `Why`. For each row where `Decision` is Approve (or any affirmative — Alexandra often writes "follow your proposal"):
   - **Read `Current Value` and confirm it still matches the record** before changing anything. If it doesn't, the record moved since the workbook was built — stop and ask, don't overwrite.
   - `Field = status` + a "retire" proposal → set `status` to `Inactive` and append a dated RETIRED note explaining why. **This genuinely hides the record** — `shouldShowEvent()` returns `'hide'` for `Inactive` (fixed 2026-08-13; before that Inactive records still rendered).
   - `Field = ... / delete` → remove the record entirely. Reserve this for events the source says are CANCELED; prefer retiring otherwise, so the record survives for reference.
   - Any other `Field` → set that field to `Proposed Value`.
   - `id = 0` means the row is a **bulk** instruction across many records (e.g. organization normalization, batch translations), not a single record. Work out the affected set yourself and report the count.
   - **After a cadence change, re-check rule 9.** A `Monthly` or `Bi-weekly` record needs an ordinal phrase in `notes` or it renders wrongly — `Monthly` without one disappears entirely, `Bi-weekly` without one fires on *every* matching weekday. Add the ordinal in the same edit.
   - **Never let a "convert to one-off" instruction create a duplicate.** If another record already covers that date, retire the recurring record instead and say so — this happened with id 177, where id 827 already held the Sep 2 date.
5. **Save** via `events_io.py`'s `save_events()` — this preserves the `{last_updated, events: [...]}` wrapper and bumps `last_updated` automatically.
6. **Verify before reporting.** Run `python check_duplicates.py` from the repo root — it does all four dedup scans from data-quality rule 13, including the one-off-vs-recurring-occurrence collision that plain string comparison cannot see. It exits non-zero if it finds anything. Every real duplicate this project has hit was one of those four shapes, and three of them were introduced by exactly this step: adding a dated one-off on top of a recurring record that already covered the date. For any `Monthly`/`Bi-weekly` record you touched, also evaluate `parseOccurrenceRule(e.notes)` and confirm it returns exactly the intended rule; watch for stray ordinal words in prose (rule 9a).
7. **Report a summary in chat**: how many events were added (with names), how many were skipped, what Record Fixes were applied, and any rows you couldn't confidently map (ask Alexandra rather than guessing).
8. **Git**: this is a routine change — commit and push directly per CLAUDE.md's git workflow. Commit summary should be short and present-tense, e.g. `Add 12 events from Jul 2 sweep`. Confirm with `git status`/`git pull` first if there's any doubt about repo state.

### Notes

- The "Attestation Log" is checked in step 0 (`check_docs.py --attestation`). Until 2026-10-10 this note said it needed no action at processing time, which meant a sweep that skipped sources could pass straight through.
- If a row is ambiguous (e.g. Decision column has something other than Approve/Skip/blank, or required fields are missing), ask Alexandra rather than guessing at what she meant.

## Ad-hoc event requests (outside the Weekly Sweep)

Separate from the recurring Weekly Sweep: Alexandra sometimes hands over a curated batch of specific events to add — from Instagram screenshots, a link, or just plain text ("Marin Moms' hike — Sept 12, 8:30 AM, King Mountain"). This is a different workflow:

- **Research each one before drafting it**: fetch any URL given (same "never assume, always verify" principle as rule 1). For screenshot-sourced events with no link, extract everything decipherable from the image itself — venue, date, time, cost — and flag anything illegible or ambiguous rather than guessing at it.
- **⚠ A DATE IN THE BATCH IS A CLAIM, NOT A FACT. Confirm every one against the ORGANISER, and re-derive the weekday.** Added 2026-09-09, after **two of nine** events in a single batch carried the **previous year's date**:
  - *San Domenico Garden Fair* was given as **Oct 25**; the school's own calendar feed says **Oct 17**. Oct 25 2026 is a Sunday and this fair has been a Saturday in every prior year found.
  - *Corte Madera Oktoberfest* was given as **Oct 11**, which was the **2025** date (a Saturday then, a Sunday in 2026). The organiser confirmed **Oct 10** — which is what `events.json` already held, so accepting the batch would have *introduced* an error into a correct record.

  **The tell is cheap and catches both: compute the weekday** (`datetime.date.fromisoformat(d).strftime('%A')`, rule 14). An annual event that suddenly lands on a different weekday than it has always used is a carried-over date until proven otherwise. This is the same year-drift that makes third-party listings unreliable — aggregators republish last year's entry — so **go to the body that runs the event**: the school, the city, the Lions Club, the district. Marin Mommies, Ronnie's Awesome List and visitmarin are for *locating* the organiser, never for confirming a date.

  **And when the batch disagrees with a record already in `events.json`, do not assume the batch wins.** Check the organiser and let it settle which is right; say plainly which way it went.

- **⚠ While you are on the organiser's page, re-read the VENUE too — an event that moves does not rename itself.** Same day, same finding: id 917 (Corte Madera Oktoberfest) was stored at *Old Corte Madera Square* and had moved **twice** since — to Menke Park for 2025, then to the Corte Madera Community Center, 498 Tamalpais Drive, for 2026. Nothing flagged it, because the name, date and town were all still right and every duplicate scan compares stored records to each other, not to the world. **A returning annual event is the shape most likely to carry a stale venue**, and the only moment anyone looks is when it comes round again — so look then.

- **⚠ Geography is a hard boundary: this app covers Marin and the three Napa towns, nothing else.** Batches will contain events families in Marin genuinely go to that are **outside** it — in the 2026-09-09 batch, the *Heirloom Apple Festival* (Gold Ridge Organic Farms, **Sebastopol**) and *Pumpkins on Pikes* (Tara Firma Farms, **Petaluma**), both Sonoma County. There is no `location_group` for either, and rule 8 forbids inventing a county-level bucket to hold them. **Do not stretch a neighbouring town's value to fit.** Report them as out of scope, with what you found, and let Alexandra decide — adding Sonoma coverage is a product decision, not a data-entry one.

- **Dedup check**: before treating anything as new, keyword-search `events.json` across `event_name` + `venue` + `organization` + `notes` for plausible matches — not just an exact-name check. A recurring series can already be in the DB under a different phrasing (e.g. "Marin Hiking Moms" vs. "Marin Moms' hike"), and a one-off date can collide with an existing recurring record's computed next-occurrence date. This is the concrete method for existing rule 6, below.
- **Public-copy conventions, settled 2026-08-20/21 through her direct edits.** These are her standing preferences, not one-off instructions:
  - **`description` is marketing copy for a parent, not a record of what we know.** She rewrote the Dirty Sneaks listing to *"tacos, margs, house music to dance to; billed as an easy Friday night hang"* — concrete, in the event's own voice. When a source gives you promotional phrasing, keep it.
  - **Every Megan Schoenbohm event is titled `Music with Megan @ <venue>`** (Spanish `Música con Megan @ <venue>`), set by Alexandra 2026-10-10, e.g. `Music with Megan @ Milkweed`, `Music with Megan @ Sports Basement (10:30 session)`. Applies whatever the venue calls it ("Music Time with Megan" etc.). She also wants a Megan listing even when it falls in an existing generic slot (id 1612 duplicates Mart Littles Music, id 56, on purpose).
  - **Event titles may carry the selling point.** She renamed that record to *"Dirty Sneaks Sunset Session - tacos & margs for sale"* and asked for *"Kids Events"* appended to the Mill Valley Fall Arts Festival title. A title is allowed to be longer than the source's if it tells a parent what they'd actually get.
  - **Strip anything a visitor doesn't need.** Twice in two days she asked for internal detail to come off a public listing — first the Dirty Sneaks commentary, then the amber notes box on id 530. See rule 19; this is the same instinct applied to `description` as well as `notes`.
  - **Cancellations are flagged, not deleted.** For "Truckloads of Fun" (Aug 21, Mill Valley) she asked for a flag reading *"cancelled - this event was erroneously posted and is not happening!"* — done as a dated `ALERT[2026-08-21]:` per rule 17, leaving the record in place. Delete only when a source itself says CANCELED and there's no value in the record.
- **Mobile tap targets.** The "Back to events" button took three attempts on 2026-08-20 before it was right, and the lesson generalizes: growing an invisible tap zone does nothing a user can perceive, and a "technically 44px" control can still read as small. Her standard is that the **text itself** is comfortably sized — `.detail-back` ended at `font-size: 1.15rem; font-weight: 600; color: #fff` with a 44px minimum target. When she says a control feels small, enlarge what's visible, not just what's clickable.
- **Grown-Ups Only! records: `ages` must not repeat the type.** The list card prints type, ages and
  cost as three pills side by side, so `ages: "Grown-ups only"` under a Grown-Ups Only! type reads
  "Grown-Ups Only! · Grown-ups only" (caught by Alexandra 2026-09-26 on the Golden Gate Mahjong
  mockup). Use **`Adults`**, or `18+` / `21+` when the organiser states a minimum. Same instinct for
  `notes`: do not restate the audience the type badge already carries.
- **Pills are short; the notes box holds the detail.** `ages` and `cost` both render as pills on the
  list card, and a long value wraps the card to three lines. For Stroller Strides the cost became
  `$20 · first class free` with the full price list in `notes`, and the age
  `0-5 yrs, with a caregiver` rather than a sentence.
- **A title longer than ~30 characters is cut on the phone list** (`.card-title` is one line with an
  ellipsis): "Chinese Mahjong Intro Night with …". The event page shows it in full. She may still
  want the long one (she did, 2026-09-26) — say so when proposing, then follow her call.
- **Online events**: `town` and `location_group` both `Virtual`, `address` "Online — link sent on
  registration" (ids 110, 1229, 1230). One record per session date, like any multi-date event.
- **Adult-focused events are her call case by case.** She skipped the Monarch seminar as
  adult-focused (item 58j) and then asked for Todd Sarner's online parenting workshop (ids
  1229/1230, sponsored, ends with a paid-cohort pitch). Flag adult-focused or sales-funnel events
  when drafting them; do not refuse them. When the organiser discloses a pitch, the description
  says so too.
- **`check_duplicates.does_event_occur_on()` is the RECURRING-occurrence port.** It never looks at a
  One-off's `event_date`, so a quick "what's on Oct 6?" loop built on it returns every One-off whose
  `day` is a Tuesday (it offered a Dec 8 Santa visit). Filter One-offs by `event_date` yourself;
  the scans already do.
- **Standing findings in `check_duplicates.py` that are CORRECT and must not be "fixed"** (there is
  no allowlist; the convention is a dated `CHECKED` note in `internal_notes` on both records):
  ids **1153/1154/1155** (three fire stations, same name and date, three places); **1156/1158**
  (one weekly Pavilion playgroup split in two because a year-wrapping season does not render);
  **3 vs 952** and **3 vs 1183** (Belvedere-Tiburon runs several programmes for different ages in
  its Wednesday 3:30 slot — confirmed on the library's own calendar for Oct 21, 2026-09-26).
- **When she asks to see them before posting**: draft full bilingual records matching the schema and present them as a list for her Approve/Skip — same shape as a sweep review, just for a handful of events instead of 37 sources. Don't write to `events.json` or push until she confirms, even though this isn't a schema/logic change (the kind of edit rule normally gates on) — the review-first ask itself is what gates it here.

## Resources tide table (live)

The "Tides & Driving in Marin" table on Resources reads `tides.json` (raw NOAA CO-OPS predictions, MLLW, built by `generate_tides.py`; stations Tam Junction, Corte Madera / Lucky Drive, Hwy 37, Bolinas). **Since 2026-10-09 every height is shown higher than NOAA: +1.07 ft, raised to +1.25 ft on 2026-10-23 (Alexandra)** (`TIDE_ADJUST_FT` in `index.html`, applied in `_tideHt()`), at Alexandra's request, to account for the El Niño Kelvin wave and sea-level rise; a note under the table says so (bilingual). The red "flood" shading on high tides (**6.9 ft and above as shown**, since 2026-10-23; was > 6 ft) uses the adjusted height.
**Rows line the stations up by time, not by order within a day** (2026-10-23, `_tideGroups()`): each tide is grouped with
the same-type tides of the other stations within 4.5 hours, and the group shows on the day of its earliest member, so a
tide that falls just past midnight upstream shows on the evening it belongs to, marked "(next day)". Checked over all of
2026-27: every tide appears exactly once. **The Hwy 37 column is NOAA 9415252, Petaluma River entrance** (0.7 km from the
Hwy 37 bridge; since 2026-10-23, was 9414290 San Francisco), which peaks about 1-1.5 hours after Tam Junction. **Do not bake the offset into `tides.json`**: the file stays raw NOAA so it can be regenerated; change or remove the offset in one place.

## Resources tab: static sections, including the Kid-Friendly Dining table

The Resources screen in `index.html` is hand-written HTML, in this order: **(temporary) Flood Watch** (`#floodWatch`, added 2026-10-24, `ecda119`: the king tide Instagram slides as a swipeable strip, images in `assets/flood/`; the section carries `data-until="YYYY-MM-DD"` and hides itself after that local date, so a new tide week means new images and a new date, nothing to remove), Tides & Driving in Marin (reads `tides.json`,
section above), Drive-Thrus in Marin County, **Kid-Friendly Dining in Marin**, Choose your own adventure (`adventure.json`, below), Yoto Player Cards (Google Drive link),
Family Swimming in Marin (external guide), Swim Lesson Vendor Directory (`swim_vendors.json`, below), Donate Baby
Essentials (Postpartum Support Center), About. None of it is in `events.json` and no sweep touches it. Every visible
string carries a `data-es` Spanish translation.

**Kid-Friendly Dining table** (`<table class="dine-grid">`, columns Restaurant | City | Why go):
- Rows sorted **by city, then by name**. A neighbourhood goes in the City cell as
  `<span style="white-space:nowrap">(Town Center)</span>`.
- Restaurant name links to the restaurant's own site (`target="_blank" rel="noopener"`); prefer a location or specials
  page that shows the deal.
- "Why go" = one or two plain sentences (food, what makes it work for kids, any kids-eat-free deal), with a matching
  `data-es` Spanish version. No em dashes.
- **Kids-eat-free deals live ONLY on this table, never as event listings** (Alexandra 2026-10-13: the five weekly
  "Kids Eat Free at …" records, ids 1118, 1119, 1356, 1357, 1369, were retired). Do not add a restaurant deal to
  `events.json`, even if a sweep source lists it as a recurring event; add or update its row here instead.
- **Asterisk = a kids-eat-free deal** (Alexandra 2026-10-10): every restaurant with one gets `*` right after its name link
  (`</a>*</td>`), explained by the bilingual footnote under the table. Add or remove the star whenever a deal
  starts or ends. Starred as of 2026-10-10: Asian Box, Finnegan's Marin, World Famous Hotboys, Amici's.
- **Kids-eat-free deals:** state only what the restaurant publishes or confirms. Aggregator-only deals (Marin Mommies'
  "Kids Eat Free in Marin" list) get a to-confirm in open item 58.
- Rows as of 2026-10-10 (17): Asian Box and Blue Barn (Corte Madera, Town Center); Boudin (Corte Madera, The Village;
  Alexandra said "Towne Center" but boudinbakery.com lists only The Village); Gott's Roadside (Greenbrae); El Huarache Loco
  and Souvla (Larkspur, Marin Country Mart); Hook Fish Co. (Tam Jct.), Mamahuhu, Tartine (Strawberry), The Junction (Tam Jct.) (Mill
  Valley); Blue Barn (Novato, Old Town, 819 Grant Ave), Finnegan's Marin (Old Town), Kitsch + Sync, World Famous Hotboys
  (Novato); Amici's and Pond Farm Brewing Co. (San Rafael, Downtown); Joinery (Sausalito). Added 2026-10-10 from
  Alexandra's list: Boudin, El Huarache Loco, Souvla, Blue Barn Novato, Pond Farm; Gott's gained its patios/parklet.
  The play areas at Blue Barn Novato and "nearby" at Marin Country Mart are Alexandra's own knowledge, not on the
  restaurants' sites; Pond Farm's play area was "possibly" and is NOT claimed (its site confirms outdoor seating and a
  kids' menu). Blue Barn's Novato page is /chestnut on bluebarngourmet.com (odd slug, but it is the Novato page).
- Deals on the table (added 2026-10-09): **Finnegan's Marin**, kids 12 and under eat free all day every Sunday with an
  adult who buys an entrée (**confirmed by the restaurant**); **Amici's**, Tuesdays from 5 PM with each adult meal, not
  on holidays (amicis.com/specials); **World Famous Hotboys** (5800 Nave Dr, Novato), Tuesdays from 4 PM (Marin Mommies);
  **Asian Box**, kids 12 and under with an adult meal, all day Sunday and Wednesdays after 5 PM (Marin Mommies only,
  **unconfirmed**: item 58zf). Toast Novato was left out: its deal ended May 31, 2026.

## Tide Pool Table (proposed third dataset — NOT started)

Open item 33, created 2026-08-15. **Name only so far — scope deliberately not guessed.** Recorded here so a new session doesn't invent a design for it.

- **Working assumption** (unconfirmed): a directory of Marin tide-pooling spots built the way the Swim Lesson Directory was — its own JSON file plus a sortable/filterable table reachable from Resources. Do NOT build it on this assumption alone.
- **The design question that has to be settled first**: tide pool information is *time-dependent* in a way swim vendors are not. A spot is only worth visiting at low tide, so a static table of locations may be close to useless — the useful artifact is probably "good low-tide windows in the next N days per spot." That is a different shape from anything else in this app: it is neither an event nor a static directory row.
- **Data is gettable free**: NOAA publishes tide predictions for Marin stations, so this does not need a paid service.
- **Two questions are outstanding with Alexandra** and should be asked before any code: (a) static list of locations, or upcoming good low-tide windows? (b) a Resources page like the swim table, or something that feeds entries into the main event feed?

## Choose your own adventure (third dataset, not events; live 2026-10-22, open item 56)

A phone-first Resources sub-page (`#adventureScreen`) listing Marin indoor playgrounds, open gyms and museums. **Not part
of `events.json` and not touched by any sweep**: a place being listed here (The Social Klub, Bay Area Discovery Museum,
Kitsch + Sync) does NOT put it in the events feed. No special treatment for sponsors.

- **Source spreadsheet**: `Resources\create_your_own_adventure_v2.xlsx` (Dropbox, not the repo; moved there 2026-10-22). Sheet
  "Create Your Own Adventure" only; "Beyond Marin" (Sonoma/SF) is unpublished, "Checks & gaps" is working notes.
- **Converter**: `python adventure_io.py` writes `adventure.json`. Columns found by header name, rows matched by a slug of
  the Place name, so inserted rows/columns are safe. **Never copied to the JSON (it is public):** "Check status" and the
  "INTERNAL: Sponsor status" column.
- **Corrections go in the converter's `OVERRIDES`, not the JSON** (same rule as the swim directory). It holds per place:
  `days` (for the Days filter), `hoursEs`, and `hours` where the sheet was wrong. On 2026-10-22 all 12 sites were checked
  and 5 rows overridden (Cal Star from its Jackrabbit calendar, Playland Mondays from Nov 2, Fox & Kit weekend hours posted
  weekly, Little Marin, Bay Area Discovery Museum). The sheet still has the old hours for those 5.
- **Three categories only** (Alexandra 2026-10-22): Indoor playground/drop-in, Open Gym, Museum. `CATEGORY` in the
  converter maps each sheet Program to one; an unmapped Program stops the run. The UI shows `category` under the header
  "Program"; `program` keeps the sheet's wording.
- **UI**: four columns (Place, Program, Location, Days & hours), no sideways scroll at 360 to 390px. Each header opens one
  shared popover (`#advPop`): sort plus a filter (Place: name search; Program/Location: checkboxes; Days & hours: "Open
  on" weekdays, sorted by days open). Place links to its website (`target="_blank" rel="noopener"`). **Default order and
  "Clear filters" = Location A to Z, then Place** (`ADV_DEFAULT_SORT`, Alexandra 2026-10-22). Bilingual: rendered from
  `currentLang`, re-rendered by `setLanguage()`.
- Data shape is meant to grow: `region` is "Marin" today; Napa/Sonoma, and items 17 and 33, may later share this directory.

## Swim Lesson Directory (second dataset — not events)

A separate reference dataset reachable from the Resources screen. **Not part of `events.json` and not touched by any sweep.**

- **Data**: `swim_vendors.json` (21 Marin swim-lesson providers). Built from `Marin_Swim_Lesson_Vendor_Dashboard_v4.xlsx` (in the Dropbox `Resources\` folder since 2026-10-22; was `OAA maintence and content/`) by the converter `swim_vendors_io.py`.
- **Corrections go in the converter, not the JSON.** `swim_vendors_io.py` holds an `OVERRIDES` dict keyed by vendor slug; a correction added there survives re-running the converter, whereas hand-editing `swim_vendors.json` is silently wiped on the next run. Example: `strawberry-recreation-district` carries `hoursSeason_override`.
- **`towns` (plural) is what the UI reads** for display and filtering — not the raw `town` field. Populate both.
- **UI** (in `index.html`, `#swimScreen`): a table, not cards. There is **no detail/drill-down screen** — a `#swimDetailScreen` existed and was deleted 2026-08-03. If you reintroduce one, note that `showScreen()` once kept a hard reference to it that threw on *every* screen change after deletion.
- Features: sortable + resizable + wrap-text columns, a frozen Vendor Name column, dropdown filters (town / class type / facility type / indoor-outdoor / age), drag-to-reorder columns with a "Default order" reset, and a user-added custom column. Column order and custom columns persist in `localStorage` under the `oaam_swim_*` keys (`oaam_swim_col_order`, `oaam_swim_custom_cols`, `oaam_swim_custom_data`), matching the existing `oaam_*` convention (`oaam_user`, `oaam_lang`, `oaam_county`).
- The page carries a "not mobile friendly, best on a computer" note by design — desktop-first was Alexandra's explicit call.
- **CSS trap worth remembering**: a container with `overflow-x:auto` computes `overflow-y:auto` too, which makes it the containing block for `position:sticky` and silently kills page-level sticky headers. The table's sticky header works because `.swim-table-scroll` is a height-bounded box with `thead` sticky at `top:0` *inside* it.
- `Swim_Dashboard_Integration_Spec.md` (Dropbox `Resources\` since 2026-10-22) describes the original card-based design and is **superseded** — the header says so.

## Open Items tracker (Alexandra's to-do list)

- **Source of truth**: `OAA maintence and content/open_items.md` (her Dropbox project folder, **not** this repo). Grouped Infrastructure / Data Quality / Marketing, with a "Recently closed" section kept for reference. Edit it directly when she says to add, update, or close an item.
- **"Show me the dashboard" / "open the open items list"** means render it as a formatted page.

  ⚠ **Corrected 2026-10-03: which generator is live.** The script in use is `OAA maintence and content/build_dashboard.py` (with `_dashboard.css` beside it), run from that folder; it writes `open_items_dashboard.html`, published to **https://claude.ai/artifact/GLDWenXPBuvDmhwDippPFH**. The `build_dashboard.py` in this repo is an older, larger copy (Sep 9) and is **not** the one to edit. As of 2026-10-03 the parser also renders **indented sub-bullets and wrapped lines** under each bullet (before that they were silently dropped, which hid item 15's open tasks and item 62's blurbs), and the "Waiting on you" cards carry the same full Notes expander as the other items.
 **Run it, do not rebuild it by hand:**
  ```bash
  python build_dashboard.py            # writes open_items_dashboard.html
  ```
  Then publish `dashboard.html` to the **existing** artifact
  `https://claude.ai/code/artifact/7c27ebfe-6674-4c8d-9b90-a0559d8e483c` (read it first — another session may have changed it). Card tones: `urgent`, `scheduled`, `open`, `hold`.

  ⚠ **Corrected 2026-09-07. This bullet used to call the generator "a scratchpad script", and that was wrong twice over.** Scratchpads are session-specific temp folders, so a tool living in one is invisible to every future session **by design** — and when it was finally looked for, `build_dashboard.py` did not exist anywhere on the machine. Every "show me the dashboard" had quietly been a hand-rebuild of ~500 lines of HTML while this file described a working process. **It is now a real file in the repo**, with `dashboard_template.html` beside it. **The general lesson: a tool documented as living in a scratchpad is a tool that does not exist.** If a process is worth writing down, its script belongs in the repo.

  ⚠ **Corrected again 2026-09-10 — the paragraph that stood here described a design the script no longer has.** It said item summaries were curated in `build_dashboard.py`'s `ITEMS` and `CLOSED` lists and were "deliberately **not** parsed out of `open_items.md`", on the reasoning that a parser over prose would read worse and fail silently. **The script was rewritten at some point to do exactly the thing that paragraph ruled out**, and this file was never updated to match.

  **Where the content actually lives:** `open_items.md` is the single source of truth and the dashboard is parsed straight out of it — the script's own docstring says "so the two cannot drift". There is no `ITEMS` list and no `CLOSED` list to edit. What the parser reads:

  | Markdown | Effect |
  |---|---|
  | `## Section` | the group heading (Infrastructure / Data Quality / …) |
  | `**54. Title**` | one item, numbered |
  | `- Status: …` | drives the status pill — see `pill_for()` for the words it matches |
  | `- Created: …` | the meta line |
  | `- **Needs from you:** …` | **promotes the item into "Waiting on you" at the top** |
  | `- ✅ **Item NN, …**` under "Recently closed" | the closed list |

  So prioritisation is controlled from the markdown, not from the script: add or remove a **Needs from you** bullet to move something in or out of the top section. Nothing in the Python needs touching to change what is prioritised.
- **There is nothing to keep in sync any more, and that is the point.** The drift this section used to warn about (item 25 stayed open on the dashboard after being closed in the markdown) is now structurally impossible, because there is only one copy of the content. **Closing an item** means: move it out of the open list in `open_items.md`, add a `- ✅ **Item NN, …**` line under "Recently closed", regenerate, and republish the Artifact. **Adding one** means writing the item into the right `## Section` with a `Status:` and `Created:` bullet. No Python edit either way.

  ⚠ **`--check` NO LONGER EXISTS. Do not put it in a command line — the script takes no arguments and will silently ignore it and just build.** It used to compare the markdown's open item numbers against the script's `ITEMS` list and fail on either kind of drift, and this file recorded it as "verified capable of failing". That guard went away with the two lists it compared; there is nothing left for it to check. **The lesson worth keeping from its removal:** a documented safety check is worth exactly as much as its last verification, and a rewrite can delete one without deleting the paragraph that promises it.
- Items resolved by a **policy decision** should be encoded where the policy actually executes — e.g. item 9 (stale Megan Schoenbohm source) and item 10 (add Slide Ranch) were both written into the sweep procedure ("Weekly sweep")'s source list so they enforce themselves every sweep, not just sit in a tracker.

# ⇢ START HERE — state of play for a new session (2026-10-17)

Read this first, then the sections above as needed.

**Health 2026-10-24**: `events.json` is **642 events, max id 1772**; notes-lint and bilingual-lint clean; duplicate scan 7 findings, all known (1770/1771 Sunday Football is a New-Year split pair like 1716/1717 and 1723/1724). **Health 2026-10-22 (end of day)**: `events.json` is **666 events, max id 1764**; notes-lint and bilingual-lint clean; duplicate scan 6 findings (the same ones reviewed after the sweep); self-test 91/91; `check_docs.py` clean. **Health 2026-10-22 (after the sweep)**: `events.json` is **658 events, max id 1756**; notes-lint and bilingual-lint clean; duplicate scan 6 findings, all reviewed (two genuinely separate same-afternoon library programs, three New-Year split pairs, 1643/1710). **Health 2026-10-21**: `events.json` is **628 events, max id 1711**; notes-lint and bilingual-lint clean; duplicate scan 3 findings; `check_docs.py` clean. **Health 2026-10-17 (end of day)**: `events.json` is **659 events, max id 1694**; notes-lint and bilingual-lint clean; duplicate scan 3 known findings. **Health 2026-10-16**: `events.json` is **640 events, max id 1666**; notes-lint and bilingual-lint clean; duplicate scan 3 known findings (1156/1158 and two Telluride room collisions); `check_docs.py` clean with **Marin at 49 sources**. **Health 2026-10-15**: `events.json` is **645 events, max id 1661**; notes-lint and bilingual-lint clean; duplicate scan 3 findings, all known (1156/1158 and two Telluride room collisions; the others dropped off as their dates passed). **Health 2026-10-14** (after the Oct 14 sweep): `events.json` is **664 events, max id 1650**; notes-lint and bilingual-lint clean; duplicate scan 6 findings, all known (1156/1158 and the 5 Telluride room collisions). **Health** (re-run and verified late 2026-10-10 from the NEW repo path `C:\Users\AWalter\Code\out-and-about-marin`): `events.json` is **665 events, max id 1614** (Marin 462, Telluride+ 160, Napa 43); self-test 91/91, notes-lint and bilingual-lint clean; duplicate scan 7 findings, all documented (1156/1158, the 5 Telluride room collisions, and 1612 vs 56, the deliberate Megan listing). Late 2026-10-09: **670 events, max id 1609**; self-test 91/91, notes-lint and bilingual-lint clean; duplicate scan shows 1156/1158 plus the 5 documented Telluride room collisions. (Earlier the same day: **510 events,
max id 1449**, all committed and pushed, level with `origin/main`.
`check_duplicates.py --self-test` is **91/91**; `--notes-lint --all` and `--bilingual-lint` are
clean; the duplicate scans show only the known, legitimate finding: the Pavilion Play Group's two
season halves 1156/1158 (the Southern Marin open houses 1153–1155 dropped off after their Oct 4 date). (464 events / max 1383 on 2026-10-06; 466 events / max 1350 on 2026-10-02 — the drop is the daily purge of past one-offs; 440 events /
max 1145 on 2026-09-10; 406 events / max 1097 on 2026-09-09. The count moves both
ways — the daily job purges expired one-offs, so a fall is the system working. **Re-run the scans
rather than trusting this sentence**; a hard-coded count in prose goes stale silently, and this
line has been wrong before.) GitHub Pages deploys off `main`, so **committing `events.json` IS
publishing** — there is no staging.

**Nothing is half-finished in the repo.** Everything is committed and pushed (last: the Oct 24 docs commit, after `9be5ba1` king tide images and `ecda119` Flood Watch; Oct 22 ended with `493e413`, Kitsch + Sync socks note; before it the Kitsch + Sync ad and 9-sponsor strip `4c6ac8d`, its 8 partner events `5322dd0`, record fixes 476/1125 `e994fdc`, the Instagram images `91c65c0`; earlier `a3d65ab`, GG Mahjong titles, after the Oct 22 sweep `b6114d0` and its record fixes `41e8f96`; the Oct 21-22 sponsor mockups live only in Dropbox; earlier `17c2a4a`, Oct 21, phone and bot commits; earlier `bcae7cf`, end of Oct 17: Telluride source #10 and its 16 events `4e1fa44`, the standard review workbook `25a2f5b`; earlier `448f182`, Village end dates and the Social Klub refresh; before that the phone commits `18432df`–`d2112a5` and `1787396`, the Oct 16 events and source 49; then `7718b72`, the Oct 15 screenshot events; before that `8f4ba49`, the Oct 14 sweep; `4ce56da` staged the week of Oct 15 Instagram slides). The old scratch and `.bak`
files were sent to the Recycle Bin during the 2026-10-10 move. **The repo and working files MOVED on 2026-10-10**: repo at
`C:\Users\AWalter\Code\out-and-about-marin`, working files at `C:\Users\AWalter\Dropbox\01. Out AND About Files`. Full
record, troubleshooting table and undo steps: `OAA maintence and content\Dropbox_move_plan_2026-10-10.md`.

## Where to pick up (2026-10-24)

The live to-do list is `open_items.md` / the dashboard (https://claude.ai/artifact/GLDWenXPBuvDmhwDippPFH). In order:

1. **Instagram, week of Oct 29 (item 15):** Thu Oct 29 5 PM, Sat Oct 31 7 AM, Sun Nov 1 5 PM, in **Template A** (the
   standard every week since Oct 22): copy `OAA marketing\Instagram templates\Template A - Thu Sat Sun posts\build_template_a_4x5.py` (Template A is 4:5, 1080x1350, since Oct 24; render with `--size 1080x1350`)
   and follow `social_media_and_marketing.md`, "Template A standard" and section 3e (Metricool). First confirm what went
   live: the king tide post (Sat Oct 24, 4 PM) and the week of Oct 22 (Sun Oct 25, 5 PM), then delete repo
   `ig/king_tide_oct25/`, `ig/week_of_oct15/` and `ig/week_of_oct22/` (`ig/README.md`).
2. **Kitsch + Sync (item 21):** only a brand colour (if they want one) and whether their events page becomes a sweep
   source are still open; the Featured ad ends Jan 21, 2027 (renew or let it lapse).
3. **Next Marin weekly sweep** (`sources/marin.md`, 49 sources). The Oct 22 sweep covered Oct 22 to Dec 3; the Learning Bus
   November PDF and Marin Magazine's November edition were not yet posted.
4. **Item 58:** zr (Diwali at Mill Valley Library) and zs (Mill Valley ShaBabies venue, ask Rachel Weiss), plus the rest.
5. **Telluride (items 65, 66, 72):** Lee Shea's setup and first partner sweep; the five library questions 66a-66e.
6. **Sponsor prospects:** Osher Marin JCC and The Cave (mockups ready); FIT4MOM still owes the direct Glofox link.
7. Items 71 and 75 closed 2026-10-24 (old folders deleted; Context Transfer skill uploaded under Customize → Skills and working in regular chats). Say "context transfer" in any chat or Code session to hand off.

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
## The pattern worth carrying into the next session

**Every significant problem in this stretch was found by Alexandra asking a question, not by a scan.** The 109 leaking notes, the nine duplicate candidates, the JCC's entire family programme missing from a sweep, id 493's broken type, and id 853 advertising two Wednesdays that do not run — all of them surfaced because she asked "is this right?", and every one had been passing every automated check at the time.

The corollary, which has now bitten repeatedly: **a scan that reports clean has not proved anything until you have seen it report dirty.** `--notes-lint` shipped with a backspace byte where `\b` belonged and could never match; the COLLISION scan compared raw time strings and hid a whole class of real double-bookings; the duplicate scans missed 310/854 because the normalised key compares only the first 14 characters of a name. Each was found by testing the check, not by trusting it.

**Third-party listings are not evidence.** In one week Marin Mommies was wrong about a movie night's day, a concert's time, a storytime's venue, a library programme's date, and the Encanto screening's date — five times, every time contradicted by the venue's own page. Fetch the source that owns the event.

## Open items worth knowing about

Full list in `OAA maintence and content/open_items.md`; the dashboard renders it at the artifact URL in `build_dashboard.py`.

- **21 / 59** — advertisers. **21**: three vendors drafted and with mockups (Social Klub ad, FIT4MOM
  Stroller Strides, Golden Gate Mahjong), all in `OAA Sponsorship and Partners/`. **59**: the app
  build those mockups imply (a sponsored Featured slot exempt from `selectFeatured()`'s rules like
  the pin, an ad-page variant of the detail screen, a PARTNER badge, social-link fields). Nothing
  built yet.
- **15** — the Instagram programme. **In progress, and the only item with work in flight** — see "Where to pick up" above.
- **24 CLOSED 2026-09-28** — the `users` table is private. **The browser must never touch `users` directly again.** Sign-in, sign-up and saving call the Edge Functions `login`, `signup` and `save-profile` (source in `supabase/functions/`, deployed by pasting into the Supabase dashboard, JWT verification OFF). Any new profile field has to be added to the function's select list (`PROFILE`) and, if the browser may change it, to `save-profile`'s `ALLOWED` list, then redeployed. The browser keeps the SHA-256 of the PIN as `currentUser.pin` (never the digits) and sends it as `pin_hash`. There is no Supabase CLI on this machine; deploys are done by Alexandra in the dashboard. A rate limit on `login` (wrong-PIN lockout) was proposed as item 60 and **declined by Alexandra 2026-09-28** (“I don't think this is a real concern”); do not re-raise it as a to-do. Likewise **`activity_log` stays written directly with the public key, by Alexandra's choice (2026-09-28, “pass”)**: the public key can add rows but a public read returns `[]`, so the only exposure is junk rows skewing usage stats, never member data.

- **Checking a change on the live site with a headless browser (learned 2026-09-28/30).** Three traps: (1) **events load only after sign-in**, so on a signed-out page `allEvents` is empty; call `loadEvents()` yourself and wait for `allEvents.length`. (2) The event page sits behind the login screen; to screenshot it, after `openDetail(id)` set `loginScreen` to `display:none` and `detailScreen` to `display:flex` (screenshots only). Stub `logActivity` and `dbUpdateUser`, and block `/rest/v1/` and `/functions/v1/` writes, so a test never touches the production database. (3) **`doesEventOccurOnDate()` does not filter one-offs by date**: it returns true for a one-off on any day, so it proves nothing about a one-off's date. **This is a test trap only:** the list itself goes through `isEventInWeek()`, which checks a one-off's `event_date` first, so visitors never see a one-off on the wrong day (confirmed 2026-09-30 with Tangled, id 1224: in the week of Nov 6, not Oct 2). To check a one-off, use `isEventInWeek(e, weekStart, weekEnd)` or read `event_date` from the live `events.json`. Also: the daily scraper removes expired one-offs, so a drop in the event count after `git pull` is normally just yesterday's events expiring; check which ids went before worrying.
  **If sign-in, sign-up or saving ever breaks because of the lock** (e.g. a function is deleted or its code breaks), the
  emergency rollback is two lines in the Supabase SQL Editor, run by Alexandra (from her printed checklist):
  ```sql
  grant select, insert, update on public.users to anon;
  alter table public.users disable row level security;
  ```
  This reopens the table to the public key, which the CURRENT site no longer uses, so on its own it fixes nothing: it only
  helps if `index.html` is also rolled back to a version that reads `users` directly (anything before `ee3668b`). Prefer
  fixing the function. If the rollback is used, re-lock as soon as the cause is fixed with
  `alter table public.users enable row level security; revoke all on public.users from anon, authenticated;`
  and record it in open items.
  **Stale tabs after the lock need nothing.** A visitor whose tab still holds the pre-`ee3668b` page cannot sign in from it
  (the old code reads `users` directly) and their saves stay on the device only. Reopening or reloading the site loads the
  new page; they stay signed in (the session is in localStorage) and their next save re-sends the whole `saved_events` list,
  so nothing is lost. Alexandra agreed no announcement or auto-reload was needed (2026-09-28).
- **44** — three library records whose cadence cannot be derived from one month of published dates (ids 43, 41, 3). The fourth, id 853, was resolved 2026-09-01 from a flyer.
- **34** — app code quality audit, not started; six confirmed findings already in hand. Needs her call on report-vs-fix.
- **33** — Tide Pool Table, scope undefined.
- **51** — id 215 carries an `expires` three months past its date, so it never got purged. One field, no user-facing effect, plus a check worth adding so it cannot recur quietly.
- **39 and 45 closed 2026-09-07**; **30** (September seasonal checks) closed on live data.

## Where the non-repo files live

**`OAA Sponsorship and Partners/`** (sibling of `OAA maintence and content/`, created by Alexandra
2026-09-26) — everything advertiser-facing:
- `Advertising Partners Upload.xlsx` — **first tab `Leadsheet` (added 2026-10-10)**: one row per sponsor that is LIVE on the
  site, columns Sponsor name | Date sponsorship went live on the site | Community Partner (x = partner events with the
  PARTNER badge) | Featured Partner (x = a sponsored card in the Featured carousel, `ads.json`). Dates come from the
  first commit that put them live; add a row the day a new sponsor goes live. **This workbook has embedded logo images:
  edit it through Excel (COM automation), never openpyxl, which drops images on save.** Then a `template` tab plus one
  tab per vendor (`TSK`,
  `Stroller Strides`, `GGMahj`). Events table in rows 4+ with columns she extended on 2026-09-26
  (Time, Town, Cost, Instagram, phone, Notes / questions for the vendor); a **Featured Partner Ads**
  block below (Ad title, Graphic, Verbiage, Mockup file).
  - **She edits it in Excel. Check it is not open before writing** (`open(path,'r+b')` raises
    PermissionError while Excel holds it) and ask her to close it rather than writing elsewhere.
  - **Write the ORIGINAL file in place and leave no copies or `.bak` files in that folder** — her
    explicit instruction 2026-09-26.
  - **Re-read the tab before writing**: she edits between passes (renumbered cells, moved the vendor
    name, added columns) and a row she deleted in Excel had shifted only some columns, leaving one
    row's values under another row's highlight. Verify row by row.
- The mockups, as `<Vendor> - <what> mockup.png` + `.html`, **one subfolder per vendor** (`Social Klub/`, `Stroller Strides/`,
  `Golden Gate Mahj/`, reorganised by Alexandra 2026-09-27; since 2026-10-21 also `JCC/`, `Kitsch + Sync/` and `The Cave/`, where each listing
  has a `... mockup` version with review notes and a `... (for <vendor>)` version without them, for sending) with the logos in a single shared `assets/` folder at the top.
  **A copy written into a vendor subfolder must reference `../assets/...`**, or its logo breaks; the repo sources keep
  `assets/...`. When re-rendering a PNG into her folder fails with `OSError [Errno 22]`, the old PNG is open in a viewer:
  render to the scratchpad and copy over it. The HTML
  sources also live in the repo's `templates/` (`ad_social_klub_web.html`, `ad_fit4mom_web.html`,
  `stroller_strides_monday.html`, `ggmahj_oct6.html`, untracked like the weekly deck templates).
  The HTML copies carry review notes written for Alexandra: **share the PNG with vendors, not the HTML.**
- What these mock up is designed but **not built** — see open item **59** and
  `social_media_and_marketing.md` section 6.

`OAA maintence and content/` in her Dropbox project folder (NOT in this repo, and never commit review workbooks): `open_items.md` (the master to-do list — count it, do not trust a number written here), `Napa_Live_Music_Tracker_v2.xlsx` (has a **Sweep Learnings** tab written 2026-08-21 — read it before a Napa sweep), and the sweep review workbooks.

## Working rhythm

**A QUESTION IS NOT AUTHORISATION. Answer it and stop.** Added 2026-09-07 at Alexandra's explicit
instruction, after I answered "why will it take an hour to fix?" and then wrote "Doing it now" and
started the work. She had asked about an estimate. She had not said go.

- **Only an instruction authorises action.** "Do it", "yes", "go ahead", "fix it". Not "why…?",
  not "how long…?", not "what about X?", not "I don't understand".
- **A question that exposes a problem is still a question.** "Why did you build it in the wrong
  shape?" identifies work worth doing — and it is not permission to do that work. Say what you
  would do, say what it costs, and wait.
- **Do not treat your own proposal as approved because she engaged with it.** Asking a follow-up
  about a plan is not adopting the plan.
- **The tell to watch for in your own drafts:** a sentence like "Doing it now", "Let me just…" or
  "I'll go ahead and…" appearing in a reply to a question. If the user's last message ended in a
  question mark and you are about to change something, stop.
- This is narrower than the general read-only/write distinction and it outranks it: it applies
  even to changes that are small, reversible, and obviously beneficial.


She runs sweeps on command and reviews candidates in Excel. Ad-hoc batches arrive between sweeps (Instagram screenshots, links, plain text) — research each, dedup, present for review before writing. **She catches real errors and she is usually right** — twice this week she pushed back on a conclusion of mine and was correct both times. Check before defending a finding.
