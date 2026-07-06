# README + Case Study — Agent Log

## 2026-07-06 02:06 PDT

Scope: README.md (root) and web/app/case-study/page.tsx only, per
docs/ARI3LLA INDEX.txt sections 34, 33, 32, 1.

**README.md** — rewritten from the casual "TLDR: I miss having time to read
vogue" crawler-project framing to the "public research index" framing.
Kept and merged the accurate technical content from the old README (pip
install command, `bash run.sh` / individual script commands, default
source list, mcp tools table, project structure) into the new section
structure specified in section 34: Overview, Live Site, Why This Exists,
Methodology, Source Sectors, Signal Taxonomy, Architecture, Data Pipeline,
MCP/LLM Layer, Ethical AI Statement, Roadmap, Limitations, Screenshots
(placeholder), What I Learned, plus a Project Structure section at the
end. Project structure section notes that some paths (report schema,
taxonomy module, archive/methodology routes, data/reports/) are still in
progress since other agents own those files — described per the intended
structure from doc sections 23/40 rather than guessing exact filenames.

**web/app/case-study/page.tsx** — new page built using the section 33
outline (problem, goal, my role, technical system, design system,
methodology, ethical AI stance, future work) adapted almost verbatim into
a numbered section layout. Matched the existing site's design language
from web/app/page.tsx and layout.tsx: Instrument Serif for headings,
Libre Franklin for body/labels, the same CSS custom properties
(`--black`, `--white`, `--red`, `--gray`, `--border`), masthead/section/
footer structure with borders, and the same "no purchasing recommendation
is implied" footer language used elsewhere in the concept doc.

No other files were touched. No commits were made.
