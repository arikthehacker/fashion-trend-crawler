import { pageMetadata } from "../../lib/site";
import { RELEASES, REPO, type Release } from "../../lib/ari3";

export const metadata = pageMetadata(
  "/ari3",
  "ARI3 releases",
  "The public release ledger for ARI3, the model system behind ARI3LLA INDEX. Every version is frozen, hashed and committed before its results are published, with its test results and limits."
);

const mono = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace";

function utc(iso: string) {
  return iso.replace("T", " ").replace("Z", " UTC");
}

function StatusPill({ status }: { status: Release["status"] }) {
  const frozen = status === "frozen";
  return (
    <span
      style={{
        fontFamily: mono,
        fontSize: "0.72rem",
        letterSpacing: "0.08em",
        textTransform: "uppercase",
        padding: "0.2rem 0.55rem",
        border: `1px solid ${frozen ? "var(--black)" : "var(--red)"}`,
        color: frozen ? "var(--black)" : "var(--red)",
        whiteSpace: "nowrap",
      }}
    >
      {frozen ? "Frozen" : "Pre-registered · pending"}
    </span>
  );
}

const h3: React.CSSProperties = {
  fontFamily: "var(--font-franklin)",
  fontSize: "0.72rem",
  letterSpacing: "0.1em",
  textTransform: "uppercase",
  color: "var(--gray)",
  margin: "1.75rem 0 0.6rem",
  fontWeight: 600,
};
const body: React.CSSProperties = {
  fontFamily: "var(--font-franklin)",
  fontSize: "0.95rem",
  lineHeight: "1.7",
  color: "var(--gray)",
  margin: "0 0 0.8rem",
};
const cell: React.CSSProperties = {
  padding: "0.55rem 0.75rem 0.55rem 0",
  borderBottom: "1px solid var(--border)",
  verticalAlign: "top",
  fontFamily: "var(--font-franklin)",
  fontSize: "0.88rem",
  lineHeight: 1.5,
};

