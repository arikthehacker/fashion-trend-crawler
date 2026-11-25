// lib/nav.ts
// One source of truth for site navigation, used by the shared header and footer.
// The photocopy edition's seven sections (design/SITE_SPEC_photocopy.md §2).

export const PRIMARY_NAV = [
  { href: "/", label: "Latest" },
  { href: "/archive", label: "Back issues" },
  { href: "/signals", label: "Signals" },
  { href: "/ari3", label: "ARI3" },
  { href: "/methodology", label: "How it works" },
  { href: "/about", label: "About" },
  { href: "/search", label: "Search" },
] as const;

export const FOOTER_NAV = [
  { href: "/glossary", label: "Glossary" },
  { href: "/taxonomy", label: "Taxonomy" },
  { href: "/sources", label: "Sources" },
  { href: "/timeline", label: "Timeline" },
  { href: "/case-study", label: "Case study" },
  { href: "/accessibility", label: "Accessibility" },
  { href: "/privacy", label: "Privacy" },
  { href: "/terms", label: "Terms" },
  { href: "/rss.xml", label: "RSS" },
  { href: "/llms.txt", label: "For AI agents" },
  { href: "/data/reports/index.json", label: "Data (JSON)" },
  { href: "https://github.com/arikthehacker/fashion-trend-crawler/blob/master/CONTRIBUTING.md", label: "How to contribute" },
] as const;

export const CONTACT_EMAIL = "ariella@duck.com";
export const ISSUES_URL = "https://github.com/arikthehacker/fashion-trend-crawler/issues";
export const REPO_URL = "https://github.com/arikthehacker/fashion-trend-crawler";
export const CONTRIBUTING_URL = `${REPO_URL}/blob/master/CONTRIBUTING.md`;
