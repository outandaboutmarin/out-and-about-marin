"""
Converts the "Choose your own adventure" spreadsheet into adventure.json.

Same idea as swim_vendors_io.py: the spreadsheet lives outside this repo (in
Alexandra's Dropbox "Resources" folder, beside the swim spreadsheet) and stays the source. When it
changes: update XLSX_PATH below if the filename changed, re-run this script,
commit the resulting adventure.json.

Only the first sheet ("Create Your Own Adventure", the Marin places) is read.
The "Beyond Marin" sheet is out-of-area and unpublished for now; the
"Checks & gaps" sheet is working notes. Two columns are deliberately NEVER
copied into the JSON, because adventure.json is public:
  - "Check status" (internal verification state)
  - "INTERNAL: Sponsor status (delete before publishing)"

Columns are found by header name (row 4), not position, and rows are matched to
OVERRIDES by a slug of the Place name, not row order, so inserting a row or a
column in the spreadsheet does not misalign anything.

OVERRIDES holds what the sheet does not: the Spanish hours text (`hoursEs`) and
the days of the week each place is open (`days`, used by the Days & hours
filter). Both are hand-assigned from the "Days & hours" cell, for the same
reason swim_vendors_io.py hand-assigns minMonths: the hours text is free-form
("Mon to Wed and Sat", "Daily", "closed Mon") and a wrong regex guess would
silently break the filter. A new place with no OVERRIDES entry still converts,
with a warning, falling back to English hours and no days.

A factual correction goes in the spreadsheet (or here as an override), never in
adventure.json by hand: the JSON is regenerated wholesale on every run.
"""
import json
import os
import re
import sys
from datetime import date, datetime

import openpyxl

XLSX_PATH = r"C:\Users\AWalter\Dropbox\01. Out AND About Files\Resources\create_your_own_adventure_v2.xlsx"
SHEET = "Create Your Own Adventure"
HEADER_ROW = 4
OUT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "adventure.json")

# The web app shows only three categories (Alexandra 2026-10-22). Each sheet
# Program maps to one; `program` keeps the sheet's own wording. A Program not
# listed here stops the run, so a new one is never shown uncategorized.
CATEGORY = {
    "Indoor playground/drop-in": "Indoor playground/drop-in",
    "Indoor Morning Power Play": "Open Gym",
    "Tumbling Tots open gym": "Open Gym",
    "Toddler Open Gym": "Open Gym",
    "Open Gym": "Open Gym",
    "Museum": "Museum",
}
CATEGORY_ES = {
    "Indoor playground/drop-in": "Parque infantil cubierto / sin cita",
    "Open Gym": "Gimnasio abierto",
    "Museum": "Museo",
}

ALL_DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

