// lib/claims_parse.mjs
// Parses CLAIM_LEDGER.md and keeps only the claim IDs on the public allowlist.
// Plain JavaScript so `node --test` can check it without a TypeScript toolchain.

const FIELDS = {
  "Claim": "claim",
  "Status": "status",
  "As of": "asOf",
  "Experiment": "experiment",
  "Artifact": "artifact",
  "Result": "result",
  "First valid commit": "firstCommit",
  "Limitations": "limitations",
  "Superseded by": "supersededBy",
};

/**
 * @param {string} ledgerText the contents of CLAIM_LEDGER.md
 * @param {string[]} allowIds claim IDs approved for publication
 * @returns {{claims: Record<string, string>[], missing: string[]}} allowlisted claims in
 *   ledger order, and allowlisted IDs the ledger does not contain
 */
export function parseLedger(ledgerText, allowIds) {
  const allow = new Set(allowIds);
  const text = ledgerText.replace(/\r\n/g, "\n");
  const claims = [];
  for (const block of text.split(/\n### /).slice(1)) {
    const [head, ...lines] = block.split("\n");
    const id = head.trim();
    if (!/^C-\d{4}$/.test(id) || !allow.has(id)) continue;
    const c = { id, claim: "", status: "", asOf: "", experiment: "", artifact: "", result: "", firstCommit: "", limitations: "", supersededBy: "" };
    for (const line of lines) {
      const m = line.match(/^- \*\*([^*]+):\*\* (.*)$/);
      if (m && FIELDS[m[1]]) c[FIELDS[m[1]]] = m[2].trim();
    }
    if (c.claim && c.status) claims.push(c);
  }
  const found = new Set(claims.map((c) => c.id));
  return { claims, missing: allowIds.filter((id) => !found.has(id)) };
}
