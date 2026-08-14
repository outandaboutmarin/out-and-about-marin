# -*- coding: utf-8 -*-
"""
Duplicate checker for events.json — run this at the start of a session and
after any batch add, sweep apply, or record replacement.

Five duplicate pairs were found on the live site in two days (2026-08-12/13),
each rendering the same event twice to users. They were NOT all catchable the
same way, which is why this runs four different scans:

  1. EXACT       same (event_name, venue, event_date)                caught 766/799, 767/800
  2. NORMALIZED  same (date, time, town, name-prefix)                caught 768/801, which
                 ignoring punctuation, bilingual "|" suffixes and    differ in BOTH name and
                 venue-string drift                                   venue string
  3. RECURRING   two recurring records in the same
                 (day, time, venue, cadence) slot                    caught 34/627
  4. COLLISION   a One-off landing on a date a recurring record      caught 572/573 vs id 74,
                 already generates — the class the other three       and 177 vs 827
                 scans structurally cannot see

Scan 4 needs the app's own occurrence logic, so parseOccurrenceRule /
parseSkipDates / doesEventOccurOnDate below are deliberate line-by-line ports
of the JavaScript in index.html. **If that logic changes, change it here too**
— `--self-test` asserts the port still agrees with known-good records.

Usage:
    python check_duplicates.py              # all scans, human-readable
    python check_duplicates.py --self-test  # verify the JS port is faithful
    python check_duplicates.py --quiet      # exit code only (0 clean, 1 findings)
"""
import sys, re, calendar, datetime
from collections import defaultdict

import events_io

DAY_NAMES = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
ORDINALS = {"first": 1, "1st": 1, "second": 2, "2nd": 2, "third": 3, "3rd": 3,
            "fourth": 4, "4th": 4, "fifth": 5, "5th": 5}
_ORD_ANY = re.compile(r"\b(1st|2nd|3rd|4th|5th|first|second|third|fourth|fifth|last)\b")


# ── ports of index.html ───────────────────────────────────────────────────
def parse_occurrence_rule(notes):
    """Port of parseOccurrenceRule(). Returns a dict or None."""
    if not notes:
        return None
    n = notes.lower()
    if "check" in n and "calendar" in n and not _ORD_ANY.search(n):
        return {"unpredictable": True}
    if re.search(r"\blast\b", n):
        return {"last": True}
    found = []
    for word, num in ORDINALS.items():
        if re.search(r"\b" + word + r"\b", n):
            found.append(num)
    if not found:
        return None
    if len(found) == 1:
        return {"nth": found[0]}
    return {"nths": sorted(set(found))}


def parse_skip_dates(notes):
    """Port of parseSkipDates()."""
    if not notes:
        return set()
    return set(re.findall(r"\bskip\s*:?\s*(\d{4}-\d{2}-\d{2})", notes, re.I))


def _nth_weekday(nth, day_index, year, month):
    count = 0
    for day in range(1, calendar.monthrange(year, month)[1] + 1):
        d = datetime.date(year, month, day)
        if (d.weekday() + 1) % 7 == day_index:
            count += 1
            if count == nth:
                return d
    return None


def _last_weekday(day_index, year, month):
    last = None
    for day in range(1, calendar.monthrange(year, month)[1] + 1):
        d = datetime.date(year, month, day)
        if (d.weekday() + 1) % 7 == day_index:
            last = d
    return last


def does_event_occur_on(e, d):
    """Port of doesEventOccurOnDate(). `d` is a datetime.date."""
    day_field = str(e.get("day") or "")
    days = [x.strip() for x in day_field.split("/")] if "/" in day_field else [day_field]
    day_index = (d.weekday() + 1) % 7          # Python Mon=0 -> JS Sun=0
    if DAY_NAMES[day_index] not in days:
        return False

    cadence = e.get("cadence")
    if cadence == "Weekly":
        occurs = True
    else:
        rule = parse_occurrence_rule(e.get("notes"))
        if not rule:
            occurs = cadence != "Monthly"
        elif rule.get("unpredictable"):
            occurs = False
        elif rule.get("last"):
            occurs = _last_weekday(day_index, d.year, d.month) == d
        elif rule.get("nth"):
            occurs = _nth_weekday(rule["nth"], day_index, d.year, d.month) == d
        elif rule.get("nths"):
            occurs = any(_nth_weekday(n, day_index, d.year, d.month) == d
                         for n in rule["nths"])
        else:
            occurs = True

    if occurs and d.isoformat() in parse_skip_dates(e.get("notes")):
        occurs = False
    return occurs


# ── scans ─────────────────────────────────────────────────────────────────
def _norm(name):
    return re.sub(r"[^a-z]", "", str(name).lower())[:14]


