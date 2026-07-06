# Repo Hygiene Log

## 2026-07-06 02:06 PDT — repo-hygiene audit

Scope: organizational/hygiene pass only, per docs/ARI3LLA INDEX.txt section 23/40 reorg.
Branch: ari3lla-index-rebuild.

**Findings:**

1. **Stray `.git` dirs**: none found. Only the root `.git/` exists anywhere in the tree.
2. **Build/cache artifacts**:
   - No `__pycache__` dirs or `*.pyc` files present anywhere at audit time — nothing to
     delete.
   - `src/.gitignore` already ignores `__pycache__` and `*.pyc`.
   - `web/.gitignore` already ignores `/node_modules` and `/.next/`.
   - Root `.gitignore` only had `.env`, `node_modules`, `.next` (no Python patterns).
     Added `__pycache__/`, `*.pyc`, `*.pyo`, `.venv/` to root `.gitignore` as a safety net
     for future files created at repo root. No files deleted.
3. **Legacy trend JSON files**: `trends_raw.json` / `trends_summary.json` exist both at
   repo root and in `src/`, with diverged content (different article sets — e.g. root
   version references a Met Gala/Cannes crossover moment, src/ version is Met-Gala-only
   with different summary text). These look stale/duplicated relative to the new
   `data/reports/*.json` schema (already has `data/reports/2026-05-07.json`). Left
   untouched per instructions; recommend removing all four legacy files once the
   `report_schema.py`-driven pipeline is confirmed fully working end to end.
4. **`src/run.sh` / `src/test_tools.py`**: still run the old pipeline (`crawler.py` ->
   `test_tools.py` -> `server.py`) and `test_tools.py` reads `trends_raw.json` directly.
   Once `report_schema.py` / `taxonomy.py` are wired into `summarize.py` / `server.py` by
   the owning agent, both files will likely need updates (pipeline order, fixture path).
   Not modified — out of scope / owned by another agent. Informational only.
5. **Project structure doc**: wrote `docs/PROJECT_STRUCTURE.md` describing the intended
   end-state tree per section 23/40, noting which paths exist already vs. are still
   pending (`web/app/archive/page.tsx`, `web/app/reports/[date]/page.tsx` not yet created
   as of this audit).

**Changes made:** edited root `.gitignore` only (added Python cache patterns); created
`docs/PROJECT_STRUCTURE.md`; created this log entry. No deletions, no commits.
