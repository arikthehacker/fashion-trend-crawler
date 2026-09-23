// lib/site.ts
// Shared site constants for metadata/sitemap/robots/JSON-LD generation.
// NEXT_PUBLIC_SITE_URL can override the production domain at deploy time.

export const SITE_URL =
  process.env.NEXT_PUBLIC_SITE_URL || "https://ari3lla.com";

export const SITE_NAME = "ARI3LLA INDEX";

