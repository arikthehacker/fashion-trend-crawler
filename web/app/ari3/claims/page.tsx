import { pageMetadata } from "../../../lib/site";
import { REPO } from "../../../lib/ari3";
import { getClaims, STATUS_LABEL } from "../../../lib/claims";
import { Stamp } from "../../components/Chrome";
import { Ari3Page, Tx } from "../ui";

export const metadata = pageMetadata(
  "/ari3/claims",
  "ARI3 claim ledger",
  "Every result ARI3 states about itself, with its status, sample, limitations and the committed artifact behind it."
);

export default function Claims() {
  const claims = getClaims();
  return (
    <Ari3Page label="Claims" current="/ari3/claims">
      <p className="lede-intro">Each published claim about ARI3, with its status, the file it comes from and its limits.</p>
      <p className="caption" style={{ maxWidth: "62ch" }}>
        A published claim is not silently rewritten or deleted. If its status changes, the later record preserves that
        change, and failed pre-registered hypotheses remain visible as not supported. Only claims approved for the site
        appear here. The full record is <a href={`${REPO}/blob/master/CLAIM_LEDGER.md`}>CLAIM_LEDGER.md</a>.
      </p>
      {claims.length === 0 ? <p className="note">No claims are recorded.</p> : (
        <div className="table-wrap" style={{ marginTop: "18px" }}>
          <table className="ledger">
            <thead>
              <tr><th scope="col">ID</th><th scope="col">Claim</th><th scope="col">Result</th><th scope="col">Limits</th><th scope="col" className="r">Status</th></tr>
            </thead>
            <tbody>
              {claims.map((c) => (
                <tr key={c.id} id={c.id.toLowerCase()}>
                  <td style={{ whiteSpace: "nowrap" }}>{c.id}<br /><span className="note">{c.asOf}</span></td>
                  <td className="s">
                    <Tx text={c.claim} />
                    {c.experiment ? <><br /><span className="note">{c.experiment}</span></> : null}
                  </td>
                  <td>
                    <Tx text={c.result} />
                    {c.artifact ? <><br /><span className="note">From <Tx text={c.artifact} /></span></> : null}
                  </td>
                  <td className="note"><Tx text={c.limitations} /></td>
                  <td className="r">
                    <Stamp>{STATUS_LABEL[c.status] ?? c.status}</Stamp>
                    {c.supersededBy && c.supersededBy !== "none" ? <><br /><span className="note">Superseded by <Tx text={c.supersededBy} /></span></> : null}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </Ari3Page>
  );
}
