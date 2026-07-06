// app/sitemap.ts
// Next.js App Router sitemap convention — generates /sitemap.xml at build time.
// Lists static pages plus all dated report routes and signal-history routes.

import type { MetadataRoute } from "next";
import { SITE_URL } from "../lib/site";
import { getAllReportDates, getAllSignalSlugs } from "../lib/reports";

export default function sitemap(): MetadataRoute.Sitemap {
  const staticRoutes: MetadataRoute.Sitemap = [
    "",
    "/archive",
    "/methodology",
    "/taxonomy",
    "/sources",
    "/about",
    "/case-study",
    "/timeline",
  ].map((route) => ({
    url: `${SITE_URL}${route}`,
    changeFrequency: route === "" || route === "/archive" || route === "/timeline"
      ? "weekly"
      : "monthly",
    priority: route === "" ? 1 : 0.6,
  }));

  const reportRoutes: MetadataRoute.Sitemap = getAllReportDates().map((date) => ({
    url: `${SITE_URL}/reports/${date}`,
    lastModified: date,
    changeFrequency: "yearly",
    priority: 0.8,
  }));

  const signalRoutes: MetadataRoute.Sitemap = getAllSignalSlugs().map((slug) => ({
    url: `${SITE_URL}/signals/${slug}`,
    changeFrequency: "weekly",
    priority: 0.5,
  }));

  return [...staticRoutes, ...reportRoutes, ...signalRoutes];
}
