# RSS spec-compliance check (rssboard.org profile / W3C Feed Validator) — run 66

Run 43 partially checked the RSS feed against the rssboard.org RSS 2.0 profile
(item title/category conventions). This run re-verified against the *specific*
checks the W3C Feed Validator and rssboard's own validator perform beyond
"well-formed XML," at current archive scale (65 reports).

## Research (confirmed via web search, not assumed)

- Both validators explicitly flag a channel missing
  `<atom:link rel="self" type="application/rss+xml" href="...">` as
  "Missing atom:link with rel='self'" — a documented rssboard.org Best
  Practices Profile recommendation (RFC 5005-style self-identification
  convention), not part of the RSS 2.0 core spec, but a real warning a
  validator run would surface. See
  https://www.rssboard.org/rss-profile and
  https://validator.w3.org/feed/docs/warning/MissingAtomSelfLink.html.
- `<language>en-us</language>` was re-confirmed valid against rssboard's
  ISO 639 language-code list (hyphenated country suffix is correct; underscore
  would not be).

## Gap found and fixed

`web/app/rss.xml/route.ts` had no `atom:link rel="self"` element — a real,
previously-unaddressed gap despite the feed otherwise following the rssboard
profile (meaningful per-item titles, `<category>` tags, corrected `<pubDate>`
from run 37). Added:

```xml
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  ...
  <atom:link href="{SITE_URL}/rss.xml" rel="self" type="application/rss+xml" />
```

This also declares the `atom` namespace on the `<rss>` root, required for the
element to be valid.

## Other checks re-confirmed clean (no changes needed)

- `escapeXml()` ordering (`&` first) still correct across title/link/guid/
  description at 65-report scale.
- `<guid isPermaLink="true">` matches `<link>` for every item — satisfies the
  spec requirement that a permalink guid be a real, dereferenceable URL.
- `<pubDate>`/`<lastBuildDate>` remain valid RFC-822 via `toUTCString()`.

## Verification

`cd web && npx tsc --noEmit` — clean, no errors.

## Files touched

`web/app/rss.xml/route.ts` only. Not committed per instructions.
