# CI Fresh Verification — Run 36

**Date:** 2026-07-06

## `gh` CLI check
Still unavailable: `gh --version` → `bash: gh: command not found`. Same as runs 4/14/22/24/35. Real GitHub Actions status remains unconfirmed via API.

## Fresh-environment local simulation (instead of re-confirming the negative)
Built a genuinely clean environment rather than reusing any cached deps from prior runs:

- **Python**: created a brand-new venv (`python -m venv`), no reuse of any existing site-packages.
  - `python -m py_compile src/*.py` → **exit 0**, no errors.
  - Note: no `requirements.txt` exists in the repo; `validate_all_reports.py` has no third-party deps, so this didn't block anything.
  - `python src/validate_all_reports.py` → **exit 0** — `OK: all 28 report(s) in data/reports/ passed schema validation.`
- **Node/web**: deleted `web/node_modules` entirely before installing (no warm cache reuse).
  - `npm ci` (in `web/`) → **exit 0**, 361 packages installed cleanly in 17s. 5 npm audit vulnerabilities reported (1 low/3 moderate/1 high) — pre-existing dependency advisories, not install failures.
  - `npx eslint .` (in `web/`) → **exit 0**, 0 errors, 1 warning (`app/reports/[date]/page.tsx:114` — unused `eslint-disable` directive for `react/no-danger`, auto-fixable).

## Conclusion
All four workflow commands from `.github/workflows/validate-reports.yml` succeed in a genuinely fresh environment — this rules out the "warm local env masking an issue" concern. The only local vs. CI difference likely to matter is the `1 warning` from ESLint, which is non-blocking (doesn't fail exit code) and unrelated to environment freshness — it's a real lint nit (stale disable comment) that should be cleaned up separately. No environment-assumption bugs found. `gh` access is still the only unresolved gap; someone with GitHub web/API access needs to check the Actions tab directly to close this out for good.
