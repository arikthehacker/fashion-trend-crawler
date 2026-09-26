import Link from "next/link";
import { pageMetadata } from "../../../lib/site";
import charts from "../../../lib/ari3_charts.json";
import { Page, Section, Callout, bodyText, mono } from "../ui";

export const metadata = pageMetadata(
  "/ari3/evaluation",
  "ARI3 evaluation charts",
  "Reliability diagrams, confusion matrices, confidence histograms, coverage curves and a learning curve for ARI3 v0.0.1 and v0.0.2."
);

type V = (typeof charts.versions)["ari3-v0.0.1"];
const VERSIONS: [string, string][] = [["ari3-v0.0.1", "v0.0.1 INDUSTRIA"], ["ari3-v0.0.2", "v0.0.2 DISCIPLINA"]];
const pct = (x: number) => `${Math.round(x * 100)}%`;
const small = { fontFamily: "var(--font-franklin)", fontSize: "0.8rem", color: "var(--gray)", lineHeight: 1.5 };
const twoUp = { display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(min(100%, 300px), 1fr))", gap: "1.5rem" };

function Reliability({ v, label }: { v: V; label: string }) {
  const S = 230, P = 44, T = 14;
  const x = (t: number) => P + t * S;
  const y = (t: number) => T + (1 - t) * S;
  const pts = v.reliability.filter((b) => b.n > 0 && b.mean_p !== null && b.observed !== null);
  return (
    <figure style={{ margin: 0 }}>
      <svg viewBox={`0 0 ${S + P + 26} ${S + T + 46}`} style={{ width: "100%", maxWidth: "340px", display: "block" }} role="img"
        aria-label={`${label} reliability: ${pts.map((b) => `predicted ${pct(b.mean_p as number)}, observed ${pct(b.observed as number)}, ${b.n} items`).join("; ")}`}>
        <line x1={x(0)} y1={y(0)} x2={x(1)} y2={y(1)} stroke="var(--gray)" strokeDasharray="4 4" />
        <line x1={x(0)} y1={y(0)} x2={x(1)} y2={y(0)} stroke="var(--black)" />
        <line x1={x(0)} y1={y(0)} x2={x(0)} y2={y(1)} stroke="var(--black)" />
        {[0, 0.5, 1].map((t) => (
          <g key={t}>
            <text x={x(t)} y={y(0) + 16} fontSize="12" textAnchor="middle" fill="var(--gray)">{pct(t)}</text>
            <text x={x(0) - 6} y={y(t) + 4} fontSize="12" textAnchor="end" fill="var(--gray)">{pct(t)}</text>
          </g>
        ))}
        <polyline fill="none" stroke="var(--black)" strokeWidth="2" points={pts.map((b) => `${x(b.mean_p as number)},${y(b.observed as number)}`).join(" ")} />
        {pts.map((b, i) => (
          <circle key={i} cx={x(b.mean_p as number)} cy={y(b.observed as number)} r={4 + Math.sqrt(b.n) * 1.4} fill="var(--black)" opacity="0.85" />
        ))}
        <text x={x(0.5)} y={y(0) + 38} fontSize="12" textAnchor="middle" fill="var(--black)">Predicted probability of style</text>
      </svg>
      <div style={{ fontFamily: "var(--font-franklin)", fontSize: "0.9rem" }}>{label}</div>
    </figure>
  );
}

function Confusion({ v, label }: { v: V; label: string }) {
  const c = v.confusion;
  const cellS = { border: "1px solid var(--black)", padding: "0.8rem", textAlign: "center" as const, fontFamily: mono, fontSize: "1.3rem" };
  const head = { ...small, padding: "0.3rem", textAlign: "center" as const };
  return (
    <div>
      <div style={{ fontFamily: "var(--font-franklin)", fontSize: "0.9rem", marginBottom: "0.5rem" }}>{label}</div>
      <table style={{ borderCollapse: "collapse", width: "100%", maxWidth: "320px" }}>
        <thead>
          <tr><td /><th scope="col" style={head}>Model: style</th><th scope="col" style={head}>Model: not style</th></tr>
        </thead>
        <tbody>
          <tr><th scope="row" style={{ ...head, textAlign: "left" }}>Editor: style</th><td style={cellS}>{c.tp}</td><td style={{ ...cellS, color: "var(--red)" }}>{c.fn}</td></tr>
          <tr><th scope="row" style={{ ...head, textAlign: "left" }}>Editor: not style</th><td style={{ ...cellS, color: "var(--red)" }}>{c.fp}</td><td style={cellS}>{c.tn}</td></tr>
        </tbody>
      </table>
      <p style={{ ...small, marginTop: "0.5rem" }}>
        Confident and right {v.single_answer.right}, confident and wrong {v.single_answer.wrong}, not sure {v.single_answer.not_sure}.
      </p>
    </div>
  );
}

