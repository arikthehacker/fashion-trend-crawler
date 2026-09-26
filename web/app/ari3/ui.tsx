// Shared building blocks for the ARI3 research notebook pages.

import type { CSSProperties, ReactNode } from "react";
import type { Metric } from "../../lib/ari3";

export const mono = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace";

export const bodyText: CSSProperties = {
  fontFamily: "var(--font-franklin)",
  fontSize: "0.95rem",
  lineHeight: 1.7,
  color: "var(--gray)",
  margin: "0 0 0.8rem",
};

export function Page({ title, children }: { title: string; children: ReactNode }) {
  return (
    <main id="main-content" style={{ flex: 1, background: "var(--white)", display: "flex", flexDirection: "column", alignItems: "center" }}>
      <header className="page-masthead">
        <h1 className="page-title">{title}</h1>
      </header>
      <div style={{ width: "100%", maxWidth: "860px", padding: "3rem 1rem 5rem", minWidth: 0 }}>{children}</div>
    </main>
  );
}

export function Section({ title, id, children }: { title: string; id?: string; children: ReactNode }) {
  const hid = id ?? title.replace(/\W+/g, "-").toLowerCase();
  return (
    <section aria-labelledby={`h-${hid}`} style={{ borderTop: "1px solid var(--border)", paddingTop: "1.4rem", marginTop: "2.4rem" }}>
      <h2 id={`h-${hid}`} style={{ fontFamily: "var(--font-instrument)", fontSize: "1.7rem", fontWeight: 400, margin: "0 0 0.9rem" }}>
        {title}
      </h2>
      {children}
    </section>
  );
}

export function List({ items }: { items: string[] }) {
  return (
    <ul style={{ margin: 0, paddingLeft: "1.1rem" }}>
      {items.map((t, i) => (
        <li key={i} style={{ ...bodyText, margin: "0 0 0.45rem" }}>{t}</li>
      ))}
    </ul>
  );
}

export function Pill({ children, tone = "ink" }: { children: ReactNode; tone?: "ink" | "red" | "gray" }) {
  const color = tone === "red" ? "var(--red)" : tone === "gray" ? "var(--gray)" : "var(--black)";
  return (
    <span style={{ fontFamily: mono, fontSize: "0.7rem", letterSpacing: "0.08em", textTransform: "uppercase", padding: "0.18rem 0.5rem", border: `1px solid ${color}`, color, whiteSpace: "nowrap" }}>
      {children}
    </span>
  );
}

export function Flow({ steps }: { steps: string[] }) {
  return (
    <ol aria-label="Method, step by step" style={{ listStyle: "none", margin: 0, padding: 0 }}>
      {steps.map((s, i) => (
        <li key={i} style={{ textAlign: "center" }}>
          <div style={{ display: "inline-block", border: "1px solid var(--black)", padding: "0.55rem 0.9rem", fontFamily: "var(--font-franklin)", fontSize: "0.88rem", maxWidth: "100%" }}>
            {s}
          </div>
          {i < steps.length - 1 && <div aria-hidden="true" style={{ color: "var(--gray)", lineHeight: 1.6 }}>↓</div>}
        </li>
      ))}
    </ol>
  );
}

function fmt(v: number, f: Metric["format"]) {
  return f === "pct" ? `${(v * 100).toFixed(1)}%` : v.toFixed(3);
}

// Horizontal bars. Percentages are drawn on a 0–100% scale. Error metrics are
// drawn on a scale set by the largest value shown, and marked "lower is better".
export function Bars({ metrics, a, b }: { metrics: Metric[]; a?: string; b: string }) {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "1.2rem" }}>
      {metrics.map((m) => {
        const max = m.format === "pct" ? 1 : Math.max(m.b, m.a ?? 0) * 1.15;
        const rows: [string, number][] = m.a !== undefined && a ? [[a, m.a], [b, m.b]] : [[b, m.b]];
        return (
          <div key={m.name}>
            <div style={{ fontFamily: "var(--font-franklin)", fontSize: "0.85rem", marginBottom: "0.3rem" }}>
              {m.name}
              {m.lowerIsBetter && <span style={{ color: "var(--gray)" }}> · lower is better</span>}
            </div>
            {rows.map(([label, v], i) => (
              <div key={label} style={{ display: "grid", gridTemplateColumns: "4.2rem minmax(0, 1fr) 4.2rem", alignItems: "center", gap: "0.6rem", margin: "0.2rem 0" }}>
                <span style={{ fontFamily: mono, fontSize: "0.75rem", color: "var(--gray)" }}>{label}</span>
                <div style={{ height: "0.8rem", background: "var(--border)" }} role="img" aria-label={`${label} ${m.name} ${fmt(v, m.format)}`}>
                  <div style={{ width: `${Math.min(100, (v / max) * 100)}%`, height: "100%", background: i === rows.length - 1 ? "var(--black)" : "var(--gray)" }} />
                </div>
                <span style={{ fontFamily: mono, fontSize: "0.8rem", textAlign: "right" }}>{fmt(v, m.format)}</span>
              </div>
            ))}
            {m.note && <div style={{ fontFamily: "var(--font-franklin)", fontSize: "0.75rem", color: "var(--gray)", marginTop: "0.2rem" }}>{m.note}</div>}
          </div>
        );
      })}
    </div>
  );
}

export function Callout({ title, children }: { title: string; children: ReactNode }) {
  return (
    <aside style={{ border: "2px solid var(--black)", padding: "1rem 1.2rem", margin: "1rem 0" }}>
      <div style={{ fontFamily: "var(--font-franklin)", fontSize: "0.72rem", letterSpacing: "0.1em", textTransform: "uppercase", fontWeight: 600, marginBottom: "0.5rem" }}>
        {title}
      </div>
      {children}
    </aside>
  );
}

export function Code({ children }: { children: string }) {
  return (
    <pre style={{ fontFamily: mono, fontSize: "0.8rem", background: "var(--black)", color: "var(--white)", padding: "1rem", overflowX: "auto", margin: 0 }}>
      {children}
    </pre>
  );
}
