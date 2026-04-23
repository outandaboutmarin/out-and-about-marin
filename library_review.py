#!/usr/bin/env python3
"""
Out AND About Marin — Library Event Review Script
══════════════════════════════════════════════════
Run this script (or ask Claude to run it) to perform a full sweep of all
library websites for new, changed, or one-off children's events.

It does two things:
  1. AUTOMATED: Fetches pages that can be reliably scraped and flags
     anything that has changed since the last run.
  2. CHECKLIST: Prints a structured checklist of every library's key
     pages to verify manually or via Claude's web_fetch tool.

Usage:
  python3 library_review.py              # Full sweep
  python3 library_review.py --quick      # Only check sites that were flagged last run
  python3 library_review.py --library "Sausalito"  # Check one library only
"""

import json
import urllib.request
import urllib.error
import hashlib
import os
import sys
import argparse
from datetime import date, datetime

# ─────────────────────────────────────────────────────────────────
# LIBRARY REGISTRY
# Complete population of all libraries and their children's
# program pages. Add new libraries here as we expand coverage.
# ─────────────────────────────────────────────────────────────────

LIBRARIES = [

    # ── BELVEDERE-TIBURON ─────────────────────────────────────────
    {
        "name": "Belvedere-Tiburon Library",
        "town": "Tiburon",
        "type": "independent",
        "programs_url": "https://www.beltiblibrary.org/kids",
        "events_url": "https://www.beltiblibrary.org/events",
        "notes": "Check kids page for recurring programs. Events page for one-offs. Registration required for storytime — check RSVP form.",
        "known_programs": [
            "Baby Bounce — Monday 10:30 AM (weekly)",
            "Tuesday Toddler Storytime — Tuesday 10:15 AM (weekly)",
            "Preschool Storytime — Wednesday 3:30 PM (weekly)",
            "Bilingual Storytime with Arlette — Thursday 10:00 AM (weekly)",
            "Friday Toddler Storytime — Friday 10:15 AM (weekly)",
            "Sunday Baby Bounce — Sunday 10:30 AM (weekly)",
            "Sunday Family Storytime — Sunday 11:00 AM (bi-monthly)",
            "Tuesday Crafternoon — Tuesday 3:30 PM (weekly, school-age)",
        ],
    },

    # ── LARKSPUR ──────────────────────────────────────────────────
    {
        "name": "Larkspur Library",
        "town": "Larkspur",
        "type": "independent",
        "programs_url": "https://www.cityoflarkspur.org/333/Story-Times",
        "events_url": "https://cityoflarkspur.org/calendar.aspx?CID=24",
        "notes": "Currently temp closed (location move). Watch for reopening and new storytime schedule. Check calendar for one-off events.",
        "known_programs": [
            "Storytime — Friday 10:00 AM (weekly, TEMP CLOSED Apr 2026)",
        ],
    },

    # ── MILL VALLEY ───────────────────────────────────────────────
    {
        "name": "Mill Valley Public Library",
        "town": "Mill Valley",
        "type": "independent",
        "programs_url": "https://www.cityofmillvalley.gov/693/Storytimes",
        "events_url": "https://millvalleylibrary.libcal.com/calendar/events",
        "notes": "All outdoor at Old Mill Park Amphitheater except Saturday Family Storytime (indoor). Pop-up Storytime rotates between Boyle and Hauke Park on Fridays — check schedule PDF for location.",
        "known_programs": [
            "Cuentos con Ritmo — Monday 10:15 AM (weekly, outdoor, Old Mill Park)",
            "Sing & Stomp with Emily — Tuesday 10:15 AM (weekly, outdoor, Old Mill Park)",
            "Toddler Storytime with Miranda — Wednesday 10:15 AM (weekly, outdoor, Old Mill Park)",
            "Pop-up Storytime in the Parks — Friday 10:15 AM (weekly, rotating park)",
            "Family Storytime — Saturday 2:30 PM (weekly, indoor, Children's Room)",
        ],
    },

    # ── SAN ANSELMO ───────────────────────────────────────────────
    {
        "name": "San Anselmo Library",
        "town": "San Anselmo",
        "type": "independent",
        "programs_url": "https://www.sananselmo.gov/624/Storytime-Programs",
        "events_url": "https://www.sananselmo.gov/calendar.aspx?CID=22",
        "notes": "Storytime outdoors on Town Plaza / Library Lawn (moves to Council Chambers in rain). Check calendar for Crafternoon and Read to a Dog dates each month.",
        "known_programs": [
            "Storytime for Babies & Toddlers — Monday 10:30 AM (weekly, outdoor)",
            "Storytime for Babies & Toddlers — Wednesday 10:30 AM (weekly, outdoor)",
            "Bilingual Spanish Storytime — Wednesday 10:30 AM (1st Wednesday monthly)",
            "Storytime for Babies & Toddlers — Friday 10:30 AM (weekly, outdoor)",
            "Read to a Dog — Wednesday 3:00 PM (3rd Wednesday monthly, registration required)",
            "Crafternoon — Wednesday 3:00 PM (last Wednesday monthly)",
        ],
    },

    # ── SAN RAFAEL PUBLIC LIBRARY ─────────────────────────────────
    {
        "name": "San Rafael Public Library — Downtown",
        "town": "San Rafael",
        "type": "independent",
        "programs_url": "https://srpubliclibrary.org/events-programming/monthly-programs-youth/",
        "events_url": "https://srpubliclibrary.org/events/",
        "notes": "Three branches: Downtown, Pickleweed, Northgate. Check youth programs page for full schedule. Read to a Dog at Downtown is monthly.",
        "known_programs": [
            "Downtown Storytime / Hora de Cuentos — Friday 10:30 AM (weekly)",
            "Lego Saturdays — 2nd & 4th Saturday 11:00 AM (Northgate branch)",
            "Read to a Dog — Saturday 11:00 AM (monthly, Downtown)",
            "Northgate Storytime — Monday 10:30 AM (weekly)",
            "Pickleweed Storytime / Hora de Cuentos — Thursday 10:30 AM (weekly)",
        ],
    },

    # ── SAUSALITO ─────────────────────────────────────────────────
    {
        "name": "Sausalito Public Library",
        "town": "Sausalito",
        "type": "independent",
        "programs_url": "https://www.sausalitolibrary.org/programs/children-s-and-teen-programs",
        "events_url": "https://www.sausalitolibrary.org/programs/library-calendar",
        "notes": "All outdoor programs at Robin Sweeny Park, weather permitting. Check calendar for cancellations. Soul4Kidz = 1st Friday, In Harmony = 3rd Friday.",
        "known_programs": [
            "Storytime in the Park with Riva — Tuesday 11:00 AM (weekly, outdoor)",
            "Spanish Storytime with Ingrid — Thursday 11:00 AM (weekly, outdoor)",
            "Soul4Kidz Music — Friday 11:00 AM (1st Friday monthly, outdoor)",
            "In Harmony Music & Movement — Friday 11:30 AM (3rd Friday monthly, outdoor)",
            "Family Storytime & Art — Saturday 2:30 PM (2nd Saturday monthly, indoor)",
        ],
    },

    # ── MCFL: CIVIC CENTER ────────────────────────────────────────
    {
        "name": "MCFL — Civic Center Library",
        "town": "San Rafael",
        "type": "mcfl",
        "programs_url": "https://marinlibrary.bibliocommons.com/v2/events",
        "events_url": "https://marinlibrary.bibliocommons.com/v2/events",
        "notes": "CLOSED for Refresh April 20 – June 10, 2026. Reopens June 11. Lego Club and storytime will resume then.",
        "known_programs": [
            "Preschool & Family Storytime — Tuesday 9:30 AM (weekly, TEMP CLOSED)",
            "Preschool & Family Storytime — Thursday 9:30 AM (weekly, TEMP CLOSED)",
            "Wednesday Kids' Lego Club — Wednesday 2:30 PM (weekly, TEMP CLOSED)",
        ],
    },

    # ── MCFL: CORTE MADERA ────────────────────────────────────────
    {
        "name": "MCFL — Corte Madera Library",
        "town": "Corte Madera",
        "type": "mcfl",
        "programs_url": "https://marinlibrary.bibliocommons.com/v2/events",
        "events_url": "https://marinlibrary.bibliocommons.com/v2/events",
        "notes": "Filter BiblioCommons by Corte Madera location. LEGO Club 1st & 3rd Wednesdays. Read to a Dog with Stinson monthly on a Sunday.",
        "known_programs": [
            "Family Storytime — Tuesday 9:30 AM (weekly)",
            "LEGO Club — Wednesday 3:30 PM (1st & 3rd Wednesdays)",
            "Read to a Dog with Stinson — Sunday 2:30 PM (monthly)",
        ],
    },

    # ── MCFL: FAIRFAX ─────────────────────────────────────────────
    {
        "name": "MCFL — Fairfax Library",
        "town": "Fairfax",
        "type": "mcfl",
        "programs_url": "https://marinlibrary.bibliocommons.com/v2/events",
        "events_url": "https://marinlibrary.bibliocommons.com/v2/events",
        "notes": "Bilingual storytime runs Tuesdays AND Thursdays — two sessions each day (9:30 and 10:15). Storytime with Iris also Thursday 10:00 AM. Outdoor under oak trees, moves inside in bad weather.",
        "known_programs": [
            "Bilingual Storytime / Hora del cuento — Tue & Thu 9:30 AM + 10:15 AM (weekly)",
            "Storytime with Iris — Thursday 10:00 AM (weekly, outdoor)",
        ],
    },

    # ── MCFL: MARIN CITY ──────────────────────────────────────────
    {
        "name": "MCFL — Marin City Library",
        "town": "Marin City",
        "type": "mcfl",
        "programs_url": "https://marinlibrary.bibliocommons.com/v2/events",
        "events_url": "https://marinlibrary.bibliocommons.com/v2/events",
        "notes": "Wiggles & Wonder is multilingual. Check BiblioCommons for any additional programs.",
        "known_programs": [
            "Wiggles & Wonder Storytime — Wednesday 10:15 AM (weekly)",
        ],
    },

    # ── MCFL: NOVATO ──────────────────────────────────────────────
    {
        "name": "MCFL — Novato Library",
        "town": "Novato",
        "type": "mcfl",
        "programs_url": "https://marinlibrary.bibliocommons.com/v2/events",
        "events_url": "https://marinlibrary.bibliocommons.com/v2/events",
        "notes": "Books & Bubbles is bi-weekly (every other Wednesday). Stories & Rhyme Wiggle Time is weekly Tuesday.",
        "known_programs": [
            "Stories & Rhyme Wiggle Time — Tuesday 10:00 AM (weekly)",
            "Books & Bubbles — Wednesday 10:00 AM (bi-weekly)",
        ],
    },

    # ── MCFL: POINT REYES ─────────────────────────────────────────
    {
        "name": "MCFL — Point Reyes Library",
        "town": "Point Reyes Station",
        "type": "mcfl",
        "programs_url": "https://marinlibrary.bibliocommons.com/v2/events",
        "events_url": "https://marinlibrary.bibliocommons.com/v2/events",
        "notes": "Small branch — Canta Conmigo is the main weekly children's program. Check for seasonal/special events.",
        "known_programs": [
            "Canta Conmigo! — Monday 10:30 AM (weekly)",
        ],
    },

    # ── MCFL: SOUTH NOVATO ────────────────────────────────────────
    {
        "name": "MCFL — South Novato Library",
        "town": "Novato",
        "type": "mcfl",
        "programs_url": "https://marinlibrary.bibliocommons.com/v2/events",
        "events_url": "https://marinlibrary.bibliocommons.com/v2/events",
        "notes": "Story Time with Mr. Brian is weekly Saturday. Música y Movimiento with Ingrid is 2nd, 4th, and 5th Wednesdays.",
        "known_programs": [
            "Story Time with Mr. Brian — Saturday 11:00 AM (weekly)",
            "Música y Movimiento with Ingrid — Wednesday 11:00 AM (2nd, 4th & 5th Wednesdays)",
        ],
    },

    # ── MCFL: BOLINAS ─────────────────────────────────────────────
    {
        "name": "MCFL — Bolinas Library",
        "town": "Bolinas",
        "type": "mcfl",
        "programs_url": "https://marinlibrary.org/locations/mb/",
        "events_url": "https://marinlibrary.bibliocommons.com/v2/events",
        "notes": "Small branch — no regular children's programming. Just reopened April 16, 2026 after Refresh. Watch for any new children's programs post-refresh.",
        "known_programs": [],
    },

    # ── MCFL: INVERNESS ───────────────────────────────────────────
    {
        "name": "MCFL — Inverness Library",
        "town": "Inverness",
        "type": "mcfl",
        "programs_url": "https://marinlibrary.org/locations/mi/",
        "events_url": "https://marinlibrary.bibliocommons.com/v2/events",
        "notes": "Small branch — no regular children's programming. Hosts occasional special events (e.g. Día de los Niños). Check BiblioCommons for upcoming one-offs.",
        "known_programs": [],
    },

    # ── MCFL: STINSON BEACH ───────────────────────────────────────
    {
        "name": "MCFL — Stinson Beach Library",
        "town": "Stinson Beach",
        "type": "mcfl",
        "programs_url": "https://marinlibrary.org/locations/ms/",
        "events_url": "https://marinlibrary.bibliocommons.com/v2/events",
        "notes": "Small branch — no regular children's programming. Check BiblioCommons for occasional special events.",
        "known_programs": [],
    },
]

