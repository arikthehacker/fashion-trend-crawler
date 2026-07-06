# Self-archival decision (run 43)

## Question
Runs 40-42 carried "periodic Wayback Save Page Now snapshotting of the site's own
`/reports/[date]` pages" as a vague future item without acting on it. Decide, don't defer.

## Decision
Built `src/generate_archive_manifest.py` now; did NOT build the actual Wayback API
integration. Reasoning:

- The site has no live deployed URL — `web/lib/site.ts`'s `SITE_URL` is still the
  placeholder `https://ari3lla-index.example.com` (confirmed, unchanged since run 5/30's
  citation work).
- There is no CI/CD deployment pipeline (`gh` CLI still unconfirmed after 8+ runs), so
  there's no scheduled place to run an automated Save-Page-Now call from anyway.
- Calling the real Save Page Now API against a non-resolving placeholder domain would
  snapshot garbage — worse than doing nothing, and the CJR risk this is meant to address
  (false confidence that "it's archived") would still apply to a snapshot of nothing.

What was built instead is genuinely useful now and has zero networking/deployment
dependency: `generate_archive_manifest.py` reads `data/reports/*.json` locally and emits
`docs/agent-logs/archive-manifest.json` — one entry per report (`report_date`, `url`
built from a `--site-url` flag, `content_hash` for fixity cross-check). Run today it
correctly outputs a `site_url_is_placeholder: true` flag and a printed warning, so it's
honest about not being actionable yet rather than silently producing dead links.

## Concrete trigger for the next step (not vague)
When `SITE_URL` is set to a real deployed domain:
1. Re-run `python src/generate_archive_manifest.py --site-url https://<real-domain>`.
2. Either manually submit each URL to `https://web.archive.org/save/<url>`, or wire a
   small scheduled job (once CI/CD exists) that does the same POST per new report.
3. Only at that point does building the actual Save Page Now API call stop being
   premature.

## Verification
`python -m py_compile src/*.py` passes. Ran the script directly: produced a 35-entry
manifest at `docs/agent-logs/archive-manifest.json`, correctly flagged as
placeholder-not-actionable.

## Outcome
Removed the vague "consider periodic Wayback snapshotting" line from `TODO.md`'s
Next-up list (carried runs 40-42) — replaced with a closed decision + the manifest
tool + this doc's concrete trigger condition, so no future run re-litigates it from
scratch.
