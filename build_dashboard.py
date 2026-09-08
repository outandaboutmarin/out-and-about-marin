# -*- coding: utf-8 -*-
"""Render Alexandra's open-items tracker as a formatted HTML page.

    python build_dashboard.py            # write dashboard.html, then publish it
    python build_dashboard.py --check    # verify against open_items.md, write nothing

WHY THIS EXISTS AS A REAL FILE. CLAUDE.md described this generator as "a
scratchpad script" for weeks. Scratchpads are session-specific temp folders, so
a tool living in one is invisible to every future session by design -- and when
it was finally looked for on 2026-09-07 it did not exist at all. Every "show me
the dashboard" had quietly been a hand-rebuild of ~500 lines of HTML. It lives
in the repo now so it is findable, diffable, and survives the session.

WHY THE ITEM TEXT IS CURATED HERE RATHER THAN PARSED FROM THE MARKDOWN. The
dashboard is not a dump of open_items.md. It summarises, reprioritises and
editorialises -- that is what makes it readable, and the markdown's entries run
to several prose paragraphs each. A parser over prose would produce something
worse AND fail silently the moment the prose changed shape. So the summaries
live here, and `--check` guards the one thing that must not drift: which item
numbers are open.

KEEPING THE TWO IN SYNC. Closing an item means editing BOTH files in the same
pass: remove it from ITEMS here and add it to CLOSED, and do the equivalent in
open_items.md. `--check` will tell you if you forget. They have drifted before.

THE ARTIFACT. Publish the generated HTML to the SAME artifact so the link Alexandra
has keeps working:
    https://claude.ai/code/artifact/7c27ebfe-6674-4c8d-9b90-a0559d8e483c
Read it before republishing -- another session may have changed it.
"""
import argparse
import html
import io
import os
import re
import sys

ARTIFACT = "https://claude.ai/code/artifact/7c27ebfe-6674-4c8d-9b90-a0559d8e483c"
MD = (r"C:\Users\AWalter\Documents\2. Claude-Work\PROJECTS\OAA Marin"
      r"\OAA maintence and content\open_items.md")
UPDATED = "2026-09-07"

