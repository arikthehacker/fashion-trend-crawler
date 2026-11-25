import { Fragment } from "react";
import { pageMetadata } from "../../../lib/site";
import { DATASETS } from "../../../lib/ari3_cards";
import { Ari3Page, Tx } from "../ui";

export const metadata = pageMetadata(
  "/ari3/data",
  "ARI3 dataset cards",
  "Dataset cards for the ARI3 item corpus and the editor's labels: sources, collection, labeling, biases, access and versions."
);

export default function Data() {
  return (
    <Ari3Page label="Dataset cards" current="/ari3/data">
      <div className="cards">
        {DATASETS.map((d) => (
          <article className="spec" key={d.name}>
            <header><h2 style={{ fontSize: "24px", letterSpacing: "0.01em" }}>{d.name}</h2><span>{d.version}</span></header>
            <dl>
              {d.rows.map((r) => (
                <Fragment key={r.k}>
                  <dt>{r.k}</dt>
                  <dd><Tx text={r.v} /></dd>
                </Fragment>
              ))}
            </dl>
          </article>
        ))}
      </div>
    </Ari3Page>
  );
}
