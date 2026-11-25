// app/robots.ts
// /robots.txt. Every crawler is allowed, and the AI crawlers are named so the
// choice is on record (design/SITE_SPEC_photocopy.md §8.4; the editor chose
// "allow all" on 2026-11-25 because the index exists to be cited).

import type { MetadataRoute } from "next";
import { SITE_URL } from "../lib/site";

export const dynamic = "force-static";

const AI_SEARCH = ["OAI-SearchBot", "ChatGPT-User", "Claude-User", "Claude-SearchBot", "PerplexityBot", "Perplexity-User"];
const AI_TRAINING = ["GPTBot", "ClaudeBot", "Google-Extended", "CCBot", "Applebot-Extended"];

export default function robots(): MetadataRoute.Robots {
  return {
    rules: [
      { userAgent: "*", allow: "/" },
      ...[...AI_SEARCH, ...AI_TRAINING].map((userAgent) => ({ userAgent, allow: "/" })),
    ],
    sitemap: `${SITE_URL}/sitemap.xml`,
    host: SITE_URL,
  };
}
