import Link from "next/link";
import { pageMetadata } from "../../../lib/site";
import { PRINCIPLES } from "../../../lib/ari3";
import { Page, bodyText } from "../ui";

export const metadata = pageMetadata(
  "/ari3/philosophy",
  "ARI3 research philosophy",
  "The principles ARI3 is built and tested by: version everything, measure everything, never hide failures, pre-register experiments."
);

export default function Philosophy() {
  return (
    <Page title="Research philosophy">
      <p style={{ ...bodyText, margin: 0 }}>
        <Link href="/ari3" style={{ color: "var(--black)" }}>ARI3 research notebook</Link>
      </p>
      <p style={{ ...bodyText, fontSize: "1.05rem", color: "var(--black)", marginTop: "1rem" }}>
        These principles decide how ARI3 is built, tested and reported. Each experiment in the
        notebook can be checked against them.
      </p>
      <ol style={{ listStyle: "none", margin: "2rem 0 0", padding: 0 }}>
        {PRINCIPLES.map((p, i) => (
          <li key={p.title} style={{ borderTop: "1px solid var(--border)", padding: "1.2rem 0", display: "grid", gridTemplateColumns: "2.5rem minmax(0, 1fr)", gap: "0.8rem" }}>
            <span style={{ fontFamily: "var(--font-instrument)", fontSize: "1.6rem", color: "var(--gray)", lineHeight: 1 }}>{i + 1}</span>
            <div>
              <h2 style={{ fontFamily: "var(--font-instrument)", fontSize: "1.5rem", fontWeight: 400, margin: "0 0 0.4rem" }}>{p.title}</h2>
              <p style={{ ...bodyText, margin: 0 }}>{p.body}</p>
            </div>
          </li>
        ))}
      </ol>
    </Page>
  );
}
