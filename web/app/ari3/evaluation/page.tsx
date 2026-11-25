import { pageMetadata } from "../../../lib/site";
import charts from "../../../lib/ari3_charts.json";
import { Ari3Page, day } from "../ui";

export const metadata = pageMetadata(
  "/ari3/evaluation",
  "ARI3 evaluation charts",
  "Reliability diagrams, confusion matrices, confidence histograms, coverage curves and a learning curve for ARI3 v0.0.1 and v0.0.2."
);

type V = (typeof charts.versions)["ari3-v0.0.1"];
type LC = typeof charts.learning_curve;
const VNAME: Record<string, string> = { "ari3-v0.0.1": "v0.0.1 INDUSTRIA", "ari3-v0.0.2": "v0.0.2 DISCIPLINA" };
const INK = "#0f0f10";
const pct = (v: number) => `${Math.round(v * 100)}%`;
const serif = { fontFamily: "var(--serif)" };

function Reliability({ v, label }: { v: V; label: string }) {
  const W = 300, H = 260, P = 34;
  const x = (p: number) => P + p * (W - P - 8);
  const y = (p: number) => H - P - p * (H - P - 8);
  const pts = v.reliability.filter((b) => b.n > 0 && b.mean_p !== null && b.observed !== null) as { n: number; mean_p: number; observed: number }[];
  const desc = pts.map((b) => `predicted ${pct(b.mean_p)}, right ${pct(b.observed)}, ${b.n} items`).join("; ");
  return (
    <svg viewBox={`0 0 ${W} ${H}`} role="img" aria-label={`${label} reliability diagram, predicted chance an item is style against how often the editor said style. Groups: ${desc}.`}>
      <line x1={x(0)} y1={y(0)} x2={x(1)} y2={y(1)} stroke={INK} strokeDasharray="4 4" strokeWidth="1" />
      <line x1={x(0)} y1={y(0)} x2={x(1)} y2={y(0)} stroke={INK} />
      <line x1={x(0)} y1={y(0)} x2={x(0)} y2={y(1)} stroke={INK} />
      {[0, 0.5, 1].map((t) => (
        <g key={t}>
          <text x={x(t)} y={H - P + 16} fontSize="11" textAnchor="middle">{t * 100}%</text>
          <text x={P - 6} y={y(t) + 4} fontSize="11" textAnchor="end">{t * 100}%</text>
        </g>
      ))}
      {pts.map((b, i) => <circle key={i} cx={x(b.mean_p)} cy={y(b.observed)} r={3 + Math.sqrt(b.n) * 1.6} fill={INK} fillOpacity="0.85" />)}
      <text x={(W + P) / 2} y={H - 2} fontSize="11" textAnchor="middle">predicted chance it&apos;s style</text>
    </svg>
  );
}

function Histogram({ v, label, id }: { v: V; label: string; id: string }) {
  const W = 300, H = 170, P = 22;
  const bw = (W - 2 * P) / v.histogram.length;
  const mx = Math.max(...v.histogram.map((b) => b.yes + b.no), 1);
  const sy = (c: number) => (c / mx) * (H - 2 * P);
  const desc = v.histogram.map((b) => `${pct(b.lo)} to ${pct(b.lo + 0.1)}: ${b.yes} style, ${b.no} not style`).join("; ");
  return (
    <svg viewBox={`0 0 ${W} ${H}`} role="img" aria-label={`${label} confidence histogram, test items by predicted chance of style, in tenths. ${desc}.`}>
      <defs>
        <pattern id={id} width="3.4" height="3.4" patternUnits="userSpaceOnUse"><circle cx="1.7" cy="1.7" r="0.95" fill={INK} /></pattern>
      </defs>
      {v.histogram.map((b, i) => {
        const x0 = P + i * bw + 1, hy = sy(b.yes), hn = sy(b.no);
        return (
          <g key={i}>
            <rect x={x0} y={H - P - hy} width={bw - 2} height={hy} fill={INK} />
            <rect x={x0} y={H - P - hy - hn} width={bw - 2} height={hn} fill={`url(#${id})`} />
          </g>
        );
      })}
      <line x1={P} y1={H - P} x2={W - P} y2={H - P} stroke={INK} />
      {[0, 0.5, 1].map((t) => <text key={t} x={P + t * (W - 2 * P)} y={H - 6} fontSize="11" textAnchor="middle">{t * 100}%</text>)}
    </svg>
  );
}

