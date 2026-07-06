// app/rss.xml/route.ts
// RSS 2.0 feed over the report archive, so readers can subscribe instead of
// checking the archive page manually. Reads the same data layer as the
// archive/report pages (lib/reports.ts) — no separate data source.

import { getAllReports } from "../../lib/reports";
import { SITE_URL, SITE_NAME } from "../../lib/site";

export const dynamic = "force-static";

function escapeXml(value: string): string {
  return value
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&apos;");
}

function toRfc822(dateStr: string): string {
  const date = new Date(`${dateStr}T00:00:00Z`);
  return date.toUTCString();
}

export async function GET() {
  const reports = getAllReports(); // newest first

  const items = reports
    .map((report) => {
      const url = `${SITE_URL}/reports/${report.report_date}`;
      const description = report.executive_summary?.trim() ?? "";
      // Mirror the report-page JSON-LD fix (run 36): if a report has been
      // corrected since publication, reflect that instead of always using
      // the original report_date, so subscribers see corrections surface.
      const lastRevision = report.revision_history?.length
        ? report.revision_history[report.revision_history.length - 1]
        : undefined;
      const lastUpdated = lastRevision?.corrected_at ?? report.report_date;
      return `    <item>
      <title>${escapeXml(report.report_date)}</title>
      <link>${escapeXml(url)}</link>
      <guid isPermaLink="true">${escapeXml(url)}</guid>
      <pubDate>${toRfc822(lastUpdated)}</pubDate>
      <description>${escapeXml(description)}</description>
    </item>`;
    })
    .join("\n");

  const lastBuildDate =
    reports.length > 0 ? toRfc822(reports[0].report_date) : new Date().toUTCString();

  const xml = `<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>${escapeXml(SITE_NAME)}</title>
    <link>${escapeXml(SITE_URL)}</link>
    <description>Weekly style signal reports: a source-linked index tracking recurring style language, silhouettes, materials, aesthetics, and cultural signals across the web.</description>
    <language>en-us</language>
    <lastBuildDate>${lastBuildDate}</lastBuildDate>
${items}
  </channel>
</rss>
`;

  return new Response(xml, {
    headers: {
      "Content-Type": "application/rss+xml; charset=utf-8",
    },
  });
}
