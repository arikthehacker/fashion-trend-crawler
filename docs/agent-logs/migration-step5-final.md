# Migration step 5 (final): legacy trends_raw.json / trends_summary.json — NOT deleted

## Verification performed

Grepped entire repo for literal `"trends_raw.json"` and `"trends_summary.json"` in `.py` files:

```
src/crawler.py:41:   DEFAULT_OUTPUT_FILE = "trends_raw.json"      # constant definition only
src/summarize.py:31: def load_trends(path="trends_raw.json"):    # literal default arg, intentional per migration-step2.md
```

No `.py` file under `src/` still hardcodes `"trends_summary.json"`. `src/report_schema.py:7` only mentions it in a comment.

## Blocker found: web/lib/trends.ts

A full-repo grep (not limited to `src/`) turned up an active reader outside Python code:

```ts
// web/lib/trends.ts
33: export function getTrends(): TrendsData {
34:   const root = path.join(process.cwd(), "..");
37:   const rawPath = path.join(root, "trends_raw.json");
38:   if (!fs.existsSync(rawPath)) { return { pages: [], summary: null, ... }; }
42:   const pages = JSON.parse(fs.readFileSync(rawPath, "utf-8"));
52:   const summaryPath = path.join(root, "trends_summary.json");
53:   const summary = fs.existsSync(summaryPath) ? JSON.parse(fs.readFileSync(summaryPath, "utf-8")) : null;
```

This is the Next.js web app's data loader. It resolves both files at **repo root** (`process.cwd()/..` from `web/`) by hardcoded literal path and actively `readFileSync`s them if present. It degrades gracefully to an empty/`null` state when the files are absent (no crash), but deleting the root-level `trends_raw.json`/`trends_summary.json` would silently change the web app's rendered output (e.g. any page currently displaying crawl data or an AI summary would revert to "never"/empty), which is a real behavior change, not just cache cleanup.

Note this reader was not caught by prior runs (`legacy-file-cleanup.md`, `hygiene-scan.md`, migration-step1-4) because they only grepped `src/*.py` / `docs`, not `web/`.

## Decision

**Did not delete any files.** Per task instructions, since verification found something still depending on the files' current content (root-level copies feed `web/lib/trends.ts`'s `getTrends()`), deletion is blocked for the two **root-level** files (`trends_raw.json`, `trends_summary.json`).

The two **`src/`-level** copies (`src/trends_raw.json`, `src/trends_summary.json`) have no reader/writer referencing that path (crawler.py/summarize.py/server.py/test_tools.py all resolve relative to their own CWD conventions documented in earlier steps, and `web/lib/trends.ts` only reads root-level paths) — but per instructions this is an all-or-nothing "4 files total" step, so none were deleted this run.

## Next step for a future run

Either: (a) migrate `web/lib/trends.ts` to read from `data/reports/` via the new schema (mirroring the `summarize.py` migration), then retire all 4 legacy files, or (b) confirm product intent to drop the web app's legacy fallback display before deleting.
