# -*- coding: utf-8 -*-
"""Render an approved weekly-post mockup to Instagram-ready PNGs.

    python render_slides.py <mockup.html> [-o OUTDIR] [--size 1080]

WHY THIS EXISTS. The weekly post is authored and approved as an HTML page (see
`social_media_and_marketing.md` section 3b, Treatment C). Instagram takes image
files. Every publishing route we might pick -- Meta Business Suite, Buffer, the
Graph API -- needs PNGs, so this step is route-independent and blocks all of
them. Open item 15.

WHAT IT DOES. Loads the page in headless Chromium, finds every `.slide`, and
screenshots each one at exactly SIZE x SIZE. It does NOT re-lay-out the page:
each slide is already `container-type: inline-size` with every dimension in
`cqw`, so setting the element's width to 1080px makes the design resolve at
1080px natively. That is the whole reason the mockups were built in container
units -- a screenshot scaled up afterwards would be soft, and text hinted for a
260px card looks wrong at 4x.

OUTPUT. `<outdir>/<deck>-<n>-<slug>.png`, numbered in document order so the
carousel upload order is the filename order. Deck names come from the `<h2>`
above each row of slides, so a page holding all three weekly posts renders
`thursday-1-cover.png`, `saturday-2-repair-fair.png` and so on.

REQUIREMENTS. Playwright:  pip install playwright  &&  playwright install chromium
It is not in the repo's requirements; this script is a local authoring tool, not
part of the daily job.

VERIFY WHAT COMES OUT. --check re-opens each PNG and asserts it is SIZE x SIZE
and not blank (a uniformly single-coloured image usually means fonts or layout
had not settled). A renderer that silently emits twelve identical white squares
is exactly the "reports clean while incapable of reporting dirty" failure this
project keeps meeting, so the check is on by default.
"""
import argparse
import asyncio
import os
import re
import sys

SLIDE_SEL = ".slide"
DECK_SEL = "h2"


def slugify(text, limit=28):
    s = re.sub(r"[^a-z0-9]+", "-", (text or "").lower()).strip("-")
    return (s[:limit].rstrip("-")) or "slide"


async def render(path, outdir, size, check, fonts_ms):
    from playwright.async_api import async_playwright

    url = "file:///" + os.path.abspath(path).replace("\\", "/")
    os.makedirs(outdir, exist_ok=True)
    written = []

    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        # deviceScaleFactor stays 1: the slides are authored in container units,
        # so we render AT 1080 rather than rendering small and scaling up.
        page = await browser.new_page(viewport={"width": size + 200, "height": size + 200},
                                      device_scale_factor=1)
        await page.goto(url, wait_until="networkidle")

        # Google Fonts arrive after networkidle often enough to matter. Wait on
        # the browser's own font-loading promise rather than a fixed sleep, then
        # keep a short settle for layout. Without this the first slide renders in
        # Georgia and the rest in Playfair, which is invisible until you compare.
        try:
            await page.evaluate("document.fonts.ready")
        except Exception:
            pass
        await page.wait_for_timeout(fonts_ms)

        # Force every slide to the target size. `container-type: inline-size`
        # means the cqw-based type and spacing follow automatically.
        # box-sizing is the one that bites. Without it a slide carrying its own
        # horizontal padding (the navy covers use `padding: 0 9cqw`) renders
        # 1080 + 2*97 = 1274px wide, and the screenshot comes out 1311. The
        # authored page has no `* { box-sizing: border-box }` of its own; the
        # Artifact wrapper supplies one, so this only shows up when rendering
        # the local file. Forced on the slide AND its descendants.
        await page.add_style_tag(content=(
            "%s,%s *{box-sizing:border-box!important;}"
            "%s{width:%dpx!important;height:%dpx!important;"
            "min-width:%dpx!important;min-height:%dpx!important;"
            "max-width:none!important;max-height:none!important;"
            "aspect-ratio:auto!important;overflow:hidden!important;"
            "border-radius:0!important;box-shadow:none!important;}"
            % (SLIDE_SEL, SLIDE_SEL, SLIDE_SEL, size, size, size, size)))
        await page.wait_for_timeout(250)

        slides = await page.query_selector_all(SLIDE_SEL)
        if not slides:
            print("No %r elements found in %s" % (SLIDE_SEL, path), file=sys.stderr)
            await browser.close()
            return []

        # Name each slide by the nearest preceding <h2>, so a page carrying all
        # three weekly posts sorts into three named decks instead of one blob.
        decks = await page.evaluate(
            """(sel) => Array.from(document.querySelectorAll(sel)).map(el => {
                 let n = el, h = null;
                 while (n && !h) {
                   let p = n.previousElementSibling;
                   while (p && !h) {
                     // the heading is often INSIDE a wrapper (.slot-head > h2),
                     // so check the sibling itself and then look within it.
                     h = p.matches('h2') ? p : p.querySelector('h2');
                     p = p.previousElementSibling;
                   }
                   n = n.parentElement;
                 }
                 const cap = el.closest('.slot') ? el.closest('.slot').querySelector('cap') : null;
                 return { deck: h ? h.textContent : '', cap: cap ? cap.textContent : '' };
               })""", SLIDE_SEL)

        # Render each slide ALONE, pinned to the viewport origin.
        #
        # The obvious approach -- screenshot the element where it sits in the
        # grid -- has two faults that only show up when you actually look at the
        # output. A grid track rarely lands on a whole device pixel, so the
        # capture box rounds outward to 1081; and because that box overspills the
        # cell, it picks up a 1-2px SLIVER OF THE NEIGHBOURING SLIDE down the
        # left edge. Cropping hides the rounding but keeps the sliver, and a
        # coloured stripe down the side of a finished post is not something to
        # ship. Confirmed by eye 2026-09-07 on sunday-4.
        #
        # Hiding every other slide and fixing this one at (0,0) makes the capture
        # exact by construction: integer origin, nothing adjacent to bleed in.
        counters = {}
        for i, (el, meta) in enumerate(zip(slides, decks)):
            deck = slugify((meta.get("deck") or "post").split("—")[0], 20)
            counters[deck] = counters.get(deck, 0) + 1
            # the cap reads like "2 · friday · id 452"; keep the middle word
            parts = [p.strip() for p in (meta.get("cap") or "").split("·")]
            label = slugify(parts[1] if len(parts) > 1 else "slide", 18)
            name = "%s-%d-%s.png" % (deck, counters[deck], label)
            dest = os.path.join(outdir, name)
            await page.evaluate(
                """([sel, idx]) => {
                     const all = Array.from(document.querySelectorAll(sel));
                     all.forEach((s, j) => {
                       if (j === idx) {
                         s.style.display = '';
                         s.style.position = 'fixed';
                         s.style.left = '0px';
                         s.style.top = '0px';
                         s.style.margin = '0';
                         s.style.zIndex = '2147483647';
                       } else {
                         s.style.display = 'none';
                       }
                     });
                   }""", [SLIDE_SEL, i])
            await page.wait_for_timeout(60)
            await page.screenshot(path=dest,
                                  clip={"x": 0, "y": 0, "width": size, "height": size})
            off = _exact(dest, size)
            written.append(dest)
            print("  %s%s" % (name, off))

        await browser.close()

    if check:
        verify(written, size)
    return written


