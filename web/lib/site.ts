// lib/site.ts
// Shared site constants for metadata/sitemap/robots/JSON-LD generation.
// Override NEXT_PUBLIC_SITE_URL at deploy time once a production domain is set;
// falls back to a placeholder so builds/dev never break.

export const SITE_URL =
  process.env.NEXT_PUBLIC_SITE_URL || "https://ari3lla-index.example.com";

export const SITE_NAME = "ARI3LLA INDEX";
