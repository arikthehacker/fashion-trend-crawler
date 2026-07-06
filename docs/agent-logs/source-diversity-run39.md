# Source diversity follow-up (run 39)

Checked `FASHION_SOURCES` (currently 9 entries after runs 17/19/20: vogue.com,
whowhatwear, hypebeast, nataal, okayafrica, fashionunited.in, tokyofashion,
vogue.mx, tribune.com.pk, savoirflair, dewimagazine) for remaining geographic
gaps. East Asia (beyond Japan) and the Middle East (beyond Pakistan) were
still uncovered.

## Verified via WebFetch (2026-07-06)

- **scmp.com/lifestyle/fashion-beauty** (South China Morning Post, Hong
  Kong) — loads real headlines (e.g. "History of Chinese-style 'frog
  buttons', seen on viral Adidas jacket"), no Cloudflare challenge. Added.
- **thenationalnews.com/lifestyle/fashion** (The National, UAE) — loads real
  headlines (e.g. "Chanel puts heritage on the runway by buying world's
  oldest shirtmaker, Charvet"), no Cloudflare challenge. Added.
- **fashionnetwork.com/news/africa** — returned HTTP 403 Forbidden on
  WebFetch. Rejected, not added.

## Honesty caveat

Both additions are English-language (like okayafrica/nataal before them) —
this is geographic, not linguistic, diversification. I did not verify
robots.txt-level crawlability with the project's actual `requests`+headers
combo (only WebFetch's own fetch), so `run.sh`/`crawler.py`'s
`get_robots_parser()` should be watched on the next real crawl in case either
host blocks the project's identifying User-Agent specifically (this has
happened before, e.g. tokyofashion.com in run 17).

## Changes

- `src/crawler.py`: added both URLs to `FASHION_SOURCES`.
- `src/taxonomy.py`: added `scmp.com` and `thenationalnews.com` to
  `DOMAIN_SECTOR_MAP` as `"editorial"`.
- Verified: `python -m py_compile src/*.py` passes.

Not committed per task instructions.