# ─────────────────────────────────────────────────────────────────
# UNPREDICTABLE EVENTS REGISTRY
# Events with no fixed week-of-month pattern whose specific dates
# must be looked up each month and added as one-offs to events.json.
# The daily scraper checks these URLs for new dates and logs them.
# ─────────────────────────────────────────────────────────────────

UNPREDICTABLE_EVENTS = [
    {
        "name": "Read to a Dog — San Rafael Downtown",
        "event_id": 26,
        "organization": "San Rafael Public Library",
        "venue": "San Rafael Public Library - Downtown",
        "town": "San Rafael",
        "address": "1100 E Street, San Rafael, CA 94901",
        "day_of_week": "Saturday",
        "time": "11:00 AM",
        "ages": "5+ yrs",
        "type": "Kids Programs",
        "lookup_url": "https://srpubliclibrary.org/events/",
        "lookup_note": "Search 'read to a dog' on SRPL events page. Date varies each month — not a fixed Saturday.",
        "template": {
            "organization": "San Rafael Public Library",
            "venue": "San Rafael Public Library - Downtown",
            "event_name": "Read to a Dog",
            "type": "Kids Programs",
            "time": "11:00 AM",
            "time_of_day": "Afternoon",
            "town": "San Rafael",
            "address": "1100 E Street, San Rafael, CA 94901",
            "ages": "5+ yrs",
            "cost": "Free",
            "indoor_outdoor": "Indoor",
            "active_sedentary": "Sedentary",
            "cadence": "One-off",
            "status": "Active",
            "featured": False,
            "description": "Practice reading aloud to friendly therapy dogs from the Marin Humane Society SHARE a Book program. Emerging readers grades 1-3. Sign up at children's desk morning of event. Limited spots.",
            "registration": "Not required — sign up at children's desk day-of",
            "website": "https://srpubliclibrary.org",
            "notes": "Date varies monthly — check srpubliclibrary.org/events for next date.",
        }
    },
    {
        "name": "Family Storytime — Belvedere-Tiburon (Sunday bi-monthly)",
        "event_id": 31,
        "organization": "Belvedere-Tiburon Library",
        "venue": "Belvedere-Tiburon Library",
        "town": "Tiburon",
        "address": "1501 Tiburon Blvd, Tiburon, CA 94920",
        "day_of_week": "Sunday",
        "time": "11:00 AM",
        "ages": "All ages",
        "type": "Library",
        "lookup_url": "https://www.beltiblibrary.org/events",
        "lookup_note": "Search 'Family Storytime' on BelTib events page. Bi-monthly on select Sundays — dates not predictable.",
        "template": {
            "organization": "Belvedere-Tiburon Library",
            "venue": "Belvedere-Tiburon Library",
            "event_name": "Family Storytime",
            "type": "Library",
            "time": "11:00 AM",
            "time_of_day": "Morning",
            "town": "Tiburon",
            "address": "1501 Tiburon Blvd, Tiburon, CA 94920",
            "ages": "All ages",
            "cost": "Free",
            "indoor_outdoor": "Indoor",
            "active_sedentary": "Sedentary",
            "cadence": "One-off",
            "status": "Active",
            "featured": False,
            "description": "Stories and songs the whole family will enjoy together. Bi-monthly on select Sundays.",
            "registration": "Not required",
            "website": "https://beltiblibrary.org",
            "notes": "Bi-monthly — check beltiblibrary.org/events for specific dates.",
        }
    },
    {
        "name": "Read to a Dog with Stinson — Corte Madera (monthly Sunday)",
        "event_id": 43,
        "organization": "Marin County Free Library",
        "venue": "Corte Madera Library",
        "town": "Corte Madera",
        "address": "707 Meadowsweet Drive, Corte Madera, CA 94925",
        "day_of_week": "Sunday",
        "time": "2:30 PM",
        "ages": "5-12 yrs",
        "type": "Kids Programs",
        "lookup_url": "https://marinlibrary.bibliocommons.com/v2/events",
        "lookup_note": "Filter BiblioCommons by Corte Madera location and search 'Read to a Dog'. Monthly on a Sunday — specific date varies. NOTE: Corte Madera Library closed for Refresh early May–mid-June 2026.",
        "template": {
            "organization": "Marin County Free Library",
            "venue": "Corte Madera Library",
            "event_name": "Read to a Dog with Stinson",
            "type": "Kids Programs",
            "time": "2:30 PM",
            "time_of_day": "Afternoon",
            "town": "Corte Madera",
            "address": "707 Meadowsweet Drive, Corte Madera, CA 94925",
            "ages": "5-12 yrs",
            "cost": "Free",
            "indoor_outdoor": "Indoor",
            "active_sedentary": "Sedentary",
            "cadence": "One-off",
            "status": "Active",
            "featured": False,
            "description": "Practice reading aloud to Stinson, a therapy dog trained to read with kids. Kindergarten and up welcome.",
            "registration": "Not required",
            "website": "https://marinlibrary.org",
            "notes": "Monthly on a Sunday — date varies. Check marinlibrary.bibliocommons.com for next date.",
        }
    },
]


