import Link from "next/link";
import { pageMetadata } from "../../../lib/site";
import { ARCHITECTURE, MODEL_CARDS } from "../../../lib/ari3_cards";
import { Page, Section, List, Pill, bodyText, mono } from "../ui";

export const metadata = pageMetadata(
  "/ari3/models",
  "ARI3 model cards",
  "Model cards for every ARI3 version: purpose, inputs, outputs, training data, metrics, limitations and failure modes."
);

const dt = { color: "var(--gray)", fontFamily: "var(--font-franklin)", fontSize: "0.82rem" };
const dd = { margin: 0, fontFamily: "var(--font-franklin)", fontSize: "0.9rem", lineHeight: 1.55 };

export default function Models() {
  return (
    <Page title="Model cards">
      <p style={{ ...bodyText, margin: 0 }}>
        <Link href="/ari3" style={{ color: "var(--black)" }}>ARI3 research notebook</Link>
      </p>
      <p style={{ ...bodyText, fontSize: "1.05rem", color: "var(--black)", marginTop: "1rem" }}>
        One card per ARI3 version. Every version so far is ARI3 Perception, which decides whether a
        news item is about style. The full experiment behind each version is in its notebook entry.
      </p>

      <Section title="Shared architecture">
        <table style={{ width: "100%", borderCollapse: "collapse" }}>
          <tbody>
            {ARCHITECTURE.map((a) => (
              <tr key={a.part}>
                <th scope="row" style={{ textAlign: "left", padding: "0.5rem 0.8rem 0.5rem 0", borderBottom: "1px solid var(--border)", fontFamily: "var(--font-franklin)", fontSize: "0.88rem", verticalAlign: "top", whiteSpace: "nowrap" }}>{a.part}</th>
                <td style={{ padding: "0.5rem 0", borderBottom: "1px solid var(--border)", fontFamily: "var(--font-franklin)", fontSize: "0.88rem", lineHeight: 1.5 }}>
                  {a.value}
                  {a.source && <div style={{ color: "var(--gray)", fontSize: "0.8rem" }}>{a.source}</div>}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </Section>

      {MODEL_CARDS.map((m) => (
        <Section key={m.version} title={`${m.name} ${m.version}`} id={m.version.replace(/\./g, "-")}>
          <div style={{ display: "flex", gap: "0.6rem", flexWrap: "wrap", marginBottom: "1rem" }}>
            <Pill tone={m.status === "Current" ? "ink" : "gray"}>{m.status}</Pill>
            <Link href={`/ari3/${m.exp}`} style={{ fontFamily: "var(--font-franklin)", fontSize: "0.85rem", color: "var(--black)" }}>Notebook entry</Link>
          </div>
          <dl style={{ display: "grid", gridTemplateColumns: "max-content minmax(0, 1fr)", gap: "0.6rem 1rem", margin: 0 }}>
            <dt style={dt}>Purpose</dt><dd style={dd}>{m.purpose}</dd>
            <dt style={dt}>Inputs</dt><dd style={dd}>{m.inputs}</dd>
            <dt style={dt}>Outputs</dt><dd style={dd}>{m.outputs}</dd>
            <dt style={dt}>Training data</dt><dd style={dd}>{m.training}</dd>
            <dt style={dt}>Intended use</dt><dd style={dd}>{m.intendedUse}</dd>
            <dt style={dt}>Not for</dt><dd style={dd}>{m.notFor}</dd>
          </dl>
          <h3 style={{ fontFamily: "var(--font-franklin)", fontSize: "0.85rem", margin: "1.3rem 0 0.5rem" }}>Metrics</h3>
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <tbody>
              {m.metrics.map((x) => (
                <tr key={x.name}>
                  <th scope="row" style={{ textAlign: "left", fontWeight: 400, padding: "0.4rem 0.8rem 0.4rem 0", borderBottom: "1px solid var(--border)", fontFamily: "var(--font-franklin)", fontSize: "0.88rem" }}>{x.name}</th>
                  <td style={{ padding: "0.4rem 0", borderBottom: "1px solid var(--border)", fontFamily: mono, fontSize: "0.82rem", textAlign: "right" }}>{x.value}</td>
                </tr>
              ))}
            </tbody>
          </table>
          <h3 style={{ fontFamily: "var(--font-franklin)", fontSize: "0.85rem", margin: "1.3rem 0 0.5rem" }}>Known limitations</h3>
          <List items={m.limitations} />
          <h3 style={{ fontFamily: "var(--font-franklin)", fontSize: "0.85rem", margin: "1.3rem 0 0.5rem" }}>Failure modes</h3>
          <List items={m.failureModes} />
        </Section>
      ))}

      <Section title="Version history">
        <List items={MODEL_CARDS.map((m) => `${m.version} ${m.name}: ${m.status.toLowerCase()}.`)} />
      </Section>
    </Page>
  );
}
