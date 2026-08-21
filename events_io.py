"""
Shared events.json read/write helpers.

Reuses the exact load/save pattern from scraper.py so every script/command
that touches events.json (the daily scraper, /process-sweep, ad hoc edits)
behaves identically: preserves the {last_updated, events: [...]} wrapper,
bumps last_updated on save, and always reads/writes UTF-8 (the file has
Spanish-accented characters — the platform default encoding on Windows
mangles them).
"""
import json
import os
from datetime import date

EVENTS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "events.json")


def load_events():
    """Load events.json. Returns the full {last_updated, events: [...]} dict."""
    with open(EVENTS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_events(data):
    """Save the full {last_updated, events: [...]} dict back to events.json."""
    data["last_updated"] = date.today().isoformat()
    with open(EVENTS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"events.json saved — {len(data['events'])} events — {data['last_updated']}")


def next_id(data):
    """Next available event id (max existing id + 1)."""
    return max((e["id"] for e in data["events"]), default=0) + 1


def find_event(data, name=None, venue=None, town=None):
    """
    Loose dedup lookup: returns events matching on name (case-insensitive
    substring) and, if given, venue/town.

    *** NOT SUFFICIENT FOR DEDUP ON ITS OWN. *** This is a substring matcher.
    It cannot see a stored record whose name differs from the source's by a
    plural, an ampersand vs 'and', a parenthesis, an inserted word, or a
    missing space — and library/venue titles differ that way constantly. On
    2026-08-20 relying on this let NINE already-existing events through a sweep
    as "new" (ids 459, 10, 69, 71, 28, 627, 209, 46, 685).

    Before proposing any candidate, dedup by VENUE instead:

        python check_duplicates.py --venue "<the candidate's venue>"

    That lists every record at the venue regardless of name or status; match on
    day + time + cadence. See rule 18 in CLAUDE.md. Use this function only as a
    convenience lookup once you already know what you're looking for.
    """
    results = []
    for e in data["events"]:
        if name and name.strip().lower() not in e.get("event_name", "").lower():
            continue
        if venue and venue.strip().lower() not in e.get("venue", "").lower():
            continue
        if town and town.strip().lower() != e.get("town", "").lower():
            continue
        results.append(e)
    return results
