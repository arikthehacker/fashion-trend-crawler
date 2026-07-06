# Static export fix

Static export now works.

## Changes

- `web/app/sitemap.ts`: added `export const dynamic = "force-static";`.
- `web/app/robots.ts`: added `export const dynamic = "force-static";`.
- `web/next.config.ts`: re-added `output: "export"` (removed the explanatory
  comment about the prior failure since it's now resolved).

## Verification

- `cd web && npx tsc --noEmit` — clean, no errors.
- `npx next build` — succeeded. Output includes `/sitemap.xml` and
  `/robots.txt` as static (○) routes, alongside all other pages (SSG report
  and signal routes included).
- Confirmed `web/out/` was actually produced, containing `sitemap.xml` and
  `robots.txt` as real static files (not just `.next/`) — this is the file
  Pagefind's `postbuild` step needs to run against.

## Net result

Static export is fully restored. The `force-static` directive on both
route handlers was the correct, documented fix per Next.js's static-export
error message — no other blockers surfaced. Pagefind's `postbuild` script
(`pagefind --site out --output-subdir _pagefind`) should now work as
originally intended in the pagefind-integration run, though `pagefind`
itself was not exercised here (out of scope — this task was only the
static-export fix). A human/agent should still run `npm run build` end to
end with `pagefind` installed to confirm `out/_pagefind/` gets generated
and `/search` renders it correctly.
