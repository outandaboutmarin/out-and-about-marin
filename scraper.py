import json
import urllib.request
import urllib.parse
from datetime import datetime, date
import os
import re
import calendar

# ─────────────────────────────────────────────
# Out AND About Marin — Daily Event Scraper
# Runs every morning via GitHub Actions
# Updates events.json with fresh data
# ─────────────────────────────────────────────

EVENTS_FILE = "events.json"
TODAY = date.today().isoformat()

def load_existing_events():
    """Load the current events.json file."""
    if os.path.exists(EVENTS_FILE):
        with open(EVENTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"last_updated": TODAY, "events": []}

def save_events(data):
    """Save updated events back to events.json."""
    data["last_updated"] = TODAY
    with open(EVENTS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"✓ events.json updated — {len(data['events'])} events — {TODAY}")

def remove_expired_events(events):
    """Remove one-off events whose expiry date has passed."""
    today = date.today()
    before = len(events)
    events = [
        e for e in events
        if not e.get("expires") or date.fromisoformat(e["expires"]) >= today
    ]
    removed = before - len(events)
    if removed > 0:
        print(f"✓ Removed {removed} expired event(s)")
    return events

MONTH_NAMES = {
    "January": 1, "February": 2, "March": 3, "April": 4, "May": 5, "June": 6,
    "July": 7, "August": 8, "September": 9, "October": 10, "November": 11,
    "December": 12,
}


def parse_season_date(value, year, is_end):
    """
    Parse a season_start/season_end value into a date.

    Mirrors parseSeasonDate() in index.html (~line 3549) exactly, because the
    frontend and this script MUST agree on what a season means:
      - "MM/DD" (the documented format, e.g. "06/01")
      - a bare month name ("May", "October"), which resolves to the FIRST day
        of that month for a start and the LAST day for an end
      - "MM-DD" is also accepted here as a forgiving extra; the frontend does
        not accept it, so never write it into events.json.

    Returns None if the value cannot be parsed at all.

    WHY THIS EXISTS: the previous code did date.fromisoformat(f"{year}-{value}"),
    which for the documented "06/01" builds "2026-06/01" - not valid ISO. That
    raised ValueError, a bare `except (ValueError, KeyError): pass` swallowed
    it, and the record was silently skipped. Confirmed 2026-08-13: ALL 12
    Seasonal records failed this way, so no seasonal event has ever been
    flipped by the scraper. index.html parsed them correctly the whole time,
    which is why the bug stayed invisible - the display side worked.
    """
    if not value:
        return None
    value = str(value).strip()

    if value in MONTH_NAMES:
        m = MONTH_NAMES[value]
        if is_end:
            last_day = calendar.monthrange(year, m)[1]
            return date(year, m, last_day)
        return date(year, m, 1)

    m = re.fullmatch(r"(\d{1,2})[/-](\d{1,2})", value)
    if m:
        month, day = int(m.group(1)), int(m.group(2))
        try:
            return date(year, month, day)
        except ValueError:
            return None
    return None


def check_seasonal_status(events):
    """
    Flag seasonal events as active or inactive based on today's date.
    Does not remove them - just updates their status.
    """
    today = date.today()
    unparsed = []

    for e in events:
        if e.get("cadence") != "Seasonal":
            continue

        raw_start, raw_end = e.get("season_start"), e.get("season_end")
        if not raw_start or not raw_end:
            continue

        start = parse_season_date(raw_start, today.year, is_end=False)
        end = parse_season_date(raw_end, today.year, is_end=True)

        if start is None or end is None:
            # Do NOT silently skip - an unparseable season means this record
            # will never flip, which is exactly the failure this fix removes.
            unparsed.append(
                f"{e.get('event_name', '?')} (id {e.get('id')}): "
                f"season_start={raw_start!r} season_end={raw_end!r}"
            )
            continue

        # A season written "11/01"-"02/28" wraps the new year; treat any end
        # earlier than its start as spanning into next year rather than as an
        # empty window that would retire the event immediately.
        in_season = (start <= today <= end) if start <= end else (today >= start or today <= end)

        if in_season and e.get("status") == "Seasonal - Inactive":
            e["status"] = "Active"
            print(f"  \u2192 Season started: {e['event_name']}")
        elif not in_season and e.get("status") == "Active":
            e["status"] = "Seasonal - Inactive"
            print(f"  \u2192 Season ended: {e['event_name']}")

    if unparsed:
        print(f"\n  \u26a0 {len(unparsed)} seasonal record(s) have an unparseable season "
              f"and will NEVER flip - fix the data:")
        for u in unparsed:
            print(f"     \u2022 {u}")

    return events


