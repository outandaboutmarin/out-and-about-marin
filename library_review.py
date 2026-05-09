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
        "filtered_events_url": "https://www.beltiblibrary.org/events?ages=Infants+%26+Toddlers%2CSchool+age",
        "notes": "Check kids page for recurring programs. Events page for one-offs. Registration required for storytime — check RSVP form. Auto-fetched via fetch_belvedere_tiburon_events() in weekly sweep.",
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
        "ical_url": "https://www.ci.larkspur.ca.us/common/modules/iCalendar/iCalendar.aspx?catID=24&feed=calendar",
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
# ADDITIONAL EVENT SOURCES
# Community blogs, rec centers, and event aggregators to check
# weekly for new one-off children's events
# ─────────────────────────────────────────────────────────────────

ADDITIONAL_SOURCES = [
    {
        "name": "Marin Mommies Calendar",
        "url": "https://www.marinmommies.com/calendar",
        "notes": "Community-submitted family events calendar. Check weekly for Marin-specific children's events. Filter for Marin County only.",
    },
    {
        "name": "Strawberry Recreation District — Junior Berries",
        "url": "https://strawberry.marin.org/recreation_early",
        "notes": "Early childhood programs ages 2-6. Mostly paid session-based. Check for drop-in options and new seasonal programs.",
    },
    {
        "name": "Mill Valley Community Center — Special Events",
        "url": "https://www.cityofmillvalley.gov/289/Special-Events",
        "notes": "One-off community events in Mill Valley. Check monthly for family-friendly daytime events.",
    },
    {
        "name": "Sausalito City Events",
        "url": "https://www.sausalito.org/events",
        "notes": "City of Sausalito events calendar. Check monthly for family-friendly events.",
    },
    {
        "name": "Enjoy Mill Valley Blog",
        "url": "https://enjoymillvalley.com/enjoy-mill-valley-blog/",
        "notes": "Mill Valley community blog with local event roundups. Check weekly.",
    },
    {
        "name": "Marin Buzz Newsletter",
        "url": "https://marinbuzz.com/",
        "notes": "Marin County community newsletter. Check weekly for family events and announcements.",
    },
    {
        "name": "Ronnie's Awesome List",
        "url": "https://www.ronniesawesomelist.com/",
        "notes": "Weekly kids event roundup for Marin and Bay Area. Excellent source for one-off children's events. Check every Thursday when newsletter drops.",
    },
    {
        "name": "Sweetwater Music Hall — Family Events",
        "url": "https://sweetwatermusichall.org/events/",
        "notes": "Check monthly for daytime all-ages children's events. Filter for: Sing & Stompers, School of Rock, Rock and Roll Playhouse, and any daytime shows.",
    },
    {
        "name": "Marin Country Mart Events",
        "url": "https://www.marincountrymart.com/events",
        "notes": "Check monthly for special Mart Littles events and seasonal programming beyond the regular weekly schedule.",
    },
    {
        "name": "Osher Marin JCC — Tot Pool Party & Family Programs",
        "url": "https://www.marinjcc.org/preschool/tot-pool-party/",
        "notes": "Monthly Tot Pool Party runs May–October on specific Fridays 3:30–5 PM. Check JCC website each month for exact date. Also check for any new JBaby or family programs. Members free, non-members $15/$20.",
    },
]

def check_additional_sources(previous_hashes):
    """Check additional event sources for page changes."""
    print("\n── Additional Event Sources — Change Detection ──")
    changed = []
    new_hashes = dict(previous_hashes)

    for source in ADDITIONAL_SOURCES:
        url = source["url"]
        name = source["name"]
        current_hash = fetch_page_hash(url)

        if current_hash is None:
            print(f"  ⚠ {name} — could not fetch")
            continue

        prev_hash = previous_hashes.get(url)
        if prev_hash is None:
            print(f"  🆕 {name} — baseline recorded")
            new_hashes[url] = current_hash
        elif current_hash != prev_hash:
            print(f"  🔔 {name} — PAGE CHANGED")
            changed.append(source)
            new_hashes[url] = current_hash
        else:
            print(f"  ✓ {name} — no change")

    return changed, new_hashes


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
        "disabled": True,  # Marked resolved 2026-05-03 — program no longer listed on SRPL Monthly Programs page; revisit if it returns
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
        "disabled": True,  # Marked resolved 2026-05-03 — bi-monthly schedule too sporadic to track; revisit if cadence stabilizes
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
        # Skip entries marked as resolved/disabled
        if ue.get("disabled"):
            print(f"  ⊘ {ue['name']} — skipped (disabled)")
            continue

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

    # Check additional event sources
    add_changed, new_hashes = check_additional_sources(new_hashes)
    if add_changed:
        print(f"\n  🔔 {len(add_changed)} additional source(s) changed:")
        for s in add_changed:
            print(f"     • {s['name']}")
            print(f"       Note: {s['notes']}")

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