# ─────────────────────────────────────────────────────────────────────────────
# The content. `body` and `ask` accept inline HTML.
#   tone:  urgent | scheduled | open | hold
#   group: call | data | notstarted
# ─────────────────────────────────────────────────────────────────────────────
ITEMS = [
    dict(n=24, group="call", tone="urgent", created="2026-08-02",
         title="Table Lockdown — make the <code>users</code> table private",
         pill="Security · deferred by you",
         body="The site talks to the <code>users</code> table directly with the public key, so "
              "<b>phone numbers and hashed PINs are readable by anyone holding that key</b> — and "
              "the key is visible in <code>index.html</code>'s own source. The fix moves sign-in, "
              "sign-up and save-profile onto three Supabase Edge Functions using the private "
              "service role, then applies a Row-Level-Security lock so the public key loses all "
              "access. <b>About 45–60 minutes.</b> The full checklist, all three functions' code "
              "and the lockdown SQL are already written in <code>table_lockdown_checklist.md</code>. "
              "Nothing has been started.",
         ask="<b>Why it leads this list:</b> it is the only open item where the cost of waiting is "
             "other people's data rather than your time, and everything needed to close it is "
             "already written down. You deferred it deliberately — this is a nudge, not a new "
             "finding."),

    dict(n=15, group="call", tone="scheduled", created="2026-07-28",
         title="Instagram posting programme — unblocked", pill="In progress",
         body="<b>Yes, it can be automated</b> — carousel <i>and</i> the Stories that carry the "
              "links. Meta Business Suite publishes and schedules a Story with a link sticker; it "
              "is Meta's own surface and is not bound by the Graph API restriction that stops "
              "third-party tools. The one real limit is narrower than this item claimed for two "
              "days: <b>no third-party tool</b> (Buffer, Later, Metricool) can do it — which is "
              "exactly why the recommended route is browser automation against Business Suite "
              "rather than Buffer.<br><br><b>The renderer is built.</b> "
              "<code>render_slides.py</code> turns an approved mockup into 1080×1080 PNGs. That "
              "was the genuine blocker — every route needs image files and the post only existed "
              "as HTML. Twelve upload-ready slides for the week of Sep 11 are in "
              "<code>slides/week_of_sep11/</code>.",
         ask="<b>Nothing here is manual.</b> An earlier version of this card asked you to post "
             "a week by hand, reasoning that the link stickers needed attaching either way — "
             "<b>a leftover from the superseded claim that no tool can publish one</b>. Business "
             "Suite can, so the automation covers the whole post. <b>Next move is mine:</b> drive "
             "Business Suite, stage the Thursday post, and stop before anything publishes. "
             "<b>Cadence settled 2026-09-07:</b> Thursday 5:00 PM, Saturday 7:00 AM, Sunday "
             "5:00 PM — exact times, since scheduling needs a single minute."),

    dict(n=49, group="call", tone="open", created="2026-09-03",
         title="Two records still missing one fact", pill="Waiting on you",
         body="<p><span class='box'>☐</span> <b>Trick or Treat on Fourth Street (id 1004), Sat Oct "
              "24</b> — no time published, so <code>time</code> is the literal <code>\"TBD\"</code> "
              "rather than invented. It has a visible consequence: an unparseable time <b>sorts "
              "last within its day</b>, so the card sits at the bottom of Oct 24 until a real time "
              "is set.</p><p><span class='box'>☐</span> <b>2nd Friday Art Walk (id 1005)</b> — same "
              "<code>\"TBD\"</code>, same sorting consequence. Art Works Downtown runs it. The "
              "<i>cadence</i> is confirmed; only the time is missing.</p><p>The third, Sunday Cafe "
              "(id 1043), was resolved 2026-09-06.</p>",
         ask="<b>The principle behind both:</b> each record is correct but incomplete, and the "
             "missing fact was left blank rather than guessed. <b>A wrong time is worse than a "
             "visibly missing one</b>, because nothing later flags it."),

    dict(n=47, group="data", tone="scheduled", created="2026-09-03",
         title="December: re-add the two fortnightly storytimes",
         pill="Scheduled — first half of December",
         body="<p>Two library storytimes are stored as dated one-offs because both run <b>every "
              "fourteen days</b>, which <code>parseOccurrenceRule()</code> cannot express — it only "
              "understands \"the Nth weekday of the month\". When the stored dates run out, the "
              "programme silently stops appearing even though it is still running.</p>"
              "<p><b>The trap worth remembering, because it will recur:</b> a fortnightly series "
              "<b>impersonates an ordinal rule in any month where the two coincide</b>. No number "
              "of dates inside a single month can tell them apart — you need dates that straddle a "
              "month boundary. id 41 was set to \"2nd and 4th Thursdays\" from two October dates; "
              "it fitted October exactly and was wrong from November onward.</p><p>Also worth "
              "re-checking then: whether the branches have published Christmas and New Year "
              "closures.</p>"),

    dict(n=44, group="data", tone="hold", created="2026-08-27",
         title="Library records needing a call or one more month of data",
         pill="3 of 4 resolved",
         body="<p><span class='box'>☐</span> <b>id 3, Preschool Storytime (Belvedere-Tiburon)</b> — "
              "stored <code>Weekly</code> Wednesday 3:30 PM, but the branch <b>alternates it "
              "fortnightly with Mandarin Storytime</b>. As <code>Weekly</code> it advertises three "
              "Wednesdays this autumn that do not happen. A <code>skip:</code> is in as a stopgap; "
              "the cadence itself still needs the branch's pattern confirmed.</p>"
              "<p><span class='check'>✓</span> ids 43, 41 and 853 all resolved between 2026-09-01 "
              "and 2026-09-03. The recurring lesson from all three: <b>a per-programme flyer beats "
              "a calendar grid for cadence.</b></p>"),

    dict(n=50, group="data", tone="open", created="2026-09-03",
         title="Events to follow up on", pill="Leads, not events",
         body="<p><span class='box'>☐</span> <b>Barnes &amp; Noble weekly storytime</b> — no "
              "location, time, age range or source. Marin has more than one store.</p>"
              "<p><span class='box'>☐</span> <b>Petco playtime, Sept 19</b> — \"playtime\" at Petco "
              "is usually pet-focused, not a kids' event. Worth confirming it is family "
              "programming at all.</p><p><span class='box'>☐</span> <b>Target Marin City</b> — Aug "
              "29 has passed; Sept 26 would still be addable with a source.</p><p>All three "
              "arrived as a list with no supporting detail. The standing bar applies: add only if "
              "independently confirmed real, family-appropriate and correctly dated — and report "
              "\"none qualify\" rather than adding anything unverified.</p>"),

    dict(n=51, group="data", tone="hold", created="2026-09-07",
         title="id 215 has the wrong <code>expires</code> date",
         pill="Small fix",
         body="<p><b>The issue.</b> Jazz and Blues by the Bay ran every Friday through the summer, "
              "each date its own record. Every past record deleted itself when its date passed \u2014 "
              "<b>except id 215, Fri 5 June.</b> Its <code>expires</code> field says 25 September "
              "instead of 5 June, and the cleanup goes by <code>expires</code>, so it was told to "
              "keep it. The three September records are all correct. <b>id 215 is the only one "
              "wrong.</b></p>"
              "<p><b>What it costs.</b> Nothing to readers \u2014 past events do not show on the site. "
              "But it appears in the venue scan run before adding anything new, looking current, "
              "which could mean a skipped event or a duplicate.</p>",
         ask="<b>Recommendation:</b> set id 215's <code>expires</code> to 2026-06-05 so it clears "
             "on the next daily run, then check whether any other one-off has an "
             "<code>expires</code> well past its own date. Worth a one-line addition to the "
             "existing scans so it cannot happen quietly again. <b>No urgency.</b>"),

    dict(n=38, group="data", tone="hold", created="2026-08-21",
         title="Napa sweep follow-ups", pill="Half closed",
         body="<p><span class='check'>✓</span> Oct 4 LMR Jazz Orchestra — answered, declined. Not "
              "to be re-proposed by a future Napa sweep; it will keep appearing on the venue's "
              "seasonal-events page.</p><p><span class='box'>☐</span> <b>Hydro Bar &amp; Grill "
              "(Calistoga)</b> — the site returned HTTP 500 on 2026-08-21. Genuinely down, unlike "
              "Lincoln Ave Brewery, which turned out to be a dead URL in our own checklist rather "
              "than a dead venue. <b>Do not retire the record on one failed fetch</b>; retry next "
              "Napa sweep.</p>"),

    dict(n=34, group="notstarted", tone="open", created="2026-08-15",
         title="App code quality audit", pill="Needs a decision on shape",
         body="<p>A deliberate pass for defects and fragility rather than finding them one at a "
              "time by accident. The case for it is the pattern: the seasonal flip had never "
              "worked for any record, the daily scraper committed nothing for 98 days, "
              "<code>shouldShowEvent()</code> had no <code>Inactive</code> branch, the ALERT banner "
              "had no date awareness. <b>Every one was silent</b> — the site looked fine and "
              "nothing failed loudly. That is the class of problem an audit is for.</p><p><b>Scale:"
              "</b> <code>index.html</code> ~5,500 lines and 183 functions, all inline, no build "
              "step. Plus <code>library_review.py</code> 1,994, <code>scraper.py</code> 373, "
              "<code>check_duplicates.py</code> ~700. Deliberately out of scope: the "
              "<code>users</code> table exposure, which is #24.</p><p><b>Your call:</b> a written "
              "report you triage, or a work-through where fixes get applied as found. Recommend "
              "the report — several would change visible behaviour and you would want to approve "
              "them one at a time.</p>"),

    dict(n=33, group="notstarted", tone="open", created="2026-08-15",
         title="Tide Pool Table", pill="Scope undefined",
         body="<p>Name only so far. Not started deliberately — guessing the scope would build the "
              "wrong thing. Working assumption: a directory of Marin tide-pooling spots built the "
              "way the Swim Lesson Directory was.</p><p><b>What makes it different, and the first "
              "thing to settle:</b> the useful information is <b>time-dependent</b>. A spot is only "
              "worth visiting at low tide, so the table needs tide predictions rather than static "
              "rows. NOAA publishes free predictions for Marin stations, so the data is gettable "
              "without a paid service.</p>"),

    dict(n=17, group="notstarted", tone="open", created="2026-08-02",
         title="Build a preschool/daycare database", pill="Open",
         body="<p>Feature idea, no scope given. Worth clarifying what fields to track, how it gets "
              "populated and kept current, and how it sits alongside the events database.</p>"),

    dict(n=21, group="notstarted", tone="open", created="2026-08-02",
         title="Anchor other advertisers", pill="Open",
         body="<p>A prospect list exists from 2026-08-15, given as names only — not verified "
              "against business records, contacts, or whether any already appear in the events "
              "database. <b>The list ended mid-sentence</b> (\"social club, ;\"), so it may have "
              "been cut off. Send the rest and I will look each one up.</p>"),

    dict(n=20, group="notstarted", tone="open", created="2026-08-02",
         title="Reach out to Annie", pill="Open",
         body="<p>No detail beyond the title.</p>"),

    dict(n=22, group="notstarted", tone="open", created="2026-08-02",
         title="Set up Stripe", pill="Open",
         body="<p>No detail beyond the title — presumably for advertiser billing.</p>"),
]

