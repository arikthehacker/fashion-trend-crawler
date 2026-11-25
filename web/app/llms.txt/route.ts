import { llmsTxt } from "../../lib/machine";

// /llms.txt: what the index is, how to cite it, and where its data lives (llmstxt.org).
export const dynamic = "force-static";

export function GET() {
  return new Response(llmsTxt(), { headers: { "Content-Type": "text/plain; charset=utf-8" } });
}