def _exact(path, size):
    """Trim the 1px overshoot CSS grid causes, and report anything larger.

    An element screenshot is taken from the element's device-pixel bounding box,
    and a grid track rarely lands on a whole pixel -- so a slide forced to
    exactly 1080px still screenshots as 1081. Cropping one row and column off
    the edge is invisible (every slide's outermost pixels are flat ground) and
    it makes the output exactly square, which Instagram cares about. Anything
    off by more than 2px is a layout fault, not rounding, so it is left alone
    for verify() to fail on loudly.
    """
    try:
        from PIL import Image
    except ImportError:
        return ""
    with Image.open(path) as im:
        w, h = im.size
        if (w, h) == (size, size):
            return ""
        if abs(w - size) > 2 or abs(h - size) > 2:
            return "  (! %dx%d)" % (w, h)
        im.crop((0, 0, size, size)).save(path)
    return "  (trimmed %dx%d)" % (w, h)


def verify(paths, size):
    """Assert each PNG is the right size and is not a single flat colour."""
    try:
        from PIL import Image
    except ImportError:
        print("\n  (--check skipped: Pillow not installed — `pip install pillow`)")
        return
    bad = []
    for p in paths:
        with Image.open(p) as im:
            if im.size != (size, size):
                bad.append("%s is %dx%d, expected %dx%d"
                           % (os.path.basename(p), im.size[0], im.size[1], size, size))
                continue
            # A slide that failed to lay out is one flat colour. Real slides carry
            # a navy bar, white card and coloured tag pills, so hundreds of values.
            colours = im.convert("RGB").getcolors(maxcolors=4096)
            if colours is not None and len(colours) < 12:
                bad.append("%s has only %d distinct colours — probably blank"
                           % (os.path.basename(p), len(colours)))
    if bad:
        print("\n❌ CHECK FAILED:")
        for b in bad:
            print("   " + b)
        sys.exit(1)
    print("\n✓ checked %d file(s): all %dx%d, none blank" % (len(paths), size, size))


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("html", help="the approved mockup page")
    ap.add_argument("-o", "--outdir", default=None,
                    help="output directory (default: ./slides/<html basename>)")
    ap.add_argument("--size", type=int, default=1080, help="square edge in px (default 1080)")
    ap.add_argument("--fonts-ms", type=int, default=600,
                    help="extra settle after document.fonts.ready (default 600)")
    ap.add_argument("--no-check", action="store_true", help="skip the output verification")
    a = ap.parse_args()

    if not os.path.exists(a.html):
        sys.exit("no such file: %s" % a.html)
    outdir = a.outdir or os.path.join("slides",
                                      os.path.splitext(os.path.basename(a.html))[0])
    print("rendering %s → %s at %dpx\n" % (a.html, outdir, a.size))
    files = asyncio.run(render(a.html, outdir, a.size, not a.no_check, a.fonts_ms))
    print("\n%d slide(s) written to %s" % (len(files), outdir))


if __name__ == "__main__":
    main()
