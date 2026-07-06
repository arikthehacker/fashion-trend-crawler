# README + case study refresh

Scope: `README.md` and `web/app/case-study/page.tsx` only.

Read both files plus `docs/CHANGELOG.md` in full (runs 1-9). Found both docs had
fallen behind actual shipped work: README's roadmap still listed schema/archive/
methodology/timeline/manual-sampling as unchecked `[ ]` items though all are built;
MCP tools table was missing `list_reports`/`get_report`; no mention anywhere of CI
validation, `derive_confidence()`, `revision_history`, transparency disclosures, or
accessibility/SEO work. Case-study "Scope" line (fixed for voice in run 1) hadn't been
touched since despite 8 subsequent runs of real feature work.

**README.md**: added sections for Archive & Reporting Surfaces (`/timeline`,
`/signals/[slug]`, JSON-LD, citation line, WCAG headings), Transparency &
Editorial Disclosures, and Manual/Compliant Social Sampling. Checked off completed
roadmap items, added open ones (live crawl not yet merged, migration step 5, scheduled
crawls). Rewrote Limitations to be specific and current: confirmed only 4 dated reports
exist (`data/reports/*.json`), none from a merged live crawl — the one successful live
crawler+summarize run collided with an existing date and was deliberately not merged
(saved at `docs/agent-logs/live-crawl-2026-07-06-real-output.json`). Rewrote Project
Structure tree to match the real file map instead of the stale "(in progress)" markers.

**case-study/page.tsx**: expanded Scope, Technical System, Design System, and
Methodology sections to mention schema validation, CI, confidence derivation, and
accessibility/citation work; added new Compliant Social Sampling and Current
Limitations sections; trimmed Future Work to what's actually still open. Kept
third-person wire-service voice throughout — no "I built" framing, per doc §2.

Verified: `cd web && npx tsc --noEmit && npx next build` — clean, all 36 routes
generate correctly, no regressions.

Not committed, per instructions.
