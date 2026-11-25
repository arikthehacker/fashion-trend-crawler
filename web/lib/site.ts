// lib/site.ts
// Shared site constants for metadata, sitemap, robots, JSON-LD and the agent files.
// NEXT_PUBLIC_SITE_URL can override the production domain at deploy time.
// www is canonical: the apex ari3lla.com redirects there (checked 2026-09-22).

export const SITE_URL = process.env.NEXT_PUBLIC_SITE_URL || "https://www.ari3lla.com";

export const SITE_NAME = "ARI3LLA INDEX";

export const SITE_DESCRIPTION =
  "A public, source-linked archive of style language: what fashion coverage is naming each week, where, and from which kinds of outlets.";

// The byline and the editor's-note label. The editor chose not to publish her name (2026-11-25).
export const EDITOR_LABEL = "Editor";

export const LLMS_TXT = "/llms.txt";

// Built from app/opengraph-image.tsx; repeated here because a page that sets
// its own openGraph replaces the inherited image.
export const OG_IMAGE = { url: "/opengraph-image", width: 1200, height: 630, alt: "ARI3LLA INDEX: a weekly, source-linked record of style language" };

type Img = { url: string; width: number; height: number; alt: string };

// Per-page metadata in one shape: the title (the layout template appends
// " | ARI3LLA INDEX"), description, canonical URL and share cards.
export function pageMetadata(
  path: string,
  title: string,
  description: string,
  opts: { type?: "website" | "article"; image?: Img; publishedTime?: string; noindex?: boolean } = {},
) {
  const url = `${SITE_URL}${path === "/" ? "" : path}`;
  const image = opts.image ?? OG_IMAGE;
  return {
    title,
    description,
    alternates: { canonical: url },
    openGraph: {
      siteName: SITE_NAME,
      title: `${title} | ${SITE_NAME}`,
      description,
      url,
      type: opts.type ?? ("website" as const),
      locale: "en_US",
      images: [image],
      ...(opts.publishedTime ? { publishedTime: opts.publishedTime } : {}),
    },
    twitter: { card: "summary_large_image" as const, title: `${title} | ${SITE_NAME}`, description, images: [image.url] },
    ...(opts.noindex ? { robots: { index: false, follow: true } } : {}),
  };
}
