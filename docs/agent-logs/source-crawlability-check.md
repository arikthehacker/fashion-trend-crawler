# Source crawlability check (run 17 follow-up)

Ran `python src/crawler.py` for real against all `FASHION_SOURCES`, checking
the 4 sources added in run 17 (see `source-diversity-expansion.md`).

## Results

- **nataal.com** — worked. Depth-1 pages returned headlines (1-9 each).
- **okayafrica.com** — worked well. Root page + regional news pages returned
  19-26 headlines each.
- **fashionunited.in** — worked. Fewer headlines (3-10 per page) but real,
  current article titles (e.g. Paris Haute Couture Week coverage), not
  boilerplate/nav text.
- **tokyofashion.com** — initially failed: crawler logged
  `[blocked by robots.txt] https://tokyofashion.com` and skipped it entirely.

## Root cause and fix

Investigated `get_robots_parser()` in `src/crawler.py`. It called
`RobotFileParser.read()`, which fetches robots.txt via bare `urllib` using
the default `Python-urllib/x.x` user-agent — not the crawler's own
identifying `HEADERS`. tokyofashion.com is behind Cloudflare, which returned
`403 Forbidden` to that default UA specifically (confirmed: `curl`/`requests`
with the crawler's own UA got a normal `200` with `User-agent: *\nAllow: /`).
Python's `RobotFileParser` treats a 401/403 on robots.txt as "disallow
everything," so the whole domain was wrongly blocked — not because the site
actually disallows crawling.

**Fix applied**: `get_robots_parser()` now fetches robots.txt with `requests`
using the same `HEADERS` as every other request, and feeds the text into
`parser.parse()` instead of `parser.read()`. Falls back to the same
401/403-disallow / other-error-allow semantics `RobotFileParser` used before.
This is a general robustness fix (any Cloudflare-protected source could hit
the same false block), not specific to tokyofashion.com.

Re-ran the crawler after the fix: tokyofashion.com now returns real headlines
(root page + article/photo/brand/music sections, 2-12 headlines per page).

## Outcome

All 4 new sources are genuinely crawlable and extracting real headlines. No
source needed removal. `python -m py_compile src/*.py` passes. Scratch
`trends_raw.json` crawl output deleted after verification.
