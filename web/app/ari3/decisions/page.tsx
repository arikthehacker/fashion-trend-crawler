import Link from "next/link";
import { pageMetadata } from "../../../lib/site";
import { DECISIONS } from "../../../lib/ari3_cards";
import { Page, bodyText, mono } from "../ui";

export const metadata = pageMetadata(
  "/ari3/decisions",
  "ARI3 decision log",
  "The decisions that shape ARI3's data, models and evidence standard, each with its reason, alternatives and tradeoff."
);

const label = { color: "var(--gray)", fontFamily: "var(--font-franklin)", fontSize: "0.78rem", letterSpacing: "0.06em", textTransform: "uppercase" as const };

export default function Decisions() {
  return (
    <Page title="Decision log">
      <p style={{ ...bodyText, margin: 0 }}>
        <Link href="/ari3" style={{ color: "var(--black)" }}>ARI3 research notebook</Link>
      </p>
      <p style={{ ...bodyText, fontSize: "1.05rem", color: "var(--black)", marginTop: "1rem" }}>
        Decisions that shape what ARI3 collects, learns from and claims, newest first. A decision is
        replaced by a new entry, never edited.
      </p>
      <ol style={{ listStyle: "none", margin: "1.5rem 0 0", padding: 0 }}>
        {DECISIONS.map((d) => (
          <li key={d.id} style={{ borderTop: "1px solid var(--border)", padding: "1.3rem 0" }}>
            <div style={{ display: "flex", flexWrap: "wrap", gap: "0.4rem 0.9rem", alignItems: "baseline" }}>
              <span style={{ fontFamily: mono, fontSize: "0.8rem" }}>{d.id}</span>
              <span style={{ fontFamily: mono, fontSize: "0.8rem", color: "var(--gray)" }}>{d.date}</span>
            </div>
            <h2 style={{ fontFamily: "var(--font-instrument)", fontSize: "1.55rem", fontWeight: 400, margin: "0.3rem 0 0.8rem" }}>{d.title}</h2>
            <dl style={{ display: "grid", gridTemplateColumns: "max-content minmax(0, 1fr)", gap: "0.5rem 1rem", margin: 0 }}>
              {([["Decision", d.decision], ["Why", d.why], ["Alternatives", d.alternatives], ["Tradeoff", d.tradeoff]] as const).map(([k, v]) => (
                <div key={k} style={{ display: "contents" }}>
                  <dt style={label}>{k}</dt>
                  <dd style={{ margin: 0, fontFamily: "var(--font-franklin)", fontSize: "0.9rem", lineHeight: 1.55 }}>{v}</dd>
                </div>
              ))}
            </dl>
            {d.exp && (
              <p style={{ ...bodyText, fontSize: "0.85rem", margin: "0.7rem 0 0" }}>
                See <Link href={`/ari3/${d.exp}`} style={{ color: "var(--black)" }}>{d.exp.toUpperCase()}</Link>.
              </p>
            )}
          </li>
        ))}
      </ol>
    </Page>
  );
}
