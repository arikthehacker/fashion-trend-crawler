# Journalism Standards Check — Run 41: Byline-Level AI Disclosure

Topic: dateline/byline conventions for AI-assisted reporting, specifically whether
per-report attribution should distinguish AI involvement, separate from the site-wide
`/about` and `/methodology` AI-disclosure pages that already exist. Not covered by any
prior agent-log (checked `ai-journalism-standards-research.md`, `accessibility-seo-research.md`,
`bias-audit-run16/18.md`, `transparency-disclosure.md`).

## Research

Current guidance (Trusting News byline template; AP/BBC disclosure studies summarized by
Nieman Lab and Journalist's Resource, 2026) converges on: AI disclosure works best **at
the byline**, immediately next to authorship, not only in a general policy page a reader
may never visit — "labels are probably best suited to the byline of an article where
audiences can have immediate insight into who authored the content." Studies also found
human-review disclosure (not just AI-use disclosure) is the strongest credibility signal:
92% of surveyed readers want to know a human vetted AI output specifically, not just that
AI was used generally.

## Audit finding

`web/app/reports/[date]/page.tsx` had a general AI-disclosure story only at the site level
(`/about`, `/methodology`) plus a conditional `reviewed_by`/`review_status` line buried in
the "Notes" section near the bottom of the page — and that line only rendered at all if
`reviewed_by` happened to be populated. There was no unconditional, byline-adjacent AI/human
disclosure on the report page itself, the actual unit readers cite and share. This is a real
gap against current per-story disclosure convention, distinct from the general-policy pages
that already existed.

## Fix

Added an unconditional one-line byline disclosure directly under the report header's
metadata row (collection window / sources scanned / items collected), before any other
content: "AI-assisted collection, extraction, and drafting for this report;
human-reviewed by `{reviewed_by}`" (falls back to "human-reviewed classification" when
`reviewed_by` isn't set), linking to `/methodology`. Kept in report/wire-service voice —
no first person, no promotional framing. Left the existing conditional Notes-section
`reviewed_by` line alone (it has more detail and a `review_status` "Draft"/"Reviewed" tag).

File touched: `web/app/reports/[date]/page.tsx` (header section only).

Verified: `cd web && npx tsc --noEmit` — passes, no errors.

Not committed per instructions.