CLOSED = [
    (39, "<code>Grown-Ups Only!</code> has zero events — <b>CLOSED 2026-09-07. The premise is gone: "
         "it has a record.</b> id 1094, the Waterfront Yoga Flow at DJs by the Bay. <b>Using it "
         "surfaced a real finding, now in CLAUDE.md:</b> the type is absent from <code>elig()</code>'s "
         "whitelist and <code>score()</code>'s weight map, so such a record <b>can never reach the "
         "Featured strip</b> — which is correct, not a bug, since the strip is family-facing."),
    (45, "should the duplicate scans ignore retired records — <b>CLOSED 2026-09-07.</b> It was never "
         "a design question: the filter already existed and had only ever been applied to half the "
         "data. <b>The payoff is not a tidier report</b> — superseded records can be retired again "
         "instead of deleted, which is what the tool had been quietly pushing against. 87 → 92 "
         "self-tests."),
    (23, "Facebook login snafu — CLOSED 2026-09-06, dropped rather than fixed. Its only significance "
         "was as a possible blocker for #15. The Instagram setup needs no Facebook Page, so it gates "
         "nothing."),
    (48, "two invisible records — CLOSED 2026-09-06. ids 31 and 586 had no ordinal phrase in "
         "<code>notes</code>, so <code>parseOccurrenceRule()</code> returned <code>null</code> and "
         "neither rendered on any date. Both set <code>Inactive</code> rather than deleted."),
    (12, "Learning Bus contact — CLOSED 2026-09-06. The September schedule was published and applied."),
    (30, "the September seasonal check — CLOSED 2026-09-03, verified on live data rather than "
         "assumed. <b>The first successful run of that code path</b> since it was repaired; before "
         "that every one of the 12 Seasonal records had been skipped in silence for months."),
    (46, "printed handouts beat websites — CLOSED 2026-09-02, your call: don't chase it. Opened and "
         "closed the same day, which is the right outcome for a question rather than a task."),
    (26, "San Anselmo storytimes — CLOSED 2026-08-28. The address could not be <i>verified</i> — the "
         "town contradicts itself across three of its own pages — so all three candidates are "
         "recorded on each record so nobody \"corrects\" it back."),
    (42, "DIY Yoto shared database — CLOSED 2026-08-28. Simpler than assumed: a Resources link to "
         "your own shared Drive folder, not a crowdsourced directory."),
    (36, "the <code>notes</code> field has no internal/public split — CLOSED 2026-08-21. All 109 "
         "records migrated, nothing deleted. <b>Verified on what the site derives</b>, not on the "
         "diff: 6,786 rendered dates before, 6,786 after."),
]

