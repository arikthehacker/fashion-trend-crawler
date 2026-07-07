# Keyboard-only navigability check (run 61)

**Topic:** Is every interactive element on the site reachable and operable via
Tab/Enter alone, beyond the existing skip-link (verified run 57)? Not previously
covered in the agent-log list.

## What was checked

Grepped every file under `web/app/**/*.tsx` for `tabIndex`, `onClick`,
`onKeyDown`, and `role=` — the usual signatures of custom (non-native) keyboard
handling that can silently break Tab/Enter operability. Findings:

- Only one `role=` in the whole app (`role="article"` on a report card,
  `web/app/page.tsx:272`) — a static landmark role, not an interactive widget,
  no keyboard implications.
- Zero `onClick`, `onKeyDown`, or `tabIndex` anywhere in `web/app`. There are no
  custom buttons, no div-as-button patterns, no positive tabindex to disrupt
  natural tab order.
- All navigation uses Next's `<Link>` (renders a real `<a href>`) or plain
  `<a>` (skip-link in `layout.tsx`). All filtering in
  `web/app/search/SearchClient.tsx` uses native `<select>` elements with
  paired `<label htmlFor>` — no custom listbox/combobox reimplementation.
- The one non-trivial widget on the site, Pagefind's `PagefindUI` (mounted in
  `SearchClient.tsx`), is third-party and out of this repo's code — but per
  Pagefind's own docs its searchbox implements the ARIA combobox pattern
  (`role="option"`, `aria-selected`, `aria-activedescendant`) specifically so
  keyboard navigation reaches its results; this is the maintainer's
  responsibility, not something this repo's own markup needs to add.

Cross-checked against WCAG 2.1.1 (Keyboard, Level A): native `<a>`/`<select>`
elements are a sufficient technique on their own — no custom `keydown`
handling is required to meet the criterion when a page is built entirely from
native interactive elements, which this site is.

## Conclusion

No gap found; no code change made. The site's own authored markup already
meets keyboard-only operability by construction (native elements only, no
custom widgets, no positive tabindex, no click-only handlers). The only
non-native widget (Pagefind's search UI) already implements the correct ARIA
combobox pattern upstream. Recorded here so a future run doesn't re-derive the
same grep from scratch — if new interactive UI is ever added (e.g. a custom
dropdown, modal, or accordion), it will need explicit keyboard handling at
that point, unlike everything currently on the site.

No `web/` files were modified, so `npx tsc --noEmit` was not re-run.