# ─────────────────────────────────────────────────────────────────
# WEEKLY EVENT SWEEP
# Produces a consolidated review report of suggested new events
# for approval. The actual fetching of Marin Mommies and other
# sources is done by Claude in chat using web_fetch tools.
#
# To trigger: open a chat with Claude and say:
# "Please run the weekly event sweep"
#
# Claude will:
#   1. Fetch Marin Mommies calendar for next 14 days
#   2. Check Sweetwater for new family events
#   3. Check Strawberry Rec calendar
#   4. Check all other sources in ADDITIONAL_SOURCES
#   5. Filter for Marin-specific family events
#   6. Produce a consolidated list for your approval
#
# This file contains the filter logic and known events list
# so Claude knows what to look for and what to skip.
# ─────────────────────────────────────────────────────────────────

# Towns we care about — filter out non-Marin events
MARIN_TOWNS = [
    "tiburon", "belvedere", "mill valley", "sausalito", "corte madera",
    "larkspur", "san anselmo", "san rafael", "fairfax", "novato",
    "marin city", "point reyes", "inverness", "bolinas", "stinson beach",
    "muir beach", "nicasio", "woodacre", "san geronimo", "kentfield",
    "greenbrae", "ross", "strawberry", "tomales", "marshall", "olema",
    "west marin", "marin", "marinwood"
]

# Keywords that suggest a children/family event
FAMILY_KEYWORDS = [
    "kids", "children", "child", "family", "families", "toddler", "baby",
    "babies", "preschool", "storytime", "story time", "playgroup", "play group",
    "music", "craft", "arts", "sing", "dance", "puppet", "nature", "farm",
    "animals", "outdoor", "festival", "fair", "carnival", "halloween",
    "holiday", "camp", "movie", "film", "pool", "swim", "splash",
    "ages 0", "ages 1", "ages 2", "ages 3", "ages 4", "ages 5",
    "all ages", "0-5", "0-3", "0-12", "little ones", "little one",
    "drop-in", "drop in", "free"
]

# Events we already have — avoid duplicates
KNOWN_EVENT_NAMES = [
    "baby bounce", "toddler storytime", "family storytime", "sing and stomp",
    "sing & stomp", "cuentos con ritmo", "musica y movimiento", "soul4kidz",
    "in harmony", "mart littles", "jymbabies", "shabbat shababies",
    "jumping jacks", "rainbow playgroup", "lego", "read to a dog",
    "crafternoon", "wiggles and wonder", "stories & rhyme", "canta conmigo",
    "farmers market", "marin country mart farmers", "marin civic center farmers",
    "strawberry village farmers", "corte madera town center farmers",
    "mill valley certified farmers", "sausalito farmers", "fairfax community farmers",
    "novato farmers", "point reyes farmers", "san rafael summer night",
    "san rafael downtown thursday", "tomales farmers",
    "sing and stompers", "school of rock", "rock and roll playhouse",
    "fishing in the city", "marin bluegrass sessions",
    "outdoor movie night", "splash bash", "strawberry community night",
    "scary at the berry", "jymbabies"
]


def is_marin_event(text):
    """Check if event text mentions a Marin town."""
    text_lower = text.lower()
    return any(town in text_lower for town in MARIN_TOWNS)


def is_family_event(text):
    """Check if event text suggests a children/family event."""
    text_lower = text.lower()
    return any(kw in text_lower for kw in FAMILY_KEYWORDS)


def is_already_known(text):
    """Check if we already have this event."""
    text_lower = text.lower()
    return any(name in text_lower for name in KNOWN_EVENT_NAMES)


def fetch_marin_mommies_day(date_str):
    """
    Fetch Marin Mommies calendar for a specific date.
    URL pattern: marinmommies.com/calendar/YYYY-MM-DD
    Hardcoded so it runs automatically in GitHub Actions without needing
    a prior URL appearance. Returns list of (title, time, location) tuples.
    """
    import re
    try:
        from html import unescape
    except ImportError:
        unescape = lambda x: x

    url = f"https://www.marinmommies.com/calendar/{date_str}"
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "OutAndAboutMarin/1.0 (weekly event sweep)"}
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode('utf-8', errors='replace')

        # Parse event blocks: h4 title + two strong tags (time, location)
        pattern = re.compile(
            r'<h4[^>]*>\s*<a[^>]*>([^<]+)</a>\s*</h4>\s*'
            r'<strong>([^<]+)</strong>\s*'
            r'<strong>([^<]+)</strong>',
            re.DOTALL
        )
        events = []
        for m in pattern.finditer(html):
            title = unescape(m.group(1).strip())
            time_str = unescape(m.group(2).strip())
            location = unescape(m.group(3).strip())
            events.append((title, time_str, location))

        return events
    except Exception:
        return []


def fetch_strawberry_rec_events():
    """Fetch upcoming events from Strawberry Rec calendar."""
    url = "https://strawberry.marin.org/calendar/"
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "OutAndAboutMarin/1.0"}
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode('utf-8', errors='replace')

        import re
        events = []
        # Extract event titles and dates
        pattern = re.compile(
            r'<h4[^>]*>\s*<a[^>]*href="([^"]+)"[^>]*>([^<]+)</a>\s*</h4>',
            re.DOTALL
        )
        date_pattern = re.compile(r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2}')

        for m in pattern.finditer(html):
            title = m.group(2).strip()
            events.append(title)

        return events
    except Exception as e:
        return []


