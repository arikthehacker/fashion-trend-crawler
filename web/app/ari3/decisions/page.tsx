import Link from "next/link";
import { pageMetadata } from "../../../lib/site";
import { DECISIONS } from "../../../lib/ari3_cards";
import { Ari3Page, day } from "../ui";

export const metadata = pageMetadata(
  "/ari3/decisions",
  "ARI3 decision log",
  "The decisions that shape ARI3's data, models and evidence standard, each with its reason, alternatives and tradeoff."
);

export default function Decisions() {
  return (
    <Ari3Page label="Decisions" current="/ari3/decisions">
      <div className="rulings">
        {DECISIONS.map((d) => (
          <article key={d.id}>
            <p className="id">{d.id}<span>{day(d.date)}</span></p>
            <div>
              <h2>{d.title}</h2>
              <dl>
                <dt>Decision</dt><dd>{d.decision}</dd>
                <dt>Why</dt><dd>{d.why}</dd>
                <dt>Instead of</dt><dd>{d.alternatives}</dd>
                <dt>Trade-off</dt><dd>{d.tradeoff}</dd>
                {d.exp ? <><dt>Entry</dt><dd><Link href={`/ari3/${d.exp}`}>{d.exp.toUpperCase()}</Link></dd></> : null}
              </dl>
            </div>
          </article>
        ))}
      </div>
    </Ari3Page>
  );
}
