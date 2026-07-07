# Reader trust-signal research (no analytics/survey infrastructure)

## What low-resource outlets actually use as trust proxies

- **The Trust Project's 8 Trust Indicators** (Best Practices, Author/Reporter Expertise,
  Type of Work, Citations/References, Methods, Locally Sourced, Diverse Voices, Actionable
  Feedback) are explicitly designed to work for small/independent publishers without survey
  infrastructure — they're a checklist a newsroom self-certifies against, not a metrics
  system. The key design principle: indicators must be **visible on the page itself and
  embedded in page markup**, not just documented somewhere on the site. UT-Austin's Center
  for Media Engagement found reader trust ratings rose simply from indicator *presence and
  visibility* on a page — no traffic/survey data needed to validate the mechanism itself,
  because the org's own research already validated it. (thetrustproject.org/trust-indicators,
  thetrustproject.org/faq)
- **Trusting News's core low-resource proxy is placement, not measurement.** Their
  corrections guidance states plainly that corrections "buried at the very bottom of a story"
  fail as a trust signal even when the content is correct — the newsroom examples they cite
  (e.g., Toronto Star) put an error-report link and corrections mention at the bottom of
  *every individual story*, not on a separate policy page. Their framing: if a reader has to
  go hunting for the transparency material, it isn't functioning as a trust signal, "presence"
  and "discoverability" are treated as two different, non-substitutable properties.
  (trustingnews.org/be-loud-about-mistakes-and-how-you-correct-them,
  trustingnews.org/trustkits/corrections)
- Reuters Institute's "Depth and breadth" research frames the same trade-off structurally:
  outlets choose between a small number of highly visible trust signals (breadth, seen by
  most readers) vs. deep transparency documentation (depth, seen by few) — small newsrooms
  without analytics can't A/B this, so the practical guidance is to bias toward breadth:
  a few signals placed where the traffic already is, rather than one exhaustive page.

## Gap check against this project

`web/app/methodology/page.tsx` and `web/app/about/page.tsx` both carry substantial, genuine
transparency content — Corrections, Editorial Independence, and AI Involvement each have a
real section. That's presence, and per the sources above presence is necessary but not the
proxy that matters.

Discoverability is the actual gap. Both pages are nav-linked from every other page's header
(`/methodology`, `/about` are in the shared nav array), which is fine for a reader who already
suspects something to check. But the sections a reader would use to decide "can I trust this"
— Corrections, Editorial Independence, AI Involvement — sit as the **last three of 15 sections**
on Methodology and the **last block before the footer** on About. A reader who lands on a
report page (`/`, `/reports/[date]`) — the actual entry point for most visits per the site's
own structure — has zero inline signal that this material exists at all; they'd have to
navigate away and scroll through unrelated taxonomy content to find it.

This matches exactly the failure mode Trusting News calls out: the content exists, but nothing
at the point of reading (the report itself) points to it or surfaces it. No survey is needed to
notice this — it's a structural/navigation fact, checkable by reading the page.

## Recommendation (not implemented — flagged for a future run)

Add a short, single-line trust-signal strip to report pages (`reports/[date]/page.tsx`) —
e.g. "Corrections & AI-use disclosed — Methodology" linking to the relevant anchor — rather than
relying on readers to find the nav link and scroll to the bottom of Methodology. This is a
placement/discoverability fix, not new transparency content; the underlying material already
exists and is accurate. Low effort, no schema or pipeline changes required.

## Sources

- https://thetrustproject.org/trust-indicators/
- https://thetrustproject.org/faq/
- https://trustingnews.org/be-loud-about-mistakes-and-how-you-correct-them/
- https://trustingnews.org/trustkits/corrections/
- https://reutersinstitute.politics.ox.ac.uk/depth-and-breadth-how-news-organisations-navigate-trade-offs-around-building-trust-news
