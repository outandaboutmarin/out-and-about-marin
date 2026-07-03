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
4. **Save** via `events_io.py`'s `save_events()` — this preserves the `{last_updated, events: [...]}` wrapper and bumps `last_updated` automatically.
5. **Report a summary in chat**: how many events were added (with names), how many were skipped, and any rows you couldn't confidently map (ask Alexandra rather than guessing).
6. **Git**: this is a routine change — commit and push directly per CLAUDE.md's git workflow. Commit summary should be short and present-tense, e.g. `Add 12 events from Jul 2 sweep`. Confirm with `git status`/`git pull` first if there's any doubt about repo state.

## Notes

- If the review file has an "Attestation Log" sheet, you don't need to do anything with it here — it's just a record of what `/run-sweep` checked.
- If a row is ambiguous (e.g. Decision column has something other than Approve/Skip/blank, or required fields are missing), ask Alexandra rather than guessing at what she meant.
