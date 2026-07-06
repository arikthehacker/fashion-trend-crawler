# Doc sync (run 23)

Scope: `README.md` and `docs/PROJECT_STRUCTURE.md` only.

**Report count:** `data/reports/*.json` = 15 files (2026-05-07 through
2026-10-05), not 10 as both docs said (stale since run 18, 4 runs of drift).
Fixed the date lists and counts in both files, including the "as of this
writing" line in README's Limitations section.

**Missing features in README:** confirmed all four exist in code and were
entirely unmentioned — added:
- `/glossary` (`web/app/glossary/page.tsx`, definitions filtered to terms
  actually observed in `data/reports/*.json`)
- "This Week's Index" homepage module (`web/app/page.tsx` line ~118,
  `aria-label="This week's index"`)
- `lint-web` CI job (second job in `.github/workflows/validate-reports.yml`,
  runs ESLint over `web/` on push/PR)
- `eslint-plugin-jsx-a11y` (confirmed in `web/package.json` deps and wired
  into `web/eslint.config.mjs` with several rules enabled)

**PROJECT_STRUCTURE.md:** added `glossary/page.tsx` under `app/`, expanded
the `eslint.config.mjs` entry to describe the jsx-a11y rules and the
documented limitation (can't catch styled-`<p>`-as-heading), and added the
`.github/workflows/` entry (was missing from the tree entirely — described
both `validate` and `lint-web` jobs). `EDITORIAL_CALENDAR.md` and
`PROMPT_CHANGELOG.md` were already present from an earlier run, no change
needed there.

**Sanity check — 3 random README claims verified against code, not trusted:**
1. "overwriting a report requires a `revision_history` entry" —
   confirmed in `src/report_schema.py` (`revision_history` field +
   validation of required keys). Holds up.
2. "`derive_confidence()` ... runs as a non-blocking warning in CI" —
   confirmed in `src/validate_all_reports.py`'s
   `find_high_confidence_warnings()`. Holds up.
3. "manual-sampling workflow ... exercised twice" —
   `docs/agent-logs/manual-sample-exercised.md` and
   `manual-sample-exercised-2.md` both exist; `human_editor_note` appears
   across most report files. Holds up.

Nothing under `web/` was edited, so `tsc --noEmit` was not run per task
instructions.
