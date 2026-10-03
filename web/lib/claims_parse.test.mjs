// Run from web/: node --test lib/claims_parse.test.mjs
import { test } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import { parseLedger } from "./claims_parse.mjs";

const claim = (id) => `### ${id}
- **Claim:** Claim text for ${id}.
- **Status:** measured
- **As of:** 2026-10-02
- **Experiment:** EXP-000
- **Artifact:** \`file.json\`
- **Result:** 1.0
- **First valid commit:** \`abc1234\`
- **Limitations:** n = 1.
- **Used in:** not yet audited
- **Superseded by:** none
`;

const ledger = `# ledger\n\n## Claims\n\n${["C-0001", "C-0009", "C-0010", "C-0099"].map(claim).join("\n")}`;

test("only allowlisted claims render", () => {
  const { claims, missing } = parseLedger(ledger, ["C-0001", "C-0010"]);
  assert.deepEqual(claims.map((c) => c.id), ["C-0001", "C-0010"]);
  assert.deepEqual(missing, []);
});

test("an unapproved future claim and C-0009 never render", () => {
  const ids = parseLedger(ledger, ["C-0001", "C-0010"]).claims.map((c) => c.id);
  assert.ok(!ids.includes("C-0099"));
  assert.ok(!ids.includes("C-0009"));
});

test("an allowlisted ID absent from the ledger is reported", () => {
  assert.deepEqual(parseLedger(ledger, ["C-0001", "C-0042"]).missing, ["C-0042"]);
});

test("the committed allowlist is the owner-approved set", () => {
  const list = JSON.parse(fs.readFileSync(new URL("./public_claims.json", import.meta.url), "utf-8")).public_claim_ids;
  assert.deepEqual(list, ["C-0001", "C-0002", "C-0003", "C-0004", "C-0005", "C-0006", "C-0007", "C-0008",
    "C-0010", "C-0011", "C-0012", "C-0013"]);
});

test("the real ledger yields exactly the allowlisted claims", () => {
  const text = fs.readFileSync(new URL("../../CLAIM_LEDGER.md", import.meta.url), "utf-8");
  const list = JSON.parse(fs.readFileSync(new URL("./public_claims.json", import.meta.url), "utf-8")).public_claim_ids;
  const { claims, missing } = parseLedger(text, list);
  assert.deepEqual(claims.map((c) => c.id), list);
  assert.deepEqual(missing, []);
});