def check_unpredictable_events(events_file="events.json"):
    """
    For each unpredictable event, check whether we have upcoming one-off
    dates already loaded in events.json. If any are missing for the next
    60 days, log them as needing manual lookup.
    """
    print("\n── Unpredictable Events — One-off Date Check ──")

    if not os.path.exists(events_file):
        print("  ⚠ events.json not found")
        return []

    with open(events_file) as f:
        data = json.load(f)

    today = date.today()
    in_60 = date(today.year, today.month, today.day)
    # 60 days out
    from datetime import timedelta
    in_60 = today + timedelta(days=60)

    existing_oneoffs = {
        e["event_name"] + "|" + e.get("event_date","")
        for e in data.get("events", [])
        if e.get("cadence") == "One-off" and e.get("event_date")
    }

    needs_lookup = []

    for ue in UNPREDICTABLE_EVENTS:
        # Find any active one-offs for this event within next 60 days
        upcoming = [
            e for e in data.get("events", [])
            if e.get("cadence") == "One-off"
            and e.get("event_name") == ue["template"]["event_name"]
            and e.get("venue") == ue["template"]["venue"]
            and e.get("event_date")
            and today <= date.fromisoformat(e["event_date"]) <= in_60
        ]

        if upcoming:
            dates_str = ", ".join(e["event_date"] for e in upcoming)
            print(f"  ✓ {ue['name']}")
            print(f"    → Upcoming date(s) loaded: {dates_str}")
        else:
            print(f"  🔔 {ue['name']}")
            print(f"    → NO upcoming dates in next 60 days — needs lookup!")
            print(f"    → Check: {ue['lookup_url']}")
            print(f"    → Note: {ue['lookup_note']}")
            needs_lookup.append(ue)

    if needs_lookup:
        print(f"\n  ⚠ {len(needs_lookup)} event(s) need one-off dates added to events.json")
        print("  ℹ To add: open a chat with Claude and say:")
        print('  ℹ "Please look up upcoming dates for unpredictable events and add them to events.json"')

    return needs_lookup


