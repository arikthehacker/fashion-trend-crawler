# Southeast Asia source attempt (run 20)

Follow-up to run 19, which left Southeast Asia unaddressed (vogue.ph blocked
by a Cloudflare JS challenge). Only `src/crawler.py` and `src/taxonomy.py`
touched.

## Tested candidates

- **dewimagazine.com** (Dewi, Indonesia) -- KEPT. Home-grown Indonesian
  fashion/lifestyle title, published in Bahasa Indonesia for a domestic
  readership, not a Western edition. `python src/crawler.py
  https://www.dewimagazine.com` crawled cleanly: 10 pages, 15-25 headlines
  each, genuine current Indonesian-language content (Kate Middleton
  feature, a Chanel/Charvet story, gallery reviews) -- no bot block.
  Added to `FASHION_SOURCES` and `DOMAIN_SECTOR_MAP` as `editorial`.

- **lofficielthailand.com** (L'Officiel Thailand) -- REJECTED, same failure
  mode as vogue.ph. Direct `requests.get()` with the crawler's own UA
  returned a `403` (bot-detection page), and the crawler itself crawled 0
  pages. `robots.txt` itself returned 200, so this is an active
  content-page block, not a robots.txt disallow -- not fixable without a
  browser-rendering crawler.

- **oivietnam.com** (Oi Vietnam) -- REJECTED on fit, not crawlability. It
  crawled without any block (10 pages, real headlines), but on inspection
  it's an English-language expat lifestyle magazine ("Everywhere You Go")
  aimed at foreigners living in Vietnam, and its content skewed
  travel/food/events rather than fashion (headlines like a craft beer
  festival, a Jamaica cruise review). Same diaspora/expat-audience problem
  run 17-19 flagged for other candidates, so not a good local-for-local
  fit even though technically crawlable.

## Result

One genuine addition: `dewimagazine.com`. This is also incidentally the
first non-English-language source in `FASHION_SOURCES` (Bahasa Indonesia),
which is a small step toward the "non-English-language extraction" gap
run 19 also called out as future work.

## Verification

`python -m py_compile src/*.py` passes. Scratch `trends_raw.json` deleted
after each test run.
