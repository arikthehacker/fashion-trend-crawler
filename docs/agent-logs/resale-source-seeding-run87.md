# Resale source seeding verification — run 87

## Context

Run 86's periodic audit flagged a structural gap: precedent 13
(`docs/confidence-discipline-precedents.md`) formalized resale-platform sourcing
discipline, and `src/taxonomy.py`'s `DOMAIN_SECTOR_MAP` already classifies
`therealreal.com`, `vestiairecollective.com`, `depop.com`, `grailed.com`, and
`poshmark.com` as `"resale"` sector — but none of these five domains are seeded in
`src/crawler.py`'s `FASHION_SOURCES`. Same bug class as the pre-run-54 dieworkwear.com
gap: a sector theoretically supported by the taxonomy but structurally unreachable by
the crawler.

This run independently verified all 5 domains against the run 73/74/75 bar:
independently fetchable without JS-rendering/Cloudflare blocks, not PR-adjacent, and
carrying genuinely extractable static-HTML headline content (not just raw product
listings) that this crawler's BeautifulSoup h1/h2/h3 extraction could find.

All fetches used `curl` with this project's actual crawler UA
(`fashion-trend-crawler/1.0 (educational project)`), matching `src/crawler.py`'s
`HEADERS`, to avoid false negatives from WebFetch's own UA/bot-detection signature
(same lesson as run 73's ffw.com.br verification).

## Results

### 1. therealreal.com — FAIL

- `https://therealreal.com/robots.txt` redirects (301) to
  `https://www.therealreal.com/robots.txt`, which returns 200 with a permissive
  robots.txt (only cart/checkout/admin/user-account paths disallowed; category/product
  browsing paths allowed).
- However, `https://www.therealreal.com/` (homepage) returns only **5,703 bytes** of
  HTML — a near-empty shell (`<body>` with no meaningful static markup after it,
  zero `<h1>`-`<h3>` tags found via direct grep on the raw response).
- Conclusion: robots.txt is permissive, but the site is a JS-rendered SPA — the actual
  page content (including any headline-style text) is injected client-side and is
  invisible to a static-HTML fetch. Fails the extraction-method bar.

### 2. vestiairecollective.com — FAIL

- `https://vestiairecollective.com/robots.txt` redirects (301) to
  `https://www.vestiairecollective.com/robots.txt`.
- That request itself returns **HTTP 403** with a Cloudflare "Just a moment..."
  managed JS challenge page (`Cf-Mitigated: challenge`, `cf_chl_opt` challenge script),
  not the actual robots.txt content.
- Conclusion: blocked at the network layer before any content — even robots.txt
  itself — can be read. Fails outright; no path to static crawlability.

### 3. depop.com — FAIL

- `https://depop.com/robots.txt` redirects (301) to `https://www.depop.com/robots.txt`.
- That request also returns a Cloudflare "Just a moment - Depop" JS-challenge page
  instead of robots.txt content (same `Cf-Mitigated: challenge` pattern as Vestiaire).
- Conclusion: identical failure mode to Vestiaire Collective — Cloudflare-gated before
  robots.txt is even readable.

### 4. grailed.com — FAIL

- `https://grailed.com/robots.txt` redirects (301) to
  `https://www.grailed.com/robots.txt`, which returns **200** with a permissive,
  hand-written robots.txt (disallows checkout/messages/search/user-account paths;
  allows listing/category browsing; publishes a sitemap). This is the one domain of
  the 5 where robots.txt itself is genuinely readable.
- Homepage (`https://www.grailed.com/`, 394,477 bytes fetched) contains **zero**
  `<h1>`-`<h6>` tags anywhere in the raw response — confirmed via direct grep. The
  only structural markup is Next.js layout/nav divs (`id="__next"`,
  `Layout_pageLayout__...`, `SiteHeader_...`); actual content is injected client-side.
- To rule out "homepage is just nav, editorial section might differ": checked
  Grailed's own editorial/blog vertical, `/drycleanonly` (named in the site's own
  robots.txt disallow rules, confirming it's a real section). That page (237,471
  bytes) does contain `<h2>`/`<h3>` tags, but their raw markup is
  `<h2 class='follow-us'>` and `<h3 class='-title'>` — empty CSS-class shells with no
  text content in the static HTML; article titles are populated client-side by JS,
  same as the homepage.
- Conclusion: robots.txt passes, but the extraction-method bar fails even on
  Grailed's dedicated editorial content — genuinely a JS-rendered SPA end to end, not
  just for product listings.

### 5. poshmark.com — FAIL

- `https://poshmark.com/robots.txt` returns 200 directly (no redirect needed) with a
  permissive-looking robots.txt (disallows listing-interaction/account-action
  endpoints; does not blanket-disallow browsing paths).
- Homepage (`https://poshmark.com/`, 1,242,260 bytes) does contain one `<h1>` tag,
  but it is `<h1 class="guest-feed-seo-header">` with **no text content** — an empty
  SEO-placeholder element styled via CSS, not a real headline. Zero `<h2>`/`<h3>` tags
  exist anywhere in the response.
- Conclusion: robots.txt is permissive and the response isn't Cloudflare-blocked, but
  there is no extractable headline-style content in the static HTML — this is a
  client-rendered infinite-scroll product feed, not editorial/trend content this
  crawler's method could use.

## Decision

**None of the 5 resale domains pass verification.** All five are consistent with the
task brief's stated real possibility: resale marketplaces are heavily JS-rendered SPAs
and none currently expose static-HTML headline content this crawler's
BeautifulSoup-based extraction can read, even where robots.txt is permissive
(grailed.com, poshmark.com, therealreal.com) or the underlying editorial section
exists (grailed.com's `/drycleanonly`). Two of the five (vestiairecollective.com,
depop.com) are additionally blocked outright by Cloudflare JS challenges before
robots.txt can even be read.

**No changes made to `src/crawler.py` or `src/taxonomy.py`.** The taxonomy's
`"resale"` sector classifications for these 5 domains remain correct (a resale
platform's URL should still classify as `"resale"` if a report ever cites one via
`summarize.py`'s WebSearch step) — the sector is real, but genuinely unreachable by
this crawler's direct-crawl method today, which is an honest structural outcome, not a
gap to force-close. This differs from the pre-run-54 dieworkwear.com case, where the
domain was a normal fetchable editorial blog that had simply been missed; here the
domains were investigated and found to be actually incompatible with the crawl
method.

Validated `python -m py_compile src/*.py` — passes (no source changes; run to confirm
baseline is still clean).

Not committed per instructions (research/verification run only).
