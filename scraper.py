import json
import urllib.request
import urllib.parse
from datetime import datetime, date
import os

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

def check_seasonal_status(events):
    """
    Flag seasonal events as active or inactive based on today's date.
    Does not remove them — just updates their status.
    """
    today = date.today()
    for e in events:
        if e.get("cadence") == "Seasonal" and e.get("season_start") and e.get("season_end"):
            try:
                year = today.year
                start = date.fromisoformat(f"{year}-{e['season_start']}")
                end = date.fromisoformat(f"{year}-{e['season_end']}")
                if start <= today <= end:
                    if e.get("status") == "Seasonal - Inactive":
                        e["status"] = "Active"
                        print(f"  → Season started: {e['event_name']}")
                else:
                    if e.get("status") == "Active" and e.get("cadence") == "Seasonal":
                        e["status"] = "Seasonal - Inactive"
                        print(f"  → Season ended: {e['event_name']}")
            except (ValueError, KeyError):
                pass
    return events

def fetch_bibliocommons_events():
    """
    Fetch events from Marin County Free Library BiblioCommons calendar.
    This is the main automated source — covers all MCFL branches.
    Returns a list of new/updated events to merge.
    
    NOTE: BiblioCommons requires an API key for full access.
    Until you obtain one from marinlibrary.org, this function
    logs a reminder and skips the fetch gracefully.
    """
    print("\n── BiblioCommons (Marin County Free Library) ──")
    
    # PLACEHOLDER: Replace with your BiblioCommons API key when obtained
    API_KEY = os.environ.get("BIBLIOCOMMONS_API_KEY", "")
    
    if not API_KEY:
        print("  ℹ No BiblioCommons API key found.")
        print("  ℹ To enable automatic library updates:")
        print("  ℹ 1. Contact marinlibrary.org to request a BiblioCommons API key")
        print("  ℹ 2. Add it as a GitHub Secret named BIBLIOCOMMONS_API_KEY")
        print("  ℹ Manual events.json data will be used until then.")
        return []
    
    try:
        url = f"https://api.bibliocommons.com/v2/events?library=marinlibrary&key={API_KEY}&limit=100"
        req = urllib.request.Request(url, headers={"User-Agent": "OutAndAboutMarin/1.0"})
        with urllib.request.urlopen(req, timeout=15) as response:
            raw = json.loads(response.read().decode("utf-8"))
        
        events = raw.get("events", [])
        print(f"  ✓ Fetched {len(events)} events from BiblioCommons")
        return events
    
    except Exception as e:
        print(f"  ✗ BiblioCommons fetch failed: {e}")
        return []

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

        # Check for upcoming reopenings
        reopening_soon = lr.check_upcoming_reopenings(EVENTS_FILE)
        if reopening_soon:
            print("\n  🔔 UPCOMING REOPENINGS:")
            for r in reopening_soon:
                days_str = "TODAY" if r["days"] == 0 else f"in {r['days']} day(s)"
                print(f"  • {r['event']} at {r['venue']} — reopens {r['reopens']} ({days_str})")

        if changed:
            print(f"\n  🔔 {len(changed)} library page(s) changed — review recommended:")
            for lib in changed:
                print(f"     • {lib['name']}")
            return [f"PAGE CHANGED: {lib['name']}" for lib in changed]
        else:
            print("  ✓ All library pages unchanged since last run")
            return []

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
    
    if issues:
        lines += ["", "Sites needing manual review:"]
        for issue in issues:
            lines.append(f"  ✗ {issue}")
    else:
        lines += ["", "All library sites responding normally."]
    
    lines.append(f"\nNext run: tomorrow at 6:00 AM PT")
    
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    
    print(f"\n✓ Report saved to {report_path}")

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
    
    # Step 3: Try to fetch from BiblioCommons (needs API key)
    fetch_bibliocommons_events()
    
    # Step 4: Health check on individual library sites
    issues = check_library_websites()
    
    # Step 5: Save updated events
    print("\n── Saving ──")
    data["events"] = events
    save_events(data)
    
    # Step 6: Write run report
    generate_run_report(events, issues)
    
    print("\n" + "=" * 50)
    print("✓ Scraper complete")
    print("=" * 50)

if __name__ == "__main__":
    main()