def generate_oneoff_entry(template, event_date_str, expires_str=None):
    """
    Helper to generate a complete one-off event entry from a template.
    Call this when you have a confirmed date to add.

    Args:
        template: dict from UNPREDICTABLE_EVENTS[n]["template"]
        event_date_str: "YYYY-MM-DD"
        expires_str: "YYYY-MM-DD" (defaults to event_date)
    """
    import calendar as cal
    d = date.fromisoformat(event_date_str)
    day_name = d.strftime("%A")

    entry = dict(template)
    entry["day"] = day_name
    entry["event_date"] = event_date_str
    entry["expires"] = expires_str or event_date_str
    entry["season_start"] = ""
    entry["season_end"] = ""
    return entry


# ─────────────────────────────────────────────────────────────────
# AUTOMATED: PAGE HASH CHECKER
# Detects when a library's programs page has changed since last run
# ─────────────────────────────────────────────────────────────────

HASH_FILE = "library_page_hashes.json"

def load_hashes():
    if os.path.exists(HASH_FILE):
        with open(HASH_FILE) as f:
            return json.load(f)
    return {}

def save_hashes(hashes):
    with open(HASH_FILE, "w") as f:
        json.dump(hashes, f, indent=2)

def fetch_page_hash(url):
    """Fetch a URL and return an MD5 hash of its content."""
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "OutAndAboutMarin/1.0 (library schedule checker)"}
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            content = resp.read()
            return hashlib.md5(content).hexdigest()
    except Exception as e:
        return None

