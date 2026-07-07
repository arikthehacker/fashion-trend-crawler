# Middle East source research — run 75

## Context

Run 73/74 flagged that `scmp.com` (added run 39) is Hong Kong -- East Asia, not
Middle East -- so the "Middle East beyond scmp.com" gap noted since run 39 is
still genuinely open. This run researches real Middle East-based/focused
fashion sources to fill it, re-checking `thenationalnews.com` (rejected run
41 for client-side rendering) along the way.

All verification below re-fetched pages directly with this project's own
`User-Agent` (`fashion-trend-crawler/1.0 (educational project)`, matching
`src/crawler.py`'s `HEADERS`) via `curl`, rather than trusting a
WebFetch-tool summary at face value -- WebFetch's own fetch initially
reported Arab News' Cloudflare challenge page as "not a Cloudflare challenge
page" with fabricated headline text, which a direct `curl` with the
project's real UA disproved immediately (see Arab News section below). Any
future run doing this kind of verification should treat WebFetch content
summaries as a lead to double-check with a raw HTTP fetch, not as ground
truth.

## Candidates checked

### 1. Arab News lifestyle section (arabnews.com) -- REJECTED

`curl -A "fashion-trend-crawler/1.0 (educational project)"` against both
`https://www.arabnews.com/robots.txt` and `https://www.arabnews.com/lifestyle`
returned **HTTP 403** with an active Cloudflare "Just a moment..." JS
challenge page (`cf_chl_opt`, `challenges.cloudflare.com` CSP, `noindex,
nofollow` robots meta tag) -- not real content, and not fetchable by a
static-HTML crawler without executing Cloudflare's JS challenge. (A first
pass via the WebFetch tool had reported this page as legitimate lifestyle
content with real headlines and "not a Cloudflare challenge page" -- that
read was wrong; the raw HTTP response with this project's actual UA is
unambiguous.) Rejected: same Cloudflare-block pattern that has knocked out
other candidates project-wide (e.g. tokyofashion.com's robots.txt in run 17,
vogue.ph in run 20).

### 2. The National (thenationalnews.com) -- RE-CHECKED, STILL REJECTED

Re-verified per the task brief's instruction to just confirm whether run
41's rejection still holds. `robots.txt` fetched cleanly (HTTP 200,
permissive for general content paths, only blocks specific sections like
`/article/`, `/blogs/`, `/search`, image resizer paths). But
`https://www.thenationalnews.com/lifestyle/fashion/` 301-redirects to
`https://www.thenationalnews.com/lifestyle/fashion-beauty/`; fetching that
final URL directly with the project UA returned HTTP 200 and an 841KB page,
but grepping for `<h1>`/`<h2>`/`<h3>` tags with >20 characters of text (the
same extraction logic `crawl()` uses) found **zero real article headlines**
-- only UI/icon element titles ("Menu Search", "Chevron", "Previous slide",
etc.), confirming the page's actual article content is still client-side
rendered and doesn't appear in the raw HTML. Run 41's rejection stands
unchanged. Not re-added.

### 3. Vogue Arabia (voguearabia.com) -- SELECTED

WebSearch to find the real domain: the commonly-guessed `vogue.me` /
`en.vogue.me` both 301-redirect to the canonical domain,
`https://www.voguearabia.com`. Background (WebSearch, multiple sources
including Wikipedia, Arab News, Semafor): Vogue Arabia launched 2016 as a
digital-first, then print, Vogue edition licensed for the Middle East,
originally published by Dubai-based Nervora; taken over directly by Condé
Nast in January 2025. Based in the UAE, covers Arab pop culture, fashion,
and celebrity style for a Middle East audience -- a genuine regional
edition, not a Western outlet's occasional Middle East coverage, and not a
PR/sponsored-content mill.

Verification steps:
- `robots.txt` (`curl` with project UA, HTTP 200): only disallows query-
  string variants (`/*?`, with `/*page`/`/*rss?`/`/*?id=` explicitly
  re-allowed), `/auth/`, `/account/`, `/user/`, `/preview/`, `/search`,
  `/product/`, `/cdn-cgi/`. Root and article content paths are fully
  permissive.
- Homepage fetch (`curl` with project UA) returned **HTTP 200**, served via
  `Server: CloudFront` (confirmed via response headers) -- not Cloudflare,
  no JS challenge.
- Inspected raw HTML (no JS execution): real static `<h2>`/`<h3>` article
  headline text directly in the markup, e.g. "Elyanna is Redefining Global
  Arab Pop -- Here's How She Got There", "The Most Dazzling Shows from Paris
  Couture Week Autumn/Winter 2027 Day 1", "Why Distressed Luxury Fashion Is
  Defining the Biggest Trend of 2026" -- same static-HTML pattern as the
  other approved sources in this list, no JS rendering required.
- Confirmed `voguearabia.com` was not already present in `FASHION_SOURCES`
  or `DOMAIN_SECTOR_MAP` before adding.

Conclusion: clears the bar -- independently fetchable with our own UA,
permissive robots.txt, static-HTML headline content, genuine Middle
East-based/focused regional edition (same pattern as `vogue.mx`, run 19),
not PR/sponsored. Added to both files.

### 4. Arab Fashion Council (arabfashioncouncil.com) -- not pursued further

`robots.txt` (HTTP 200) is fully permissive (`Disallow: /wp-admin/` only).
Homepage fetch (HTTP 200) does contain real static `<h2>` heading markup
(e.g. "FASHION FUND APPLICATION"), so it likely would have been fetchable.
Not investigated further for institutional-body legitimacy (vs.
event/PR-org, the same distinction that sank SPFW in run 74) once a clean
Vogue Arabia pass was already in hand and the task brief only required one
qualifying candidate. Left as an open candidate for a future institutional-
sector-focused run, not added this run.

### 5. Dubai Design District / d3 -- not pursued

Not investigated this run; task brief listed it as a candidate but time was
spent verifying the four candidates above once a clear pass (Vogue Arabia)
was found. Open for a future run if more Middle East diversity is wanted.

## Decision

Added `https://www.voguearabia.com` to `FASHION_SOURCES` in
`src/crawler.py`, and `"voguearabia.com": "editorial"` to
`DOMAIN_SECTOR_MAP` in `src/taxonomy.py`. This is the first genuine Middle
East source in the project (scmp.com, run 39, is Hong Kong/East Asia, not
Middle East, as flagged run 73). Arab News rejected (active Cloudflare JS
challenge). The National re-confirmed rejected (still 0 real headlines via
static-HTML scraping). Arab Fashion Council and Dubai Design District/d3
remain open, unverified candidates for a future run.

Validated with `python -m py_compile src/*.py` -- passes.

Not committed per instructions (research/verification run only).
