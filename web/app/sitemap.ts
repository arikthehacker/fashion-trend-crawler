// app/sitemap.ts
// Next.js App Router sitemap convention — generates /sitemap.xml at build time.
// Lists static pages plus all dated report routes and signal-history routes.

import type { MetadataRoute } from "next";
import { SITE_URL } from "../lib/site";
import { getAllReportDates, getAllSignalSlugs, getLatestReport } from "../lib/reports";

export const dynamic = "force-static";

export default function sitemap(): MetadataRoute.Sitemap {
  // Google ignores changeFrequency/priority as of 2025+ (confirmed via Search Central
  // docs) — the only field that actually affects crawl behavior is lastModified, and
  // only when it's accurate. changeFrequency/priority are kept below as harmless,
  // roughly-honest hints for other crawlers/tools that do read them, but real accuracy
  // effort goes into lastModified instead of tuning those numbers.
  //
  // Pages whose content depends on the report archive (homepage, archive, timeline,
  // search, glossary, signals) genuinely change every time a new report ships, so they
  // get the latest report's date as lastModified. Pages with fixed prose (methodology,
  // taxonomy, sources, about, case-study) have no reliable last-edit timestamp available
  // at build time, so they're left without lastModified rather than guessing one.
  const latestReportDate = getLatestReport()?.report_date;

  const archiveDependentRoutes = new Set([
    "",
    "/archive",
    "/timeline",
    "/search",
    "/glossary",
  ]);

  const staticRoutes: MetadataRoute.Sitemap = [
    "",
    "/archive",
    "/methodology",
    "/ari3",
    "/ari3/philosophy",
    "/ari3/models",
    "/ari3/data",
    "/ari3/decisions",
    "/ari3/timeline",
    "/ari3/exp-001",
    "/ari3/exp-002",
    "/taxonomy",
    "/sources",
    "/about",
    "/case-study",
    "/timeline",
    "/glossary",
    "/search",
    "/privacy",
    "/terms",
    "/accessibility",
  ].map((route) => ({
    url: `${SITE_URL}${route}`,
    ...(archiveDependentRoutes.has(route) && latestReportDate
      ? { lastModified: latestReportDate }
      : {}),
    changeFrequency: archiveDependentRoutes.has(route) ? "weekly" : "monthly",
    priority: route === "" ? 1 : 0.6,
  }));

  const reportRoutes: MetadataRoute.Sitemap = getAllReportDates().map((date) => ({
    url: `${SITE_URL}/reports/${date}`,
    lastModified: date,
    // A dated report is a fixed archival snapshot — it does not get revised after
    // publication (see docs/agent-logs/sitemap-robots-jsonld.md), so "yearly" is the
    // honest floor rather than a real recurrence estimate.
    changeFrequency: "yearly",
    priority: 0.8,
  }));

  const signalRoutes: MetadataRoute.Sitemap = getAllSignalSlugs().map((slug) => ({
    url: `${SITE_URL}/signals/${slug}`,
    // A signal page's content changes whenever any report re-mentions that signal,
    // which in practice tracks the latest report date rather than a per-slug timestamp
    // (per-signal last-seen dates aren't exposed by getAllSignalSlugs()).
    ...(latestReportDate ? { lastModified: latestReportDate } : {}),
    changeFrequency: "weekly",
    priority: 0.5,
  }));

  return [...staticRoutes, ...reportRoutes, ...signalRoutes];
}
