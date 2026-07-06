# Dominant mood staleness cutoff — run 44

Follow-up to run 43's flagged (non-urgent) observation: `dominantMood` was
being carried forward indefinitely from a stale source report (~24 weeks old
at the time), disclosed via `dominantMoodSourceDate` but arguably meaningless
at that distance.

## Change

`web/lib/reports.ts` — `getThisWeeksIndex()`:

- Added `MOOD_STALENESS_CUTOFF_DAYS = 84` (12 weeks), matching run 43's
  suggested max-lookback and the site's existing "thin week" honesty
  conventions (disclose gaps rather than hide or fake freshness).
- When walking backward to find the most recent report with an
  `aesthetic_terms` entry, if the candidate is a carry-forward (not the
  latest report) and more than 84 days older than the latest report's date,
  the walk stops and sets a new field `dominantMoodTooStale: true` instead of
  returning the old term. The carry-forward mechanism itself is unchanged for
  gaps within the cutoff (still returns the term + `dominantMoodSourceDate`).
- Added `dominantMoodTooStale?: boolean` to the `ThisWeeksIndex` interface,
  documented inline.

`web/app/page.tsx` — homepage "This Week's Index" module:

- "Dominant mood" row now falls through three states: real mood this week ->
  carried-forward mood with disclosed source date (unchanged, within cutoff)
  -> **new: "No distinct mood signal in recent weeks"** when
  `dominantMoodTooStale` is true -> "None logged this window" (no term
  anywhere in the walked history at all, distinct from "found one but it's
  too old").

## Verification

- `npx tsc --noEmit` — clean.
- `npx eslint .` — clean.
- `npx next build` — succeeds, all 99 static pages generated.
- Manually inspected `.next/server/app/index.html`: the "Dominant mood" field
  now renders "No distinct mood signal in recent weeks" for current data
  (real source was ~24 weeks stale, past the 84-day/12-week cutoff), replacing
  the old "succession narrative (Zankov at DVF) (carried from 2026-09-14; ...)"
  text. No other homepage metrics changed.

No changes to report data or other modules. Not committed per instructions.
