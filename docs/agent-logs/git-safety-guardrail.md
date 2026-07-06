# Git safety guardrail (run 9)

Added convention #7 to `.claude/skills/ari3lla-index/SKILL.md`'s "Workflow conventions"
section, documenting the run 8 coordination bug: an agent's broad `git checkout`/revert
while cleaning up its own exploratory changes to `summarize.py`/`trends_raw.json` silently
wiped out two other concurrently-running agents' uncommitted work (`server.py`,
`validate_all_reports.py`).

**Fix documented:** when multiple subagents work concurrently on the same branch/working
tree, any agent reverting its own exploratory changes must scope the revert to the exact
file paths it personally modified (`git checkout -- <path>`, `git restore <path>`) — never
a bare `git checkout .` / `git restore .` / `git clean` that could touch other agents'
concurrent uncommitted work.

Also refreshed the file map and "Common next steps" section to reflect run 8 changes that
had drifted since run 7's refresh:
- `summarize.py`: noted `max_tokens=4000` fix (was 2000, truncated real API output).
- `server.py`: noted it now uses the shared `DEFAULT_OUTPUT_FILE` constant.
- `validate_all_reports.py`: noted it now runs `derive_confidence()` as a non-blocking
  warning.
- Added `docs/agent-logs/live-crawl-2026-07-06-real-output.json` to the file map.
- Updated "Common next steps" to reflect run 8's status (live crawl succeeded but not
  merged due to date collision; 2/5 migration steps remain; `revision_history` proposal
  still open).

Only `.claude/skills/ari3lla-index/SKILL.md` was touched, no other files. Not committed.