function Histogram({ v, label }: { v: V; label: string }) {
  const max = Math.max(...v.histogram.map((b) => b.yes + b.no), 1);
  return (
    <div>
      <div style={{ fontFamily: "var(--font-franklin)", fontSize: "0.9rem", marginBottom: "0.5rem" }}>{label}</div>
      <div style={{ display: "flex", alignItems: "flex-end", gap: "3px", height: "140px", borderBottom: "1px solid var(--black)" }}
        role="img" aria-label={`${label} probability histogram: ${v.histogram.map((b) => `${pct(b.lo)} to ${pct(b.lo + 0.1)}: ${b.yes} style, ${b.no} not style`).join("; ")}`}>
        {v.histogram.map((b) => (
          <div key={b.lo} style={{ flex: 1, display: "flex", flexDirection: "column", justifyContent: "flex-end", height: "100%" }}>
            <div style={{ height: `${(b.no / max) * 100}%`, background: "var(--gray)" }} />
            <div style={{ height: `${(b.yes / max) * 100}%`, background: "var(--red)" }} />
          </div>
        ))}
      </div>
      <div style={{ ...small, display: "flex", justifyContent: "space-between" }}><span>0%</span><span>50%</span><span>100%</span></div>
    </div>
  );
}

function LearningCurve() {
  const pts = charts.learning_curve;
  const W = 320, H = 200, P = 40;
  const maxN = pts[pts.length - 1].n_train;
  const x = (n: number) => P + (n / maxN) * (W - P - 10);
  const y = (t: number) => 10 + (1 - (t - 0.3) / 0.7) * (H - 40);
  const series = [
    { key: "accuracy", color: "var(--black)", mean: (p: (typeof pts)[number]) => p.accuracy_mean, lo: (p: (typeof pts)[number]) => p.accuracy_min, hi: (p: (typeof pts)[number]) => p.accuracy_max },
    { key: "confident", color: "var(--red)", mean: (p: (typeof pts)[number]) => p.single_mean, lo: (p: (typeof pts)[number]) => p.single_min, hi: (p: (typeof pts)[number]) => p.single_max },
  ];
  return (
    <figure style={{ margin: 0 }}>
      <svg viewBox={`0 0 ${W} ${H + 20}`} style={{ width: "100%", maxWidth: "520px", display: "block" }} role="img"
        aria-label={`Learning curve: ${pts.map((p) => `${p.n_train} labels, accuracy ${pct(p.accuracy_mean)}, confident ${pct(p.single_mean)}`).join("; ")}`}>
        {[0.4, 0.6, 0.8, 1].map((t) => (
          <g key={t}>
            <line x1={P} x2={W - 10} y1={y(t)} y2={y(t)} stroke="var(--border)" />
            <text x={P - 6} y={y(t) + 4} fontSize="11" textAnchor="end" fill="var(--gray)">{pct(t)}</text>
          </g>
        ))}
        {pts.map((p) => <text key={p.n_train} x={x(p.n_train)} y={H - 12} fontSize="10" textAnchor="middle" fill="var(--gray)">{p.n_train}</text>)}
        <text x={(W + P) / 2} y={H + 8} fontSize="11" textAnchor="middle" fill="var(--black)">Random training labels</text>
        {series.map((s) => (
          <g key={s.key}>
            <polygon fill={s.color} opacity="0.12" points={[...pts.map((p) => `${x(p.n_train)},${y(s.hi(p))}`), ...[...pts].reverse().map((p) => `${x(p.n_train)},${y(s.lo(p))}`)].join(" ")} />
            <polyline fill="none" stroke={s.color} strokeWidth="2" points={pts.map((p) => `${x(p.n_train)},${y(s.mean(p))}`).join(" ")} />
          </g>
        ))}
        <circle cx={x(maxN)} cy={y(0.82)} r="5" fill="none" stroke="var(--red)" strokeWidth="2" />
        <text x={x(pts[1].n_train)} y={y(pts[1].accuracy_mean) - 8} fontSize="11" fill="var(--black)">accuracy</text>
        <text x={x(pts[3].n_train)} y={y(pts[3].single_mean) + 16} fontSize="11" fill="var(--red)">confident answers</text>
        <text x={x(maxN) - 8} y={y(0.82) + 4} fontSize="11" textAnchor="end" fill="var(--red)">with hard cases</text>
      </svg>
    </figure>
  );
}

