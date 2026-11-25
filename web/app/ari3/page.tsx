import Link from "next/link";
import { pageMetadata } from "../../lib/site";
import { EXPERIMENTS, PROJECT_STATE, REPO } from "../../lib/ari3";
import { Stamp } from "../components/Chrome";
import { Ari3Page } from "./ui";

export const metadata = pageMetadata(
  "/ari3",
  "ARI3 research notebook",
  "The research notebook for ARI3, the model system behind ARI3LLA INDEX: every experiment, its question, hypotheses, results and costs, frozen and hashed."
);

export default function Ari3Overview() {
  return (
    <Ari3Page label="Overview" current="/ari3">
      <p className="lede-intro">
        ARI3 is the model system behind ARI3LLA INDEX, run as a small research program. Each experiment is a permanent
        notebook entry with its question, hypotheses, method, results, costs and open questions. Every model version is
        frozen, hashed and committed to the public repository before its results appear here.
      </p>

      <h2 className="sec" id="experiment-registry">Experiment registry</h2>
      <div className="reg">
        {EXPERIMENTS.map((e) => (
          <article key={e.id}>
            <div>
              <h3><Link href={`/ari3/${e.slug}`}>{e.id}</Link></h3>
              {e.version ? <p className="id">Release {e.version}</p> : null}
            </div>
            <div>
              <p className="hl">{e.headline}</p>
            </div>
            <div className="stamps">
              <Stamp>{e.status}</Stamp>
              {/^Yes/.test(e.preregistered) ? <Stamp>Pre-registered</Stamp> : null}
            </div>
          </article>
        ))}
      </div>
      <p className="caption">Entries are permanent. A correction is added as a dated note, never by editing the result.</p>

      <h2 className="sec">State of the project</h2>
      <div className="state">
        {PROJECT_STATE.map((g) => (
          <div key={g.status}>
            <h3>{g.status}</h3>
            {g.items.map((i) => <p key={i.area}><b>{i.area}</b>{i.detail}</p>)}
          </div>
        ))}
      </div>
      <p className="caption">
        Planned names mark intent. None has a date. Every entry lists its commit and the SHA-256 hash of each file, so a
        downloaded file can be checked. The source is at <a href={REPO}>github.com/arikthehacker/fashion-trend-crawler</a>.
      </p>
    </Ari3Page>
  );
}