def check_for_page_changes(libraries, previous_hashes):
    """
    Compare current page hashes against stored hashes.
    Returns list of libraries whose pages have changed.
    """
    changed = []
    new_hashes = dict(previous_hashes)

    print("\n── Checking for page changes ──")
    for lib in libraries:
        url = lib["programs_url"]
        name = lib["name"]
        current_hash = fetch_page_hash(url)

        if current_hash is None:
            print(f"  ⚠ {name} — could not fetch page")
            continue

        prev_hash = previous_hashes.get(url)
        if prev_hash is None:
            print(f"  🆕 {name} — first run, baseline recorded")
            new_hashes[url] = current_hash
        elif current_hash != prev_hash:
            print(f"  🔔 {name} — PAGE CHANGED since last run!")
            changed.append(lib)
            new_hashes[url] = current_hash
        else:
            print(f"  ✓ {name} — no change")

    return changed, new_hashes

# ─────────────────────────────────────────────────────────────────
# AUTOMATED: TEMP CLOSURE MONITOR
# Flags closures that are about to expire (reopen within 7 days)
# ─────────────────────────────────────────────────────────────────

def check_upcoming_reopenings(events_file="events.json"):
    """Flag events that are temp closed but reopening within 7 days."""
    if not os.path.exists(events_file):
        return []

    with open(events_file) as f:
        data = json.load(f)

    today = date.today()
    reopening_soon = []

    for e in data.get("events", []):
        if e.get("status") != "Temp. closed":
            continue
        notes = e.get("notes", "")
        import re
        match = re.search(r"[Rr]eopen(?:ing|s)\s+([A-Z][a-z]+ \d{1,2}(?:, \d{4})?)", notes)
        if match:
            try:
                date_str = match.group(1)
                if "," not in date_str:
                    date_str += f", {today.year}"
                reopen_date = datetime.strptime(date_str, "%B %d, %Y").date()
                days_away = (reopen_date - today).days
                if 0 <= days_away <= 7:
                    reopening_soon.append({
                        "event": e["event_name"],
                        "venue": e["venue"],
                        "reopens": reopen_date.strftime("%B %d"),
                        "days": days_away
                    })
            except ValueError:
                pass

    return reopening_soon

