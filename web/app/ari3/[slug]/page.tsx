import { Fragment } from "react";
import { notFound } from "next/navigation";
import { pageMetadata } from "../../../lib/site";
import { EXPERIMENTS, type Experiment } from "../../../lib/ari3";
import { Stamp } from "../../components/Chrome";
import { Ari3Page, Bul, ListSection, Tx, fmtVal } from "../ui";

// Only the listed experiments exist. Any other slug is a 404, never another entry.
export const dynamicParams = false;

export function generateStaticParams() {
  return EXPERIMENTS.map((e) => ({ slug: e.slug }));
}

// Search descriptions, 70 to 160 characters each, written from each entry's own results.
const DESCRIPTIONS: Record<string, string> = {
  "exp-001": "ARI3 v0.0.1, the first style classifier: 145 editor labels, 0.882 held-out accuracy and no confident mistakes on 34 test items.",
  "exp-002": "ARI3 v0.0.2: 35 hard cases chosen by active learning raised confident answers from 66% to 82% at equal training size. Pre-registered.",
  "exp-003": "ARI3 v0.0.3: v0.0.2 on newer articles kept its coverage but missed its accuracy mark, 0.833 against 0.85. The forecast detector failed.",
  "exp-004": "EXP-004 grounded retrieval: a frozen hybrid retriever reached Recall@10 0.770 and Hit@10 1.000 on 12 held-out questions with a relevant item.",
  "exp-007": "EXP-007: can an LLM stand in for the editor on weekly report decisions? DeepSeek reached kappa 0.079 on 216 cards, and thinking first did not help.",
  "exp-008": "EXP-008: a taste profile of the editor, written by a Claude subagent, did not raise DeepSeek's agreement with her report decisions. Kappa 0.086.",
  "exp-009": "EXP-009: the editor's past decisions predict her report calls best. Kappa 0.542 for same as last time, 0.515 for a taste model, 0.182 for DeepSeek.",
};

function describe(e: Experiment) {
  const d = DESCRIPTIONS[e.slug] ?? `ARI3 ${e.id} ${e.name}: ${e.headline}`;
  return d.length <= 160 ? d : `${d.slice(0, 157).replace(/\s+\S*$/, "")}...`;
}

export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const e = EXPERIMENTS.find((x) => x.slug === slug);
  if (!e) return {};
  return pageMetadata(`/ari3/${e.slug}`, e.version ? `${e.id}, release ${e.version}` : `${e.id}: ${e.name}`, describe(e));
}

