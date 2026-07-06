# Source diversity expansion (run 17)

Follow-up to bias-audit run 16 finding (a): all three original `FASHION_SOURCES`
(vogue.com, whowhatwear.com, hypebeast.com) are English-language Western
editorial/retail outlets, and BFS crawling from those seeds can't self-correct
for that. Only `src/crawler.py` and `src/taxonomy.py` touched.

## Sources added

- **nataal.com** — global media brand (founded 2015, editorial staff formerly
  of AnOther/Arise) dedicated to contemporary African fashion, arts, and
  culture. English-language, public, no paywall.
- **okayafrica.com** — established English-language African culture/fashion
  outlet, part of the Okayplayer network; regularly covers African designers
  and fashion weeks (Lagos included).
- **fashionunited.in** — Indian edition of FashionUnited, an international B2B
  fashion trade-news network; covers Indian fashion industry/retail news in
  English, public and crawlable.
- **tokyofashion.com** — long-running, independent English-language site
  covering Japanese street fashion (Harajuku/Tokyo), still actively publishing
  in 2026 with a large following; not affiliated with a Western publisher.

All four were verified via web search as real, currently active, and publicly
accessible (no hard paywall/login gate) before being added — no domains were
invented.

## Changes

- `src/crawler.py`: appended the four URLs to `FASHION_SOURCES` with a comment
  linking back to this log and the bias-audit finding.
- `src/taxonomy.py`: added the four domains to `DOMAIN_SECTOR_MAP` under
  `editorial` (each outlet is fundamentally an editorial/publisher voice, same
  category as vogue.com/hypebeast.com, not designer-owned, retail-commerce, or
  reader-generated criticism). Verified `classify_source()` resolves all four
  to `"editorial"` and `python -m py_compile src/*.py` passes clean.

## What this does not fix

This only adds four seeds — it does not guarantee balanced geographic
coverage per crawl, since BFS still depends on what each seed happens to link
to that week, and three of the four outlets (nataal, okayafrica, fashionunited
India) are still English-language and editorially adjacent to Western media
conventions (nataal/okayafrica in particular are diaspora- and
Western-audience-facing rather than locally-published-for-local-readers).
Non-English-language sources and locally-published (non-diaspora) outlets
remain unaddressed and should be considered in a future pass if the pipeline
ever supports non-English extraction.