def fetch_sweetwater_kids_events():
    """Fetch upcoming children's events from Sweetwater Music Hall."""
    url = "https://sweetwatermusichall.org/events/"
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "OutAndAboutMarin/1.0"}
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode('utf-8', errors='replace')

        import re
        events = []
        pattern = re.compile(
            r'<h2[^>]*class="tribe-events-list-event-title"[^>]*>.*?<a[^>]*>([^<]+)</a>',
            re.DOTALL
        )
        for m in pattern.finditer(html):
            title = m.group(1).strip()
            if is_family_event(title):
                events.append(title)

        return events
    except Exception as e:
        return []


def fetch_larkspur_ical():
    """
    Fetch the Larkspur Library iCal feed and return a list of upcoming events.
    URL is hardcoded so it runs automatically every sweep without manual input.
    Filters out past events and 'No Storytime' notices.
    """
    LARKSPUR_ICAL_URL = "https://www.ci.larkspur.ca.us/common/modules/iCalendar/iCalendar.aspx?catID=24&feed=calendar"

    try:
        import urllib.request
        from datetime import datetime, timedelta
        import re

        req = urllib.request.Request(
            LARKSPUR_ICAL_URL,
            headers={"User-Agent": "OutAndAboutMarin/1.0"}
        )
        with urllib.request.urlopen(req, timeout=15) as response:
            raw = response.read().decode("utf-8", errors="replace")

        today = date.today()
        events = []

        for block in raw.split("BEGIN:VEVENT")[1:]:
            summary_m = re.search(r"SUMMARY:(.+?)(?:\r?\n[A-Z])", block, re.DOTALL)
            dtstart_m = re.search(r"DTSTART[^:]*:(\d+T\d+)", block)
            desc_m = re.search(r"DESCRIPTION:(.+?)(?:\r?\n[A-Z])", block, re.DOTALL)
            uid_m = re.search(r"UID:(\S+)", block)

            if not summary_m or not dtstart_m:
                continue

            summary = re.sub(r"\r?\n[ \t]", "", summary_m.group(1)).strip()
            desc = re.sub(r"\r?\n[ \t]", "", desc_m.group(1)).strip() if desc_m else ""
            uid = uid_m.group(1).strip() if uid_m else ""

            # Parse date
            try:
                dt = datetime.strptime(dtstart_m.group(1)[:8], "%Y%m%d").date()
            except ValueError:
                continue

            # Skip past events
            if dt < today:
                continue

            # Skip 'No Storytime' notices
            if "no storytime" in summary.lower():
                continue

            # Skip if already in our known events (basic title match)
            if is_already_known(summary):
                continue

            events.append({
                "date": dt.isoformat(),
                "day": dt.strftime("%A"),
                "title": summary,
                "time": "See website",
                "location": "Larkspur Library",
                "description": desc.replace("\\,", ",").replace("\\n", " "),
                "source": "Larkspur Library iCal",
                "uid": uid,
                "website": f"https://www.ci.larkspur.ca.us/calendar.aspx?EID={uid}" if uid else "https://www.ci.larkspur.ca.us/calendar.aspx?CID=24",
            })

        return events

    except Exception as e:
        print(f"  ✗ Larkspur iCal fetch failed: {e}")
        return []


