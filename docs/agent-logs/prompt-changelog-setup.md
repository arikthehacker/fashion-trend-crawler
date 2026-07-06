# Prompt changelog setup

Created `docs/PROMPT_CHANGELOG.md`, a dedicated log for substantive changes to
`summarize.py`'s `build_prompt()` instructions, separate from `docs/CHANGELOG.md`'s
general code-change log. Motivated by the gap flagged in
`docs/agent-logs/ai-journalism-standards-research.md`: AP/Reuters treat AI-generation
instructions as editorial policy requiring periodic review, but this repo had been
tracking prompt edits as ordinary commits with no dedicated review trail.

Reconstructed history retroactively from `git log -p -- src/summarize.py` and
`docs/CHANGELOG.md`/`docs/changelog-entries/*.md`, documenting three substantive
instruction changes:
- **Run 0** (`91a7ea0`): initial editorial prompt — no-first-person/no-hype/no-purchase-
  advice rules, source-incentive-aware classification, social-defaults-to-volatile.
- **Run 3** (`7435adb`): Reuters-attribution tightening (banned evaluative verbs like
  "declared"/"proves" in favor of "said"/"reported") and a ubiquity-language ban
  ("everyone is wearing") plus a thin-evidence honesty instruction.
- **Run 7** (`6634e39`): thin-week honesty instruction — explicit ban on
  stretching/manufacturing signals to look comprehensive, paired with the
  `collection_status`/`thin_week_note` schema fields.

Also listed three commits reviewed and excluded as non-substantive (parameterization,
max_tokens fix, revision_history plumbing) to show the distinction was applied
deliberately, not just to every commit touching the file.

Added a header section stating the file's purpose and a proposed (not yet tooled)
quarterly review cadence, mirroring AP's practice. No code was touched — only
`docs/PROMPT_CHANGELOG.md` (new) and this log were written.
