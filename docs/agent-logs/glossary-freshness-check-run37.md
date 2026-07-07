# Glossary freshness check (run 37)

Verified `web/app/glossary/page.tsx` against the grown archive (13 reports at
build time in run 20, now 29 in `data/reports/`).

## Findings

The build-time extraction still works correctly: `loadGlossaryTerms()` reads
every report file fresh on each build, so it already reflects all 29 reports
with no stale caching. The design (only render terms that exist in *both* the
archive *and* the curated `DEFINITIONS` dict) is sound and correctly excludes
event/schedule/entity noise (CFDA schedules, NYFW dates, Golden Globes, Black
Friday, etc.) that dominates reports from run ~30 onward — that noise is
working as intended, not a bug.

However, one genuine new aesthetic term from a newer report had no curated
definition and was therefore silently dropped rather than shown with any
placeholder: **"funmaxxing"** (`data/reports/2026-11-09.json`, a TikTok-sourced
maximalist-play aesthetic — icy blue/candy pink, 80s sportswear, tassels).
Its raw string in `top_signals[].name` (`"funmaxxing" maximalist-play
aesthetic (icy blue/candy pink, 80s sportswear, tassels)`) didn't match any
existing `normalize()` pattern or dictionary key, so it never appeared on the
page at all — no fallback, just absence. Spot-checked several other run-30+
reports (NYFW/LFW/MFW schedules, CFDA Fashion Fund/Awards silence tracking,
Golden Globes) and found no other new genuine aesthetic/styling terms; those
reports are dominated by institutional/factual tracking signals, correctly
excluded by design.

## Fix applied

- Added a `normalize()` rule collapsing the full `"funmaxxing" maximalist-play
  aesthetic (...)` string down to the dictionary key `funmaxxing`.
- Added a `funmaxxing` entry to `DEFINITIONS` with a real wire-service-voice
  definition sourced from the report's own evidence field.

## Verification

`cd web && npx tsc --noEmit && npx next build` — both clean, `○ /glossary`
present in the static route list. Not committed per instructions.