def check_library_websites():
    """
    Check all library program pages for changes using the
    library_review.py hash-based detection system.
    Returns list of sites with issues for the run report.
    """
    print("\n── Library Page Change Detection ──")

    try:
        import importlib.util, sys, hashlib
        spec = importlib.util.spec_from_file_location(
            "library_review",
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "library_review.py")
        )
        lr = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(lr)

        prev_hashes = lr.load_hashes()
        changed, new_hashes = lr.check_for_page_changes(lr.LIBRARIES, prev_hashes)
        lr.save_hashes(new_hashes)

        # Check for upcoming reopenings.
        # These used to be printed here and nowhere else — not added to
        # `issues`, so never written into scraper_log.txt and never surfaced
        # anywhere a human would look. Found 2026-08-15 while wiring up
        # notifications; a branch reopening inside 7 days is exactly the kind
        # of thing worth a nudge, so it now travels with the other findings.
        reopening_soon = lr.check_upcoming_reopenings(EVENTS_FILE)
        if reopening_soon:
            print("\n  🔔 UPCOMING REOPENINGS:")
            for r in reopening_soon:
                days_str = "TODAY" if r["days"] == 0 else f"in {r['days']} day(s)"
                print(f"  • {r['event']} at {r['venue']} — reopens {r['reopens']} ({days_str})")

        # Check unpredictable events for missing one-off dates
        needs_lookup = lr.check_unpredictable_events(EVENTS_FILE)

        issues = []
        if changed:
            print(f"\n  🔔 {len(changed)} library page(s) changed — review recommended:")
            for lib in changed:
                print(f"     • {lib['name']}")
            issues += [f"PAGE CHANGED: {lib['name']}" for lib in changed]
        else:
            print("  ✓ All library pages unchanged since last run")

        if needs_lookup:
            issues += [f"NEEDS ONE-OFF DATE: {e['name']}" for e in needs_lookup]

        if reopening_soon:
            issues += [
                f"REOPENING SOON: {r['event']} at {r['venue']} — reopens {r['reopens']}"
                + (" (TODAY)" if r["days"] == 0 else f" (in {r['days']} day(s))")
                for r in reopening_soon
            ]

        return issues

    except Exception as e:
        print(f"  ⚠ library_review.py not found or failed: {e}")
        print("  ℹ Falling back to basic health check")
        issues = []
        for url, name in [
            ("https://beltiblibrary.org", "Belvedere-Tiburon"),
            ("https://srpubliclibrary.org", "San Rafael"),
            ("https://sausalitolibrary.org", "Sausalito"),
            ("https://marinlibrary.org", "MCFL"),
        ]:
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "OutAndAboutMarin/1.0"})
                with urllib.request.urlopen(req, timeout=10) as r:
                    if r.status != 200:
                        issues.append(f"{name}: status {r.status}")
            except Exception as ex:
                issues.append(f"{name}: {str(ex)[:50]}")
        return issues

