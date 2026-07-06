# SPFW institutional-sector gap — second look (run 74)

## Context

Run 73 left the institutional-sector gap open, noting SPFW "appears
event-management-run, not a standalone governing-body site" but didn't push
further. This run re-checks SPFW directly and looks for an alternative
Latin American institutional candidate, without re-doing run 73's broader
South America sourcing pass.

## SPFW re-check

WebSearch confirmed the current domain is `spfw.com.br` (the earlier
`spfw.com` guess doesn't hold). WebSearch and WebFetch on `https://spfw.com.br/`
both confirm run 73's read:

- Realization/organizing credited to IMM, INMODE, and F2 (event-production
  entities), with institutional *support* (not governance) from São Paulo
  city hall and Lei Rouanet cultural sponsorship -- support/sponsorship is
  not the same as being a governing body.
- WebFetch classified the homepage itself as "event management and PR" --
  editorial-style designer/collection writeups plus Eventim ticket sales,
  not a council/federation publishing on its own institutional authority
  the way cfda.com or fhcm.paris do.

Conclusion: SPFW re-confirmed as NOT institutional. Run 73's call stands
after a second, closer look. Not added.

## Alternative candidate search

Searched for a Latin American national fashion council/chamber more
clearly analogous to CFDA/FHCM. Candidates surfaced and rejected:

- **Bogota Fashion Week (BFW)** -- explicitly a commercial/promotional
  platform of the Bogota Chamber of Commerce, not itself a standalone
  fashion governing body. Not pursued.
- **Colombia Fashion Summit** -- an event/summit brand, not a governing
  institution.

**Inexmoda (inexmoda.org.co) -- SELECTED.** Instituto para la Exportacion y
la Moda, a private nonprofit institute founded 1987 to grow Colombia's
textile/fashion export sector. Runs Colombiatex and Colombiamoda trade
fairs, but distinct from SPFW in that its core identity and site content
are institutional/research-driven: industry trend reports, market research,
training, and internationalization support for the "Sistema Moda" --
functionally closer to a national fashion institute than an event-PR shop.

### Verification steps

- WebSearch: multiple independent Colombian press sources (El Tiempo, El
  Espectador, Portafolio) describe Inexmoda as a long-running nonprofit
  foundation/institute, not a PR firm or event promoter.
- `robots.txt` (WebFetch): explicitly allows AI crawlers (ClaudeBot, GPTBot)
  and search engines; only disallows `/wp-admin/`, `/xmlrpc.php`, trackbacks,
  readme files -- fully permissive for real content paths. Sitemap listed.
- WebFetch on `https://inexmoda.org.co/` directly returned HTTP 403 (same
  bot-detection pattern seen with ffw.com.br in run 73).
- Re-tested with `curl` using this project's actual `User-Agent`
  (`fashion-trend-crawler/1.0 (educational project)`, matching
  `src/crawler.py`'s `HEADERS`): returned **HTTP 200**.
- Inspected raw HTML (no JS execution): real static `<h1>`/`<h2>` markup
  directly in the page, e.g. `<h1>INFORME DE TENDENCIAS` (trend report),
  `<h2>PROYECCIONES PARA LA INDUSTRIA DE LA MODA!` (industry projections),
  plus Colombiamoda/Colombiatex "knowledge pavilion" section headings.
  WordPress/Elementor-built but static-rendered, same pattern as other
  approved sources in this list.
- Confirmed `inexmoda.org.co` was not already present in `FASHION_SOURCES`
  or `DOMAIN_SECTOR_MAP` before adding.

Conclusion: clears the bar -- independently fetchable with our own UA,
permissive robots.txt, static-HTML headline/report content, genuine
institutional (not PR/event) identity. Added to both files.

## Decision

- SPFW: re-confirmed NOT institutional. Gap-closing attempt via SPFW itself
  remains closed out as a non-match; not added.
- Added `https://inexmoda.org.co` to `FASHION_SOURCES` in `src/crawler.py`,
  and `"inexmoda.org.co": "institutional"` to `DOMAIN_SECTOR_MAP` in
  `src/taxonomy.py`. This is the second genuine institutional-sector source
  beyond cfda.com/fhcm.paris/britishfashioncouncil.co.uk/fitnyc.edu/
  metmuseum.org/vam.ac.uk/kci.or.jp, and the first South American
  institutional source.

Validated with `python -m py_compile src/*.py` -- passes.

Not committed per instructions (research/verification run only).
