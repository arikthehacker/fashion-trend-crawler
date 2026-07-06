# Full-archive coherence review, run 47 (40-report milestone)

**Result: found and fixed real doc-sync gaps. Signal-link integrity and voice audit are
clean.**

## 1. Doc-sync (README.md / PROJECT_STRUCTURE.md)

Confirmed three real, undocumented additions since run 42/45/46:
- `src/generate_archive_manifest.py` (run 43) was in the repo but absent from README.md,
  PROJECT_STRUCTURE.md, and SKILL.md's file map. Added to all three.
- `web/scripts/copy-reports.mjs` (run 45, hardened run 46 to also run from
  `next.config.ts` directly, not just the npm `prebuild` hook) was undocumented. Added to
  README's structure tree, PROJECT_STRUCTURE.md (new `scripts/` entry plus a note on
  `next.config.ts` invoking it directly), and SKILL.md.
- The `Dataset` JSON-LD block (run 46: CC BY 4.0 `license` URL + `DataDownload`
  distribution) and the visible "download raw data" link on `/reports/[date]` were only
  described as generic "`NewsArticle` JSON-LD" in README — updated to reflect both JSON-LD
  types and the download link/license line.

Bonus fix (not in the three named items but found while reading SKILL.md's file map):
SKILL.md still said full-text search "(Pagefind) deliberately deferred" under
`search/page.tsx`, but Pagefind was actually implemented and verified end-to-end (runs
14/15, confirmed working in `agent-logs/pagefind-verification-run15.md`; PROJECT_STRUCTURE.md
already reflected this correctly). Corrected the stale line in SKILL.md.

No download route.ts exists — the "download route" is a static file
(`public/data/reports/<date>.json`) produced by `copy-reports.mjs`, not an API route;
docs now describe it accurately as such.

## 2. Signal-link integrity

Read-only Node scan of all 40 `data/reports/*.json` files: 51 distinct `signal_id` values
across `top_signals[]`. Zero empty/whitespace/malformed IDs. Since `getAllSignalSlugs()`/
`getSignalHistory()` iterate the same field, links resolve structurally by construction —
consistent with runs 27/40. Rename batches 36/44 introduced no dangling references.

## 3. Voice audit (targeted spot-check of new material)

Read executive summaries + all `top_signals[].name`/`index_note` for the four newest
reports (2027-03-08, 03-15, 03-22, 03-29). All wire-service tone: no first person, no
hype, uncertainty stated plainly (e.g. the Wales Bonner "untracked pending new
information" transition is narrated as a process decision, not a resolved fact).

Checked the newest UI additions directly in `web/app/reports/[date]/page.tsx`:
- License line ("classification and summary metadata licensed CC BY 4.0; underlying
  source articles remain the property of their original publishers") — plain, accurate.
- "How This Report Was Compiled" methodology box (collection window / sources scanned /
  items collected + AI-disclosure byline note) — factual, no hype.
- "Download raw data (JSON)" link — plain label, no voice issue.

No violations found; nothing needed fixing in report/UI copy itself.

## Verification

Docs-only changes (README.md, docs/PROJECT_STRUCTURE.md, SKILL.md) — no `src/` or `web/`
code touched, so `py_compile`/`tsc`/`eslint` were not required and not run. Not committed
per task instructions.
