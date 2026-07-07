# Skill doc refresh 4 (covers runs 18-28)

Cross-checked `.claude/skills/ari3lla-index/SKILL.md`'s file map against actual
`web/app/`, `src/`, `docs/` trees. Found two real gaps and fixed them:

- `src/check_field_coverage.py` (added run 25) was missing from the file map entirely —
  added with a note on what it does and why it exists (structural fix for the
  human_editor_note/revision_history/thin_week_note "claimed but not shown" bug pattern).
- `web/app/glossary/page.tsx` (shipped run 20) was missing — added.

Everything else in the file map still matched the live tree; no stale entries found
(prior refreshes have kept it clean).

Added workflow convention #9: schema fields being populated is not the same as being
rendered, and documented instructions are not the same as working instructions. Cites
the three-run pattern (21/23/24: human_editor_note, revision_history, thin_week_note all
shipped in data before ever being displayed) and run 28's README `bash run.sh` fix as the
same underlying lesson — verify transparency/operational claims end-to-end, don't trust
that "it's in the data/doc" means "it's true of the live site."

Updated "Common next steps" to point at run 28's actual "Next up (run 29 candidates)"
list from `TODO.md`: the untested run-19 confidence-gate fix, unavailable `gh` CLI
blocking real CI verification, the still-unresolved CFDA Fashion Fund/Awards signals,
and periodic re-verification of README's now-fixed run instructions.

Did not touch `docs/CHANGELOG.md` or `docs/changelog-entries/`, per instructions. No
other files modified.
