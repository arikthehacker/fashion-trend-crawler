import { pageMetadata } from "../../../lib/site";
import { PRINCIPLES } from "../../../lib/ari3";
import { Ari3Page } from "../ui";

export const metadata = pageMetadata(
  "/ari3/philosophy",
  "ARI3 research philosophy",
  "The principles ARI3 is built and tested by: version everything, measure everything, never hide failures, pre-register experiments."
);

export default function Philosophy() {
  return (
    <Ari3Page label="Philosophy" current="/ari3/philosophy" folioH1={false}>
      <h1 className="hed toner" style={{ fontSize: "clamp(36px,4.6vw,58px)", marginBottom: "22px" }}>The principles behind the program</h1>
      <ol className="princ">
        {PRINCIPLES.map((p) => <li key={p.title}><b>{p.title}</b><p>{p.body}</p></li>)}
      </ol>
    </Ari3Page>
  );
}
