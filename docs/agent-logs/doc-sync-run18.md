# Doc sync (run 18)

Scope: `README.md` and `docs/PROJECT_STRUCTURE.md` only.

**Sanity check — report count:** `ls data/reports/*.json` = 10 files
(2026-05-07 through 2026-08-31). README's Limitations section said "7 dated
reports as of this writing" and its Project Structure code block listed only
4 dates (-05-07, -07-06, -07-13, -07-20). Both stale — fixed to 10 and the
full date list. `PROJECT_STRUCTURE.md` said "7 reports as of run 13
(2026-05-07 through 2026-08-10)" and only itemized 3 files — updated to 10,
full range through 2026-08-31, all files listed.

**Pagefind:** confirmed real (`web/package.json` has the `pagefind`
devDependency + `postbuild` script, `next.config.ts` has `output: "export"`,
and `agent-logs/pagefind-verification-run15.md` shows it verified end-to-end
via a real build). README's Archive & Reporting Surfaces section didn't
mention `/search` or `/rss.xml` at all — added both. PROJECT_STRUCTURE.md's
search entry still described only the old facet-filter-only state — updated
to note Pagefind, citing both `pagefind-integration.md` and
`pagefind-verification-run15.md`, and added notes on the `package.json`/
`next.config.ts` changes Pagefind required.

**Missing docs:** `docs/EDITORIAL_CALENDAR.md` and `docs/PROMPT_CHANGELOG.md`
existed but weren't listed in PROJECT_STRUCTURE.md's docs/ tree — added both
with one-line descriptions. README doesn't carry a docs/ tree listing so no
change needed there.

No other content changed. Skill doc, CHANGELOG, changelog-entries untouched.
Nothing under `web/` touched, so `tsc --noEmit` not run per task instructions.
