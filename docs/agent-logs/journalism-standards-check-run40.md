# Journalism standards check — run 40: correction-notice placement

**Topic researched:** correction-notice placement standards in professional newsrooms
(AP/NYT/Reuters/Trusting News/ONA Ethics), not previously covered by prior runs (checked
`docs/agent-logs/` — AI-journalism-standards, forecast-calibration, IPTC-metadata,
archival-permanence, bias-audit, retention-versioning, ICD-203, Costume-Core/Getty-AAT are
all done; correction placement was not).

## What the standard says

- Corrections should be labeled plainly and given "prominence... roughly equal to" the
  original content's throw weight (Trusting News, ONA Ethics).
- In digital publishing, the convention is an editor's note **pinned near the top** of the
  original piece (not just archived in a bottom section or a separate corrections page),
  so a reader encountering the piece sees the correction before reading the (partly
  outdated) body.
- Most outlets do NOT maintain a standalone corrections page (NYT/Slate/Tribune are the
  exception); in-place top-of-article notice is the more common pattern.

## Gap found on the site

`web/app/reports/[date]/page.tsx` already had a full "Correction History" section
(`revision_history`) and correct IPTC `dateModified` handling in JSON-LD — both solid.
But the correction section sat near the bottom of the page (after taxonomy/glossary
sections), with **no signal near the top** that a report had ever been corrected. A
reader who didn't scroll the whole report would never know.

## Fix applied

- Added `id="correction-history"` anchor to the existing section.
- Added a small pinned notice directly under the report `<header>`, rendered only when
  `report.revision_history` has entries, showing the most recent correction's date/reason
  with a jump link to the full history. Matches "equal prominence, near the top" without
  restyling anything else or adding new schema fields — purely a rendering-order fix
  (same pattern class as prior "populated but never surfaced" bugs noted in the skill's
  workflow-convention #9).

## Verification

`cd web && npx tsc --noEmit` — passes, no errors.

Files touched: `web/app/reports/[date]/page.tsx`.
