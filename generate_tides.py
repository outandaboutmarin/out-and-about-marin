#!/usr/bin/env python3
"""
generate_tides.py  —  Out AND About Marin
Builds tides.json: every high & low tide, for every day, for four
tide-impacted Marin driving spots.

Data source: NOAA CO-OPS Tide Predictions API (free, no key).
  product=predictions, interval=hilo, datum=MLLW, time_zone=lst_ldt, units=english

Tide predictions are astronomical and computed years ahead, so this is a
ONE-TIME pull (re-run only to extend the year range). No daily job needed —
the app reads this fixed table and figures out "today" from the device clock.

USAGE
  python3 generate_tides.py                  # current year + next year
  python3 generate_tides.py --begin 20260101 --end 20271231
  python3 generate_tides.py --sample         # offline synthetic data (preview only)

If NOAA is unreachable from where you run this, just open each station URL in a
browser, save the JSON, and rebuild from the saved files (see build_from_files).
Writes tides.json next to this script.
"""

import json, sys, datetime, urllib.request

# Four locations, in left-to-right column order (key, NOAA id, column header, full name, ES name)
STATIONS = [
    {"key": "tam",     "noaa_id": "9414806", "short": "Tam Junction",
     "name": "Tam Junction / Sausalito", "name_es": "Tam Junction / Sausalito"},
    {"key": "corte",   "noaa_id": "9414874", "short": "Corte Madera",
     "name": "Corte Madera Creek", "name_es": "Corte Madera Creek"},
    {"key": "hwy37",   "noaa_id": "9414290", "short": "Hwy 37",
     "name": "Hwy 37 (Golden Gate reference)", "name_es": "Hwy 37 (referencia Golden Gate)"},
    {"key": "bolinas", "noaa_id": "9414958", "short": "Bolinas",
     "name": "Bolinas Lagoon", "name_es": "Laguna de Bolinas"},
]
API = "https://api.tidesandcurrents.noaa.gov/api/prod/datagetter"


def fetch_station(noaa_id, begin, end):
    url = (f"{API}?begin_date={begin}&end_date={end}&station={noaa_id}"
           f"&product=predictions&datum=MLLW&time_zone=lst_ldt"
           f"&interval=hilo&units=english&format=json&application=outandaboutmarin")
    req = urllib.request.Request(url, headers={"User-Agent": "outandaboutmarin/1.0"})
    with urllib.request.urlopen(req, timeout=90) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    if "predictions" not in data:
        raise RuntimeError(f"No predictions for {noaa_id}: {data}")
    return data["predictions"]


def synth_station(begin, end, phase):
    import math
    d0 = datetime.datetime.strptime(begin, "%Y%m%d").date()
    d1 = datetime.datetime.strptime(end, "%Y%m%d").date()
    out, day = [], d0
    while day <= d1:
        n = (day - d0).days
        sh = (n * 50) % 1440
        for mins, typ, h in [(60 + sh, "L", 0.7 + 0.12*phase - 0.5*math.sin(n/3)),
                              (432 + sh, "H", 5.9 + 0.25*phase + 0.5*math.sin(n/3.2)),
                              (804 + sh, "L", 1.4 - 0.1*phase - 0.4*math.cos(n/4)),
                              (1176 + sh, "H", 4.7 + 0.2*phase + 0.4*math.cos(n/4.5))]:
            hh, mm = divmod(int(mins) % 1440, 60)
            out.append({"t": f"{day.isoformat()} {hh:02d}:{mm:02d}", "type": typ, "v": str(round(h, 1))})
        day += datetime.timedelta(days=1)
    return out


def group(preds):
    byday = {}
    for p in preds:
        date, tm = p["t"].split(" ")
        byday.setdefault(date, []).append([tm, p["type"], round(float(p["v"]), 1)])
    return byday


def build(sample=False, begin=None, end=None):
    today = datetime.date.today()
    if not begin:
        begin = f"{today.year}0101"
    if not end:
        end = f"{today.year + 1}1231"          # current year + next year
    tides = {}
    for i, st in enumerate(STATIONS):
        if sample:
            preds = synth_station(begin, end, i)
        else:
            print(f"  fetching {st['name']} ({st['noaa_id']}) {begin}-{end} ...")
            preds = fetch_station(st["noaa_id"], begin, end)
        tides[st["key"]] = group(preds)

    out = {
        "generated": today.isoformat(),
        "sample": bool(sample),
        "datum": "MLLW", "units": "ft",
        "source": "NOAA CO-OPS tide predictions",
        "stations": [{k: st[k] for k in ("key", "noaa_id", "short", "name", "name_es")}
                     for st in STATIONS],
        "tides": tides,
    }
    with open("tides.json", "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, separators=(",", ":"))
    days = len(next(iter(tides.values())))
    print(f"Wrote tides.json — {len(STATIONS)} stations, ~{days} days each, "
          f"{'SAMPLE' if sample else 'REAL'} data, {begin}-{end}.")


if __name__ == "__main__":
    a = sys.argv[1:]
    kw = {"sample": "--sample" in a}
    if "--begin" in a:
        kw["begin"] = a[a.index("--begin") + 1]
    if "--end" in a:
        kw["end"] = a[a.index("--end") + 1]
    build(**kw)
