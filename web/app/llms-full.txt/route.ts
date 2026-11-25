import { llmsFullTxt } from "../../lib/machine";

// /llms-full.txt: the latest report as plain text, for agents that read one file.
export const dynamic = "force-static";

export function GET() {
  return new Response(llmsFullTxt(), { headers: { "Content-Type": "text/plain; charset=utf-8" } });
}
