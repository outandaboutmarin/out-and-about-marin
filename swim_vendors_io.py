"""
Converts the Marin swim lesson vendor spreadsheet into swim_vendors.json.

Source spreadsheet lives outside this repo (in Alexandra's "OAA maintence and
content" folder, not checked into git — matches how sweep review Excels are
kept out of the repo). Workflow when the spreadsheet changes: update the
XLSX_PATH below if the filename changed, re-run this script, commit the
resulting swim_vendors.json.

The "Ages Served" column is free text (e.g. "6 months+", "3 years+", "All
ages"), so minMonths per vendor is hand-assigned below rather than regex-
parsed — several phrasings are genuinely ambiguous ("3+" means 3 years in
context, not 3 months) and guessing wrong would silently break the age
filter. Same reasoning for facilityType (mapped to the 7 canonical
categories from the spreadsheet's own Notes sheet) and classTypes (mapped to
the 12 standardized labels, stripping vendor-specific parenthetical detail
which stays in `notes` instead).
"""
import json
import os
from datetime import date

XLSX_PATH = r"C:\Users\AWalter\Documents\2. Claude-Work\PROJECTS\OAA Marin\OAA maintence and content\Marin_Swim_Lesson_Vendor_Dashboard_v4.xlsx"
OUT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "swim_vendors.json")

# Per-vendor overrides that can't be safely auto-derived from the raw sheet text.
# Keyed by row index (0-based, in sheet order) as a cross-check against VENDOR_NAME.
# indoorOutdoor is normalized to exactly one of: Indoor, Outdoor, Both, Varies
# (the raw column mixes in parenthetical detail like "(private pools)" that
# belongs in poolInfo/notes instead of a filter value).
OVERRIDES = [
    dict(id="osher-marin-jcc", minMonths=6, towns=["San Rafael"],
         facilityType="JCC / YMCA", indoorOutdoor="Both",
         classTypes=["Parent & Child", "Group Lessons", "Semi-Private Lessons", "Private Lessons", "Adult Lessons"]),
    dict(id="marin-ymca", minMonths=6, towns=["San Rafael"],
         facilityType="JCC / YMCA", indoorOutdoor="Indoor",
         classTypes=["Parent & Child", "Group Lessons", "Private Lessons", "Water Safety Classes", "Swim Team"]),
    dict(id="marinwood-swim-academy", minMonths=36, towns=["San Rafael"],
         facilityType="City/Public Recreation Pool", indoorOutdoor="Outdoor",
         classTypes=["Group Lessons"]),
    dict(id="terra-linda-community-pool", minMonths=6, towns=["San Rafael"],
         facilityType="City/Public Recreation Pool", indoorOutdoor="Outdoor",
         classTypes=["Group Lessons", "Private Lessons"]),
    dict(id="rafael-racquet-club-aquatics", minMonths=36, towns=["San Rafael"],
         facilityType="Private Club (Membership)", indoorOutdoor="Outdoor",
         classTypes=["Group Lessons", "Private Lessons"]),
    dict(id="miss-jean-swimming", minMonths=0, towns=["San Rafael", "Mill Valley"],
         facilityType="Independent Instructor (Mobile/Multiple Locations)", indoorOutdoor="Outdoor",
         classTypes=["Group Lessons", "Private Lessons"],
         notes_append="Teaches at private pools (locations vary by instructor)."),
    dict(id="la-petite-baleen-sf-presidio", minMonths=2, towns=["San Francisco"],
         facilityType="Swim School (Established Business)", indoorOutdoor="Indoor", inMarin=False,
         classTypes=["Parent & Child", "Group Lessons", "Semi-Private Lessons", "Private Lessons"]),
    dict(id="la-petite-baleen-rohnert-park", minMonths=2, towns=["Rohnert Park"],
         facilityType="Swim School (Established Business)", indoorOutdoor="Indoor", inMarin=False,
         classTypes=["Parent & Child", "Group Lessons", "Semi-Private Lessons", "Private Lessons"]),
    dict(id="bay-club-rolling-hills", minMonths=6, towns=["Novato"],
         facilityType="Private Club (Membership)", indoorOutdoor="Outdoor",
         classTypes=["Parent & Child", "Group Lessons"]),
    dict(id="hamilton-community-pool", minMonths=6, towns=["Novato"],
         facilityType="City/Public Recreation Pool", indoorOutdoor="Outdoor",
         classTypes=["Parent & Child", "Group Lessons", "Water Aerobics"]),
    dict(id="miwok-aquatic-fitness-center", minMonths=0, towns=["Novato"],
         facilityType="City/Public Recreation Pool", indoorOutdoor="Indoor",
         classTypes=["Group Lessons", "Water Aerobics", "Lap Swim"]),
    dict(id="mill-valley-recreation-aquatics", minMonths=6, towns=["Mill Valley"],
         facilityType="City/Public Recreation Pool", indoorOutdoor="Indoor",
         classTypes=["Parent & Child", "Group Lessons", "Semi-Private Lessons", "Private Lessons"]),
    dict(id="scott-valley-swimming-tennis-club", minMonths=6, towns=["Mill Valley"],
         facilityType="Private Club (Membership)", indoorOutdoor="Outdoor",
         classTypes=["Parent & Child", "Group Lessons"]),
    dict(id="strawberry-recreation-district", minMonths=6, towns=["Mill Valley"],
         facilityType="City/Public Recreation Pool", indoorOutdoor="Outdoor",
         classTypes=["Group Lessons"]),
    dict(id="infant-swimming-resource-marin", minMonths=6, towns=["Mill Valley", "San Rafael"],
         facilityType="Independent Instructor (Mobile/Multiple Locations)", indoorOutdoor="Outdoor",
         classTypes=["Private Lessons"]),
    dict(id="ac-swim-club", minMonths=18, towns=["San Rafael"],
         facilityType="Swim School (Established Business)", indoorOutdoor="Outdoor",
         classTypes=["Group Lessons", "Competitive-Track Lessons"]),
    dict(id="protea-swim-company", minMonths=0,
         towns=["Mill Valley", "San Rafael", "Corte Madera", "Sausalito", "Novato"],
         facilityType="Independent Instructor (Mobile/Multiple Locations)", indoorOutdoor="Varies",
         classTypes=["Group Lessons", "Semi-Private Lessons", "Private Lessons"]),
    dict(id="bay-club-ross-valley", minMonths=6, towns=["Kentfield"],
         facilityType="Private Club (Membership)", indoorOutdoor="Outdoor",
         classTypes=["Parent & Child", "Group Lessons", "Stroke Clinics", "Adult Lessons"]),
    dict(id="mt-tam-racquet-athletic-club", minMonths=0, towns=["Larkspur"],
         facilityType="Private Club (Membership)", indoorOutdoor="Both",
         classTypes=["Parent & Child", "Group Lessons", "Stroke Clinics", "Water Aerobics", "Summer Camps"]),
    dict(id="belvedere-tennis-club", minMonths=0, towns=["Tiburon"],
         facilityType="Private Club (Membership)", indoorOutdoor="Outdoor",
         classTypes=["Group Lessons", "Private Lessons"]),
    dict(id="tiburon-peninsula-club", minMonths=0, towns=["Tiburon"],
         facilityType="Private Club (Membership)", indoorOutdoor="Outdoor",
         classTypes=["Group Lessons"]),
]


