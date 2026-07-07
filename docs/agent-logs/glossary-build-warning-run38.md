# Glossary build warning (run 38)

Follow-up to run 37, which flagged that terms without a curated `DEFINITIONS`
entry are silently dropped from `/glossary`, and that TODO.md wanted a
build-time warning instead of a periodic manual check.

## Change

`web/app/glossary/page.tsx` — in `loadGlossaryTerms()`, the per-term loop now
branches: if `DEFINITIONS[key]` exists, behavior is unchanged (dedupe into
`found`); if not, it calls `console.warn()` with the cleaned term name and
source file, then continues. No throw, no build failure — matches the
non-blocking spirit of `audit_confidence.py` / `check_field_coverage.py`.

## Verification

Ran `npx next build` in `web/`. The warning fired for real, currently
undefined terms already present in the archive — mostly long, narrative-style
`top_signals[].name` entries from recent report windows (CFDA Fashion Awards
tracking notes, Golden Globes date entries, Wales Bonner/Hermès transition
notes, etc.), e.g.:

```
[glossary] no DEFINITIONS entry for term "Grace Wales Bonner succeeding
Veronique Nichanian at Hermes menswear after her 37-year tenure"
(from 2027-01-18.json) — term will not be shown on /glossary
```

This confirms the code path is genuinely reachable — no scratch term was
needed. The build completed successfully (exit 0, all 91 static pages
generated), confirming the warning does not block the build.

`npx tsc --noEmit` produced no output/errors.

## Note

These specific unwarned terms look like long forecast/signal narrative
strings rather than short aesthetic terms meant for the glossary (they read
more like `top_signals` headlines). That's a candidate for a future
normalization/filtering pass, but out of scope here — this task only adds
the warning mechanism per the instructions (`web/app/glossary/page.tsx` was
the only file touched).
