# Synthetic example reports — not real research

The 95 files in this folder (`2026-05-07.json` through `2028-04-24.json`) were produced
during the project's early build/loop iterations (loop runs 0-102, see
`docs/CHANGELOG.md` and `docs/agent-logs/`) to develop and exercise the report schema,
taxonomy, confidence-discipline system, and site rendering (archive, timeline, signals,
search, RSS, JSON-LD).

**They are not genuine trend research.** Their dates run forward past the actual
build date (up to 2028-04-24, more than a year and a half past the real session date of
2026-07-06). Some entries are hand-authored placeholders; most later ones were produced
by an agent running real `WebSearch` queries against those fictional future dates,
honestly finding no genuine contemporaneous coverage and correctly marking the week
`collection_status: "thin"` rather than fabricating signals — see, e.g.,
`docs/agent-logs/real-report-2028-04-24.md`. The methodology discipline is real; the
dates and the underlying "current" trends they describe are not.

They're kept here for two reasons:

1. **Format/schema reference.** They're valid `report_schema.py` output covering a wide
   range of edge cases (thin weeks, revision history, manual social sampling, every
   confidence/volatility/origin-classification value, etc.) — useful for testing code
   against real schema variety without needing a populated real archive.
2. **Provenance.** They're the concrete artifact behind a large body of documented
   editorial-methodology reasoning (`docs/confidence-discipline-precedents.md`,
   `docs/PROMPT_CHANGELOG.md`, `docs/agent-logs/`) that remains valid and worth keeping,
   even though the reports themselves are being superseded.

**Do not** move these back into `data/reports/`, and do not treat any claim inside them
(a signal, a source count, a "current" trend) as real. `data/reports/` is being rebuilt
from genuine backdated research — see `data/reports/README.md` and
`docs/CHANGELOG.md` for the migration decision and rationale.
