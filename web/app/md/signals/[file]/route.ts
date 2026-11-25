import { allSignalSlugs, signalMarkdown } from "../../../../lib/machine";

// /md/signals/<signal_id>.md: a signal, week by week, as clean Markdown.
export const dynamic = "force-static";
export const dynamicParams = false;

export function generateStaticParams() {
  const slugs = allSignalSlugs();
  return (slugs.length ? slugs : ["none"]).map((s) => ({ file: `${s}.md` }));
}

export async function GET(_req: Request, { params }: { params: Promise<{ file: string }> }) {
  const { file } = await params;
  const body = signalMarkdown(file.replace(/\.md$/, ""));
  if (!body) return new Response("Not found", { status: 404 });
  return new Response(body, { headers: { "Content-Type": "text/markdown; charset=utf-8" } });
}