def scan(events, horizon_days=180):
    """Returns a list of (severity, label, detail) findings."""
    findings = []
    one_offs = [e for e in events if e.get("cadence") == "One-off" and e.get("event_date")]
    recurring = [e for e in events
                 if e.get("cadence") not in ("One-off", "", None)
                 and e.get("status") not in ("Inactive", "Seasonal - Inactive")]

    # 1. exact
    g = defaultdict(list)
    for e in one_offs:
        g[(str(e.get("event_name")).strip().lower(),
           str(e.get("venue")).strip().lower(),
           e["event_date"])].append(e["id"])
    for k, ids in sorted(g.items()):
        if len(ids) > 1:
            findings.append(("EXACT", f"ids {ids}", f"{k[0][:44]!r} @ {k[1][:30]} on {k[2]}"))

    # 2. normalized
    g = defaultdict(list)
    for e in one_offs:
        g[(e["event_date"], str(e.get("time")), str(e.get("town")).lower(),
           _norm(e.get("event_name")))].append(e["id"])
    for k, ids in sorted(g.items()):
        if len(ids) > 1:
            findings.append(("NORMALIZED", f"ids {ids}",
                             f"{k[0]} {k[1]} in {k[2]} — name-prefix {k[3]!r}"))

    # 3. recurring same-slot — only when the ordinals ALSO match. Two Monthly
    #    records can legitimately share a slot on different weeks of the month
    #    (San Anselmo runs Read to a Dog on the 3rd Wednesday and Crafternoon on
    #    the last Wednesday, both 3:00 PM). Flagging those is noise.
    g = defaultdict(list)
    for e in recurring:
        g[(str(e.get("day")), str(e.get("time")), str(e.get("venue")).lower(),
           e.get("cadence"))].append(e)
    for k, group in sorted(g.items(), key=lambda kv: str(kv[0])):
        if len(group) < 2:
            continue
        by_rule = defaultdict(list)
        for e in group:
            by_rule[repr(parse_occurrence_rule(e.get("notes")))].append(e["id"])
        for rule, ids in by_rule.items():
            if len(ids) > 1:
                findings.append(("RECURRING", f"ids {ids}",
                                 f"{k[0]} {k[1]} @ {k[2][:34]} ({k[3]}) — same slot AND "
                                 f"same occurrence rule {rule}"))

    # 4. one-off colliding with a recurring record's computed dates.
    #    Only a SAME-TIME collision is a real signal: a library legitimately
    #    runs storytime at 9:30 and a puzzle swap at 1:00 on the same Thursday.
    #    Same venue + same date + same time is the shape every real duplicate
    #    had (572/573 vs 74, 177 vs 827). Use --all to see the rest.
    show_all = "--all" in sys.argv
    today = datetime.date.today()
    horizon = today + datetime.timedelta(days=horizon_days)
    for e in one_offs:
        try:
            d = datetime.date.fromisoformat(e["event_date"])
        except ValueError:
            continue
        if not (today <= d <= horizon):
            continue
        for r in recurring:
            if str(r.get("venue")).strip().lower() != str(e.get("venue")).strip().lower():
                continue
            if not does_event_occur_on(r, d):
                continue
            same_time = str(r.get("time")).strip() == str(e.get("time")).strip()
            if not same_time and not show_all:
                continue
            findings.append((
                "COLLISION" if same_time else "collision?",
                f"one-off {e['id']} vs recurring {r['id']}",
                f"{d} {e.get('time')} @ {str(e.get('venue'))[:30]} — "
                f"{str(e.get('event_name'))[:34]!r} lands on a date id {r['id']} "
                f"({str(r.get('event_name'))[:28]!r}) already generates"
                + ("" if same_time else
                   f" [different times: {e.get('time')} vs {r.get('time')} — "
                   f"probably two separate programs]")
                + (" — either these are the same event, or the recurring record "
                   "needs a 'skip: %s' note" % d if same_time else "")))
    return findings


# ── self-test: does the port still match the JS? ──────────────────────────
def self_test(events):
    evs = {e["id"]: e for e in events}
    checks, failures = 0, []

    def expect(cond, msg):
        nonlocal checks
        checks += 1
        if not cond:
            failures.append(msg)

    # rule parsing, against records verified in-browser 2026-08-13
    known = {74: {"nth": 2}, 705: {"nths": [1, 3]}, 815: {"nths": [2, 4]},
             824: {"nth": 4}, 36: {"nth": 3}, 45: {"last": True}}
    for i, want in known.items():
        if i in evs:
            got = parse_occurrence_rule(evs[i].get("notes"))
            expect(got == want, f"id {i} rule: want {want}, got {got}")

    # id 74 is 2nd-Friday: must hit the city's published dates, miss others
    if 74 in evs:
        for iso in ("2026-07-10", "2026-08-14", "2026-09-11"):
            expect(does_event_occur_on(evs[74], datetime.date.fromisoformat(iso)),
                   f"id 74 should occur on {iso}")
        for iso in ("2026-08-21", "2026-08-07"):
            expect(not does_event_occur_on(evs[74], datetime.date.fromisoformat(iso)),
                   f"id 74 should NOT occur on {iso}")

    # a Monthly record with no ordinal must render nowhere (rule 9)
    for i in (31, 43):
        if i in evs and evs[i].get("cadence") == "Monthly":
            any_hit = any(does_event_occur_on(evs[i], datetime.date.today() + datetime.timedelta(days=k))
                          for k in range(90))
            expect(not any_hit, f"id {i} is Monthly with no usable rule and should never occur")

    print(f"self-test: {checks - len(failures)}/{checks} passed")
    for f in failures:
        print("  FAIL:", f)
    return not failures


def main():
    data = events_io.load_events()
    events = data["events"]
    if "--self-test" in sys.argv:
        sys.exit(0 if self_test(events) else 1)

    findings = scan(events)
    quiet = "--quiet" in sys.argv
    if not quiet:
        print(f"checked {len(events)} events\n")
        if not findings:
            print("No duplicates found. All four scans clean.")
        else:
            for sev, who, detail in findings:
                print(f"[{sev:10}] {who}\n             {detail}")
            print(f"\n{len(findings)} finding(s). COLLISION and EXACT are almost always "
                  f"real; RECURRING and NORMALIZED need a look — differing ordinals or "
                  f"genuinely distinct programs can share a slot.")
    sys.exit(1 if findings else 0)


if __name__ == "__main__":
    main()
