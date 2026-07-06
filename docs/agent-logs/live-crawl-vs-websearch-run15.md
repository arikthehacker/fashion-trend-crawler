# Live crawl vs WebSearch — run 15

Ran `python src/crawler.py` for real (no code changes) against current
`FASHION_SOURCES` (Vogue, Who What Wear, Hypebeast). Confirms run 8's findings still
hold: crawler works, no network/robots blocks beyond the one already-known
`vogue.com/search` skip.

**Raw output**: 30 pages crawled, `trends_raw.json` produced with **119 headline
strings, 106 unique** (13 exact duplicates from repeated nav links). Did not run
`summarize.py` — the raw-title inspection alone is enough to answer the volume
question, and it avoids spending real API tokens.

**Substance check (manual sample of ~25 random titles):** the volume is real but
mostly not style-discourse signal. Breakdown of what showed up:
- Genuine fashion-adjacent items: couture/runway recaps ("Fall 2016 Couture
  Rewind", "Spring 2027 Menswear Street Style Paris"), one designer-collab item
  (Christelle Kocher x Levi's), a vintage-revival sneaker/watch collab (Rowing
  Blazers x Seiko).
- Celebrity-wardrobe noise, not trend signal: Taylor Swift's wedding dress,
  Britney Spears's sons' runway debut, Madonna retrospective, Beyoncé anniversary
  countdown.
- Off-topic site noise: Hypebeast music/art/automotive verticals, PlayStation
  hardware news, an Oasis documentary, earthquake relief, promo-code pages,
  boilerplate ("Hypebeast. Driving Culture Forward", "Introducing our new AI
  chat function").
- Zodiac/seasonal-roundup filler that the project's own rules (per prior thin
  reports) explicitly exclude as undated noise ("Best Summer 2026 Trend ...
  According to Your Zodiac Sign").

Of 106 unique titles, a generous read finds on the order of 8-12 that would
plausibly clear the bar for a `top_signal` (would still need corroboration across
sources, which the crawler doesn't check) — most of the rest is celebrity
coverage, unrelated verticals, or site chrome that the existing manual
WebSearch-based process already correctly filters out before it ever becomes a
signal.

## Recommendation

The 4-thin-week streak looks like a real quiet period, not a WebSearch
under-finding artifact. A live crawl surfaces higher raw volume (119 vs. a
handful of WebSearch hits) but not higher *signal* volume — the crawler pulls
whole-site navigation output including sections (celebrity, beauty, music, auto,
earthquake relief) that were never candidates for style-discourse signals in the
first place, and don't add cross-source corroboration for the specific
recurring/declining signals (`peplum-waist-revival`, `sheer-layering`,
`off-duty-varsity`) the recent thin reports were actually checking on. Running
the crawler doesn't surface a fashion-week or comparable event that WebSearch
missed. No evidence this changes the thin-week calls already made.

No temp files were left — `trends_raw.json` (git-untracked crawl output) is
being removed as cleanup after this check; `summarize.py` was not run, so no
scratch report file exists to delete.
