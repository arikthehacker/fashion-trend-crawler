import Link from "next/link";
import { pageMetadata } from "../../../lib/site";
import { ARCHITECTURE, MODEL_CARDS, type ModelCard } from "../../../lib/ari3_cards";
import { Stamp } from "../../components/Chrome";
import { Ari3Page, Tx } from "../ui";

export const metadata = pageMetadata(
  "/ari3/models",
  "ARI3 model cards",
  "Model cards for every ARI3 version: purpose, inputs, outputs, training data, metrics, limitations and failure modes."
);

function Ul({ items }: { items: string[] }) {
  return <ul>{items.map((x, i) => <li key={i}><Tx text={x} /></li>)}</ul>;
}

function SpecCard({ c }: { c: ModelCard }) {
  return (
    <article className="spec" id={c.version.replace(/\./g, "-")}>
      <header><h2>{c.name}</h2><span>{c.version} · <Stamp>{c.status}</Stamp></span></header>
      <p className="purpose">{c.purpose}</p>
      <dl>
        <dt>Reads</dt><dd>{c.inputs}</dd>
        <dt>Gives</dt><dd>{c.outputs}</dd>
        <dt>Trained on</dt><dd>{c.training}</dd>
        <dt>How it did</dt>
        <dd>
          <table className="metrics num">
            <tbody>{c.metrics.map((m) => <tr key={m.name}><td>{m.name}</td><td className="v">{m.value}</td></tr>)}</tbody>
          </table>
        </dd>
        <dt>Limits</dt><dd><Ul items={c.limitations} /></dd>
        <dt>Where it errs</dt><dd><Ul items={c.failureModes} /></dd>
        <dt>Use it for</dt><dd>{c.intendedUse}</dd>
        <dt>Not for</dt><dd>{c.notFor}</dd>
      </dl>
      <footer>Notebook entry: <Link href={`/ari3/${c.exp}`}>{c.exp.toUpperCase()}</Link></footer>
    </article>
  );
}

export default function Models() {
  return (
    <Ari3Page label="Model cards" current="/ari3/models">
      <div className="cards">{MODEL_CARDS.map((c) => <SpecCard key={c.version} c={c} />)}</div>
      <h2 className="sec">Shared architecture</h2>
      <div className="table-wrap">
        <table className="ledger">
          <tbody>
            {ARCHITECTURE.map((a) => (
              <tr key={a.part}>
                <td style={{ width: "10em", fontWeight: 600 }}>{a.part}</td>
                <td className="s">{a.value}</td>
                <td className="r" style={{ fontStyle: "italic" }}>{a.source}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Ari3Page>
  );
}