GROUPS = [
    ("data", "Data &amp; content", "Work in flight. None blocked on you."),
    ("notstarted", "Not started",
     "Three of these (#20, #21, #22) are the business-development thread and have sat untouched "
     "since 2 August with a line each. They are either a real workstream that deserves scoping, or "
     "they should come off the list — right now they are doing neither."),
]


# ─────────────────────────────────────────────────────────────────────────────
def open_numbers_in_markdown(path=MD):
    """The item numbers currently OPEN in open_items.md (above 'Recently closed')."""
    s = io.open(path, encoding="utf-8").read()
    body = s[:s.index("## Recently closed")]
    return {int(n) for n in re.findall(r"^\*\*(\d+)\.", body, re.M)}


def check():
    """Guard the one thing that must never drift: WHICH items are open."""
    try:
        md = open_numbers_in_markdown()
    except OSError as e:
        print("could not read %s: %s" % (MD, e))
        return 1
    mine = {i["n"] for i in ITEMS}
    missing = sorted(md - mine)     # open in markdown, absent from the dashboard
    extra = sorted(mine - md)       # on the dashboard, no longer open in markdown
    closed_here = {n for n, _ in CLOSED}
    both = sorted(mine & closed_here)
    ok = True
    if missing:
        print("MISSING from ITEMS (open in open_items.md): %s" % missing); ok = False
    if extra:
        print("STALE in ITEMS (not open in open_items.md): %s" % extra); ok = False
    if both:
        print("IN BOTH ITEMS and CLOSED: %s" % both); ok = False
    if ok:
        print("in sync: %d open items match open_items.md" % len(mine))
    return 0 if ok else 1


