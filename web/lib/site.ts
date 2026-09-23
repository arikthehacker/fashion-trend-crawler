// lib/site.ts
// Shared site constants for metadata/sitemap/robots/JSON-LD generation.
// NEXT_PUBLIC_SITE_URL can override the production domain at deploy time.
// www is canonical: the apex ari3lla.com redirects there (checked 2026-09-22).

export const SITE_URL =
  process.env.NEXT_PUBLIC_SITE_URL || "https://www.ari3lla.com";

export const SITE_NAME = "ARI3LLA INDEX";


// Built from app/opengraph-image.tsx; repeated here because a page that sets
// its own openGraph replaces the inherited image.
export const OG_IMAGE = { url: "/opengraph-image", width: 1200, height: 630, alt: "ARI3LLA INDEX" };

// Per-page metadata in one shape: the title (the layout template appends
// " | ARI3LLA INDEX"), description, canonical URL and share cards.
export function pageMetadata(path: string, title: string, description: string) {
  const url = `${SITE_URL}${path}`;
  return {
    title,
    description,
    alternates: { canonical: url },
    openGraph: { siteName: SITE_NAME, title: `${title} | ${SITE_NAME}`, description, url, type: "website" as const, images: [OG_IMAGE] },
    twitter: { card: "summary_large_image" as const, title: `${title} | ${SITE_NAME}`, description, images: [OG_IMAGE.url] },
  };
}
