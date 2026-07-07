# Independent-criticism source investigation (run 54)

## Question
Why has the run-19 confidence-gate fix (`independent_criticism` added to
`HIGH_RELIABILITY_SECTORS`) stayed untested for 30+ runs — is the sector
structurally unreachable, or has it just not come up in report-writing?

## Finding: (a) — structurally unreachable, now fixed

`taxonomy.py`'s `DOMAIN_SECTOR_MAP` has classified four domains as
`independent_criticism` since run 12: `substack.com`, `blackbirdspyplane.com`,
`dieworkwear.com`, `throwingfits.com`. But **none of these were ever present
in `crawler.py`'s `FASHION_SOURCES`** seed list — every seed is editorial
(vogue.com, hypebeast.com, tokyofashion.com, etc.), retail, or diaspora
editorial. Worse, `crawl()`'s `is_same_domain()` check means the BFS never
leaves a seed's own domain, so even if a seed page linked out to
dieworkwear.com, the crawler would not follow it. Combined, the sector had
zero possible path into `trends_raw.json`, regardless of what
`summarize.py`'s report-writing/WebSearch step did afterward. The run-19 fix
itself (adding `independent_criticism` to `HIGH_RELIABILITY_SECTORS`) is
correctly implemented — it simply had no input to ever act on.

## Fix applied
Added `https://dieworkwear.com` to `FASHION_SOURCES` in `src/crawler.py`.
Verified via WebFetch (not just existence check):
- Loads as a real static-HTML blog with genuine article headlines (no JS
  rendering needed), independently run (not a major-outlet property, not
  PR/brand-adjacent — long-running menswear/workwear criticism blog).
- `robots.txt` is fully permissive (`Disallow:` empty).

Rejected candidate: `throwingfits.com` — 302-redirects to a Patreon login
gate (`patreon.com/login-sync-domains?...`), not independently fetchable as
static HTML. Left out of `FASHION_SOURCES`; its `DOMAIN_SECTOR_MAP` entry can
stay as-is in case it becomes directly reachable later, but it should not be
added as a seed until it is.

`substack.com` and `blackbirdspyplane.com` were not evaluated for seeding
this run (scope: identify 1-2 sources) — `substack.com` in particular isn't a
single site so would need a specific author's subdomain, not the bare
domain.

## Verification
`python -m py_compile src/*.py` passes.

## Recommendation
`TODO.md`'s carried-forward note can now be updated: the sector is reachable
going forward from the next crawl run. The run-19 gate fix remains
*logically* correct/untested-in-isolation until an actual crawl run picks up
a dieworkwear.com headline and it flows through `summarize.py`'s confidence
derivation — that's a runtime observation for the next pipeline run, not
something resolvable by static analysis alone.