def fetch_belvedere_tiburon_events():
    """
    Fetch the Belvedere-Tiburon Library events page filtered for
    Infants & Toddlers + School Age audiences, looking 6 months ahead.
    URL is hardcoded so it runs automatically in GitHub Actions.
    Parses event titles, dates, and times from the WordPress event listing.
    """
    import re
    from datetime import timedelta

    BASE_URL = "https://www.beltiblibrary.org/events"
    today = date.today()
    start_str = today.strftime("%Y-%m-%d")
    url = f"{BASE_URL}?start={start_str}&ages=Infants+%26+Toddlers%2CSchool+age"

    # Known recurring programs already in app — skip these
    KNOWN_RECURRING = [
        'baby bounce', 'toddler storytime', 'preschool storytime',
        'bilingual storytime', 'friday toddler', 'sunday baby bounce',
        'family storytunes', 'crafternoon', 'tuesday crafternoon',
        'read to a dog', 'craft challenge', 'game day', 'mosaic monday',
    ]

    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "OutAndAboutMarin/1.0"}
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode('utf-8', errors='replace')

        try:
            from html import unescape
        except ImportError:
            unescape = lambda x: x

        cutoff = today + timedelta(days=180)
        events = []

        # Parse event blocks: title in h3/h4 anchor, date in time or span
        # BelTib uses WordPress with The Events Calendar plugin
        # Pattern: event article blocks with title + datetime
        title_pattern = re.compile(
            r'<h3[^>]*class="[^"]*tribe-events-list-event-title[^"]*"[^>]*>'
            r'\s*<a[^>]*>([^<]+)</a>',
            re.DOTALL
        )
        # Also try simpler h2/h3/h4 anchor pattern as fallback
        title_pattern2 = re.compile(
            r'<(?:h2|h3|h4)[^>]*>\s*<a[^>]*href="([^"]*)"[^>]*>([^<]+)</a>\s*</(?:h2|h3|h4)>',
            re.DOTALL
        )
        date_pattern = re.compile(
            r'<abbr[^>]*class="[^"]*tribe-events-abbr[^"]*"[^>]*title="([^"]+)"',
            re.DOTALL
        )
        time_pattern = re.compile(
            r'<div[^>]*class="[^"]*tribe-events-schedule[^"]*"[^>]*>(.*?)</div>',
            re.DOTALL
        )

        # Try primary pattern
        titles = [(m.group(1).strip(), '') for m in title_pattern.finditer(html)]

        # Fallback to simpler pattern
        if not titles:
            titles = [(unescape(m.group(2).strip()), m.group(1)) for m in title_pattern2.finditer(html)]

        dates = [m.group(1).strip() for m in date_pattern.finditer(html)]

        for i, (title, href) in enumerate(titles):
            title = unescape(title)

            # Skip known recurring programs
            if any(k in title.lower() for k in KNOWN_RECURRING):
                continue

            # Skip if already known
            if is_already_known(title):
                continue

            # Try to get date
            event_date_str = dates[i] if i < len(dates) else ""
            event_date = None
            for fmt in ('%Y-%m-%d', '%B %d, %Y', '%b %d, %Y'):
                try:
                    event_date = datetime.strptime(event_date_str[:10], fmt[:len(event_date_str[:10])]).date()
                    break
                except (ValueError, TypeError):
                    pass

            if event_date and (event_date < today or event_date > cutoff):
                continue

            events.append({
                "date": event_date.isoformat() if event_date else "TBD",
                "day": event_date.strftime("%A") if event_date else "TBD",
                "title": title,
                "time": "See website",
                "location": "Belvedere Tiburon Library",
                "source": "Belvedere-Tiburon Library events page",
                "website": href if href else BASE_URL,
            })

        return events

    except Exception as e:
        print(f"  ✗ Belvedere-Tiburon events fetch failed: {e}")
        return []


def fetch_marin_parks_ical():
    """
    Fetch the Marin County Parks Trumba iCal feed and return upcoming family events.
    URL: https://www.trumba.com/calendars/marin-parks-open-space.ics
    Filters out admin/commission meetings and past events.
    """
    MARIN_PARKS_ICAL_URL = "https://www.trumba.com/calendars/marin-parks-open-space.ics"
    SKIP_KEYWORDS = ['commission', 'ipm', 'board meeting', 'staff meeting']

    try:
        import urllib.request
        from datetime import timedelta
        import re as re_mod

        req = urllib.request.Request(
            MARIN_PARKS_ICAL_URL,
            headers={"User-Agent": "OutAndAboutMarin/1.0"}
        )
        with urllib.request.urlopen(req, timeout=15) as response:
            raw = response.read().decode("utf-8", errors="replace")

        today = date.today()
        cutoff = today + timedelta(days=180)
        events = []

        for block in raw.split("BEGIN:VEVENT")[1:]:
            def get_field(b, field):
                m = re_mod.search(
                    rf'{field}[^:]*:(.+?)(?:\r?\nBEGIN|\r?\nEND|\r?\n[A-Z][A-Z0-9\-]*[;:])',
                    b, re_mod.DOTALL
                )
                if m:
                    return re_mod.sub(r'\r?\n[ \t]', '', m.group(1)).replace('\\,', ',').replace('\\n', ' ').replace('&#39;', "'").strip()
                return ''

            summary = get_field(block, 'SUMMARY')
            dtstart = get_field(block, 'DTSTART')
            location = get_field(block, 'LOCATION')
            desc = get_field(block, 'DESCRIPTION')

            if not summary or not dtstart:
                continue

            # Skip admin meetings
            if any(kw in summary.lower() for kw in SKIP_KEYWORDS):
                continue

            # Parse date/time
            try:
                if 'T' in dtstart:
                    dt = datetime.strptime(dtstart[:15], '%Y%m%dT%H%M%S')
                    event_date = dt.date()
                    time_str = dt.strftime('%-I:%M %p')
                else:
                    event_date = datetime.strptime(dtstart[:8], '%Y%m%d').date()
                    time_str = 'TBD'
            except (ValueError, KeyError):
                continue

            if event_date < today or event_date > cutoff:
                continue

            if is_already_known(summary):
                continue

            events.append({
                "date": event_date.isoformat(),
                "day": event_date.strftime("%A"),
                "time": time_str,
                "title": summary,
                "location": location or "Marin County Parks",
                "description": desc[:200],
                "source": "Marin County Parks (Trumba iCal)",
                "website": "https://parks.marincounty.gov/discoverlearn/events-calendar",
            })

        return events

    except Exception as e:
        print(f"  ✗ Marin Parks iCal fetch failed: {e}")
        return []


