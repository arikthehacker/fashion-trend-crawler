# run 65 — .env.example + README setup docs

Closed the remaining gap from `api-key-investigation-run64.md`: the key itself
was confirmed available, but there was no `.env.example` and no human-facing
explanation of the `.env` mechanism.

## Changes

- Created `.env.example` at repo root: a placeholder
  `ANTHROPIC_API_KEY=your-api-key-here` with a comment explaining it's copied
  to `.env` (git-ignored) and loaded by `src/summarize.py` via
  `python-dotenv`'s `load_dotenv()`.
- Confirmed `.env` is already listed in `.gitignore` (line 1) — did not
  assume, checked directly.
- Added a short "### API key setup" section to `README.md`, just above the
  existing "### How to run it" section: copy `.env.example` to `.env`, fill
  in a real key, note that `summarize.py` loads it automatically via
  python-dotenv. Kept to ~10 lines, consistent with the existing terse doc
  style.

## Verification

- No Python files touched, so `py_compile` not required.
- Ran `grep -n "sk-ant-\|sk-" .env.example README.md` against both edited
  files — **zero matches**. Confirmed no real API key value leaked into
  either file; both only reference the `ANTHROPIC_API_KEY` variable name and
  a placeholder string.

## Files touched

- `.env.example` (new)
- `README.md` (added one section)
