# Journalism standards check — run 47: Trust Project's 8 Trust Indicators

## Topic
Compared the site against The Trust Project's 8 Trust Indicators (Best Practices,
Author/Reporter Expertise, Type of Work, Citations and References, Methods, Locally
Sourced, Diverse Voices, Actionable Feedback) — not previously covered in agent-logs.
Source: thetrustproject.org/trust-indicators/, thetrustproject.org/faq/.

## Findings against the live site

- **Best Practices** (ownership/funding/ethics disclosure): met. About page's
  "Independence, Corrections, AI Use" section states no brand/publication/retailer
  affiliation and discloses AI's role.
- **Methods**: met. `/methodology` covers classification, confidence, volatility,
  scraping ethics in detail.
- **Citations and References**: met, with a documented deliberate deviation
  (domain-level, not article-level, citation — explained and justified in
  methodology's "How Citations Work").
- **Type of Work**: not applicable in the usual sense (no opinion/analysis/sponsored
  mix) — reports are a single consistent report type; About's "This Index Is/Is Not"
  section functions as the labeling.
- **Author/Reporter Expertise**: not applicable — no bylined human reporters; AI +
  human-editor-note model is disclosed instead, which is the honest equivalent.
- **Locally Sourced**: not applicable — not a local-news outlet.
- **Diverse Voices**: partially met via source-sector diversity requirements for
  confidence, not demographic/voice diversity — reasonable given subject matter.
- **Actionable Feedback**: **gap found.** No contact link, email, or correction-request
  channel exists anywhere on the site (grepped web/ for contact|feedback|mailto — no
  matches) despite the corrections policy on About/Methodology implying errors get
  caught and fixed. There was no real channel to name, so fabricating a fake mailto/contact
  form would itself be a false trust claim.

## Fix applied
Added an honest limitation disclosure to `web/app/methodology/page.tsx`'s "Limitations"
section: notes there is currently no reader-facing channel for flagging a suspected
error, and corrections currently come from internal review only. This keeps the
methodology page's claims accurate rather than implying a feedback loop that doesn't
exist.

## Verification
`cd web && npx tsc --noEmit` — passes, no errors.

## File touched
- `web/app/methodology/page.tsx` (Limitations section, one added sentence)
