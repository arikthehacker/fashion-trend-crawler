# EXP-008 amendment 2: self-edits and short replies (2026-11-25, the owner's decision)

**Before any profile was sealed or read, and before any DeepSeek call.**

## What happened

Under amendment 1, five of the seven profiles passed both software checks on their first attempt (held-out weeks 2026-10-18, 10-25, 11-01, 11-15 and 11-22). Two weeks failed the transcript audit twice, which under the pre-registration stops the run and leaves the decision to the owner:

| Held-out week | Attempt 1 | Attempt 2 (fresh subagent, same instructions) |
|---|---|---|
| 2026-10-11 | edited its own profile 4 times and reread it | replied "About 537 words (counted by hand, no tool run)." instead of a bare number |
| 2026-11-08 | edited its own profile 16 times | edited its own profile 4 times, and replied with a sentence about the word count |

In all four attempts, the subagent read only its six allowed input files and wrote only to its own profile path. Every profile passed the leak check: no signal names, outlet names or 5-word headline runs, and under 800 words. The first attempts are kept unread as `profiles/<week>.attempt1.md`.

## The owner's decision

On 2026-11-25 the owner chose to amend the audit and use the second attempts for both weeks. The other options were to run five weeks only or to give the two weeks a third attempt with stricter wording.

## The change

`audit_transcript` in `src/exp008.py` now also allows:

1. **Read and Edit of the subagent's own profile file.** Rereading and revising its own draft does not expose anything beyond its six inputs. Any read, edit or write of any other path still fails.
2. **A reply of at most 300 characters that passes the same leak check as the profiles.** A longer reply, or one containing a signal name, outlet or headline run, still fails.

Two smaller changes go with it:
- `check_profile` counts attempts as distinct profiles, so checking the same profile again under new rules is not a new attempt.
- `seal_profiles` records, for each week, the attempts, the number of checks run, the audit rules in force and each failed attempt's problems.

Nothing else changes: the allowed inputs, the instructions, the leak check, the word cap, the prompt and the DeepSeek reader.

## What this means for the result

The five weeks that passed under amendment 1 would also pass under amendment 2. For weeks 2026-10-11 and 11-08, the profile used is the second attempt. The comparison report states this beside the results, and the per-week metrics let anyone check those two weeks separately.

## Freezing

`protocol/amendment_2.json` records the SHA-256 of this file, of the original protocol and of the amended code. The runner accepts the amended code only through that record, and needs every amendment record committed and pushed before the DeepSeek run.
