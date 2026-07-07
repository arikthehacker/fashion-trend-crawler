# Non-English source handling assessment (run 21)

## crawler.py
Headline extraction (`src/crawler.py`, ~lines 143-158) pulls text from `h1`/`h2`/`h3`
tags via BeautifulSoup and filters with `len(text) > 20`. No English-specific logic:
no punctuation assumptions, no regex tied to Latin word-boundaries, no English
stopword filtering. Character-count filtering works fine on Bahasa Indonesia (Latin
script). No crawler change needed, even for non-Latin scripts in the future — the
filter is character-count based, not word-based.

## summarize.py build_prompt()
Before this run, the prompt said nothing about non-English headline text. Given
`dewimagazine.com` (Bahasa Indonesia) is now a live source, Claude would silently
translate and classify Indonesian headlines exactly as English ones, with no signal
in `evidence`/`index_note` that translation occurred.

**Judged a real gap**, not a non-issue: the project's core discipline is stating
uncertainty/limitations plainly rather than smoothing them over (doc section 2, and
the existing thin-evidence and terminology-drift instructions already in the prompt).
Silent translation is the same category of smoothing-over, just for language instead
of evidentiary confidence.

**Change made:** added one instruction to `build_prompt()` in `src/summarize.py`,
placed after the existing carried-forward garment-terminology instruction:

> "If a headline is in a language other than English, do not silently translate and
> classify it as if it were equivalent to English-language coverage. You may interpret
> it to extract the signal, but note in the evidence or index_note field that the
> source material was non-English (name the language if identifiable) and that the
> term/description is a translation, not a direct quote."

Logged as Run 21 in `docs/PROMPT_CHANGELOG.md` per its convention.

## Verification
`python -m py_compile src/*.py` — passes.

## Files touched
- `src/summarize.py` (one instruction line added to `build_prompt()`)
- `docs/PROMPT_CHANGELOG.md` (Run 21 entry appended)
- `docs/agent-logs/non-english-source-handling.md` (this file, new)

No commit made.