# ─────────────────────────────────────────────────────────────────
# REVIEW CHECKLIST PRINTER
# Structured output for Claude or human to work through
# ─────────────────────────────────────────────────────────────────

def print_review_checklist(libraries, changed_libs=None, filter_name=None):
    """Print a structured checklist for manual/Claude review."""

    changed_names = {lib["name"] for lib in (changed_libs or [])}

    print("\n" + "═" * 60)
    print("OUT AND ABOUT MARIN — LIBRARY REVIEW CHECKLIST")
    print(f"Date: {date.today().strftime('%B %d, %Y')}")
    print("═" * 60)
    print("""
INSTRUCTIONS FOR CLAUDE:
For each library below, use web_fetch on the programs_url and
events_url. Compare what you find against known_programs. Flag:
  [NEW]     A recurring program not in known_programs
  [CHANGED] A known program with different day/time/status
  [ONEOFF]  A one-off children's event within the next 60 days
  [CLOSED]  A program that appears to have been discontinued
  [OK]      No changes found
""")

    for lib in libraries:
        if filter_name and filter_name.lower() not in lib["name"].lower():
            continue

        changed_flag = " 🔔 PAGE CHANGED" if lib["name"] in changed_names else ""
        print(f"\n{'─' * 60}")
        print(f"📚 {lib['name']} — {lib['town']}{changed_flag}")
        print(f"   Programs: {lib['programs_url']}")
        print(f"   Events:   {lib['events_url']}")
        print(f"   Notes:    {lib['notes']}")

        if lib["known_programs"]:
            print(f"\n   Known recurring programs:")
            for p in lib["known_programs"]:
                print(f"     • {p}")
        else:
            print(f"\n   Known recurring programs: None — watch for new additions")

        print(f"\n   → Review status: [ ] OK  [ ] Changes found")
        print(f"   → Changes/new events:")
        print(f"     ___________________________________________________")
        print(f"     ___________________________________________________")

    print("\n" + "═" * 60)
    print("END OF CHECKLIST")
    print("═" * 60)

