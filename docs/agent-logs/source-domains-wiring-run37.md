# Source domains wiring (run 37)

Closes the two gaps run 36 explicitly left open for `Signal.source_domains`
(added schema/data-layer only, deliberately unpopulated and unrendered).

## Changes

1. `src/summarize.py` `build_prompt()`: added an instruction telling the
   model to populate `source_domains` with bare homepage domain(s) per
   signal, reusing the exact domain-extraction convention already used for
   the `[domain | source_sector]` headline tags (`page["url"].split("/")[2]
   .replace("www.", "")`) rather than inventing a new definition. Restated
   "never a full article URL or path" inline, on top of `validate_report()`'s
   existing schema-level rejection (run 36) of `/`- or `http(s):`-containing
   entries — belt and suspenders. Added a `"source_domains": ["vogue.com",
   "whowhatwear.com"]` example line next to the existing `source_sectors`
   example in the prompt's JSON structure.

2. `web/app/reports/[date]/page.tsx`: added a `Sources: {domain, domain}`
   `<span>` to the existing per-signal metadata row (alongside Sectors/
   Corroborated by), rendered only when `signal.source_domains` is
   non-empty. Additive one-line change to an existing paragraph/row — no
   new heading needed (doc-workflow-item-3's heading-semantics concern
   doesn't apply; nothing new to mis-style as a heading).

3. `docs/PROMPT_CHANGELOG.md`: appended a dated "Run 37" entry documenting
   the exact instruction text added, rationale, and what remains
   out of scope.

## Explicitly not done

- No backfill of `source_domains` into existing archived `data/reports/*.json`
  files — only reports generated after this change will have it populated.
  Existing reports remain valid (field is optional/backward-compatible per
  run 36's schema work).
- No archival/Wayback/Perma.cc follow-up — still a separate, lower-priority
  future task per run 35/36.

## Verification

- `python -m py_compile src/*.py` — passed.
- `cd web && npx tsc --noEmit` — passed, no errors.
- `cd web && npx next build` — succeeded, all 88 pages generated
  (including all `/reports/[date]` and `/signals/[slug]` static paths).

## Files touched

- `C:\Users\User\Desktop\fashion-trend-crawler\src\summarize.py`
- `C:\Users\User\Desktop\fashion-trend-crawler\web\app\reports\[date]\page.tsx`
- `C:\Users\User\Desktop\fashion-trend-crawler\docs\PROMPT_CHANGELOG.md`
