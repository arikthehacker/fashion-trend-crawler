import { getAllReportDates, getReportByDate } from "../../../../lib/reports";
import { reportMarkdown } from "../../../../lib/machine";

// /md/reports/<date>.md: the report as clean Markdown, for agents and readers who want text only.
export const dynamic = "force-static";
export const dynamicParams = false;

export function generateStaticParams() {
  const dates = getAllReportDates();
  return (dates.length ? dates : ["none"]).map((d) => ({ file: `${d}.md` }));
}

export async function GET(_req: Request, { params }: { params: Promise<{ file: string }> }) {
  const { file } = await params;
  const r = getReportByDate(file.replace(/\.md$/, ""));
  if (!r) return new Response("Not found", { status: 404 });
  return new Response(reportMarkdown(r), { headers: { "Content-Type": "text/markdown; charset=utf-8" } });
}
