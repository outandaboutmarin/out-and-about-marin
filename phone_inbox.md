# Phone inbox

To-dos from phone (cloud) sessions for Dropbox files they cannot reach: `open_items.md`, memory notes,
`Telluride\PARTNER_SETUP.md`. **A desktop session applies these at start, then empties this list and
commits.** See "Phone inbox" in CLAUDE.md. Skip any entry the target file already has.

## Pending

- **Memory note / to-do (2026-11-17, Alexandra):** when she asks how many clicks an event got (e.g. a sponsor listing), Claude should
  look it up for her in Supabase through her signed-in browser (Table Editor → `activity_log`, `action_type = event_click`,
  `event_id = <id>`; count rows, and distinct non-blank `user_id` for unique signed-in users) and tell her the number. She only
  knows how to open Supabase and read the table. First request: The Cave's Free Open Gym, id 2031 (Sun Nov 15).
- **`social_media_and_marketing.md` (2026-11-17, Alexandra):** one-off rainy-day post scheduled **Sun Nov 22, 4 PM** (Metricool id
  432433886): 5 slides, cover "School's out. Rain's in. Grandma's here." (turkey-post style with a faded umbrella), then
  Marin (14), Sonoma (5) and San Francisco (4) lists from Choose your own adventure, then the normal end slide. Staged at
  `ig/rainy_day_nov22/`. The regular Sun Nov 22, 5 PM weekly post is still to be built as usual.
- **`open_items.md`, new item under Marketing (2026-11-18, Alexandra): "No-Stuff Gift Guide Instagram post: decide when to
  post."** Status: slides, caption and first comment approved; not scheduled. Needs from you: pick the post date and time
  (ideas: Black Friday Nov 27 or Small Business Saturday Nov 28). Files: repo `ig/gift_guide_draft/` (4 slides + caption.md).
  4 slides: cover "THE 2026 GIFT GUIDE / No more stuff. / Give the gift of getting out of the house." (navy, faded gift box);
  "Gifts for Marin kids" and "Worth the drive" (Sonoma & SF) as gift tags with red bows tied through the holes, under
  "Dear Santa, no more stuff, please!" in red handwriting; then the normal end slide. Slides say "Prices from each venue ·
  ask about gift cards" (no venue was checked for gift cards).
- **`social_media_and_marketing.md` (2026-11-18):** record the one-off posts made from phone sessions this week: turkey trots
  (published Sun Nov 15, 5 PM, replaced the regular Sun Nov 15 post, which is a draft in Metricool, id 427425352); rainy-day
  post (scheduled Sun Nov 22, 4 PM, id 432433886); gift guide (approved, unscheduled, `ig/gift_guide_draft/`). Alexandra's
  style notes from the gift guide: no gold text or bows (use red); bows must look like real ribbon bows, not "bugs"; she
  liked the Halloween-post style for one-off posts and doubled cover fonts.
- **`open_items.md`, item 58 (to-confirm list) (2026-11-19, Alexandra: "wait for now"):** "Elevated Holiday: a curated luxury
  holiday pop-up weekend," Fri Dec 11 - Sun Dec 13, Downtown Tiburon (flyer from @chausaenz_official, reposted by @bebebitez,
  tags @outandaboutmarin). Not added yet: hours and exact venue/address not posted (the flyer's bottom line was hidden).
  Add as three one-offs (Community Event, free entry, goods for sale) once the hours and venue are published.
- **`Resources\create_your_own_adventure_v2.xlsx`, sheet "Create Your Own Adventure" (2026-11-19, Alexandra):** add a row for
  **Jump! City San Rafael** (Place name exactly that, so its slug matches `jump-city-san-rafael` in `adventure_io.py`), copying
  the values now live in `adventure.json`: Program "Indoor playground/drop-in"; town San Rafael; address Northgate Mall, 5800
  Northgate Drive, San Rafael, CA 94903; hours "Tue to Fri 4 to 7pm; Sat 11am to 7pm; Sun noon to 6pm; closed Mon"; ages "Kids
  at least 24 inches tall"; cost "$18 for unlimited play; group discounts for 3 or more; grip socks required"; booking "Drop-in;
  sometimes closed for private parties (dates on their site)"; Indoor; phone (877) 586-7248; website
  realjumpcity.com/park-locations/san-rafael; description EN/ES as in adventure.json; last verified 2026-11-19. Without the row,
  the next `python adventure_io.py` drops it (the converter warns "OVERRIDES entries with no matching row"). Edit the sheet in
  Excel, never openpyxl, if it has images.
