import { searchIndex } from "../../../lib/machine";

// /data/search.json: the compact index the search page loads.
export const dynamic = "force-static";

export function GET() {
  return Response.json(searchIndex());
}