# ─────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Out AND About Marin — Library Review")
    parser.add_argument("--quick", action="store_true", help="Only check changed pages")
    parser.add_argument("--library", type=str, help="Filter to one library by name")
    parser.add_argument("--checklist-only", action="store_true", help="Print checklist without fetching")
    args = parser.parse_args()

    print("═" * 60)
    print("Out AND About Marin — Library Review Script")
    print(f"Running: {date.today().strftime('%B %d, %Y')}")
    print("═" * 60)

    # Check unpredictable events for missing one-off dates
    check_unpredictable_events()

    # Check for upcoming reopenings
    reopening_soon = check_upcoming_reopenings()
    if reopening_soon:
        print("\n🔔 UPCOMING REOPENINGS (within 7 days):")
        for r in reopening_soon:
            days_str = "TODAY" if r["days"] == 0 else f"in {r['days']} day(s)"
            print(f"   • {r['event']} at {r['venue']} — reopens {r['reopens']} ({days_str})")
        print("   → Update these events' status to 'Active' in events.json")

    if args.checklist_only:
        print_review_checklist(LIBRARIES, filter_name=args.library)
        return

    # Run page hash checks
    previous_hashes = load_hashes()
    changed_libs, new_hashes = check_for_page_changes(LIBRARIES, previous_hashes)
    save_hashes(new_hashes)

    # If --quick, only show changed libraries
    if args.quick and changed_libs:
        print(f"\n⚡ Quick mode: {len(changed_libs)} library page(s) changed")
        print_review_checklist(changed_libs, changed_libs, filter_name=args.library)
    elif args.quick and not changed_libs:
        print("\n✓ Quick mode: No page changes detected. Nothing to review today.")
    else:
        # Full checklist
        print_review_checklist(LIBRARIES, changed_libs, filter_name=args.library)

    # Summary
    print(f"\n✓ Review complete — {len(LIBRARIES)} libraries in population")
    print(f"✓ Hash file updated: {HASH_FILE}")
    if changed_libs:
        print(f"🔔 {len(changed_libs)} page(s) changed since last run:")
        for lib in changed_libs:
            print(f"   • {lib['name']}")

if __name__ == "__main__":
    main()