def generate_run_report(events, issues):
    """Write a simple log file summarising what happened this run."""
    report_path = "scraper_log.txt"
    lines = [
        f"Out AND About Marin — Scraper Run Report",
        f"Date: {TODAY}",
        f"Time: {datetime.now().strftime('%H:%M:%S')}",
        f"",
        f"Total events in events.json: {len(events)}",
        f"Active events: {len([e for e in events if e.get('status') == 'Active'])}",
        f"Temp. closed: {len([e for e in events if e.get('status') == 'Temp. closed'])}",
        f"",
        f"Events by type:",
    ]
    
    # Count by type
    type_counts = {}
    for e in events:
        t = e.get("type", "Unknown")
        type_counts[t] = type_counts.get(t, 0) + 1
    for t, count in sorted(type_counts.items()):
        lines.append(f"  {t}: {count}")
    
    lines += [
        f"",
        f"Events by town:",
    ]
    town_counts = {}
    for e in events:
        town = e.get("town", "Unknown")
        town_counts[town] = town_counts.get(town, 0) + 1
    for town, count in sorted(town_counts.items()):
        lines.append(f"  {town}: {count}")
    
    page_changes = [i for i in issues if i.startswith("PAGE CHANGED")]
    date_lookups = [i for i in issues if i.startswith("NEEDS ONE-OFF DATE")]
    reopenings = [i for i in issues if i.startswith("REOPENING SOON")]

    if reopenings:
        lines += ["", "Libraries reopening within 7 days:"]
        for issue in reopenings:
            lines.append(f"  🔔 {issue}")

    if page_changes:
        lines += ["", "Library pages changed — review recommended:"]
        for issue in page_changes:
            lines.append(f"  🔔 {issue}")
    else:
        lines += ["", "All library pages unchanged since last run."]

    if date_lookups:
        lines += ["", "Unpredictable events needing one-off dates added:"]
        for issue in date_lookups:
            lines.append(f"  🔔 {issue}")
        lines.append("  → Open a chat with Claude and say:")
        lines.append("  → \"Please look up upcoming dates for unpredictable events and add them to events.json\"")
    else:
        lines += ["", "All unpredictable events have upcoming dates loaded. ✓"]
    
    lines.append(f"\nNext run: tomorrow at 6:00 AM PT")

    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"\n✓ Report saved to {report_path}")

    write_findings(date_lookups, reopenings)


# Findings the workflow turns into a GitHub Issue. Deliberately a SUBSET of
# what goes in the log: only things a human has to act on.
FINDINGS_FILE = "scraper_findings.json"

# " (TODAY)" / " (in 5 day(s))" — display detail, deliberately excluded from
# the change signature so a countdown ticking down doesn't read as new news.
COUNTDOWN_RE = re.compile(r"\s*\((?:TODAY|in \d+ day\(s\))\)\s*$")

def write_findings(date_lookups, reopenings):
    """
    Emit the actionable findings for the notification step in daily.yml.

    PAGE CHANGED is deliberately excluded. The hash check MD5s the entire raw
    page, so a rotating banner counts as a change; across the two scheduled
    runs on 2026-08-14/15 it flagged 11 and 13 of 16 pages against a FRESH
    baseline. Notifying daily on that trains you to ignore the notification,
    which then hides the rare finding that matters. It stays in the log for
    the weekly sweep to read.

    `signature` is what the workflow compares against the open issue to decide
    whether anything actually changed — if it matches, the run stays silent.
    Each finding therefore carries a `key` separate from its display `text`:
    the key strips the "(in N day(s))" countdown, which otherwise ticks down
    every morning and makes an unchanged reopening look like a new finding
    every single day — the daily-email problem this design exists to avoid.
    """
    findings = []
    for item in reopenings:
        text = item[len("REOPENING SOON: "):]
        findings.append({
            "kind": "reopening",
            "text": text,
            "key": COUNTDOWN_RE.sub("", text).strip(),
        })
    for item in date_lookups:
        text = item[len("NEEDS ONE-OFF DATE: "):]
        findings.append({"kind": "needs_date", "text": text, "key": text})

    payload = {
        "generated": TODAY,
        "count": len(findings),
        "findings": findings,
        "signature": " || ".join(sorted(f"{f['kind']}:{f['key']}" for f in findings)),
    }
    with open(FINDINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
    print(f"✓ {len(findings)} actionable finding(s) written to {FINDINGS_FILE}")

def main():
    print("=" * 50)
    print("Out AND About Marin — Daily Scraper")
    print(f"Running: {TODAY}")
    print("=" * 50)
    
    # Load existing data
    data = load_existing_events()
    events = data.get("events", [])
    print(f"\n✓ Loaded {len(events)} existing events")
    
    # Step 1: Remove expired one-off events
    print("\n── Checking for expired events ──")
    events = remove_expired_events(events)
    
    # Step 2: Update seasonal event status
    print("\n── Checking seasonal event status ──")
    events = check_seasonal_status(events)
    
    # Step 3: Health check on individual library sites
    issues = check_library_websites()
    
    # Step 4: Save updated events
    print("\n── Saving ──")
    data["events"] = events
    save_events(data)
    
    # Step 5: Write run report
    generate_run_report(events, issues)
    
    print("\n" + "=" * 50)
    print("✓ Scraper complete")
    print("=" * 50)

if __name__ == "__main__":
    main()