function LearningCurve({ lc }: { lc: LC }) {
  const W = 640, H = 260, L = 44, B = 34, T = 10, Rr = 12;
  const xs = lc.map((p) => p.n_train), x0 = Math.min(...xs), x1 = Math.max(...xs);
  const x = (v: number) => L + ((v - x0) / (x1 - x0)) * (W - L - Rr);
  const y = (v: number) => H - B - ((v - 0.3) / 0.7) * (H - B - T);
  type K = "accuracy_min" | "accuracy_max" | "single_min" | "single_max" | "accuracy_mean" | "single_mean";
  const band = (lo: K, hi: K) =>
    `M${lc.map((p) => `${x(p.n_train)},${y(p[hi])}`).join(" L")} L${[...lc].reverse().map((p) => `${x(p.n_train)},${y(p[lo])}`).join(" L")} Z`;
  const line = (k: K) => lc.map((p) => `${x(p.n_train)},${y(p[k])}`).join(" ");
  const mid = lc.find((p) => p.n_train >= 125) ?? lc[lc.length - 1];
  const desc = lc.map((p) => `${p.n_train} labels: accuracy ${pct(p.accuracy_mean)}, confident answers ${pct(p.single_mean)}`).join("; ");
  return (
    <svg viewBox={`0 0 ${W} ${H}`} role="img" aria-label={`Learning curve, mean accuracy and confident-answer share against the number of random training labels. ${desc}. With 35 hard cases at 194 labels, confident answers reached 82%.`}>
      <defs>
        <pattern id="ht-lc" width="3.6" height="3.6" patternUnits="userSpaceOnUse"><circle cx="1.8" cy="1.8" r="0.8" fill={INK} fillOpacity="0.6" /></pattern>
      </defs>
      <path d={band("accuracy_min", "accuracy_max")} fill="url(#ht-lc)" opacity="0.55" />
      <path d={band("single_min", "single_max")} fill="url(#ht-lc)" opacity="0.3" />
      <polyline points={line("accuracy_mean")} fill="none" stroke={INK} strokeWidth="2.2" />
      <polyline points={line("single_mean")} fill="none" stroke={INK} strokeWidth="2.2" strokeDasharray="6 4" />
      <circle cx={x(194)} cy={y(0.82)} r="7" fill="none" stroke={INK} strokeWidth="2" />
      <text x={x(194) - 12} y={y(0.82) + 4} fontSize="12" textAnchor="end" fontStyle="italic" style={serif}>with 35 hard cases</text>
      <text x={x(125)} y={y(mid.accuracy_mean) - 8} fontSize="12" textAnchor="middle" style={serif}>accuracy</text>
      <text x={x(125)} y={y(mid.single_mean) + 18} fontSize="12" textAnchor="middle" style={serif}>confident answers</text>
      <line x1={L} y1={H - B} x2={W - Rr} y2={H - B} stroke={INK} />
      {[0.4, 0.6, 0.8, 1].map((v) => (
        <g key={v}>
          <text x={L - 6} y={y(v) + 4} fontSize="11" textAnchor="end">{Math.round(v * 100)}%</text>
          <line x1={L} x2={W - Rr} y1={y(v)} y2={y(v)} stroke={INK} strokeOpacity="0.12" />
        </g>
      ))}
      {xs.map((v) => <text key={v} x={x(v)} y={H - B + 16} fontSize="11" textAnchor="middle">{v}</text>)}
      <text x={(W + L) / 2} y={H - 2} fontSize="11" textAnchor="middle">random training labels</text>
    </svg>
  );
}

