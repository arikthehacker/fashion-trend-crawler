# Changelog reorganization

`docs/CHANGELOG.md` had grown to 12 loop-run entries plus branch-setup entries in one file.
Reorganized it as a concise master index (one paragraph per run, linking out) with full
detail moved to `docs/changelog-entries/`.

## What changed

- Created `docs/changelog-entries/run-01.md` through `run-12.md`, one per loop run, each
  containing that run's full original section content verbatim (no summarization or
  deletion), plus a "back to index" link.
- Created `docs/changelog-entries/run-00-branch-setup.md` containing the pre-loop branch
  setup, the five-parallel-subagents overnight build section, the consolidation pass, and
  the "Known gaps / deliberately not done tonight" section — verbatim.
- Rewrote `docs/CHANGELOG.md` as a scannable index: one paragraph summary per run/entry, in
  original chronological order (newest first, matching the original), each linking to its
  detail file. Pointer to `TODO.md` for current open items retained at the bottom.
- Updated `.claude/skills/ari3lla-index/SKILL.md`'s file map: `CHANGELOG.md` line now
  describes it as the master index, and added a new `changelog-entries/*.md` line pointing
  to the detail files.

## Verification

- Grepped the whole repo for `CHANGELOG.md#` and similar anchor references — none found, so
  no other file (skill docs, README, TODO.md) links to a specific line/anchor that would
  break from the reorg.
- All original content preserved; nothing deleted, only relocated and indexed.

## Note on concurrency

The SKILL.md file was edited by another concurrently running agent mid-task (it had added
run 12/13-era details I hadn't seen on my first read). I re-read the current file before
applying my file-map edit, so only the `CHANGELOG.md`/`changelog-entries` lines were
touched — the other agent's unrelated changes are untouched.
