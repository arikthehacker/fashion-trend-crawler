import { Fragment } from "react";
import { pageMetadata } from "../../../lib/site";
import { REPO } from "../../../lib/ari3";
import { getClaims, STATUS_LABEL } from "../../../lib/claims";
import { Page, Pill, bodyText, mono } from "../ui";

export const metadata = pageMetadata(
  "/ari3/claims",
  "ARI3 claim ledger",
  "Every result ARI3 states about itself, with its status, sample, limitations and the committed artifact behind it."
);

const label = { color: "var(--gray)", fontFamily: "var(--font-franklin)", fontSize: "0.78rem" };
const value = { margin: 0, fontFamily: "var(--font-franklin)", fontSize: "0.9rem", lineHeight: 1.55, overflowWrap: "anywhere" as const };

// The ledger marks file names and hashes with backticks. Render those spans as code.
function Ticks({ text }: { text: string }) {
  return (
    <>
      {text.split("`").map((part, i) =>
        i % 2 ? <code key={i} style={{ fontFamily: mono, fontSize: "0.82em" }}>{part}</code> : <Fragment key={i}>{part}</Fragment>
      )}
    </>
  );
}

export default function Claims() {
  const claims = getClaims();
  return (
    <Page title="Claim ledger">
      <p style={{ ...bodyText, fontSize: "1.05rem", color: "var(--black)", marginTop: "1rem" }}>
        This page lists the claims approved for publication from ARI3&apos;s claim ledger, with the
        committed artifact that supports each one. A published claim is not silently rewritten or
        deleted. If its status changes, the later record preserves that change. Failed
        pre-registered hypotheses remain visible as not supported.
      </p>
      <p style={bodyText}>
        The repository ledger is the underlying record. This page publishes only claim IDs explicitly
        approved for the site. The ledger file is at{" "}
        <a href={`${REPO}/blob/master/CLAIM_LEDGER.md`} style={{ color: "var(--black)" }}>CLAIM_LEDGER.md</a>.
      </p>
      {claims.length === 0 && <p style={bodyText}>No claims are recorded.</p>}
      <ol style={{ listStyle: "none", margin: "1.5rem 0 0", padding: 0 }}>
        {claims.map((c) => (
          <li key={c.id} id={c.id.toLowerCase()} style={{ borderTop: "1px solid var(--black)", padding: "1.1rem 0 1.3rem" }}>
            <div style={{ display: "flex", flexWrap: "wrap", gap: "0.5rem 0.9rem", alignItems: "baseline" }}>
              <h2 style={{ fontFamily: mono, fontSize: "0.95rem", fontWeight: 600, margin: 0 }}>{c.id}</h2>
              <Pill tone={c.status === "not_supported" ? "red" : c.status === "superseded" || c.status === "historical" ? "gray" : "ink"}>
                {STATUS_LABEL[c.status] ?? c.status}
              </Pill>
              <span style={{ ...label, fontFamily: mono }}>{c.experiment} · as of {c.asOf}</span>
            </div>
            <p style={{ ...bodyText, color: "var(--black)", margin: "0.6rem 0 0.8rem" }}><Ticks text={c.claim} /></p>
            <dl style={{ display: "grid", gridTemplateColumns: "max-content minmax(0, 1fr)", gap: "0.45rem 1rem", margin: 0 }}>
              {([
                ["Result", c.result],
                ["Limitations", c.limitations],
                ["Artifact", c.artifact],
                ["First valid commit", c.firstCommit],
                ...(c.supersededBy && c.supersededBy !== "none" ? [["Superseded by", c.supersededBy]] : []),
              ] as [string, string][]).filter(([, v]) => v).map(([k, v]) => (
                <div key={k} style={{ display: "contents" }}>
                  <dt style={label}>{k}</dt>
                  <dd style={value}><Ticks text={v} /></dd>
                </div>
              ))}
            </dl>
          </li>
        ))}
      </ol>
    </Page>
  );
}
