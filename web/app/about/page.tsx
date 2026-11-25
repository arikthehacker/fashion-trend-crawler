// app/about/page.tsx
// About in the photocopy edition: the colophon, with text on the left and the staff box on the right.

import Link from "next/link";
import { EDITOR_LABEL, pageMetadata } from "../../lib/site";
import { CONTACT_EMAIL, ISSUES_URL, REPO_URL } from "../../lib/nav";
import { Folio } from "../components/Chrome";

export const metadata = pageMetadata("/about", "About", "What ARI3LLA INDEX is and is not: an independent, source-linked archive of style language, its editorial independence, AI use and corrections policy.");

const IS_NOT = ["Trend forecasting", "Fashion blogging", "Shopping recommendation", "Brand analytics", "A TikTok trend recap", "AI-generated taste", "Influencer commentary"];
const IS = ["Source-linked reporting", "Style signal indexing", "A public archive", "Cultural documentation", "Style discourse tracked by source and incentive", "Human-edited research"];

export default function About() {
  return (
    <main id="main-content">
      <Folio left="About" />
      <div className="colophon">
        <div>
          <h1 className="hed md toner">About this paper</h1>
          <div className="cols drop">
            <p>ARI3LLA INDEX is a weekly style signal report. It collects public style discourse from across the web, classifies signals by source sector and volatility, and preserves them as dated reports.</p>
            <p>It does not predict what people should wear or what brands should sell. It tracks what style culture is naming, repeating, reviving and absorbing, with attention to source incentives, platform noise, visual coherence and historical continuity.</p>
            <p>ARI3LLA INDEX does not issue guidance on how readers should dress or live. It documents the sources, incentives and language that shape style discourse.</p>
          </div>

          <h2 className="sec">What the index is and is not</h2>
          <div className="pair">
            <div>
              <h3>This index is not</h3>
              <ul className="bul">{IS_NOT.map((x) => <li key={x}>{x}</li>)}</ul>
            </div>
            <div>
              <h3>This index is</h3>
              <ul className="bul">{IS.map((x) => <li key={x}>{x}</li>)}</ul>
            </div>
          </div>

          <h2 className="sec">Independence, corrections and AI use</h2>
          <div className="cols">
            <p>ARI3LLA INDEX is not sponsored by or affiliated with any brand, publication, retailer or platform named in its reports. Editorial sources are cited as a source sector with its own commercial incentives, not treated as neutral authority.</p>
            <p>ARI3LLA INDEX is an independent research project built and maintained by one researcher and developer. Its source code is public. It has no editorial board, owners or funding to disclose.</p>
            <p>Software collects items and extracts style terms, and ARI3, a machine-learning model, flags which items are about style. Software does not decide what matters. Every claim in a report links to a specific, dated source, and a report is published only after human review. Each report states its recorded software or AI assistance, or says when those details were not recorded. The human-editor note on each signal is written by the editor, never by software.</p>
            <p>Errors in a published report are not silently edited. A dated correction is added to the report and the original entry is kept. Suspected errors can be reported by email to <a href={`mailto:${CONTACT_EMAIL}`}>{CONTACT_EMAIL}</a> or as an issue on the <a href={ISSUES_URL} rel="noopener noreferrer">project&apos;s public repository</a>. The full process is on the <Link href="/methodology">How it works</Link> page.</p>
          </div>
        </div>

        <aside aria-label="Masthead">
          <dl className="staff">
            <dt>Editor and developer</dt>
            <dd>The {EDITOR_LABEL.toLowerCase()}</dd>
            <dt>Model</dt>
            <dd><Link href="/ari3">ARI3</Link>, a machine-learning model that flags which items are about style</dd>
            <dt>Funding</dt>
            <dd>None to disclose. No owners, sponsors or editorial board</dd>
            <dt>Corrections and tips</dt>
            <dd><a href={`mailto:${CONTACT_EMAIL}`}>{CONTACT_EMAIL}</a></dd>
            <dt>Source code</dt>
            <dd><a href={REPO_URL} rel="noopener noreferrer">{REPO_URL.replace(/^https:\/\//, "")}</a></dd>
          </dl>
        </aside>
      </div>
    </main>
  );
}
