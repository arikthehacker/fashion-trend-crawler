# Source diversity research — run 73

## Context

Read `src/crawler.py`'s `FASHION_SOURCES` (runs 17-55 history) and
`src/taxonomy.py`'s `DOMAIN_SECTOR_MAP`. Confirmed gaps going in:

- South America: 0 sources. `vogue.mx` (run 19) is Mexico -- North America,
  not South America. No other Latin American source in the list is South
  American either (tribune.com.pk is Pakistan/South Asia, savoirflair.com
  is Pakistan/Middle East-adjacent, dewimagazine.com is Indonesia).
- Middle East beyond scmp.com: scmp.com (run 39) is Hong Kong -- East Asia,
  mislabeled as Middle East coverage in the task brief; still an open gap.
- Institutional sector beyond CFDA/FHCM/BFC/Met/V&A/FIT/KCI: candidates
  investigated but not confirmed as genuinely fetchable governing bodies.

Focused this run on **South America**, the cleanest 0-source gap.

## Candidates investigated

### 1. São Paulo Fashion Week governing body (institutional angle)
WebSearch turned up SPFW itself (a trade show, Wikipedia-documented) but no
clear standalone governing-body website analogous to cfda.com/fhcm.paris --
SPFW appears to be organized by IMG/other event-management entities rather
than a discrete national council with its own institutional domain. Not
pursued further as a verified candidate this run.

### 2. FFW (ffw.com.br) -- SELECTED
WebSearch: FFW describes itself as Brazil's leading independent fashion and
culture media outlet, running since 2009, ~500k monthly readers, based in
São Paulo. Independent digital editorial platform (site, Instagram,
podcast), not a retailer, not a PR wire, no obvious affiliate/sponsored-
content-mill pattern in search results.

Verification steps:
- `robots.txt` (fetched via WebFetch): only `Disallow: /wp-admin/`,
  `Allow: /wp-admin/admin-ajax.php`, sitemap listed. Fully permissive for
  the actual content paths.
- WebFetch on `https://ffw.com.br/` directly returned an HTTP 403 (likely a
  bot-detection layer keyed to WebFetch's own fetch signature/UA).
- Re-tested with `curl` using this project's actual `User-Agent` string
  (`fashion-trend-crawler/1.0 (educational project)`, matching
  `src/crawler.py`'s `HEADERS`) against both `https://ffw.com.br/` and
  `https://ffw.com.br/materias/`: both returned **HTTP 200**.
- Inspected the raw HTML (no JS execution): root page contains real
  static `<a href="https://ffw.com.br/category/moda/">` (moda = fashion)
  and other category links; `/materias/` contains real `<h1>`/`<h2>`
  article headline text directly in the markup (e.g. "Quem é Cece Hamali,
  a designer por trás das camisas de látex virais da Copa"). No
  JS-rendering required -- same pattern as the other approved static-HTML
  sources in this list.
- Confirmed `ffw.com.br` is not already present in `FASHION_SOURCES` or
  `DOMAIN_SECTOR_MAP` before adding.

Conclusion: clears the bar (independently fetchable with our own UA,
permissive robots.txt, static-HTML headlines, independent editorial voice,
genuine new geography). Added to both files.

## Decision

Added `https://ffw.com.br` to `FASHION_SOURCES` in `src/crawler.py`, and
`"ffw.com.br": "editorial"` to `DOMAIN_SECTOR_MAP` in `src/taxonomy.py`.
This is the first South American source in the project. Middle East (true
regional coverage, not East Asia mislabeled) and a second genuine
institutional-sector source remain open gaps for a future run.

Validated with `python -m py_compile src/*.py` -- passes.

Not committed per instructions (research/verification run only).
