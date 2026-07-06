# Correction-request channel decision — run 48

## Question
Run 47 honestly disclosed there is no correction-request channel (a real Trust
Indicators gap) rather than fabricating one. TODO.md flagged this as "consider adding a
real one" — this run makes the actual call instead of leaving it open indefinitely.

## Constraints confirmed
- `output: "export"` in `next.config.ts` — fully static site, no backend for form
  submissions or a mail relay.
- `SITE_URL` in `web/lib/site.ts` is still `ari3lla-index.example.com`, a placeholder —
  no deployed domain exists yet (per runs 39/43).
- The project IS a real git repository with a real GitHub remote:
  `github.com/arikthehacker/fashion-trend-crawler`.

## Small archival/news-site convention check
Small documentation/data/archive projects with no deployed reader-facing infra commonly
route correction/error reports through their public issue tracker rather than standing up
a contact form or inbox before launch (common pattern for open, repo-backed publications
and data projects). That fits this project's exact situation: real repo, no real domain,
no backend.

## Decision (closed, not "consider" anymore)
A contact form or mailto inbox is premature infrastructure for a static-export site with
no live domain — building it now would be speculative work for readers that don't exist
yet. But "no channel at all" was also not the honest ceiling: the repo itself is real
today. Linking its Issues tracker costs nothing, requires no infra, and is a genuine,
functioning channel right now, not a placeholder.

Implemented:
- `web/app/about/page.tsx` — Corrections paragraph now links to
  `https://github.com/arikthehacker/fashion-trend-crawler/issues` as a real,
  non-staffed-but-monitored channel, alongside the existing correction-process text.
- `web/app/methodology/page.tsx` — Limitations bullet rewritten from "no mechanism
  exists" to point at the same Issues link, with an honest caveat that it isn't a
  staffed inbox.
- `TODO.md` — item converted from open "consider" to a closed, considered decision with
  a pointer to this log, so it stops resurfacing as a perpetual candidate.

## Verification
`cd web && npx tsc --noEmit` — passes, no errors.

## Caveat for future runs
This assumes the GitHub repo stays public. If it's ever made private, this channel
silently breaks for external readers — worth a periodic check. Revisit if the tracker
proves unmonitored in practice, or once a real deployed domain exists (at which point a
dedicated inbox may become worth the infra cost).

## Files touched
- `web/app/about/page.tsx`
- `web/app/methodology/page.tsx`
- `TODO.md`
