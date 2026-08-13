Process a completed Weekly Sweep review file: apply Alexandra's Approve/Skip decisions to `events.json`, then commit and push.

Read `CLAUDE.md` first for the event schema and data quality rules — every event you add must follow them.

## Process

1. **Locate the filled-in review file.** Default location: `C:\Users\AWalter\Documents\2. Claude-Work\PROJECTS\OAA Marin\OAA maintence and content\daily_sweep_YYYY-MM-DD_review.xlsx` (most recent one, unless Alexandra points you at a specific file/path).
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
6. **Verify before reporting.** Run both dedup scans from data-quality rule 13 — exact `(event_name, venue, event_date)` **and** normalized `(event_date, time, town, name-prefix)` — plus a recurring-slot scan on `(day, time, venue, cadence)`. All must come back empty. For any `Monthly`/`Bi-weekly` record you touched, evaluate `parseOccurrenceRule(e.notes)` in the browser and confirm it returns exactly the intended rule; watch for stray ordinal words in prose (rule 9a).
7. **Report a summary in chat**: how many events were added (with names), how many were skipped, what Record Fixes were applied, and any rows you couldn't confidently map (ask Alexandra rather than guessing).
8. **Git**: this is a routine change — commit and push directly per CLAUDE.md's git workflow. Commit summary should be short and present-tense, e.g. `Add 12 events from Jul 2 sweep`. Confirm with `git status`/`git pull` first if there's any doubt about repo state.

## Notes

- If the review file has an "Attestation Log" sheet, you don't need to do anything with it here — it's just a record of what `/run-sweep` checked.
- If a row is ambiguous (e.g. Decision column has something other than Approve/Skip/blank, or required fields are missing), ask Alexandra rather than guessing at what she meant.
