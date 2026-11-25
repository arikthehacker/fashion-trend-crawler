import { reportIndex } from "../../../../lib/machine";

// /data/reports/index.json: every report with its headline, counts and signals.
export const dynamic = "force-static";

export function GET() {
  return Response.json(reportIndex());
}
