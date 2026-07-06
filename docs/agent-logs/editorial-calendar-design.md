# Editorial Calendar Design (research + proposal)

Research only, no code changes.

## What trade/beat journalism practice says

Editorial-calendar guidance (Kordiam, Convit, trade-PR sources) converges on one
principle: newsrooms plan around a backbone of **fixed, recurring topics** (trade
shows, earnings seasons, product launches, awards shows, industry milestones) and
leave flexible slots for genuine breaking news — rather than treating each cycle as
independent. Beat reporting practice (per beat-journalism literature referenced via
SPJ/ONA-adjacent sources) similarly relies on reporters maintaining standing
knowledge of a domain's recurring rhythm so routine events aren't mistaken for
anomalies. Long-lead trade press specifically plans pitches/coverage 2–6 months
ahead of known calendar events for this reason.

Applied here: this project's "run 14–16" pattern — independently re-researching
fashion week dates each run to explain a low-volatility stretch — is exactly the
failure mode this practice guards against. A shared, durable calendar reference
removes the need to re-derive it.

Sources:
- [Editorial Calendar: The Foundation of Newsroom Planning](https://kordiam.io/editorial-calendar)
- [Editorial planning: definition, approaches and recommendations](https://convit.de/en/editorial-calendar-and-planning-definition-strategies-and-recommendations)
- [Beat reporting — Grokipedia](https://grokipedia.com/page/Beat_reporting)
- [A Guide to Planning Your Annual PR Editorial Calendar](https://5wpr.net/a-guide-to-planning-your-annual-pr-editorial-calendar/)

## Proposal

Add `docs/EDITORIAL_CALENDAR.md`: a short, durable reference of known recurring
high-volatility windows (fashion weeks now; extensible to Met Gala, major trade
fairs, etc. later). Report-writing agents should check it before flagging a
volume/volatility shift as anomalous or re-researching dates from scratch. This
is additive documentation, not a schema/pipeline change, so it ships now rather
than staying a proposal.
