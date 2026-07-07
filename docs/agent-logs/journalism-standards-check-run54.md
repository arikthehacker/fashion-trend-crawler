# Run 54 — Web font loading performance (font-display / next/font)

**Topic:** Whether the site's custom fonts (Instrument Serif, Libre Franklin, Reenie
Beanie) risk FOIT (flash of invisible text) or block-rendering delays — the standard
concern web performance guidance (Google/web.dev, Next.js docs) raises for third-party
web fonts.

**Research:** Confirmed via Next.js official docs
(https://nextjs.org/docs/app/api-reference/components/font) and changelog discussion
(vercel/next.js#43098/#43178) that `next/font`'s `display` option has defaulted to
`swap` since Next.js 13.2 — a deliberate change specifically to avoid invisible text
during font load. This is a framework-level default, not something each call site needs
to opt into.

**Checked against the actual site:** `web/app/layout.tsx` loads all three custom fonts
via `next/font/google` (`Instrument_Serif`, `Libre_Franklin`, `Reenie_Beanie`), none of
which pass an explicit `display` override — so all three inherit the `swap` default.
`web/package.json` pins `"next": "16.2.4"`, far past the 13.2 threshold where this
became the default behavior.

Beyond `display: swap`, `next/font/google` also self-hosts the font files at build time
(no request to fonts.googleapis.com at runtime), which is a stronger guarantee than
`font-display` alone — it removes the third-party network round-trip entirely, so there's
no separate DNS/connection cost before the swap behavior even matters.

**Conclusion:** No gap found. The site already meets current web font loading best
practice (self-hosted + `font-display: swap`) by virtue of using `next/font/google` on a
modern Next.js version — no explicit `display` prop or other change is needed. No code
changes made this run.
