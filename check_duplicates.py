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

The four scans above audit events.json for duplicates ALREADY IN IT. They
cannot see a sweep candidate that hasn't been added yet — that is a different
job, and it is what --venue is for (added 2026-08-20 after nine already-existing
events were proposed as new in a single sweep). See rule 18 in CLAUDE.md.

Usage:
    python check_duplicates.py              # all scans, human-readable
    python check_duplicates.py --self-test  # verify the JS port is faithful
    python check_duplicates.py --quiet      # exit code only (0 clean, 1 findings)
    python check_duplicates.py --venue "Marin City Library"
                                            # BEFORE proposing a sweep candidate:
                                            # lists every record at that venue,
                                            # any name, any status. Match on
                                            # day+time+cadence, never on name.
"""
import sys, re, calendar, datetime, unicodedata
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


def alert_dates(notes):
    """
    Dates carried by date-scoped alerts — "ALERT[2026-09-22]: ..." — matching
    getAlertNote() in index.html. A bare "ALERT:" has no date and yields none.
    """
    if not notes:
        return set()
    return set(re.findall(r"ALERT\[(\d{4}-\d{2}-\d{2})\]:", notes, re.I))


def acknowledged_on(event, d):
    """
    True when this record already explains itself on date `d` — a date-scoped
    ALERT saying it's cancelled or replaced that day. Distinct from a `skip:`,
    which removes the occurrence entirely; an ALERT keeps it visible and tells
    the reader what's happening instead. Either way a human has decided, so the
    collision is resolved rather than outstanding.
    """
    iso = d.isoformat()
    return iso in alert_dates(event.get("notes")) or iso in parse_skip_dates(event.get("notes"))


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


def _start_time(t):
    """
    Just the START time, normalized — '12:30 PM - 2:00 PM' and '12:30 PM' are
    the same slot and must compare equal.

    WHY (found 2026-08-20): the COLLISION scan compared the raw `time` strings,
    so a recurring record storing a RANGE ('12:30 PM - 2:00 PM', id 208) never
    matched a one-off storing only a start ('12:30 PM', id 870) on the same
    date at the same venue. The finding was demoted to low-signal and hidden
    without --all, so a genuine double-booking passed a clean scan. Roughly a
    fifth of records store a range, so this was suppressing a whole class.
    """
    m = re.search(r"(\d{1,2})(?::(\d{2}))?\s*([AaPp])", str(t or ""))
    if not m:
        return str(t or "").strip().lower()
    h = int(m.group(1)) % 12
    if m.group(3).lower() == "p":
        h += 12
    return f"{h:02d}:{int(m.group(2) or 0):02d}"


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
            # Already acknowledged: the recurring record carries a date-scoped
            # ALERT for exactly this date, so a human has looked at the clash
            # and chosen to keep both — the recurring one rendering with a
            # "cancelled today" banner beside the one-off that replaces it.
            # Without this, a resolved collision is re-reported every night,
            # and since these findings now open a GitHub Issue (open item 31)
            # that would make the very first notification a false alarm.
            # First case: ids 781/6, Civic Center, 2026-09-22.
            if acknowledged_on(r, d) and not show_all:
                continue
            same_time = _start_time(r.get("time")) == _start_time(e.get("time"))
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

    # date-scoped ALERTs resolve a collision; bare ones must NOT (they carry no
    # date, so they say nothing about any particular day)
    sep22 = datetime.date(2026, 9, 22)
    sep15 = datetime.date(2026, 9, 15)
    dated = {"notes": "ALERT[2026-09-22]: Cancelled today — replaced by the bilingual storytime."}
    bare = {"notes": "ALERT: On break for all of August."}
    skipped = {"notes": "skip: 2026-09-22"}
    expect(acknowledged_on(dated, sep22), "dated ALERT should acknowledge its own date")
    expect(not acknowledged_on(dated, sep15), "dated ALERT must not acknowledge other dates")
    expect(not acknowledged_on(bare, sep22), "bare ALERT must not acknowledge any date")
    expect(acknowledged_on(skipped, sep22), "a skip: should acknowledge its date")
    expect(not acknowledged_on({"notes": ""}, sep22), "empty notes acknowledge nothing")

    # the live case this was built for: id 6 is flagged cancelled on Sep 22,
    # so its clash with the one-off id 781 is resolved, not outstanding
    if 6 in evs:
        expect(acknowledged_on(evs[6], sep22),
               "id 6 should be acknowledged on 2026-09-22 (ALERT scoped to that date)")
        expect(not acknowledged_on(evs[6], sep15),
               "id 6 should NOT be acknowledged on an ordinary Tuesday")

    # A range and a bare start time are the SAME slot. Comparing raw strings
    # hid a real id 208 / id 870 double-booking behind a clean scan.
    expect(_start_time("12:30 PM – 2:00 PM") == _start_time("12:30 PM"),
           "a time range must compare equal to its own start time")
    expect(_start_time("10:15 AM – 10:45 AM") == _start_time("10:15 AM"),
           "range/start equivalence must hold for morning times too")
    expect(_start_time("3:30 PM") != _start_time("3:45 PM"),
           "genuinely different start times must NOT collapse")
    expect(_start_time("12:00 PM") != _start_time("12:00 AM"),
           "noon and midnight must not collapse")

    # venue_scan must surface every duplicate the 2026-08-20 sweep missed.
    # These nine are the regression suite for rule 18 — if a future change to
    # the matching makes any of them stop appearing, that change reintroduces
    # the exact failure the scan was built to prevent.
    for venue, want in [("Lower Main Street, Tiburon", 459), ("Marin City Library", 10),
                        ("Town Center Corte Madera", 69), ("Bolinas Park", 71),
                        ("Robin Sweeny Park", 28), ("Sausalito Public Library", 627),
                        ("MarinMOCA", 209), ("Civic Center Library", 46),
                        ("San Anselmo Library", 685)]:
        if want in evs:
            ids = [e["id"] for e in venue_scan(events, venue)]
            expect(want in ids,
                   f"venue_scan({venue!r}) must surface id {want} (rule 18 regression)")

    print(f"self-test: {checks - len(failures)}/{checks} passed")
    for f in failures:
        print("  FAIL:", f)
    return not failures


def _norm_loose(s):
    """Aggressive normalize for venue/name comparison: strip accents, fold
    '&'->'and', drop all punctuation. 'Wiggles & Wonder' and 'Wiggles and
    Wonder' must land on the same string, and so must 'Storytime in the Park
    (with Riva)' and 'Storytime in the Park with Riva'."""
    s = unicodedata.normalize("NFKD", str(s or "")).encode("ascii", "ignore").decode()
    s = s.lower().replace("&", " and ")
    s = re.sub(r"[^a-z0-9 ]", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def venue_scan(events, needle):
    """
    List EVERY record at a venue/town, so a sweep candidate can be checked
    against the full slate rather than against a name guess.

    WHY THIS EXISTS (added 2026-08-20). The 2026-08-20 sweep proposed 37
    candidates; NINE were already in events.json. Every miss came from
    deduping by name substring — the stored names differed only by an
    ampersand, a parenthesis, a plural, or an inserted word:

        proposed 'Friday Night on Main'      -> stored 'Friday NightS on Main'   (id 459)
        proposed 'Wiggles AND Wonder'        -> stored 'Wiggles & Wonder'        (id 10)
        proposed 'Corte Madera Farmers Mkt'  -> stored '... TOWN CENTER Farmers' (id 69)
        proposed 'Fairfax Farmers Market'    -> stored '... COMMUNITY Farmers'   (id 71)
        proposed 'Storytime ... with Riva'   -> stored 'Storytime ... (with Riva)'(id 28)
        proposed '2nd Saturdays Storytime'   -> stored '... FAMILY Storytime'    (id 627)
        proposed 'Marin MOCA Family Day'     -> stored 'MarinMOCA Family Day'    (id 209)
        proposed 'Bookworms Book Club'       -> stored '... BY GORDON KORMAN'    (id 685)

    events_io.find_event() cannot catch these — it is a *substring* matcher and
    says so in its own docstring, yet it was the only candidate-stage tool.
    check_duplicates' four scans don't help either: they audit events.json for
    duplicates ALREADY IN IT and cannot see a candidate that hasn't been added.
    This closes that gap. Scanning by venue caught all nine instantly, because
    a venue name is short, stable, and doesn't get editorialised the way an
    event title does.
    """
    STOP = {"the", "a", "an", "of", "at", "in", "and", "de", "la", "el"}
    # Words too common across Marin venues to identify anything on their own.
    # Without this, 'Bolinas Park' matched every venue containing 'park' — 55
    # of 290 records — which is a list nobody reads, and an unread list is the
    # same failure as no list.
    # Marin-side generics, plus the wine-country ones. Napa venues are almost
    # all "<name> Vineyards / Winery / Cellars / Estate", so those words carry
    # no identifying signal there — matching on them made Ballentine, Romeo and
    # Markham all "match" Merryvale (ids 545-547) on the 2026-08-21 Napa sweep.
    GENERIC = {"park", "library", "center", "centre", "public", "room", "hall",
               "plaza", "field", "marin", "county", "st", "ave", "road", "street",
               "vineyards", "vineyard", "winery", "wineries", "cellars", "cellar",
               "estate", "ranch", "napa", "valley", "bar", "grill", "restaurant",
               "lounge", "cafe", "club", "the"}

    def tok(s):
        return {w for w in _norm_loose(s).split() if w not in STOP and len(w) > 1}

    n = _norm_loose(needle)
    nt = tok(needle)
    if not nt:
        return []
    hits = []
    for e in events:
        v, t = _norm_loose(e.get("venue")), _norm_loose(e.get("town"))
        vt, tt = tok(e.get("venue")), tok(e.get("town"))
        # Token overlap, NOT substring — venue words get reordered too.
        # 'Town Center Corte Madera' vs stored 'Corte Madera Town Center'
        # share every token but no useful substring, and that reordering
        # hid id 69 on the first pass at this very check.
        shared = nt & vt
        overlap = len(shared) / len(nt) if vt else 0
        distinctive = bool(shared - GENERIC)   # a shared 'park' proves nothing
        if ((overlap >= 0.5 and distinctive)
                or (vt and vt <= nt and distinctive)
                or (nt & tt and len(nt & tt) == len(nt))
                or n in v or (v and v in n)):
            hits.append(e)
    hits.sort(key=lambda e: (str(e.get("day") or ""), str(e.get("time") or "")))
    return hits


def main():
    data = events_io.load_events()
    events = data["events"]
    if "--self-test" in sys.argv:
        sys.exit(0 if self_test(events) else 1)

    if "--venue" in sys.argv:
        i = sys.argv.index("--venue")
        if i + 1 >= len(sys.argv):
            print("usage: check_duplicates.py --venue \"<venue or town>\"")
            sys.exit(2)
        needle = sys.argv[i + 1]
        hits = venue_scan(events, needle)
        print(f"{len(hits)} record(s) at a venue/town matching {needle!r}:\n")
        for e in hits:
            print(f"  id {e['id']:<5} {str(e.get('cadence')):<9} {str(e.get('day')):<10} "
                  f"{str(e.get('time')):<18} {str(e.get('status')):<14} {e.get('event_name')}")
            print(f"        venue={e.get('venue')}  date={e.get('event_date') or '-'}")
        if not hits:
            print("  (none — nothing on file at this venue, so any candidate here is genuinely new)")
        print("\nRead this whole list before proposing anything here. Match on "
              "day+time+cadence, NOT on the event name — see rule 18 in CLAUDE.md.")
        sys.exit(0)

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
