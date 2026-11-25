// app/taxonomy/page.tsx
// Taxonomy in the photocopy edition: the controlled vocabulary as ledger tables.

import Link from "next/link";
import { pageMetadata } from "../../lib/site";
import { Folio } from "../components/Chrome";

export const metadata = pageMetadata("/taxonomy", "Taxonomy", "The controlled vocabulary behind ARI3LLA INDEX reports: signal types, confidence levels, volatility labels and origin classifications.");

const signalTypes = [
  "Garment", "Silhouette", "Material", "Color", "Styling behavior", "Aesthetic term",
  "Commerce language", "Cultural reference", "Brand behavior", "Platform behavior",
  "Designer-origin signal", "Retail adoption signal", "Visual mood", "Accessory signal",
  "Beauty/fragrance signal", "Lifestyle signal",
];

type Row = { label: string; def: string };

const sourceSectors: Row[] = [
  { label: "Designer-origin", def: "Official brand websites, collection pages, show notes, lookbooks, campaign pages, press releases, designer interviews, creative director statements." },
  { label: "Runway", def: "Show coverage, show notes and look-by-look records of collections." },
  { label: "Editorial", def: "Style publications reporting on collections, designers and seasonal direction." },
  { label: "Retail", def: "Product titles, category names, new arrivals, material and color labels, styling copy, sold-out language, retailer trend edits." },
  { label: "Social", def: "Captions, comments and creator content on platforms such as TikTok, Instagram, YouTube, Reddit and Pinterest, collected through official reports, APIs or manual sampling." },
  { label: "Visual archive", def: "Visual search and reference platforms, used to observe recurring imagery." },
  { label: "Independent criticism", def: "Substack fashion writers, independent newsletters, long-form blogs, and cultural commentary outside institutional media." },
  { label: "Institutional", def: "Museum collections, costume history databases, academic papers, and archival runway records." },
  { label: "Street and user-generated", def: "Street style photography and public outfit documentation, distinct from platform-native captions and comments." },
  { label: "Resale", def: "Secondhand marketplace listings and descriptions, tracked separately from primary retail." },
  { label: "Trade intelligence", def: "B2B commercial trend-forecasting and retail-analytics vendors, whose public content markets a paid prediction or merchandising product rather than reporting independently on discourse. Excluded from high-reliability sectors." },
];

const volatility: Row[] = [
  { label: "Stable", def: "Consistent presence with no strong upward or downward movement." },
  { label: "Emerging", def: "Newly appearing with early but not yet broad recurrence." },
  { label: "Seasonal", def: "Tied to a predictable calendar, weather, or retail rhythm." },
  { label: "Volatile", def: "Fluctuates quickly, concentrated in short-cycle or platform-driven sources." },
  { label: "Flash", def: "Appears suddenly in high-noise sources with little broader support." },
  { label: "Microtrend", def: "Visible in social/platform language but likely short-cycle." },
  { label: "Recurring", def: "Appears repeatedly across reports over time." },
  { label: "Revival", def: "Clearly connected to a previous era or documented style cycle." },
  { label: "Long-tail", def: "Not dominant but continues appearing over an extended period." },
  { label: "Saturated", def: "Over-repeated, likely near exhaustion." },
  { label: "Declining", def: "Mentions or coherence are decreasing over successive reports." },
];

const confidence: Row[] = [
  { label: "Low", def: "Appears in one noisy source type or weakly across sources." },
  { label: "Medium", def: "Appears across two or more source types with some language consistency." },
  { label: "High", def: "Appears across multiple distinct sectors, such as designer, editorial, retail, social, and visual search." },
  { label: "Archival", def: "Recurring across multiple time periods or connected to documented historical cycles." },
];

const originClassification: Row[] = [
  { label: "Designer-originated", def: "Traced to a brand or creative team's own material (collection pages, show notes, campaigns, interviews) before any outside interpretation." },
  { label: "Editorial-amplified", def: "Carried into wider discourse primarily through runway coverage or style-publication interpretation of what a designer showed or meant." },
  { label: "Retail-adopted", def: "Carried into wider discourse primarily through product naming, category language, or trend-edit copy applied at the point of sale." },
  { label: "Social-amplified", def: "Carried into wider discourse primarily through platform captions, comments, or creator content, independent of editorial or retail framing." },
  { label: "Platform-native", def: "Originates on a social platform itself, with no clear designer, editorial, or retail point of origin." },
  { label: "Archive revival", def: "Traced to a previously documented style cycle or archival record resurfacing rather than a new origin point." },
  { label: "Unclear", def: "No reliable origin point could be established from available sources." },
];

function Ledger({ caption, head, rows }: { caption: string; head: string; rows: Row[] }) {
  return (
    <div className="table-wrap">
      <table className="ledger">
        <caption className="sr-only">{caption}</caption>
        <thead>
          <tr><th scope="col">{head}</th><th scope="col">Definition</th></tr>
        </thead>
        <tbody>
          {rows.map((r) => (
            <tr key={r.label}>
              <td className="s">{r.label}</td>
              <td>{r.def}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default function Taxonomy() {
  return (
    <main id="main-content">
      <Folio h1 left="Taxonomy" right="Five dimensions of classification" />
      <p className="lede-intro">
        Signals are classified along five dimensions: signal type, source sector, volatility,
        confidence, and origin classification. This page does not define style or aesthetic
        terms such as quiet luxury. Those are on the <Link href="/glossary">Glossary</Link> page.
      </p>

      <section aria-labelledby="h-types">
        <h2 className="sec" id="h-types">Signal types</h2>
        <div className="cols three">
          <ul className="bul">{signalTypes.map((t) => <li key={t}>{t}</li>)}</ul>
        </div>
      </section>

      <section aria-labelledby="h-sectors">
        <h2 className="sec" id="h-sectors">Source sectors</h2>
        <Ledger caption="Source sectors and what each covers" head="Sector" rows={sourceSectors} />
      </section>

      <section aria-labelledby="h-volatility">
        <h2 className="sec" id="h-volatility">Volatility labels</h2>
        <Ledger caption="Volatility labels and their definitions" head="Label" rows={volatility} />
      </section>

      <section aria-labelledby="h-confidence">
        <h2 className="sec" id="h-confidence">Confidence levels</h2>
        <Ledger caption="Confidence levels and their definitions" head="Level" rows={confidence} />
      </section>

      <section aria-labelledby="h-origin">
        <h2 className="sec" id="h-origin">Origin classification</h2>
        <div className="cols one">
          <p>
            Origin is recorded separately from confidence and volatility. It keeps apart what a
            designer made, what editors said it meant, what retailers sold it as and what a platform
            renamed it.
          </p>
        </div>
        <Ledger caption="Origin classifications and their definitions" head="Origin" rows={originClassification} />
      </section>
    </main>
  );
}