def pill(tone, text):
    return '<span class="pill %s">%s</span>' % (tone, text)


def render():
    tpl = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dashboard_template.html")
    shell = io.open(tpl, encoding="utf-8").read()

    calls = [i for i in ITEMS if i["group"] == "call"]
    cards = []
    for it in calls:
        cards.append(
            '<div class="pcard" style="--stripe:var(--s-%s)">\n'
            '  <div class="pcard-top">\n'
            '    <div class="pcard-title"><span class="item-no">#%d</span> %s</div>\n'
            '    %s\n  </div>\n'
            '  <div class="notes-body" style="margin-top:10px;padding-top:0;border-top:none">%s</div>\n'
            '  %s\n</div>'
            % (it["tone"], it["n"], it["title"], pill(it["tone"], it["pill"]), it["body"],
               ('<div class="pcard-ask">%s</div>' % it["ask"]) if it.get("ask") else ""))

    sections = []
    for key, label, note in GROUPS:
        rows = [i for i in ITEMS if i["group"] == key]
        out = ['<section class="group">',
               '<div class="group-head"><h2>%s</h2><div class="rule"></div>'
               '<span class="n">%d item%s</span></div>' % (label, len(rows), "" if len(rows) == 1 else "s"),
               '<p class="group-note">%s</p>' % note]
        for it in rows:
            out.append(
                '<div class="item">\n  <div class="item-row">\n'
                '    <div class="item-title"><span class="item-no">#%d</span> %s</div>\n'
                '    %s\n  </div>\n'
                '  <div class="item-meta">Created %s</div>\n'
                '  <details class="notes"><summary>Notes</summary>\n'
                '    <div class="notes-body">%s</div>\n  </details>\n</div>'
                % (it["n"], it["title"], pill(it["tone"], it["pill"]), it["created"], it["body"]))
        out.append("</section>")
        sections.append("\n".join(out))

    closed = "\n".join(
        '<div class="closed-item"><span class="check">✓</span><span class="body">'
        '<b style="color:var(--text-muted)">#%d</b> %s</span></div>' % (n, t)
        for n, t in CLOSED)

    n_call = len(calls)
    n_data = len([i for i in ITEMS if i["group"] == "data"])
    n_not = len([i for i in ITEMS if i["group"] == "notstarted"])

    return (shell
            .replace("{{UPDATED}}", UPDATED)
            .replace("{{N_CALL}}", str(n_call))
            .replace("{{N_DATA}}", str(n_data))
            .replace("{{N_NOTSTARTED}}", str(n_not))
            .replace("{{N_TOTAL}}", str(len(ITEMS)))
            .replace("{{N_CLOSED}}", str(len(CLOSED)))
            .replace("{{PRIORITY_CARDS}}", "\n".join(cards))
            .replace("{{SECTIONS}}", "\n".join(sections))
            .replace("{{CLOSED_LIST}}", closed))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-o", "--out", default="dashboard.html")
    ap.add_argument("--check", action="store_true",
                    help="verify ITEMS matches open_items.md; write nothing")
    a = ap.parse_args()

    if a.check:
        sys.exit(check())

    rc = check()   # always check before writing, so a stale page cannot ship quietly
    page = render()

    # rule 23: temp file, verify, then replace
    tmp = a.out + ".tmp"
    with io.open(tmp, "w", encoding="utf-8", newline="\n") as f:
        f.write(page)
    assert io.open(tmp, encoding="utf-8").read() == page, "temp did not round-trip"
    os.replace(tmp, a.out)

    print("wrote %s (%d chars)" % (a.out, len(page)))
    print("publish it to the SAME artifact, reading it first:\n  %s" % ARTIFACT)
    sys.exit(rc)


if __name__ == "__main__":
    main()
