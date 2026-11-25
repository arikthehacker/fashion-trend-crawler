import { getAllReportDates, getReportByDate } from "../../../lib/reports";
import { headline, longWindow, ranked, items, n } from "../../../lib/editorial";
import { shareCard, OG_SIZE } from "../../../lib/og";

// One share card per weekly report: the week, its headline and its three largest signals.
export const dynamic = "force-static";
export const dynamicParams = false;
export const alt = "ARI3LLA INDEX weekly report";
export const size = OG_SIZE;
export const contentType = "image/png";

export function generateStaticParams() {
  const dates = getAllReportDates();
  return dates.length ? dates.map((date) => ({ date })) : [{ date: "none" }];
}

export default async function Image({ params }: { params: Promise<{ date: string }> }) {
  const { date } = await params;
  const r = getReportByDate(date);
  if (!r) return shareCard({ kicker: "Weekly report", title: "Report not found", foot: "ARI3LLA INDEX" });
  const top = ranked(r).slice(0, 3).map((s) => `${s.name}: ${items(s).length} articles`);
  return shareCard({
    kicker: `Week of ${longWindow(r)}`,
    title: headline(r),
    lines: [top.join("   ·   "), `${n(r.items_collected)} items from ${r.sources_scanned} sources, ${r.top_signals.length} signals kept`],
    foot: "THE FULL REPORT",
  });
}