export default function Evaluation() {
  const C = charts;
  const V = Object.entries(C.versions) as [string, V][];
  const short = (k: string) => (VNAME[k] ?? k).split(" ")[0];
  return (
    <Ari3Page label="Evaluation" current="/ari3/evaluation">
      <p className="lede-intro">
        Both frozen versions, scored on the same {C.n_test} held-out items from EXP-002. The frozen weights are used as
        released and never refit. Each chart uses {C.n_test} items, so small differences between versions are within noise.
      </p>

      <h2 className="sec">Fig. 1 · When it says 80%, is it right 80% of the time?</h2>
      <div className="figs">
        {V.map(([k, v]) => (
          <figure key={k}><p className="ft">{VNAME[k] ?? k}</p><Reliability v={v} label={VNAME[k] ?? k} /></figure>
        ))}
      </div>
      <p className="caption">
        Each dot is a group of items with similar predictions; bigger dots hold more items. Dots on the dashed line mean
        the stated chance matches how often it was right.
      </p>

      <h2 className="sec">Fig. 2 · Right and wrong, against the editor</h2>
      <div className="figs">
        {V.map(([k, v]) => {
          const c = v.confusion, s = v.single_answer;
          return (
            <figure key={k}>
              <p className="ft">{VNAME[k] ?? k}</p>
              <table className="cm num">
                <caption className="sr-only">{VNAME[k] ?? k}: the editor&apos;s answers in rows, the model&apos;s in columns</caption>
                <thead>
                  <tr><td /><th scope="col">Model: style</th><th scope="col">Model: not style</th></tr>
                </thead>
                <tbody>
                  <tr><th scope="row">Editor: style</th><td>{c.tp}</td><td className="miss">{c.fn}</td></tr>
                  <tr><th scope="row">Editor: not style</th><td className="miss">{c.fp}</td><td>{c.tn}</td></tr>
                </tbody>
              </table>
              <figcaption>Confident and right {s.right}, confident and wrong {s.wrong}, not sure {s.not_sure}.</figcaption>
            </figure>
          );
        })}
      </div>
      <p className="caption">Rows are the editor&apos;s answer, columns the model&apos;s, at a 50% threshold. Dotted cells are mistakes.</p>

      <h2 className="sec">Fig. 3 · How sure it was</h2>
      <div className="figs">
        {V.map(([k, v]) => (
          <figure key={k}><p className="ft">{VNAME[k] ?? k}</p><Histogram v={v} label={VNAME[k] ?? k} id={`ht-${k.replace(/\W/g, "")}`} /></figure>
        ))}
      </div>
      <p className="caption">
        Solid is items the editor labeled style, dotted is not style. Items piled at the edges are confident; items in the
        middle are the not-sure ones.
      </p>

      <h2 className="sec">Table 1 · Coverage against confidence</h2>
      <div className="table-wrap">
        <table className="ledger num">
          <thead>
            <tr>
              <th scope="col">α</th>
              <th scope="col" className="r">Target</th>
              {V.map(([k]) => [
                <th key={`${k}-c`} scope="col" className="r">{short(k)} coverage</th>,
                <th key={`${k}-s`} scope="col" className="r">{short(k)} confident</th>,
              ])}
            </tr>
          </thead>
          <tbody>
            {V[0][1].coverage_vs_alpha.map((row, i) => (
              <tr key={row.alpha}>
                <td>{row.alpha.toFixed(2)}</td>
                <td className="r">{pct(1 - row.alpha)}</td>
                {V.map(([k, v]) => [
                  <td key={`${k}-c`} className="r s">{pct(v.coverage_vs_alpha[i].coverage)}</td>,
                  <td key={`${k}-s`} className="r s">{pct(v.coverage_vs_alpha[i].single_share)}</td>,
                ])}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <p className="caption">
        A lower α promises the right answer more often and gives more not-sure answers. Released versions use α = 0.10.
        Thresholds recomputed for each α on the {C.n_calibration} calibration labels.
      </p>

      <h2 className="sec">Fig. 4 · Learning curve (exploratory)</h2>
      <figure>
        <LearningCurve lc={C.learning_curve} />
        <figcaption>
          Fresh models trained on growing numbers of random labels, 20 random subsets per size; dotted bands span the
          subsets. Accuracy levels off near 88% after about 100 labels, and confident answers stay near 66%. Swapping 35
          random labels for hard cases raised confident answers to 82%. Not pre-registered, and not released models.
        </figcaption>
      </figure>
      <p className="note" style={{ marginTop: "14px" }}>
        Computed {day(C.generated_at.slice(0, 10))} in {C.runtime_seconds} s (Python {C.environment.python}, scikit-learn{" "}
        {C.environment.scikit_learn}).
      </p>
    </Ari3Page>
  );
}
