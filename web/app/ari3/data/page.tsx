import { pageMetadata } from "../../../lib/site";
import { DATASETS } from "../../../lib/ari3_cards";
import { Page, Section, bodyText } from "../ui";

export const metadata = pageMetadata(
  "/ari3/data",
  "ARI3 dataset cards",
  "Dataset cards for the ARI3 item corpus and the editor's style labels: sources, collection, labeling, biases, access and versions."
);

export default function Data() {
  return (
    <Page title="Dataset cards">
      <p style={{ ...bodyText, fontSize: "1.05rem", color: "var(--black)", marginTop: "1rem" }}>
        ARI3 learns from two datasets: the items it collects, and the editor&apos;s labels on a sample
        of them. Counts are dated because the corpus grows every 4 hours.
      </p>
      {DATASETS.map((d) => (
        <Section key={d.name} title={d.name}>
          <p style={{ ...bodyText, fontFamily: "ui-monospace, Menlo, Consolas, monospace", fontSize: "0.8rem" }}>{d.version}</p>
          <dl style={{ display: "grid", gridTemplateColumns: "max-content minmax(0, 1fr)", gap: "0.6rem 1rem", margin: 0 }}>
            {d.rows.map((r) => (
              <div key={r.k} style={{ display: "contents" }}>
                <dt style={{ color: "var(--gray)", fontFamily: "var(--font-franklin)", fontSize: "0.82rem" }}>{r.k}</dt>
                <dd style={{ margin: 0, fontFamily: "var(--font-franklin)", fontSize: "0.9rem", lineHeight: 1.55 }}>{r.v}</dd>
              </div>
            ))}
          </dl>
        </Section>
      ))}
    </Page>
  );
}