def run_weekly_sweep(events_file="events.json"):
    """
    Full weekly sweep of all event sources.
    Produces a consolidated report of suggested new events for review.
    """
    from datetime import timedelta
    import time as time_module

    today = date.today()
    print("\n" + "═" * 60)
    print("OUT AND ABOUT MARIN — WEEKLY EVENT SWEEP")
    print(f"Sweeping next 14 days: {today} → {today + timedelta(days=14)}")
    print("═" * 60)

    suggested = []  # List of suggested events to review

    # ── 1. MARIN MOMMIES — next 14 days ──────────────────────────
    # Note: marinmommies.com/calendar/YYYY-MM-DD is hardcoded — runs
    # automatically in GitHub Actions without needing prior URL fetch.
    # Rate limited to 1.5s per page to be polite to their server.
    # We fetch 14 days (the meaningful near-term window) rather than
    # 6 months — Marin Mommies calendar only shows confirmed upcoming
    # events, so 14 days gives reliable coverage without hammering them.
    print("\n── Marin Mommies Calendar (next 14 days) ──")
    for i in range(14):
        sweep_date = today + timedelta(days=i)
        date_str = sweep_date.strftime("%Y-%m-%d")
        day_label = sweep_date.strftime("%A, %B %-d")

        events = fetch_marin_mommies_day(date_str)
        day_suggestions = []

        for title, time_str, location in events:
            if not is_marin_event(location) and not is_marin_event(title):
                continue  # Skip non-Marin events
            if not is_family_event(title) and not is_family_event(location):
                continue  # Skip non-family events
            if is_already_known(title):
                continue  # Skip events we already have

            day_suggestions.append({
                "date": date_str,
                "day_label": day_label,
                "title": title,
                "time": time_str,
                "location": location,
                "source": "Marin Mommies"
            })

        if day_suggestions:
            print(f"\n  📅 {day_label}:")
            for s in day_suggestions:
                print(f"     • {s['title']} — {s['time']} @ {s['location']}")
            suggested.extend(day_suggestions)
        else:
            print(f"  ✓ {day_label} — nothing new")

        # Rate limit — be polite to Marin Mommies
        time_module.sleep(1.5)

    # ── 2. MARIN MOMMIES WEEKEND POST ────────────────────────────
    print("\n── Marin Mommies Weekend Post ──")
    # Find this week's weekend post URL
    # Auto-fetch homepage to find the current weekend post URL.
    # Marin Mommies changed their URL pattern — now uses:
    #   marin-bay-area-weekend-family-fun-may-8-10 (hyphen, "bay area" in title)
    # Older pattern was:
    #   marin-weekend-family-fun-may-8%E2%80%9310 (en dash, no "bay area")
    # We fetch the homepage and extract the actual URL to handle either pattern.
    print("  ℹ Fetching Marin Mommies homepage to find current weekend post URL...")
    weekend_post_url = None
    try:
        req = urllib.request.Request(
            "https://www.marinmommies.com/",
            headers={"User-Agent": "OutAndAboutMarin/1.0"}
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            hp_html = resp.read().decode('utf-8', errors='replace')

        import re as _re
        # Look for weekend family fun post links (both URL patterns)
        patterns = [
            r'href="(https?://www\.marinmommies\.com/marin(?:-bay-area)?-weekend-family-fun-[a-z]+-\d+[^"]*)"',
        ]
        for pat in patterns:
            m = _re.search(pat, hp_html)
            if m:
                weekend_post_url = m.group(1)
                break

        if weekend_post_url:
            print(f"  → Found weekend post: {weekend_post_url}")
            print("  → Claude: please fetch this URL, filter for Marin-only events,")
            print("    and add new ones to the sweep Excel for approval.")
        else:
            next_sat = today + timedelta(days=(5 - today.weekday()) % 7)
            next_sun = next_sat + timedelta(days=1)
            month_name = next_sat.strftime("%B").lower()
            print(f"  ⚠ Could not auto-detect weekend post URL.")
            print(f"  → Try these patterns manually:")
            print(f"     marinmommies.com/marin-bay-area-weekend-family-fun-{month_name}-{next_sat.day}-{next_sun.day}")
            print(f"     marinmommies.com/marin-weekend-family-fun-{month_name}-{next_sat.day}%E2%80%93{next_sun.day}")
    except Exception as e:
        print(f"  ✗ Homepage fetch failed: {e}")
        print("  → Fetch marinmommies.com manually to find the weekend post.")

    # ── 3. STRAWBERRY REC ─────────────────────────────────────────
    print("\n── Strawberry Recreation District ──")
    srd_events = fetch_strawberry_rec_events()
    srd_new = [e for e in srd_events if not is_already_known(e)]
    if srd_new:
        print(f"  🔔 {len(srd_new)} possible new event(s):")
        for e in srd_new:
            print(f"     • {e}")
            suggested.append({
                "date": "TBD",
                "day_label": "Check calendar",
                "title": e,
                "time": "See website",
                "location": "Strawberry Recreation District, Mill Valley",
                "source": "Strawberry Rec"
            })
    else:
        print("  ✓ No new events beyond what we already have")

    # ── 3. SWEETWATER ─────────────────────────────────────────────
    print("\n── Sweetwater Music Hall (family events) ──")
    sw_events = fetch_sweetwater_kids_events()
    sw_new = [e for e in sw_events if not is_already_known(e)]
    if sw_new:
        print(f"  🔔 {len(sw_new)} possible new family event(s):")
        for e in sw_new:
            print(f"     • {e}")
            suggested.append({
                "date": "TBD",
                "day_label": "Check calendar",
                "title": e,
                "time": "See website",
                "location": "Sweetwater Music Hall, Mill Valley",
                "source": "Sweetwater"
            })
    else:
        print("  ✓ No new family events beyond what we already have")

    # ── 4. LARKSPUR LIBRARY iCAL ──────────────────────────────────
    print("\n── Larkspur Library iCal Feed ──")
    larkspur_events = fetch_larkspur_ical()
    if larkspur_events:
        print(f"  🔔 {len(larkspur_events)} new event(s) found at Larkspur Library:")
        for e in larkspur_events:
            print(f"     • {e['date']} {e['day']} — {e['title']}")
            suggested.append({
                "date": e["date"],
                "day_label": f"{e['day']}, {e['date']}",
                "title": e["title"],
                "time": e["time"],
                "location": e["location"],
                "description": e.get("description", ""),
                "source": e["source"],
                "website": e.get("website", ""),
            })
    else:
        print("  ✓ No new Larkspur Library events beyond what we already have")

    # ── 5. MARIN COUNTY PARKS iCAL ───────────────────────────────
    print("\n── Marin County Parks Events (Trumba iCal) ──")
    parks_events = fetch_marin_parks_ical()
    if parks_events:
        print(f"  🔔 {len(parks_events)} new Marin Parks event(s) found:")
        for e in parks_events:
            print(f"     • {e['date']} {e['day']} {e['time']} — {e['title']}")
            print(f"       📍 {e['location']}")
            suggested.append({
                "date": e["date"],
                "day_label": f"{e['day']}, {e['date']}",
                "title": e["title"],
                "time": e["time"],
                "location": e["location"],
                "description": e.get("description", ""),
                "source": e["source"],
                "website": e.get("website", ""),
            })
    else:
        print("  ✓ No new Marin Parks events beyond what we already have")

    # ── 6. BELVEDERE-TIBURON LIBRARY ─────────────────────────────
    print("\n── Belvedere-Tiburon Library Events ──")
    beltib_events = fetch_belvedere_tiburon_events()
    if beltib_events:
        print(f"  🔔 {len(beltib_events)} new Belvedere-Tiburon event(s) found:")
        for e in beltib_events:
            print(f"     • {e['date']} {e['day']} — {e['title']}")
            suggested.append({
                "date": e["date"],
                "day_label": f"{e['day']}, {e['date']}",
                "title": e["title"],
                "time": e["time"],
                "location": e["location"],
                "description": e.get("description", ""),
                "source": e["source"],
                "website": e.get("website", ""),
            })
    else:
        print("  ✓ No new Belvedere-Tiburon events beyond what we already have")

    # ── CONSOLIDATED REPORT ───────────────────────────────────────
    print("\n" + "═" * 60)
    print("CONSOLIDATED SUGGESTED EVENTS FOR REVIEW")
    print("═" * 60)

    if not suggested:
        print("\n✓ No new events found this week — all sources are up to date!")
    else:
        print(f"\n{len(suggested)} suggested event(s) to review:\n")
        print("For each event, tell Claude: APPROVE, SKIP, or MORE INFO\n")

        for i, s in enumerate(suggested, 1):
            print(f"[{i}] {s['title']}")
            print(f"     📅 {s['day_label']}  ⏰ {s['time']}")
            print(f"     📍 {s['location']}")
            print(f"     🔗 Source: {s['source']}")
            print()

    print("═" * 60)
    print("TO ADD APPROVED EVENTS:")
    print("Open a chat with Claude and say:")
    print('"Please add events [1], [3], [5] from the weekly sweep report"')
    print("═" * 60)

    # Save report to file for reference
    report = {
        "sweep_date": str(today),
        "suggested_events": suggested
    }
    with open("weekly_sweep_report.json", "w") as f:
        json.dump(report, f, indent=2)
    print(f"\n✓ Report saved to weekly_sweep_report.json")

    return suggested


def fetch_sausalito_programs():
    """
    Fetch the Sausalito Library Kids & Teens Programs page.
    URL: sausalitolibrary.org/kids-teens/children-s-and-teen-programs
    Plain HTML — fully fetchable without JavaScript.
    Used for both weekly sweep (new programs) and monthly audit (verify existing).
    Returns page content as string.
    """
    SAUSALITO_PROGRAMS_URL = "https://www.sausalitolibrary.org/kids-teens/children-s-and-teen-programs"
    try:
        req = urllib.request.Request(
            SAUSALITO_PROGRAMS_URL,
            headers={"User-Agent": "OutAndAboutMarin/1.0"}
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except Exception as e:
        print(f"  ✗ Sausalito Library programs fetch failed: {e}")
        return None


def fetch_srpl_programs():
    """
    Fetch San Rafael Public Library events page.
    Used for monthly audit of IDs 6, 7, 24, 25, 26, 27, 32, 46.
    """
    SRPL_URL = "https://srpubliclibrary.org/events/"
    try:
        req = urllib.request.Request(SRPL_URL, headers={"User-Agent": "OutAndAboutMarin/1.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except Exception as e:
        print(f"  ✗ SRPL fetch failed: {e}")
        return None


def fetch_mcfl_branch(branch_code, branch_name):
    """
    Fetch MCFL branch page from marinlibrary.org.
    branch_code: e.g. 'mn' (Novato), 'mc' (Marin City), 'mb' (Bolinas),
                 'mm' (Corte Madera), 'mf' (Fairfax), 'mp' (Point Reyes),
                 'mi' (Inverness), 'ms' (Stinson Beach)
    Returns page content or None.
    """
    url = f"https://marinlibrary.org/locations/{branch_code}/"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "OutAndAboutMarin/1.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except Exception as e:
        print(f"  ✗ MCFL {branch_name} fetch failed: {e}")
        return None


def fetch_sananselmo_programs():
    """
    Fetch San Anselmo Library storytime programs page.
    Used for monthly audit of IDs 21, 33, 44, 45, 82.
    """
    SA_URL = "https://www.sananselmo.gov/624/Storytime-Programs"
    try:
        req = urllib.request.Request(SA_URL, headers={"User-Agent": "OutAndAboutMarin/1.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except Exception as e:
        print(f"  ✗ San Anselmo fetch failed: {e}")
        return None


def run_monthly_audit(events_file="events.json"):
    """
    Monthly audit of all recurring events in events.json.
    Runs on the first Monday of each month via daily.yml.
    For each Weekly/Monthly event, checks whether it still appears
    on its source calendar. Flags events that can't be confirmed.
    NEVER auto-deletes — outputs a report for human review only.
    """
    import re as re_mod
    from datetime import timedelta

    print("\n" + "═" * 60)
    print("MONTHLY RECURRING EVENTS AUDIT")
    print(f"Run date: {date.today()}")
    print("═" * 60)

    with open(events_file) as f:
        data = json.load(f)

    recurring = [e for e in data["events"]
                 if e.get("cadence") in ("Weekly", "Monthly", "Bi-weekly")
                 and e.get("status") not in ("Inactive",)]

    print(f"\nAuditing {len(recurring)} recurring events...\n")

    confirmed = []
    not_found = []
    manual_check = []
    fetch_failed = []

    # Source fetch cache — avoid re-fetching same URL
    fetch_cache = {}

    def fetch_source(url, label):
        if url in fetch_cache:
            return fetch_cache[url]
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "OutAndAboutMarin/1.0"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                content = resp.read().decode("utf-8", errors="replace")
            fetch_cache[url] = content
            return content
        except Exception as e:
            fetch_cache[url] = None
            print(f"  ✗ Could not fetch {label}: {e}")
            return None

    # Source routing — map each event to the right audit source URL
    # MCFL branch codes: mn=Novato, mc=Marin City, mb=Bolinas, mm=Corte Madera,
    #                    mf=Fairfax, mp=Point Reyes, mi=Inverness, ms=Stinson Beach
    MCFL_BRANCH_MAP = {
        'novato': 'mn', 'marin city': 'mc', 'bolinas': 'mb',
        'corte madera': 'mm', 'fairfax': 'mf', 'point reyes': 'mp',
        'inverness': 'mi', 'stinson beach': 'ms',
    }

    def get_source_url(event):
        venue = event.get("venue", "").lower()
        town = event.get("town", "").lower()
        name = event.get("event_name", "").lower()
        org = event.get("organization", "").lower()
        website = event.get("website", "").lower()

        # Belvedere-Tiburon Library
        if "belvedere" in venue or "tiburon" in venue or town == "tiburon":
            return ("https://www.beltiblibrary.org/events", "Belvedere-Tiburon Library")
        # Mill Valley Library
        if "mill valley" in venue and "library" in venue:
            return ("https://millvalleylibrary.libcal.com/ical_subscribe.php?src=p&cid=17002&aud=5670,5671", "Mill Valley Library iCal")
        # Larkspur Library
        if "larkspur" in venue and "library" in venue:
            return ("https://www.ci.larkspur.ca.us/common/modules/iCalendar/iCalendar.aspx?catID=24&feed=calendar", "Larkspur Library iCal")
        # Sausalito Library / Robin Sweeny Park programs
        if ("sausalito" in venue and "library" in venue) or "robin sweeny" in venue:
            return ("https://www.sausalitolibrary.org/kids-teens/children-s-and-teen-programs", "Sausalito Library Programs")
        # San Anselmo Library
        if "san anselmo" in venue or town == "san anselmo":
            return ("https://www.sananselmo.gov/624/Storytime-Programs", "San Anselmo Library")
        # SRPL — San Rafael Public Library
        if "srpubliclibrary" in website or any(x in venue for x in ["downtown", "northgate", "pickleweed"]):
            return ("https://srpubliclibrary.org/events/", "SRPL Events")
        # MCFL branches by town
        for branch_town, branch_code in MCFL_BRANCH_MAP.items():
            if branch_town in town or branch_town in venue:
                return (f"https://marinlibrary.org/locations/{branch_code}/", f"MCFL {branch_town.title()}")
        # MCFL Civic Center (San Rafael)
        if "civic center" in venue or ("marinlibrary" in website and "san rafael" in town):
            return ("https://marinlibrary.org/locations/mb/", "MCFL Civic Center")
        # Marin Country Mart
        if "marin country mart" in venue or "marincountrymart" in website:
            return ("https://marincountrymart.com/events", "Marin Country Mart")
        # Goodman Building Supply / Goodie's Kids Club
        if "goodman" in venue or "goodie" in name:
            return ("https://goodmanbuildingsupply.net/goodies-kids-club/", "Goodman Building Supply")
        # Parks Conservancy (Nike Missile, Battery Townsley)
        if "parksconservancy" in website or "missile" in name or "townsley" in name:
            return ("https://www.parksconservancy.org/events", "Parks Conservancy")
        # JymBabies / Marin JCC
        if "jymbabies" in name or "marinjcc" in website:
            return ("https://www.marinjcc.org/preschool/jym-babies/", "Marin JCC")
        # MarinMOCA
        if "marinmoca" in name or "marinmoca" in website:
            return ("https://www.marinmoca.org/family", "MarinMOCA")
        # San Geronimo Valley Community Center
        if "sgvcc" in website or "san geronimo" in town:
            return ("https://www.sgvcc.org/our-programs/youth-programs", "SGVCC")
        # The Redwoods Senior Living
        if "redwoods senior" in venue or "redwoods" in org:
            return (None, "MANUAL — The Redwoods Senior Living (no online calendar)")
        # Sweetwater Music Hall
        if "sweetwater" in venue:
            return (None, "MANUAL — Sweetwater Music Hall (variable schedule)")
        # Strawberry Rec
        if "strawberry" in venue or "strawberry" in org:
            return (None, "MANUAL — Strawberry Rec (check strawberryrec.com)")
        # Farmers Markets — stable, manual annual spot-check
        if "farmers market" in name:
            return (None, "MANUAL — Farmers Market (check market website annually)")
        # Default
        return (None, f"MANUAL — no auto-fetch configured (website: {event.get('website','none')})")

    for e in recurring:
        name = e["event_name"]
        eid = e["id"]
        url, source_label = get_source_url(e)

        if url is None:
            manual_check.append((eid, name, source_label))
            continue

        content = fetch_source(url, source_label)
        if content is None:
            fetch_failed.append((eid, name, source_label, url))
            continue

        # Check if event name (or key words) appear in fetched content
        search_terms = [w for w in name.lower().split() if len(w) > 4][:3]
        found = sum(1 for term in search_terms if term in content.lower())

        if found >= 2:
            confirmed.append((eid, name, source_label))
        else:
            not_found.append((eid, name, source_label, url))

    # ── Print report ──
    print(f"✅ CONFIRMED ({len(confirmed)} events):")
    for eid, name, source in confirmed:
        print(f"   ID {eid}: {name} [{source}]")

    print(f"\n⚠  NOT CONFIRMED — NEEDS REVIEW ({len(not_found)} events):")
    for eid, name, source, url in not_found:
        print(f"   ID {eid}: {name}")
        print(f"   Source: {source} — {url}")
        print(f"   Action: verify at source URL and update/remove if no longer running")

    print(f"\n🔍 MANUAL CHECK REQUIRED ({len(manual_check)} events):")
    for eid, name, source in manual_check:
        print(f"   ID {eid}: {name} — {source}")

    print(f"\n❌ SOURCE FETCH FAILED ({len(fetch_failed)} events):")
    for eid, name, source, url in fetch_failed:
        print(f"   ID {eid}: {name} — {source}")
        print(f"   URL: {url} — try again or check manually")

    # Save audit report
    report = {
        "audit_date": str(date.today()),
        "total_audited": len(recurring),
        "confirmed": [{"id": e[0], "name": e[1]} for e in confirmed],
        "not_found": [{"id": e[0], "name": e[1], "source": e[2], "url": e[3]} for e in not_found],
        "manual_check": [{"id": e[0], "name": e[1], "reason": e[2]} for e in manual_check],
        "fetch_failed": [{"id": e[0], "name": e[1], "source": e[2]} for e in fetch_failed],
    }
    with open("monthly_audit_report.json", "w") as f:
        json.dump(report, f, indent=2)

    print("\n" + "═" * 60)
    print(f"Audit complete. Report saved to monthly_audit_report.json")
    print(f"✅ {len(confirmed)} confirmed  ⚠ {len(not_found)} need review  "
          f"🔍 {len(manual_check)} manual  ❌ {len(fetch_failed)} failed")
    print("═" * 60)

    return report


if __name__ == "__main__":
    import sys
    if "--weekly-sweep" in sys.argv:
        run_weekly_sweep()
    elif "--monthly-audit" in sys.argv:
        run_monthly_audit()
    else:
        main()
