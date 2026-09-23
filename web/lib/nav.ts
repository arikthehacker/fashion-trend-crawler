// lib/nav.ts
// One source of truth for site navigation, used by the shared header and footer.

export const PRIMARY_NAV = [
  { href: "/", label: "Index" },
  { href: "/archive", label: "Archive" },
  { href: "/timeline", label: "Timeline" },
  { href: "/search", label: "Search" },
  { href: "/glossary", label: "Glossary" },
  { href: "/methodology", label: "Methodology" },
  { href: "/taxonomy", label: "Taxonomy" },
  { href: "/sources", label: "Sources" },
  { href: "/about", label: "About" },
] as const;

export const FOOTER_NAV = [
  { href: "/case-study", label: "Case Study" },
  { href: "/privacy", label: "Privacy" },
  { href: "/terms", label: "Terms" },
  { href: "/accessibility", label: "Accessibility" },
  { href: "/rss.xml", label: "RSS" },
] as const;

export const CONTACT_EMAIL = "ariella@duck.com";
export const ISSUES_URL = "https://github.com/arikthehacker/fashion-trend-crawler/issues";
export const REPO_URL = "https://github.com/arikthehacker/fashion-trend-crawler";