function ReleaseCard({ r }: { r: Release }) {
  return (
    <article
      id={r.version}
      aria-labelledby={`t-${r.version}`}
      style={{ borderTop: "2px solid var(--black)", paddingTop: "1.5rem", marginTop: "3.5rem" }}
    >
      <div style={{ display: "flex", flexWrap: "wrap", alignItems: "baseline", gap: "0.75rem 1rem" }}>
        <h2
          id={`t-${r.version}`}
          style={{ fontFamily: "var(--font-instrument)", fontSize: "2.4rem", fontWeight: 400, margin: 0 }}
        >
          ARI3 {r.version}
        </h2>
        <StatusPill status={r.status} />
      </div>
      <p style={{ ...body, margin: "0.4rem 0 0", color: "var(--black)" }}>{r.kind}</p>

      <dl
        style={{
          display: "grid",
          gridTemplateColumns: "max-content minmax(0, 1fr)",
          gap: "0.35rem 1rem",
          margin: "1.25rem 0 0",
          fontSize: "0.82rem",
        }}
      >
        <dt style={{ color: "var(--gray)", fontFamily: "var(--font-franklin)" }}>Committed</dt>
        <dd style={{ margin: 0, fontFamily: mono }}>
          <time dateTime={r.committedAt}>{utc(r.committedAt)}</time>
        </dd>
        <dt style={{ color: "var(--gray)", fontFamily: "var(--font-franklin)" }}>Commit</dt>
        <dd style={{ margin: 0, fontFamily: mono, overflowWrap: "anywhere" }}>
          <a href={`${REPO}/commit/${r.commit}`} style={{ color: "var(--black)" }}>
            {r.commit.slice(0, 7)}
          </a>
        </dd>
        {r.files.map((f) => (
          <div key={f.path} style={{ display: "contents" }}>
            <dt style={{ color: "var(--gray)", fontFamily: "var(--font-franklin)" }}>{f.label}</dt>
            <dd style={{ margin: 0, fontFamily: mono, overflowWrap: "anywhere" }}>
              <a href={`${REPO}/blob/${r.commit}/${f.path}`} style={{ color: "var(--black)" }}>
                {f.path}
              </a>
              <br />
              <span style={{ color: "var(--gray)" }}>sha256 {f.sha256}</span>
            </dd>
          </div>
        ))}
      </dl>

      <div style={{ marginTop: "1.5rem" }}>
        {r.summary.map((p, i) => (
          <p key={i} style={body}>{p}</p>
        ))}
      </div>

      {r.method && (
        <>
          <h3 style={h3}>How it works</h3>
          <div style={{ overflowX: "auto" }}>
            <table style={{ width: "100%", borderCollapse: "collapse" }}>
              <tbody>
                {r.method.map((m) => (
                  <tr key={m.stage}>
                    <th scope="row" style={{ ...cell, textAlign: "left", fontWeight: 600, whiteSpace: "nowrap" }}>{m.stage}</th>
                    <td style={cell}>
                      {m.technique}
                      {m.source && <div style={{ color: "var(--gray)", fontSize: "0.8rem" }}>{m.source}</div>}
                    </td>
                    <td style={{ ...cell, fontFamily: mono, fontSize: "0.8rem" }}>{m.value}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}

      {r.metrics && (
        <>
          <h3 style={h3}>Results on 34 held-out items</h3>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(min(100%, 190px), 1fr))", gap: "0.75rem" }}>
            {r.metrics.map((m) => (
              <div key={m.name} style={{ border: "1px solid var(--border)", padding: "0.9rem 1rem" }}>
                <div style={{ fontFamily: "var(--font-franklin)", fontSize: "0.75rem", color: "var(--gray)" }}>{m.name}</div>
                <div style={{ fontFamily: mono, fontSize: "1.35rem", margin: "0.25rem 0" }}>{m.value}</div>
                {m.note && <div style={{ fontFamily: "var(--font-franklin)", fontSize: "0.75rem", lineHeight: 1.45, color: "var(--gray)" }}>{m.note}</div>}
              </div>
            ))}
          </div>
        </>
      )}

      {r.hypotheses && (
        <>
          <h3 style={h3}>Hypotheses, fixed before the experiment</h3>
          <div style={{ overflowX: "auto" }}>
            <table style={{ width: "100%", borderCollapse: "collapse" }}>
              <thead>
                <tr>
                  {["", "Claim", "Supported if", "Result"].map((h) => (
                    <th key={h} scope="col" style={{ ...cell, textAlign: "left", color: "var(--gray)", fontWeight: 500, fontSize: "0.75rem" }}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {r.hypotheses.map((h) => (
                  <tr key={h.id}>
                    <th scope="row" style={{ ...cell, fontFamily: mono, textAlign: "left" }}>{h.id}</th>
                    <td style={cell}>{h.claim}</td>
                    <td style={{ ...cell, color: "var(--gray)" }}>{h.test}</td>
                    <td style={{ ...cell, fontFamily: mono, fontSize: "0.78rem", textTransform: "uppercase", whiteSpace: "nowrap" }}>{h.status}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}

      <h3 style={h3}>Limits</h3>
      <ul style={{ margin: 0, paddingLeft: "1.1rem" }}>
        {r.limits.map((l, i) => (
          <li key={i} style={{ ...body, margin: "0 0 0.4rem" }}>{l}</li>
        ))}
      </ul>
    </article>
  );
}

export default function Ari3Page() {
  return (
    <main id="main-content" style={{ flex: 1, background: "var(--white)", display: "flex", flexDirection: "column", alignItems: "center" }}>
      <header className="page-masthead">
        <h1 className="page-title">ARI3</h1>
      </header>

      <section style={{ width: "100%", maxWidth: "820px", padding: "3.5rem 1rem 5rem" }}>
        <p style={{ ...body, fontSize: "1.05rem", color: "var(--black)" }}>
          ARI3 is the model system behind ARI3LLA INDEX. This page is its release ledger. Every
          version is frozen, hashed and committed to the public repository before its results appear here, and
          every experiment states its pass criteria before it runs. A frozen version is never
          retrained, and results are reported whether they hold or fail.
        </p>
        <p style={body}>
          ARI3 v0.0.1, the current frozen version, reads a news item&apos;s headline and feed excerpt,
          judges whether the item is about style, and says when it is not sure. Items it flags as
          uncertain are meant for the editor&apos;s review. ARI3 v0.0.2 is planned and not yet
          trained. No ARI3 version forecasts, ranks trends or writes reports.
        </p>

        {RELEASES.map((r) => (
          <ReleaseCard key={r.version} r={r} />
        ))}

        <div style={{ borderTop: "2px solid var(--black)", paddingTop: "1.5rem", marginTop: "3.5rem" }}>
          <h2 style={{ fontFamily: "var(--font-instrument)", fontSize: "1.8rem", fontWeight: 400, margin: "0 0 0.75rem" }}>
            Checking a release
          </h2>
          <p style={body}>
            Each release links to its commit, whose timestamp is recorded by GitHub. To confirm a file
            is the one committed, download it from the linked commit and compare its SHA-256 hash with
            the one listed. The manifest entry lists the manifest&apos;s internal <code style={{ fontFamily: mono }}>manifest_sha256</code> field,
            which the manifest file itself states.
          </p>
          <pre
            style={{
              fontFamily: mono,
              fontSize: "0.8rem",
              background: "var(--black)",
              color: "var(--white)",
              padding: "1rem",
              overflowX: "auto",
              margin: 0,
            }}
          >
{`git clone ${REPO}.git
cd fashion-trend-crawler
git show 79e95bc:models/ari3-v0.0.2/PREREGISTRATION.md | sha256sum
git show 9c296bd:models/ari3-v0.0.1/weights.npz | sha256sum`}
          </pre>
        </div>
      </section>
    </main>
  );
}
