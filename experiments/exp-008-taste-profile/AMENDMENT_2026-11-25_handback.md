# EXP-008 amendment 1: the subagent's reply channel (2026-11-25)

**Before any profile was sealed or read, and before any DeepSeek call.**

## What happened

All seven profile subagents finished. The first transcript audit (`check-profile`, held-out week 2026-11-15) failed on exactly one call: `SubagentHandback`, the tool the Claude Code harness makes every subagent use to return its final reply. The pre-registered audit allowed only Read and Write. As written, it could not be passed by any subagent, so the pre-registered retry (a fresh subagent) would fail the same way.

That reply carried only the word count the instructions asked for (`532`). The same transcript shows Read calls on exactly the six allowed input files and one Write to the profile path. The leak check on that profile found no problems.

## The change

`audit_transcript` in `src/exp008.py` also allows one kind of call: `SubagentHandback` whose message is only a number, optionally followed by "word" or "words". A reply holding anything else, such as profile text, still fails the audit. A test covers both cases. Every other rule is unchanged: the allowed reads, the single write, the leak check, the 800-word cap and the one-retry rule.

The record of the failed first check is kept, renamed `data/store/blind/exp008/profile_checks/2026-11-15.pre-amendment.jsonl`, so that each week's attempt count counts profile attempts and not runs of the checker.

## Freezing

`protocol/amendment_1.json` records the SHA-256 of this file, of the original protocol it amends and of the amended code. The runner accepts the amended code only through that record, and needs it committed and pushed before the DeepSeek run, as for the protocol.
