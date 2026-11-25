import { signalHistory, allSignalSlugs } from "../../../../lib/machine";

// /data/signals/<signal_id>.json: one signal, week by week, with every article.
export const dynamic = "force-static";
export const dynamicParams = false;

export function generateStaticParams() {
  const slugs = allSignalSlugs();
  return (slugs.length ? slugs : ["none"]).map((s) => ({ file: `${s}.json` }));
}

export async function GET(_req: Request, { params }: { params: Promise<{ file: string }> }) {
  const { file } = await params;
  const body = signalHistory(file.replace(/\.json$/, ""));
  return body ? Response.json(body) : new Response("Not found", { status: 404 });
}
