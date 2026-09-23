# data/archive/simulated/

**These 94 reports are simulated. They are not observations and are not evidence.**

They're kept for the record and as schema examples. The site does not build or publish them.

## What they are

- **Produced:** in one autonomous agent loop on 2026-07-06 (101 runs over about 16.5 hours). Each run treated itself as "the next week" and wrote a new dated report.
- **Dates:** 2026-05-07 to 2028-04-17. 92 of the 94 were committed before their own `report_date`.
- **Sources:** written from agent web searches, not from a crawl. No signal links to a specific article. At least one invented source (`uraniumwaves.com`) got in and was later removed (commit `c5025c1`).

## Why they were withdrawn

The project's promise is a dated, source-linked record. A report dated in the future, or a claim without a link to its evidence, breaks that promise however carefully it's written. These reports were published on ari3lla.com until 2026-09-22 and were withdrawn that day.

## Rules

- Don't move these back into `data/reports/`.
- Don't cite them as evidence or extend their calendar.
- Their git history is intact; `git log --follow` on any file shows where it came from.
