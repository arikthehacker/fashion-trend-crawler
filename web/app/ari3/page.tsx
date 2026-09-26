import Link from "next/link";
import { pageMetadata } from "../../lib/site";
import { EXPERIMENTS, PROJECT_STATE, RELEASE_NAMES, REPO } from "../../lib/ari3";
import { Page, Section, Pill, bodyText, mono } from "./ui";

export const metadata = pageMetadata(
  "/ari3",
  "ARI3 research notebook",
  "The research notebook for ARI3, the model system behind ARI3LLA INDEX: every experiment, its question, hypotheses, results and costs, frozen and hashed."
);

export default function Ari3Page() {
  return (
    <Page title="ARI3">
      <p style={{ ...bodyText, fontSize: "1.05rem", color: "var(--black)" }}>
        ARI3 is the model system behind ARI3LLA INDEX, run as a small research program. Each
        experiment is a permanent notebook entry with its question, hypotheses, method, results,
        costs and open questions. Every model version is frozen, hashed and committed to the public
        repository before its results appear here.
      </p>
      <p style={bodyText}>
        ARI3 v0.0.2, the current version, reads a news item&apos;s headline and feed excerpt,
        judges whether the item is about style, and says when it is not sure. No ARI3 version
        forecasts, ranks trends or writes reports. The principles behind the program are on
        the <Link href="/ari3/philosophy" style={{ color: "var(--black)" }}>research philosophy</Link> page.
      </p>

      <Section title="Experiment registry">
        <p style={bodyText}>Entries are permanent. A correction is added as a dated note, never by editing the result.</p>
        <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
          {EXPERIMENTS.map((e) => (
            <Link key={e.id} href={`/ari3/${e.slug}`} style={{ display: "block", border: "1px solid var(--black)", padding: "1.1rem 1.2rem", color: "var(--black)", textDecoration: "none" }}>
              <div style={{ display: "flex", flexWrap: "wrap", gap: "0.5rem 0.9rem", alignItems: "baseline" }}>
                <span style={{ fontFamily: mono, fontSize: "0.85rem" }}>{e.id}</span>
                <span style={{ fontFamily: "var(--font-instrument)", fontSize: "1.8rem", lineHeight: 1.1 }}>
                  {e.name} <span style={{ fontSize: "1.1rem", color: "var(--gray)" }}>{e.version}</span>
                </span>
                <Pill>{e.status}</Pill>
                {e.hypotheses && <Pill tone="gray">Pre-registered</Pill>}
              </div>
              <div style={{ fontFamily: "var(--font-franklin)", fontStyle: "italic", color: "var(--gray)", margin: "0.3rem 0 0.5rem" }}>{e.motto}</div>
              <div style={{ fontFamily: "var(--font-franklin)", fontSize: "0.95rem", lineHeight: 1.5 }}>{e.headline}</div>
              <div style={{ fontFamily: "var(--font-franklin)", fontSize: "0.8rem", color: "var(--gray)", marginTop: "0.6rem", textDecoration: "underline" }}>Read the notebook entry</div>
            </Link>
          ))}
        </div>
      </Section>

      <Section title="State of the project">
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(min(100%, 240px), 1fr))", gap: "1rem" }}>
          {PROJECT_STATE.map((g) => (
            <div key={g.status} style={{ border: "1px solid var(--border)", padding: "0.9rem 1rem" }}>
              <h3 style={{ fontFamily: "var(--font-franklin)", fontSize: "0.8rem", letterSpacing: "0.08em", textTransform: "uppercase", margin: "0 0 0.6rem" }}>
                <span aria-hidden="true">{g.mark} </span>{g.status}
              </h3>
              {g.items.map((it) => (
                <div key={it.area} style={{ margin: "0 0 0.6rem" }}>
                  <div style={{ fontFamily: "var(--font-franklin)", fontSize: "0.9rem", fontWeight: 600 }}>{it.area}</div>
                  <div style={{ fontFamily: "var(--font-franklin)", fontSize: "0.82rem", lineHeight: 1.5, color: "var(--gray)" }}>{it.detail}</div>
                </div>
              ))}
            </div>
          ))}
        </div>
      </Section>

      <Section title="Release names">
        <p style={bodyText}>Released versions link to their notebook entries. Planned names mark intent. None has a date.</p>
        <ol style={{ listStyle: "none", margin: 0, padding: 0 }}>
          {RELEASE_NAMES.map((r) => (
            <li key={r.version} style={{ display: "grid", gridTemplateColumns: "4rem minmax(0, 1fr) auto", gap: "0.8rem", alignItems: "baseline", padding: "0.6rem 0", borderBottom: "1px solid var(--border)" }}>
              <span style={{ fontFamily: mono, fontSize: "0.8rem", color: "var(--gray)" }}>{r.version}</span>
              <span>
                {r.exp ? (
                  <Link href={`/ari3/${r.exp}`} style={{ fontFamily: "var(--font-instrument)", fontSize: "1.35rem", color: "var(--black)" }}>{r.name}</Link>
                ) : (
                  <span style={{ fontFamily: "var(--font-instrument)", fontSize: "1.35rem", color: "var(--gray)" }}>{r.name}</span>
                )}
                <span style={{ fontFamily: "var(--font-franklin)", fontSize: "0.85rem", color: "var(--gray)" }}> · {r.motto}</span>
              </span>
              <Pill tone={r.status === "Released" ? "ink" : "gray"}>{r.status}</Pill>
            </li>
          ))}
        </ol>
      </Section>

      <Section title="Checking a release">
        <p style={bodyText}>
          Every entry lists its commit, whose time GitHub records, and the SHA-256 hash of each file. A file
          downloaded from the linked commit should produce the listed hash. The source is
          at <a href={REPO} style={{ color: "var(--black)" }}>github.com/arikthehacker/fashion-trend-crawler</a>.
        </p>
      </Section>
    </Page>
  );
}