def _clean(v):
    if v is None:
        return ""
    return str(v).strip()


def load_vendors():
    import openpyxl
    wb = openpyxl.load_workbook(XLSX_PATH, data_only=True)
    ws = wb["Swim Lesson Vendors"]
    rows = list(ws.iter_rows(values_only=True))
    header = rows[3]
    data_rows = [r for r in rows[4:] if any(c is not None for c in r)]
    assert len(data_rows) == len(OVERRIDES), (
        f"Row count changed ({len(data_rows)} rows vs {len(OVERRIDES)} overrides) "
        "-- update OVERRIDES to match before regenerating."
    )

    idx = {h: i for i, h in enumerate(header)}
    vendors = []
    for row, ov in zip(data_rows, OVERRIDES):
        name = _clean(row[idx["Vendor Name"]])
        website_raw = _clean(row[idx["Website"]])
        website = website_raw if website_raw.startswith("http") else ("https://" + website_raw) if website_raw else ""
        notes = _clean(row[idx["Notes"]])
        if ov.get("notes_append"):
            notes = (notes + " " + ov["notes_append"]).strip()
        vendors.append({
            "id": ov["id"],
            "name": name,
            "facilityType": ov["facilityType"],
            "town": _clean(row[idx["Town"]]),
            "towns": ov["towns"],
            "address": _clean(row[idx["Address"]]),
            "phone": _clean(row[idx["Phone"]]),
            "website": website,
            "agesServed": {
                "minMonths": ov["minMonths"],
                "displayText": _clean(row[idx["Ages Served"]]),
            },
            "classTypes": ov["classTypes"],
            "poolInfo": _clean(row[idx["Pool Info"]]),
            "indoorOutdoor": ov["indoorOutdoor"],
            "hoursSeason": _clean(row[idx["Hours / Season"]]),
            "notes": notes,
            "inMarin": ov.get("inMarin", True),
            "lastVerified": "2026-07-01",
        })
    return vendors


def save_vendors(vendors):
    data = {"last_updated": date.today().isoformat(), "vendors": vendors}
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"swim_vendors.json saved — {len(vendors)} vendors — {data['last_updated']}")


if __name__ == "__main__":
    save_vendors(load_vendors())