export default function Evaluation() {
  const a = charts.versions["ari3-v0.0.1"], b = charts.versions["ari3-v0.0.2"];
  return (
    <Page title="Evaluation">
      <p style={{ ...bodyText, margin: 0 }}>
        <Link href="/ari3" style={{ color: "var(--black)" }}>ARI3 research notebook</Link>
      </p>
      <p style={{ ...bodyText, fontSize: "1.05rem", color: "var(--black)", marginTop: "1rem" }}>
        Both frozen versions, scored on the same {charts.n_test} held-out items from EXP-002. The frozen
        weights are used as released and never refit. Each chart uses 61 items, so small differences between versions are within noise.
      </p>

      <Section title="Reliability diagrams">
        <p style={bodyText}>
          When the model says 80%, is it right about 80% of the time? Points on the dashed line mean yes. Each dot is a group of items with similar predictions, and bigger dots hold more items.
          Temperature scaling (Guo et al. 2017) is what moves the points toward the line.
        </p>
        <div style={twoUp}>
          <Reliability v={a} label={VERSIONS[0][1]} />
          <Reliability v={b} label={VERSIONS[1][1]} />
        </div>
      </Section>

      <Section title="Confusion matrices">
        <p style={bodyText}>Rows are the editor&apos;s answer, columns the model&apos;s, at a 50% threshold. Red cells are mistakes.</p>
        <div style={twoUp}>
          <Confusion v={a} label={VERSIONS[0][1]} />
          <Confusion v={b} label={VERSIONS[1][1]} />
        </div>
      </Section>

      <Section title="Confidence histograms">
        <p style={bodyText}>
          How the predicted probabilities spread across the test items. Red is items the editor labeled style, grey
          is not style. Items piled at the edges are confident. Items in the middle are the not-sure ones.
        </p>
        <div style={twoUp}>
          <Histogram v={a} label={VERSIONS[0][1]} />
          <Histogram v={b} label={VERSIONS[1][1]} />
        </div>
      </Section>

      <Section title="Coverage against confidence">
        <p style={bodyText}>
          Conformal prediction trades coverage for confident answers through one setting, α. A lower α promises the
          right answer more often and gives more not-sure answers. Released versions use α = 0.10.
        </p>
        <div style={{ overflowX: "auto" }}>
          <table style={{ width: "100%", borderCollapse: "collapse", fontFamily: mono, fontSize: "0.82rem" }}>
            <thead>
              <tr>
                {["α", "Target", "v0.0.1 coverage", "v0.0.1 confident", "v0.0.2 coverage", "v0.0.2 confident"].map((h) => (
                  <th key={h} scope="col" style={{ textAlign: "left", padding: "0.45rem 0.6rem 0.45rem 0", borderBottom: "1px solid var(--black)", fontFamily: "var(--font-franklin)", fontWeight: 500, fontSize: "0.78rem" }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {a.coverage_vs_alpha.map((r, i) => (
                <tr key={r.alpha} style={{ fontWeight: r.alpha === 0.1 ? 700 : 400 }}>
                  <td style={{ padding: "0.4rem 0.6rem 0.4rem 0", borderBottom: "1px solid var(--border)" }}>{r.alpha.toFixed(2)}</td>
                  <td style={{ padding: "0.4rem 0.6rem 0.4rem 0", borderBottom: "1px solid var(--border)" }}>{pct(1 - r.alpha)}</td>
                  <td style={{ padding: "0.4rem 0.6rem 0.4rem 0", borderBottom: "1px solid var(--border)" }}>{pct(r.coverage)}</td>
                  <td style={{ padding: "0.4rem 0.6rem 0.4rem 0", borderBottom: "1px solid var(--border)" }}>{pct(r.single_share)}</td>
                  <td style={{ padding: "0.4rem 0.6rem 0.4rem 0", borderBottom: "1px solid var(--border)" }}>{pct(b.coverage_vs_alpha[i].coverage)}</td>
                  <td style={{ padding: "0.4rem 0.6rem 0.4rem 0", borderBottom: "1px solid var(--border)" }}>{pct(b.coverage_vs_alpha[i].single_share)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p style={{ ...small, marginTop: "0.6rem" }}>Thresholds recomputed for each α on the {charts.n_calibration} calibration labels.</p>
      </Section>

      <Section title="Learning curve (exploratory)">
        <p style={bodyText}>
          Fresh models trained on growing numbers of random labels, with the released design, 20 random subsets per
          size. The two lines are labeled on the chart. Shaded bands span the 20 subsets, and the red ring marks the 82% reached with 35 hard cases in EXP-002. This analysis was not pre-registered, and these are not released models.
        </p>
        <LearningCurve />
        <Callout>
          <p style={{ ...bodyText, color: "var(--black)", margin: 0 }}>
            With random labels only, accuracy levels off near 88% after about 100 labels, and confident answers stay
            near 66% from 75 labels to 194. Swapping 35 random labels for hard cases raised confident answers to 82%.
            More random labeling alone was not moving that number.
          </p>
        </Callout>
      </Section>

      <p style={{ ...small, marginTop: "2.5rem" }}>
        Computed {charts.generated_at.slice(0, 10)} by src/ari3_charts.py in {charts.runtime_seconds} s (Python {charts.environment.python},
        scikit-learn {charts.environment.scikit_learn}).
      </p>
    </Page>
  );
}
