// app/case-study/page.tsx
// Case study in the photocopy edition: one long article in a single column.

import { pageMetadata } from "../../lib/site";
import { Folio } from "../components/Chrome";

export const metadata = pageMetadata("/case-study", "Case study", "How ARI3LLA INDEX is built: the evidence standard, the data pipeline, the report schema and the static site, including current limitations.");

const sections: { title: string; body: string[] }[] = [
  {
    title: "Problem",
    body: [
      "Style discourse moves quickly across platforms, editorial media, retail copy, and brand campaigns. Signals are often flattened into trends without source context, historical memory, or incentive analysis.",
    ],
  },
  {
    title: "Goal",
    body: [
      "A public, dated record of style language: what is being named, where it first appears, and how it moves between runway, editorial, social, retail, and resale sources. Every claim links to the specific source it rests on. No shopping advice and no forecasting.",
    ],
  },
  {
    title: "What exists",
    body: [
      "A robots.txt-respecting ingester that reads outlet RSS and Atom feeds and stores each item with its URL, publish date and a content hash in a SQLite item store. A source taxonomy that maps more than 125 outlets to sectors, including publications outside the English-speaking press. A report schema with controlled vocabularies, and a publish gate in CI that rejects future-dated reports and any claim without a linked article. A static Next.js site with an archive, a timeline, per-signal histories, full-text search, RSS and structured data.",
    ],
  },
  {
    title: "Design system",
    body: [
      "Editorial tone, restrained typography, clear hierarchy and an index-like structure. Report pages carry structured data, a stable citation line and real heading markup for screen readers.",
    ],
  },
  {
    title: "Evidence standard",
    body: [
      "A claim is published only with a link to a specific, dated article or record. An outlet's homepage is not evidence. A report may not be dated after the day it is published. Signals are weighed by recurrence, source diversity, source incentive, visual coherence, and historical continuity, and confidence is stated plainly, including when it is low.",
    ],
  },
  {
    title: "Human and machine",
    body: [
      "Software collects items and extracts style terms. It does not decide what matters. Interpretation, naming, and the human-editor note on each signal belong to the editor. Social platforms will be sampled only through official APIs or by hand, never by scraping, and none is sampled yet. Runway images are linked, never rehosted.",
    ],
  },
  {
    title: "Current limitations",
    body: [
      "The archive grows only with reports whose every claim links to a dated, fetched source. Since 2026-10-07 a scheduled job prepares each week's candidates and draft from the item store, and the editor decides and approves every report. Most collected sources are editorial, because brand, retail and resale sites rarely publish dated feeds. Social data waits on access to official platform APIs.",
    ],
  },
  {
    title: "Next",
    body: [
      "Style terms are extracted from stored items with Lexicon v1, and each weekly window is scored and extracted when it closes. Next are per-term pages that show where a term first appeared and how it moved between sectors.",
    ],
  },
];

const slug = (s: string) => s.toLowerCase().replace(/[^a-z0-9]+/g, "-");

export default function CaseStudy() {
  return (
    <main id="main-content">
      <Folio left="Case study" right={`${sections.length} sections`} />
      <h1 className="hed md toner">Building a weekly style signal report</h1>
      <article className="prose">
        {sections.map((s) => (
          <section key={s.title} aria-labelledby={`h-${slug(s.title)}`}>
            <h2 id={`h-${slug(s.title)}`}>{s.title}</h2>
            {s.body.map((p, j) => <p key={j}>{p}</p>)}
          </section>
        ))}
      </article>
    </main>
  );
}
