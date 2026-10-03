// lib/claims.ts
// Reads the repository's claim ledger (../CLAIM_LEDGER.md) at build time, so the
// public claims page shows the ledger's own wording. Only the IDs listed in
// public_claims.json are published. Any other claim, including one added to the
// ledger later, stays off the site until it is added to that list.

import fs from "fs";
import path from "path";
import publicClaims from "./public_claims.json";
import { parseLedger } from "./claims_parse.mjs";

export type Claim = {
  id: string;
  claim: string;
  status: string;
  asOf: string;
  experiment: string;
  artifact: string;
  result: string;
  firstCommit: string;
  limitations: string;
  supersededBy: string;
};

export function getClaims(): Claim[] {
  const file = path.join(process.cwd(), "..", "CLAIM_LEDGER.md");
  const { claims, missing } = parseLedger(fs.readFileSync(file, "utf-8"), publicClaims.public_claim_ids);
  if (missing.length) {
    throw new Error(`public claims missing from CLAIM_LEDGER.md: ${missing.join(", ")}`);
  }
  return claims as Claim[];
}

export const STATUS_LABEL: Record<string, string> = {
  measured: "Measured",
  supported: "Supported",
  not_supported: "Not supported",
  superseded: "Superseded",
  historical: "Historical",
};