# `hours`, where present, replaces the sheet's "Days & hours" cell: each was
# checked against the place's own website on 2026-10-22 and the sheet was out
# of date. Places with no `hours` here matched their website that day.
OVERRIDES = {
    "the-social-klub": dict(
        days=["Mon", "Tue", "Wed", "Thu", "Fri", "Sat"],
        hoursEs="Lun, mié y vie 9 a. m. a 5 p. m.; mar y jue 9 a. m. a 2:15 p. m.; sáb 10 a. m. a 4 p. m.; cerrado dom"),
    # "Two-hour sessions" is not on littlemarin.com; dropped.
    "little-marin": dict(
        days=ALL_DAYS,
        hours="Daily 9am to 5pm",
        hoursEs="Todos los días 9 a. m. a 5 p. m."),
    "kitsch-sync": dict(
        days=["Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
        hoursEs="Jue a dom 9 a. m. a 8 p. m.; mar 4 a 8 p. m.; mié 2 a 8 p. m.; cerrado lun"),
    # From Cal Star's Power Play calendar (Jackrabbit, Oct and Nov 2026): no Tuesday
    # sessions, a Wednesday 1pm session. The calendar shows start times only.
    "cal-star-gymnastics": dict(
        days=["Mon", "Wed", "Fri", "Sat"],
        hours="Sessions start Mon and Sat 9:30am; Wed 9:30am and 1pm; Fri 10am and 11am",
        hoursEs="Las sesiones empiezan lun y sáb 9:30 a. m.; mié 9:30 a. m. y 1 p. m.; vie 10 a. m. y 11 a. m."),
    "novato-gymnastics-center-city-of-novato": dict(
        days=["Tue", "Thu", "Sun"],
        hoursEs="Mar y jue 12:30 a 1:15 p. m. y 5:30 a 6:15 p. m.; dom mediodía a 12:45 p. m. (sesión de otoño del 26 de oct. al 19 de dic.)"),
    # Toddler Open Gym is Sat and Sun only; the Friday slot is the All Ages Open Gym.
    # Toddler and All Ages open gyms combined in one row (Alexandra 2026-10-24, open gym audit); Fri added to the day filter.
    "flying-dutchman-gymnastics": dict(
        days=["Fri", "Sat", "Sun"],
        hours="Toddler Open Gym (ages 0 to 4): Sat and Sun 9 to 11am. All Ages Open Gym: Sat and Sun 11am to 3pm; Fri 4:30 to 6:30pm",
        hoursEs="Gimnasio abierto para niños pequeños (0 a 4 años): sáb y dom 9 a 11 a. m. Gimnasio abierto para todas las edades: sáb y dom 11 a. m. a 3 p. m.; vie 4:30 a 6:30 p. m."),
    "gymworld-gymnastics-parkour": dict(
        days=["Mon", "Tue", "Wed", "Thu", "Fri", "Sun"],
        hoursEs="Lun a vie 9:30 a 11:30 a. m.; dom 9 a 11 a. m."),
    # foxandkit.com posts weekend hours one weekend at a time ("this weekend: 10/24 & 10/25").
    "fox-kit": dict(
        days=ALL_DAYS,
        hours="Mon to Fri 8am to 5pm; Sat and Sun hours are posted each week on the website",
        hoursEs="Lun a vie 8 a. m. a 5 p. m.; el horario de sáb y dom se publica cada semana en su sitio web"),
    # Mt. Tam Adventures' page: fall/winter open play is Mondays from Nov 2; the
    # Saturday 9:30 to 11:30 slot is its summer schedule.
    "playland-mt-tam-adventures-and-city-of-sausalito": dict(
        days=["Mon"],
        hours="Mon 9am to noon, fall and winter, starting Nov 2 (free music class included)",
        hoursEs="Lun 9 a. m. a mediodía, otoño e invierno, a partir del 2 de nov. (incluye una clase de música gratis)"),
    "bay-area-discovery-museum": dict(
        days=["Wed", "Thu", "Fri", "Sat", "Sun"],
        hours="Wed to Fri 10am to 4pm; Sat and Sun 9am to 4pm; closed Mon and Tue during the school year",
        hoursEs="Mié a vie 10 a. m. a 4 p. m.; sáb y dom 9 a. m. a 4 p. m.; cerrado lun y mar durante el año escolar"),
    "play-well-teknologies": dict(
        days=ALL_DAYS,
        hoursEs="Lun a vie 10 a. m. a 6 p. m.; sáb y dom 9 a. m. a 5 p. m."),
    # A climbing gym for everyone, not a kids' open gym: kept, with the age rule in the hours (Alexandra 2026-10-24).
    # Weekend Open Studio, added 2026-10-24 (Alexandra). The page URL says "9-11 am"; the page itself lists two one-hour Sunday sessions.
    "art-barn": dict(
        days=["Sun"],
        hoursEs="Dom 9:30 a 10:30 a. m. y 10:30 a 11:30 a. m. (estudio abierto de fin de semana)"),
    "gravity-vault-marin": dict(
        days=ALL_DAYS,
        hours="Mon to Fri 9am to 10pm; Sat and Sun 9am to 8pm. Kids 5 and up climb with a booked staff belay",
        hoursEs="Lun a vie 9 a. m. a 10 p. m.; sáb y dom 9 a. m. a 8 p. m. Niños de 5 años en adelante escalan con un asegurador del personal reservado con antelación"),
}


# Ages, shown in the "Days, Hours & Age" column (Alexandra 2026-10-24). English comes from the sheet's "Ages" column
# unless AGES overrides it; Spanish is hand-written here, like hoursEs.
AGES = {
    "flying-dutchman-gymnastics": "0 to 4 (toddler session), then all ages",
}
AGES_ES = {
    "the-social-klub": "0 a 7 años",
    "little-marin": "9 meses a 6 años",
    "kitsch-sync": "Desde bebés hasta edad escolar; Little Zone aparte para bebés y niños pequeños",
    "cal-star-gymnastics": "1 a 5 años",
    "novato-gymnastics-center-city-of-novato": "12 meses a 5 años",
    "flying-dutchman-gymnastics": "0 a 4 años (sesión para niños pequeños), luego todas las edades",
    "gymworld-gymnastics-parkour": "0 a 13 años",
    "fox-kit": "9 meses a 11 años (menores de 9 meses con un hermano mayor)",
    "playland-mt-tam-adventures-and-city-of-sausalito": "6 años y 11 meses o menos (desde el 2 de noviembre)",
    "bay-area-discovery-museum": "Pensado para 0 a 8 años",
    "play-well-teknologies": "Todas las edades; menores de 5 con supervisión",
    "gravity-vault-marin": "5 años en adelante para escalar con un asegurador del personal",
    "art-barn": "Todas las edades",
}


def _clean(v):
    if v is None:
        return ""
    s = re.sub(r"\s+", " ", str(v)).strip()
    return s.rstrip(";").strip()


def _slug(name):
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def _iso(v):
    if isinstance(v, datetime):
        return v.date().isoformat()
    s = _clean(v)
    for fmt in ("%b %d, %Y", "%B %d, %Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(s, fmt).date().isoformat()
        except ValueError:
            pass
    return s


def load_places():
    ws = openpyxl.load_workbook(XLSX_PATH, read_only=True)[SHEET]
    rows = list(ws.iter_rows(min_row=HEADER_ROW, values_only=True))
    idx = {_clean(h): i for i, h in enumerate(rows[0]) if _clean(h)}

    def col(row, header):
        return _clean(row[idx[header]]) if header in idx else ""

    places, seen = [], set()
    for row in rows[1:]:
        name = col(row, "Place")
        if not name:
            continue
        pid = _slug(name)
        if pid in seen:
            sys.exit(f"Duplicate place slug: {pid}")
        seen.add(pid)
        ov = OVERRIDES.get(pid)
        if ov is None:
            print(f"WARNING: no OVERRIDES entry for '{pid}': English hours used for Spanish, no days for the day filter")
            ov = {}
        program = col(row, "Program")
        if program not in CATEGORY:
            sys.exit(f"Program '{program}' ({name}) has no category: add it to CATEGORY")
        category = CATEGORY[program]
        website = col(row, "Website")
        if not website.startswith("http"):
            print(f"WARNING: no website for {name}")
        hours = ov.get("hours") or col(row, "Days & hours")
        places.append({
            "id": pid,
            "name": name,
            "program": program,
            "category": category,
            "categoryEs": CATEGORY_ES[category],
            "town": col(row, "Town"),
            # Region prefix on every location ("Marin/Novato"), so Phase 2 can add "Sonoma/..." (Alexandra 2026-10-24).
            "locationGroup": "Marin/" + col(row, "Location group (app filter)"),
            "region": "Marin",
            "days": ov.get("days", []),
            "hours": hours,
            # Non-breaking space inside "a. m." / "p. m." so a narrow phone column never splits them.
            "hoursEs": re.sub(r"\b([ap])\. m\.", "\\1.\u00a0m.", ov.get("hoursEs", hours)),
            "address": col(row, "Address"),
            "ages": AGES.get(pid) or col(row, "Ages"),
            "agesEs": AGES_ES.get(pid, ""),
            "cost": col(row, "Cost"),
            "booking": col(row, "Drop-in or book ahead"),
            "indoorOutdoor": col(row, "Indoor/Outdoor"),
            "phone": col(row, "Phone"),
            "website": website,
            "description": col(row, "Description"),
            "descriptionEs": col(row, "Description (ES)"),
            "lastVerified": _iso(row[idx["Last verified"]]) if "Last verified" in idx else "",
        })
    for pid in seen - set(AGES_ES):
        print(f"WARNING: no Spanish ages (AGES_ES) for '{pid}'")
    unused = set(OVERRIDES) - seen
    if unused:
        print(f"WARNING: OVERRIDES entries with no matching row: {sorted(unused)}")
    return places


def save_places(places):
    data = {"last_updated": date.today().isoformat(), "places": places}
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"adventure.json saved: {len(places)} places, {data['last_updated']}")


if __name__ == "__main__":
    save_places(load_places())