export default async function ExperimentPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const e = EXPERIMENTS.find((x) => x.slug === slug);
  if (!e) notFound();

  const hasA = e.metrics.some((m) => m.a !== undefined);
  const preregistered = /^Yes/.test(e.preregistered);

  return (
    <Ari3Page label="Notebook entry" folioH1={false}>
      <div className="entry">
        <div>
          <h1 className="hed toner" style={{ fontSize: "clamp(56px,8vw,104px)", marginBottom: "6px" }}>
            <span style={{ whiteSpace: "nowrap" }}>{e.id}</span>
            <span className="sr-only">: {e.version ? `release ${e.version}` : e.name}</span>
          </h1>
          <p aria-hidden="true" style={{ fontFamily: "var(--serif)", fontSize: "clamp(24px,2.6vw,34px)", lineHeight: 1.1, letterSpacing: "-0.015em", margin: "0 0 10px" }}>{e.version ? `Release ${e.version}` : e.name}</p>
          <p style={{ margin: "6px 0 16px", display: "flex", gap: "10px", flexWrap: "wrap" }}>
            <Stamp>{e.status}</Stamp>
            {preregistered ? <Stamp>Pre-registered</Stamp> : null}
          </p>
          <p className="lede-intro" style={{ fontSize: "22px" }}>{e.headline}</p>
          <div className="cols drop" style={{ marginTop: "16px" }}>
            {e.summary.map((p, i) => <p key={i}><Tx text={p} /></p>)}
          </div>
        </div>
        <aside className="facts" aria-labelledby="record-h">
          <h2 className="sec" id="record-h" style={{ marginTop: 0 }}>The record</h2>
          <dl>
            {e.meta.map((m) => (
              <Fragment key={m.label}>
                <dt>{m.label}</dt>
                <dd>{m.href ? <a href={m.href}>{m.value}</a> : m.value}</dd>
              </Fragment>
            ))}
          </dl>
        </aside>
      </div>

      <h2 className="sec">The question</h2>
      <p className="lede-intro">{e.question}</p>
      {e.preregistered ? <p className="caption">Pre-registered: {e.preregistered}</p> : null}

      {e.hypotheses ? (
        <>
          <h2 className="sec">Hypotheses</h2>
          <div className="table-wrap">
            <table className="ledger">
              <thead>
                <tr>
                  <th scope="col"><span className="sr-only">Hypothesis</span></th>
                  <th scope="col">Claim</th>
                  <th scope="col">Test</th>
                  <th scope="col">Result</th>
                  <th scope="col"><span className="sr-only">Verdict</span></th>
                </tr>
              </thead>
              <tbody>
                {e.hypotheses.map((h) => (
                  <tr key={h.id}>
                    <td>{h.id}</td>
                    <td className="s">{h.claim}</td>
                    <td>{h.test}</td>
                    <td>{h.result}</td>
                    <td className="r"><Stamp>{h.verdict}</Stamp></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      ) : null}

      <ListSection title="Why run it" items={e.why} />
      <ListSection title="Method" items={e.method} />
      {e.held.length || e.changed.length ? (
        <div className="pair" style={{ marginTop: "28px" }}>
          <div><h3>Held fixed</h3><Bul items={e.held} /></div>
          <div><h3>Changed</h3><Bul items={e.changed} /></div>
        </div>
      ) : null}

      <h2 className="sec">Results</h2>
      {e.resultsIntro ? <p className="caption" style={{ margin: "0 0 10px" }}>{e.resultsIntro}</p> : null}
      <div className="table-wrap">
        <table className="ledger num">
          <thead>
            <tr>
              <th scope="col">Measure</th>
              {hasA ? <th scope="col" className="r">{e.compare?.a ?? "Before"}</th> : null}
              <th scope="col" className="r">{e.compare?.b ?? e.metrics[0]?.label ?? "Result"}</th>
              <th scope="col">Note</th>
            </tr>
          </thead>
          <tbody>
            {e.metrics.map((m) => (
              <tr key={m.name}>
                <td className="s">{m.name}</td>
                {hasA ? <td className="r s">{m.a !== undefined ? fmtVal(m.a, m.format) : ""}</td> : null}
                <td className="r s">{fmtVal(m.b, m.format)}</td>
                <td>{m.note ?? ""}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="pair" style={{ marginTop: "28px" }}>
        <div><h3>What it gained</h3><Bul items={e.benefits} /></div>
        <div><h3>What it cost</h3><Bul items={e.costs} /></div>
      </div>

      <ListSection title="Surprises" items={e.surprises} />
      <ListSection title="Threats to the result" items={e.threats} />
      <ListSection title="What was built" items={e.engineering} />

      {e.log.length ? (
        <>
          <h2 className="sec">From idea to result</h2>
          <ol className="steps-log">
            {e.log.map((l) => <li key={l.step}><b>{l.step}</b><span><Tx text={l.text} /></span></li>)}
          </ol>
        </>
      ) : null}

      <ListSection title="Lessons" items={e.lessons} />
      <ListSection title="Open questions" items={e.openQuestions} />

      <h2 className="sec">Reproducing it</h2>
      <p className="lede-intro" style={{ fontSize: "17px" }}><Tx text={e.reproduce.text} /></p>
      <div className="table-wrap">
        <pre><code>{e.reproduce.commands}</code></pre>
      </div>
    </Ari3Page>
  );
}
