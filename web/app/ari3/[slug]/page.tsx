import Link from "next/link";
import { notFound } from "next/navigation";
import { pageMetadata } from "../../../lib/site";
import { EXPERIMENTS } from "../../../lib/ari3";
import { Page, Section, List, Pill, Flow, Bars, Callout, Code, bodyText, mono } from "../ui";

export const dynamicParams = false;

export function generateStaticParams() {
  return EXPERIMENTS.map((e) => ({ slug: e.slug }));
}

export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const e = EXPERIMENTS.find((x) => x.slug === slug);
  if (!e) return {};
  return pageMetadata(`/ari3/${e.slug}`, `${e.id} ${e.name}`, `ARI3 ${e.version} ${e.name}: ${e.headline}`);
}

const cell = { padding: "0.55rem 0.75rem 0.55rem 0", borderBottom: "1px solid var(--border)", verticalAlign: "top" as const, fontFamily: "var(--font-franklin)", fontSize: "0.88rem", lineHeight: 1.5 };

export default async function ExperimentPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const e = EXPERIMENTS.find((x) => x.slug === slug);
  if (!e) notFound();

  return (
    <Page title={e.id}>
      <p style={{ ...bodyText, margin: 0 }}>
        <Link href="/ari3" style={{ color: "var(--black)" }}>ARI3 research notebook</Link> · ARI3 Perception {e.version}
      </p>
      <div style={{ display: "flex", flexWrap: "wrap", gap: "0.6rem 1rem", alignItems: "baseline", marginTop: "1rem" }}>
        <h2 style={{ fontFamily: "var(--font-instrument)", fontSize: "3rem", fontWeight: 400, margin: 0, lineHeight: 1 }}>{e.name}</h2>
        <Pill>{e.status}</Pill>
        {e.hypotheses && <Pill tone="gray">Pre-registered</Pill>}
      </div>
      <p style={{ fontFamily: "var(--font-franklin)", fontStyle: "italic", color: "var(--gray)", margin: "0.4rem 0 1.2rem" }}>{e.motto}</p>

      <Callout title="Headline">
        <p style={{ fontFamily: "var(--font-instrument)", fontSize: "1.5rem", lineHeight: 1.3, margin: 0 }}>{e.headline}</p>
      </Callout>

      <Section title="Summary">
        {e.summary.map((p, i) => <p key={i} style={bodyText}>{p}</p>)}
      </Section>

      <Section title="Metadata">
        <dl style={{ display: "grid", gridTemplateColumns: "max-content minmax(0, 1fr)", gap: "0.45rem 1rem", margin: 0, fontSize: "0.82rem" }}>
          {e.meta.map((m) => (
            <div key={m.label} style={{ display: "contents" }}>
              <dt style={{ color: "var(--gray)", fontFamily: "var(--font-franklin)" }}>{m.label}</dt>
              <dd style={{ margin: 0, fontFamily: m.mono ? mono : "var(--font-franklin)", overflowWrap: "anywhere" }}>
                {m.href ? <a href={m.href} style={{ color: "var(--black)" }}>{m.value}</a> : m.value}
              </dd>
            </div>
          ))}
        </dl>
      </Section>

      <Section title="Research question">
        <p style={{ ...bodyText, color: "var(--black)", fontSize: "1.05rem" }}>{e.question}</p>
        <p style={bodyText}>Pre-registered: {e.preregistered}</p>
      </Section>

      {e.hypotheses && (
        <Section title="Hypotheses and results">
          <div style={{ overflowX: "auto" }}>
            <table style={{ width: "100%", borderCollapse: "collapse" }}>
              <thead>
                <tr>
                  {["", "Claim", "Supported if", "Result", "Verdict"].map((h) => (
                    <th key={h} scope="col" style={{ ...cell, textAlign: "left", color: "var(--gray)", fontWeight: 500, fontSize: "0.75rem" }}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {e.hypotheses.map((h) => (
                  <tr key={h.id}>
                    <th scope="row" style={{ ...cell, fontFamily: mono, textAlign: "left" }}>{h.id}</th>
                    <td style={cell}>{h.claim}</td>
                    <td style={{ ...cell, color: "var(--gray)" }}>{h.test}</td>
                    <td style={{ ...cell, fontFamily: mono, fontSize: "0.8rem" }}>{h.result}</td>
                    <td style={{ ...cell, fontFamily: mono, fontSize: "0.75rem", textTransform: "uppercase" }}>{h.verdict}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Section>
      )}

      {e.why && (
        <Section title="Why these hypotheses">
          {e.why.map((p, i) => <p key={i} style={bodyText}>{p}</p>)}
        </Section>
      )}

      <Section title="Method">
        <Flow steps={e.method} />
      </Section>

      <Section title="Experimental controls">
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(min(100%, 260px), 1fr))", gap: "1.2rem" }}>
          <div>
            <h3 style={{ fontFamily: "var(--font-franklin)", fontSize: "0.85rem", margin: "0 0 0.5rem" }}>Held constant</h3>
            <List items={e.held} />
          </div>
          <div>
            <h3 style={{ fontFamily: "var(--font-franklin)", fontSize: "0.85rem", margin: "0 0 0.5rem" }}>Changed</h3>
            <List items={e.changed} />
          </div>
        </div>
      </Section>

      <Section title="Results">
        <p style={bodyText}>
          {e.compare
            ? `${e.compare.a} and ${e.compare.b} scored on the same ${e.compare.n} held-out items.`
            : "Scored on held-out items the model never trained on."}
        </p>
        <Bars metrics={e.metrics} a={e.compare?.a} b={e.compare?.b ?? e.version} />
      </Section>

      <Section title="Cost of improvement">
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(min(100%, 260px), 1fr))", gap: "1.2rem" }}>
          <div>
            <h3 style={{ fontFamily: "var(--font-franklin)", fontSize: "0.85rem", margin: "0 0 0.5rem" }}>Gained</h3>
            <List items={e.benefits} />
          </div>
          <div>
            <h3 style={{ fontFamily: "var(--font-franklin)", fontSize: "0.85rem", margin: "0 0 0.5rem" }}>Cost</h3>
            <List items={e.costs} />
          </div>
        </div>
      </Section>

      <Section title="Surprising findings">
        {e.surprises.map((s, i) => (
          <Callout key={i} title={`Finding ${i + 1}`}>
            <p style={{ ...bodyText, color: "var(--black)", margin: 0 }}>{s}</p>
          </Callout>
        ))}
      </Section>

      <Section title="Threats to validity">
        <List items={e.threats} />
      </Section>

      <Section title="Engineering changes">
        <List items={e.engineering} />
      </Section>

      <Section title="Research log">
        <ol style={{ listStyle: "none", margin: 0, padding: 0 }}>
          {e.log.map((l, i) => (
            <li key={l.step}>
              <div style={{ display: "grid", gridTemplateColumns: "7.5rem minmax(0, 1fr)", gap: "0.8rem" }}>
                <span style={{ fontFamily: mono, fontSize: "0.75rem", textTransform: "uppercase", color: "var(--gray)", paddingTop: "0.2rem" }}>{l.step}</span>
                <span style={{ ...bodyText, color: "var(--black)", margin: 0 }}>{l.text}</span>
              </div>
              {i < e.log.length - 1 && <div aria-hidden="true" style={{ color: "var(--gray)", paddingLeft: "2.5rem" }}>↓</div>}
            </li>
          ))}
        </ol>
      </Section>

      <Section title="Lessons">
        <List items={e.lessons} />
      </Section>

      <Section title="Open questions">
        <ol style={{ margin: 0, paddingLeft: "1.3rem" }}>
          {e.openQuestions.map((q, i) => <li key={i} style={{ ...bodyText, margin: "0 0 0.45rem" }}>{q}</li>)}
        </ol>
      </Section>

      <Section title="Reproducibility">
        <p style={bodyText}>{e.reproduce.text}</p>
        <Code>{e.reproduce.commands}</Code>
      </Section>
    </Page>
  );
}
