# structure-taxonomy-sync

Scope: `docs/PROJECT_STRUCTURE.md`, `src/taxonomy.py` only.

## PROJECT_STRUCTURE.md

Walked the actual tree (excluding node_modules/.next/__pycache__/.git) and reconciled it
against the doc. Added previously undocumented items: `TODO.md`, `.codex/config.toml`,
`.claude/` (settings.local.json, scheduled_tasks.lock, skills/ari3lla-index/SKILL.md), all
15 `docs/agent-logs/*.md` files, the two additional dated reports
(`data/reports/2026-07-06.json`, `2026-07-13.json`), and the web build/tooling files
(next-env.d.ts, tsconfig.tsbuildinfo, eslint.config.mjs, postcss.config.mjs). Flipped
`archive/page.tsx`, `reports/[date]/page.tsx`, `methodology/page.tsx`, `taxonomy/page.tsx`,
`sources/page.tsx`, and `about/page.tsx` from "TARGET/not yet created" to "existing" since
they're all built. Added `/timeline` and `/signals/[slug]` as explicit **PLANNED** entries
(doc section 24, per SKILL.md "Common next steps") since they don't exist yet but are named
future work — not removed, just marked accurately. Notes/Follow-ups section updated to
match.

## taxonomy.py

Cross-checked doc section 11's named outlet lists (the runway/editorial list: Vogue Runway,
WWD, Business of Fashion, GQ Style, Harper's Bazaar, Elle, i-D, Dazed, Highsnobiety,
Hypebeast, The Cut, New York Times Style — the only sector in §11 that names specific
outlets rather than generic source-type categories) against `DOMAIN_SECTOR_MAP` in
`classify_source()`. All 12 already have domain entries (vogue.com, wwd.com,
businessoffashion.com, gq.com, harpersbazaar.com, elle.com, i-d.co, dazeddigital.com,
highsnobiety.com, hypebeast.com, thecut.com, nytimes.com). Retail, resale, social,
institutional, and independent-criticism sections in §11 only list generic source-type
descriptions (e.g. "product titles," "museum collections"), not named domains, so there was
nothing further to check against. **No gaps found — `taxonomy.py` left unchanged.**

## Verify

`python -m py_compile src/*.py` — passes clean.
