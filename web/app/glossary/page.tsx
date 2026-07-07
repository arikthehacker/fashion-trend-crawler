// page.tsx
// glossary page for ARI3LLA INDEX — weekly style signal report
// doc section 24: "style terms, aesthetic terms, recurring classifications"
//
// Terms are sourced from the archive's aesthetic_terms, cultural_references, and
// top_signals[].name fields (data/reports/*.json), read at build time and matched
// against a curated definition set below. Only terms that actually appear in the
// archive are rendered, so the glossary stays tied to what the Index has observed
// rather than an abstract style dictionary. Distinct from /taxonomy, which documents
// the classification system rather than the aesthetic terms themselves.

import Link from "next/link";
import { getAllReports } from "../../lib/reports";

interface ReportShape {
  aesthetic_terms?: string[];
  cultural_references?: string[];
  top_signals?: { name?: string }[];
}

// Curated short definitions in wire-service voice. Only terms that are found in
// at least one archived report are rendered — this dictionary intentionally
// includes more entries than any single report so it stays valid as new reports
// are added; entries never observed in the archive are simply not shown.
const DEFINITIONS: Record<string, string> = {
  "1970s boho": "A style reference to loose, textured, folk-influenced dressing associated with the 1970s, cited when current coverage draws an explicit historical parallel.",
  "1990s minimalism": "A pared-back, low-ornamentation aesthetic associated with 1990s fashion, referenced when current minimal styling is framed as a revival rather than a new development.",
  "1990s sitcom style": "A style reference to the casual, brand-forward dressing seen in 1990s American television, cited as a visual shorthand rather than a designer-originated term.",
  "archival romanticism": "Styling that draws visibly on historical or archival garment references — antique construction, period silhouettes, preserved detailing — presented as romantic rather than costume-like.",
  "aspirational realism": "A menswear framing describing loose, soft, muted tailoring positioned as attainable rather than formal or overtly luxury-coded.",
  "boho revival": "A recurrence of loose, layered, folk- and craft-influenced dressing associated with earlier bohemian style cycles.",
  "bug-eye sunglasses": "Oversized, rounded, wraparound-style sunglasses noted repeatedly across sources as a recurring accessory shape.",
  "coastal cowgirl": "A styling term combining beach-adjacent casualwear with Western references such as denim, fringe, and boots.",
  "color drenching": "A styling approach of dressing in a single color head-to-toe, including accessories, rather than mixing multiple colors in one look.",
  "eighties luxury": "A style reference to the structured, high-shine, status-signaling dressing associated with 1980s luxury fashion.",
  "funmaxxing": "A maximalist-play aesthetic cluster observed on TikTok combining icy-blue and candy-pink palettes, 1980s technical sportswear, and tassels or fringe; logged as the narrower, checkable styling cluster rather than the broader generational-mood framing some coverage has attached to the term.",
  "layered tops styling": "A styling pattern of wearing multiple visible top layers — camisoles, shirts, sweaters — rather than a single garment, observed primarily in social-platform sources.",
  "maximalism": "A styling approach favoring visible pattern mixing, layering, color, and ornamentation, framed in coverage as a counterpoint to pared-back minimalism.",
  "micro-bag styling": "The continued presence of small, low-capacity handbags as a recurring accessory signal rather than a newly emerging one.",
  "off-duty varsity": "A styling pattern combining sports-team jerseys or collegiate references with casual, non-athletic pieces such as cargo bottoms.",
  "office siren": "A style reference combining traditionally formal, buttoned-up officewear with more overtly styled or revealing elements.",
  "peplum / exaggerated-waistline revival": "A silhouette signal describing the recurrence of flared, structured, or exaggerated waist treatments, tracked across several reports as a forecast-stage signal not yet confirmed at retail.",
  "poetcore": "A dark-academia-adjacent, literary-coded aesthetic term originating on Pinterest, associated with muted tones and vintage-inflected styling.",
  "preppy layering": "A styling pattern combining traditionally preppy garments — collared shirts, sweater vests, knee socks — in layered combinations.",
  "preppy uniform dressing": "Styling that borrows structural elements of school-uniform dressing — collars, pleats, knee-length hems — read through a preppy aesthetic lens.",
  "quiet luxury": "A style term describing unbranded, understated, high-quality dressing that avoids visible logos or overt status signaling.",
  "saturated purple": "A specific, highly pigmented shade of purple noted as a recurring dominant color across a reporting period.",
  "sheer layering": "A styling pattern combining sheer or transparent fabrics with opaque layers underneath or over them.",
  "soft minimalism": "A minimalist styling approach that favors rounded silhouettes and softer fabrics over the sharper, more austere lines of earlier minimalist cycles.",
  "soft tailoring": "Tailoring that retains structured garment shapes — blazers, trousers — while using looser fit and softer fabrication than traditional formal tailoring.",
  "textured maximalist layering": "A styling pattern combining multiple contrasting textures — fur, sheer fabric, denim — within a single maximalist look.",
  "uneven and handkerchief-hem silhouettes": "Garment hems cut at asymmetric or angular lengths rather than a uniform hemline, named for their resemblance to a folded handkerchief corner.",
  "utility belt": "A wide, hardware-heavy belt style referencing workwear and functional gear rather than purely decorative belting.",
  "victorian undergarments": "A historical reference to 19th-century foundation garments — corsetry, underpinnings — cited when current silhouettes are read as drawing on that period.",
  "y2k nostalgia": "A style reference to early-2000s fashion — low-rise cuts, logo-forward branding, metallics — recurring across reports as a sustained rather than one-off revival.",
  "1990s minimalism revival": "A pared-back, low-ornamentation aesthetic associated with 1990s fashion, referenced when current minimal styling is framed as an explicit historical revival.",
  "1970s 'boho' revival styling": "A recurrence of loose, textured, folk-influenced dressing associated with 1970s fashion, cited when current coverage draws an explicit period parallel.",
  "resale/secondhand retail growth": "Continued expansion of secondhand and resale clothing sales as a retail category, tracked as a structural market trend rather than a seasonal style signal.",
  "coastal-cowgirl styling evolution": "Continued change in the coastal cowgirl styling term — combining beach-adjacent casualwear with Western references such as denim, fringe, and boots — tracked across reports as the specific combination of elements shifts.",
  "2026 fifa world cup": "The 2026 FIFA World Cup, a men's international soccer tournament co-hosted by the United States, Canada, and Mexico, cited as a source of team-branded and sport-referencing style coverage.",
  "oversized 'bug-eye' sunglasses": "Oversized, rounded, wraparound-style sunglasses noted repeatedly across sources as a recurring accessory shape.",
  "utility-detailed belts": "Wide, hardware-heavy belt styles referencing workwear and functional gear rather than purely decorative belting.",
  "copenhagen fashion week ss27": "Copenhagen Fashion Week's Spring/Summer 2027 runway season, cited as a designer-origin source event for signals tracked in that reporting window.",
  "collina strada international guest slot": "A guest-designer or guest-show slot on an international fashion week schedule occupied by the New York-based label Collina Strada, cited as a designer-origin sourcing event.",
  "cfda september 2026 nyfw schedule": "The Council of Fashion Designers of America's published show schedule for New York Fashion Week in September 2026, cited as a designer-origin source document.",
  "pre-fashion-week anticipation": "Coverage published ahead of a fashion week's official start that speculates about or previews upcoming shows, tracked as anticipatory rather than confirmed-runway coverage.",
  "cfda fur-free policy": "A policy position from the Council of Fashion Designers of America addressing the use of fur in member designers' collections, cited as an institutional-sector source.",
  "cfda/vogue fashion fund 2026": "The 2026 cycle of the CFDA/Vogue Fashion Fund, an annual award and mentorship program for emerging American designers jointly run by the CFDA and Vogue.",
  "rachel comey 25th anniversary": "The 25th anniversary of designer Rachel Comey's eponymous label, cited as a designer-origin milestone event.",
  "conner ives nyfw debut": "Designer Conner Ives's first runway show at New York Fashion Week, cited as a designer-origin sourcing event.",
  "magda butrym nyfw debut": "Designer Magda Butrym's first runway show at New York Fashion Week, cited as a designer-origin sourcing event.",
  "nostalgic maximalism": "A styling approach combining heavy pattern, color, and ornamentation with explicit references to past decades, distinguishing it from maximalism that is not tied to a specific historical period.",
  "leisure dressing": "A styling category built around loose, comfort-oriented garments — sweats, knits, soft tailoring — worn outside a strictly athletic or at-home context.",
  "beaded jewelry and accessory revival": "A recurrence of beaded necklaces, bracelets, and bag or garment trim as a noted accessory category, tracked as a return of a previously common styling element.",
  "met gala 2027 coverage gap": "A tracked absence of confirmed reporting on the 2027 Met Gala's theme, guest list, or outcomes during a window when such coverage would typically be expected.",
  "precision over spectacle": "An editorial framing describing tailoring or styling choices as controlled and exact rather than dramatic or attention-seeking.",
  "old hollywood glamour": "A style reference to the polished, formal, high-shine dressing associated with mid-20th-century American film stars, cited when current styling draws an explicit historical parallel.",
  "marlene dietrich": "A mid-20th-century American film actress cited as a historical style reference point, typically for tailored menswear-influenced womenswear.",
  "ed ruscha": "An American visual artist cited as a reference point when coverage draws a parallel between his work and current design or styling choices.",
  "nautical revival": "A recurrence of maritime-referencing styling elements — stripes, rope detailing, navy-and-white palettes — associated with earlier nautical style cycles.",
  "mermaidcore": "An aesthetic term describing styling built around iridescent, scaled, or water-associated textures and a blue-green color palette.",
  "1920s chanel sportswear/workwear codes": "A historical reference to sportswear and workwear-influenced garment codes established by Chanel in the 1920s, cited when current designs draw an explicit lineage to that period.",
  "biarritz basque coastal heritage": "A regional style reference to the coastal Basque resort town of Biarritz, France, cited when current collections or coverage draw on its historical association with leisurewear.",
  "glamoratti": "A styling term combining high-glamour dressing with an exaggerated, theatrical sensibility, used in trend-forecasting coverage.",
  "pinterest predicts annual trend report": "Pinterest's yearly published forecast of anticipated style and lifestyle trends, cited as a social-platform source rather than an editorial or retail one.",
  "miximalism": "A styling term describing the deliberate mixing of disparate patterns, textures, or eras within a single maximalist look.",
  "new naturalism": "A styling framing favoring muted, earth-toned palettes and unstructured, texture-forward garments positioned as a counterpoint to more polished aesthetics.",
  "human craft vs ai": "A framing used in coverage to contrast garments or design work presented as handmade or artisan-produced against AI-generated or AI-assisted design and imagery.",
  "messy chic": "A styling term describing deliberately undone, imperfect hair, makeup, or garment styling presented as an aesthetic choice rather than an oversight.",
  "deconstructed tailoring": "Tailoring that exposes or leaves visible its own construction — raw seams, unfinished edges, visible interfacing — rather than concealing it, associated with the deconstructivist design lineage.",
  "raw-edge finishing": "A garment-finishing technique that leaves fabric edges unhemmed or unbound, exposing raw or fraying edges as a deliberate design choice rather than an incomplete one.",
  "glenn martens": "A Belgian designer who became creative director of Maison Margiela in 2027, cited as a designer-origin reference when coverage tracks his design choices there.",
  "maison margiela": "A Paris-based fashion house founded by Martin Margiela in 1988, known for deconstructivist design, cited as a designer-origin source when its runway or retail output is tracked.",
  "paris fashion week": "The Paris leg of the international ready-to-wear fashion week circuit, cited as a designer-origin source event when collections shown there are tracked.",
  "ssense": "A Montreal-based online luxury and streetwear retailer, cited as a retail-adoption source when its buying or merchandising decisions are tracked.",
  "tiktok": "A short-form video social media platform, cited as a social-amplification source sector when style content circulating there is tracked.",
  "fhcm": "The Fédération de la Haute Couture et de la Mode, the organizing body that publishes the official Paris fashion week and haute couture show calendars, cited as an institutional-sector source.",
  "who what wear": "An online fashion and style publication, cited as an editorial-sector source when its coverage is tracked.",
  "vogue": "A Conde Nast fashion and lifestyle publication, cited as an editorial-sector source when its coverage is tracked; distinct from the CFDA/Vogue Fashion Fund, a separate jointly run award program.",
  "cfda": "The Council of Fashion Designers of America, a nonprofit trade association of American fashion designers, cited as an institutional-sector source.",
  "new york fashion week": "The New York leg of the international ready-to-wear fashion week circuit, cited as a designer-origin source event when collections shown there are tracked.",
  "retro sexiness": "A styling framing describing overtly body-conscious, revealing garment choices presented as a deliberate historical throwback rather than a new development.",
  "demna": "A Georgian-born designer known for his tenure at Balenciaga, who became creative director of Gucci in 2027, cited as a designer-origin reference when coverage tracks his design choices there.",
  "gucci": "An Italian luxury fashion house, cited as a designer-origin source when its runway or retail output is tracked.",
  "balenciaga": "A Paris-based luxury fashion house, cited as a designer-origin source when its runway, retail, or archival output is tracked.",
  "demna's gucci debut reception": "Critical and retail response to Demna's first collection as Gucci's creative director, tracked as a designer-origin signal pending confirmation of retail follow-through.",
  "deconstructivist": "A design approach that exposes, disrupts, or reworks a garment's own construction — visible seams, asymmetric cutting, unfinished edges — rather than presenting a conventionally finished silhouette.",
  "unfinished seams": "Garment seams left raw, exposed, or without a concealing finish, used as a deliberate construction detail rather than left incomplete.",
  "martin margiela": "The Belgian designer who founded Maison Margiela in 1988 and pioneered deconstructivist design, cited as a historical reference point when current design work is read against his legacy.",
  "john galliano": "A British designer known for past tenures at Givenchy, Dior, and Maison Margiela, cited as a historical or comparative reference point in coverage of designer transitions.",
  "martens' margiela debut reception": "Critical and retail response to Glenn Martens's first collection as Maison Margiela's creative director, tracked as a designer-origin signal pending confirmation of retail follow-through.",
  "charvet": "A Paris-based shirtmaker and menswear house on Place Vendôme, cited as a designer-origin source when its acquisition or output is tracked.",
  "matthieu blazy": "A Belgian-Italian designer who became creative director of Chanel in 2024, cited as a designer-origin reference when coverage tracks his design choices there.",
  "place vendome": "A historic square in Paris associated with high-jewelry and luxury houses, cited as a location reference when coverage ties a brand or event to that district.",
  "chanel acquires charvet": "Chanel's acquisition of the Paris shirtmaker Charvet, tracked as a designer-origin business signal rather than a styling trend.",
  "shock-casting": "A runway casting strategy that deliberately selects provocative, controversial, or attention-drawing models or presenters to generate coverage and social discussion.",
  "attention-economy runway": "A framing describing runway shows staged or cast primarily to maximize social-media and press attention rather than to present a collection on its own terms.",
  "clavicular / braden peters": "An independent designer label operating under the name Clavicular, headed by designer Braden Peters, cited as a designer-origin source in coverage of provocative-casting runway strategy.",
  "424": "A Los Angeles-based streetwear-adjacent fashion label, cited as a designer-origin source in coverage of provocative-casting runway strategy.",
  "spectacle staging": "A runway or show-production approach built around a dramatic physical setting or production element intended to generate coverage beyond the garments themselves.",
  "climate-optics backlash": "Critical response to a fashion event or staging choice read as tone-deaf against a concurrent climate event, such as extreme weather.",
  "2026 european heatwave": "An extreme-heat weather event across Europe in 2026, cited as context when a concurrent fashion event's staging drew climate-optics criticism.",
  "preppy tailoring": "Tailoring that incorporates traditionally preppy design cues — collars, blazers, structured proportions — within an otherwise formal tailored garment.",
  "nature motif embroidery": "Embroidered or applied decoration depicting botanical or natural imagery — florals, leaves, insects — as a garment's primary surface decoration.",
  "palazzo serbelloni": "A historic Milan palazzo used as a runway show venue, cited as a location reference for the show staged there.",
  "milan men's fashion week ss27": "The Milan leg of the international menswear fashion week circuit for the Spring/Summer 2027 season, cited as a designer-origin source event.",
  "archival reverence": "A design or editorial framing that treats a house's or designer's historical archive as a primary reference point, presented as respectful continuation rather than pastiche.",
  "paris haute couture week": "The Paris haute couture show season, distinct from ready-to-wear fashion week, cited as a designer-origin source event for made-to-order collections.",
  "cristobal balenciaga archive": "The historical design archive of the house's founder, Cristóbal Balenciaga, cited as a reference point when current collections draw on his original work.",
  "tenniscore": "A styling term describing tennis-inspired garments and accessories — pleated skirts, polo shirts, headbands — worn outside an athletic context.",
  "wimbledon 2027": "The 2027 edition of the Wimbledon tennis championships, cited as a source event for tennis-adjacent style coverage.",
  "spectator style": "Dressing associated with attending, rather than competing in, a sporting event — tailored but occasion-specific rather than purely athletic.",
  "royal courtside style": "Style coverage focused on members of the British royal family's dress choices while attending a sporting event, such as Wimbledon.",
  "wimbledon 2027 tenniscore event dressing": "Style coverage of tennis-inspired dressing tied specifically to attendance at the 2027 Wimbledon championships.",
  "blokecore": "A styling term describing casual dressing built around football (soccer) jerseys and related fan apparel, worn outside a sporting context.",
  "royal ascot": "An annual British horse race meeting known for its formal dress code, cited as a source event for occasion-dressing style coverage.",
  "expressive dressing": "A styling framing describing bold, individualized garment or color choices presented as self-expression rather than following a single prevailing trend.",
  "archive revival": "The reintroduction or reference of a house's past archival designs into current collections or coverage, distinct from a broader historical-era revival.",
  "unfinished seam": "A garment seam left raw, exposed, or without a concealing finish, used as a deliberate construction detail rather than left incomplete.",
  "net-a-porter": "A London-based online luxury retailer, cited as a retail-adoption source when its buying or merchandising decisions are tracked.",
  "antwerp six": "A group of six designers who graduated from Antwerp's Royal Academy of Fine Arts in the 1980s and became associated with a shared deconstructivist design lineage, cited as a historical reference point for that design approach.",
  "return to structure": "An editorial framing describing a shift toward defined, structured garment shapes -- tailoring, boning, waist definition -- as a counterpoint to looser or unstructured silhouettes, tracked across resort 2028 coverage.",
  "waist definition": "A silhouette signal describing garments that visibly shape or emphasize the waist -- boning, corseting, structured waistbands -- as distinct from a looser or undefined torso line.",
  "bogota fashion week": "Bogota's market-week fashion showcase, organized in coordination with Inexmoda, Colombia's fashion and textile institute, cited as an institutional-sector source event for Latin American runway and market coverage.",
  "inexmoda": "Instituto para la Exportacion y la Moda, Colombia's nonprofit fashion and textile industry institute, which organizes the Bogota-area Colombiatex and Colombiamoda trade fairs and publishes trend and market research, cited as an institutional-sector source.",
  "farfetch": "A London-based online luxury fashion marketplace, cited as a retail-adoption source when its buying or merchandising decisions are tracked.",
  "corseted waistband": "A boned or structured waistband worn as an outer garment element, typically over softer fabrication such as jersey or shirting, rather than as a concealed undergarment.",
  "shirting": "Lightweight woven fabric traditionally used for dress shirts, cited as a material when it appears in a garment or silhouette outside its conventional shirt context.",
  "structured waist": "A silhouette built around a defined, shaped waistline -- through boning, corsetry, or structured tailoring -- rather than a loose or undefined torso line.",
  "boning": "Rigid or semi-rigid strips inserted into a garment, traditionally into corsetry, to hold and shape its structure, cited as a material/construction element when used to create a defined silhouette.",
  "silhouette echo": "A term describing the independent, apparently uncoordinated appearance of the same garment silhouette across separate designers or market weeks, without one citing or responding to the other -- distinct from a trend that spreads by direct citation or retail adoption.",
  "ffw": "FFW (ffw.com.br), an independent Brazilian fashion and culture editorial platform, cited as an editorial-sector source for South American runway and market coverage.",
  "sao paulo fashion week": "Sao Paulo's market-week fashion showcase, cited as a source event for South American runway and resort-collection coverage.",
  "dieworkwear": "Dieworkwear.com, an independent menswear and tailoring criticism site, cited as an independent-criticism-sector source.",
  "business of fashion": "Business of Fashion (businessoffashion.com), a trade and industry-news editorial title, cited as an editorial-sector source.",
  "opera gloves": "Long gloves extending past the elbow, traditionally worn with formal eveningwear, cited when current styling or retail coverage revives them as an occasion-dressing element.",
  "awards season dressing": "Style coverage tied to the period surrounding televised or industry award ceremonies, tracked as occasion-specific rather than everyday styling.",
  "british fashion awards": "An annual British Fashion Council ceremony recognizing designers and industry figures, cited as a source event for pre-ceremony occasion-dressing style coverage.",
  "restraint dressing": "A critical framing describing covered-hand, high-neckline eveningwear as a deliberate counterpoint to overtly skin-baring red-carpet styling, proposed in independent-criticism commentary rather than by a designer or retailer.",
  "chanel": "A Paris-based luxury fashion house, cited as a designer-origin source when its runway, resort, or retail output is tracked.",
  "gift-wrap dressing": "A social-platform styling term for bow-and-ribbon accent detailing added to coats, bags, or hair, observed circulating on TikTok during the Black Friday/Cyber Monday holiday shopping window; tracked as a single-source, platform-native signal, not yet picked up editorially or at retail.",
  "obi-sash cocoon coat": "A rounded, sculpted cocoon-shaped coat closed with a wide obi-style sash tied at the waist, observed across resort 2028 previews from multiple houses.",
  "cocoon silhouette": "A rounded, voluminous garment shape that tapers inward at the hem, named for its resemblance to a cocoon rather than a fitted or A-line cut.",
  "elle": "A fashion and lifestyle magazine title, cited as an editorial-sector source when its coverage is tracked.",
  "dior": "A Paris-based luxury fashion house, cited as a designer-origin source when its runway, resort, or retail output is tracked.",
  "the realreal": "An online resale and consignment marketplace for luxury goods, cited as a resale-sector source when its search-demand or listing data is tracked.",
  "puffer-shell skirt": "A voluminous, quilted skirt built with exaggerated, rounded volume at the hip and hem, using puffer-jacket-style quilted construction on a bottom garment rather than an outerwear piece.",
  "quilted puffer-shell silhouette": "A rounded, exaggerated-volume garment shape produced by puffer-jacket-style quilted construction, distinct from the tapered cocoon silhouette in that its volume is evenly quilted rather than smoothly sculpted.",
  "shawl-collar overcoat": "An overcoat with a rounded, seamless collar that curves continuously from the back of the neck to the front closure, without a notch, observed as an exaggerated, oversized construction choice in Fall/Winter 2028 menswear runway coverage.",
  "dropped-shoulder overcoat": "An overcoat cut with the shoulder seam extended past the wearer's natural shoulder line, producing a broader, more structured shoulder line than a set-in sleeve construction, observed in Fall/Winter 2028 menswear runway coverage as a distinct construction choice from the shawl-collar overcoat's rounded-collar treatment.",
  "bias-cut column dress": "A column dress cut on the fabric's diagonal (bias) grain rather than the straight grain, producing a close, fluid drape against the body, observed in Haute Couture Spring/Summer 2028 runway coverage.",
  "spiral-seam wrap coat": "A wrap coat constructed with a single seam that spirals diagonally around the torso rather than running vertically down the front or side, producing an asymmetric front closure line, observed in Fall/Winter 2028 New York Fashion Week runway coverage.",
  "cantilevered-shoulder blazer": "A tailored blazer built with an internal structural framework that extends the shoulder line beyond the wearer's natural silhouette in a rigid, unsupported-looking projection, observed in Fall/Winter 2028 New York Fashion Week runway coverage.",
  "london fashion week": "The London leg of the international ready-to-wear fashion week circuit, organized by the British Fashion Council, cited as an institutional-sector source event when its published calendar or participating collections are tracked.",
};

function normalize(term: string): string {
  return term
    .replace(/\s*\(carryover\)\s*$/i, "")
    .replace(/,\s*(forecast stage|third and final recheck|still unconfirmed at [^)]*|dormancy check|continuing|social)\s*$/i, "")
    .replace(/^"funmaxxing".*$/i, "funmaxxing")
    .trim();
}

// A genuine glossary term is short vocabulary (e.g. "peplum", "quiet luxury"),
// not a narrative sentence tracking a signal's status. This filters out
// long/sentence-like candidates before they're ever checked against
// DEFINITIONS, so build-time warnings only surface real curatable terms.
// See docs/agent-logs/glossary-build-warning-run38.md for the ~130-hit
// warning list this was written to reduce.
function isPlausibleGlossaryTerm(term: string): boolean {
  if (term.length > 40) return false;
  if (term.split(/\s+/).length > 5) return false;
  // Sentence-like punctuation: parenthetical explanations, commas joining
  // clauses, dashes used as asides, or terminal punctuation.
  if (/[()]/.test(term)) return false;
  if (/[,;:]/.test(term)) return false;
  if (/--|—|–/.test(term)) return false;
  if (/[.!?]\s*$/.test(term)) return false;
  return true;
}

function loadGlossaryTerms(): { term: string; def: string }[] {
  const found = new Map<string, string>(); // lowercase key -> display term

  {
    const reports = getAllReports() as unknown as ReportShape[];
    for (const report of reports) {
      const candidates = [
        ...(report.aesthetic_terms ?? []),
        ...(report.cultural_references ?? []),
        ...(report.top_signals ?? []).map((s) => s.name ?? ""),
      ];

      for (const raw of candidates) {
        const cleaned = normalize(raw);
        if (!cleaned) continue;
        if (!isPlausibleGlossaryTerm(cleaned)) continue;
        const key = cleaned.toLowerCase();
        if (DEFINITIONS[key]) {
          if (!found.has(key)) {
            found.set(key, cleaned);
          }
        } else {
          // Non-blocking build-time warning: surfaces terms observed in the
          // archive that have no curated definition, so they don't silently
          // drop off /glossary. See docs/agent-logs/glossary-freshness-check-run37.md.
          console.warn(
            `[glossary] no DEFINITIONS entry for term "${cleaned}" (from ${(report as { report_date?: string }).report_date ?? "unknown report"}) — term will not be shown on /glossary`
          );
        }
      }
    }
  }

  return Array.from(found.entries())
    .map(([key, term]) => ({ term, def: DEFINITIONS[key] }))
    .sort((a, b) => a.term.localeCompare(b.term));
}

export default function Glossary() {
  const terms = loadGlossaryTerms();

  return (
    <main id="main-content"
      style={{
        minHeight: "100vh",
        background: "var(--white)",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
      }}
    >
      <header
        style={{
          width: "100%",
          borderBottom: "3px solid var(--black)",
          padding: "3rem 2rem 2rem",
          textAlign: "center",
        }}
      >
        <p
          style={{
            fontFamily: "var(--font-franklin)",
            fontSize: "0.7rem",
            letterSpacing: "0.15em",
            textTransform: "uppercase",
            color: "var(--gray)",
            marginBottom: "0.75rem",
          }}
        >
          ARI3LLA INDEX
        </p>
        <h1
          style={{
            fontFamily: "var(--font-instrument)",
            fontSize: "clamp(2.5rem, 8vw, 5rem)",
            fontWeight: "400",
            lineHeight: "0.95",
            letterSpacing: "-0.02em",
            textTransform: "uppercase",
            color: "var(--black)",
          }}
        >
          Glossary
        </h1>
        <nav
          aria-label="Site sections"
          style={{ display: "flex", justifyContent: "center", gap: "1.5rem", marginTop: "1.5rem", flexWrap: "wrap" }}
        >
          {[
            { href: "/", label: "Report" },
            { href: "/methodology", label: "Methodology" },
            { href: "/taxonomy", label: "Taxonomy" },
            { href: "/sources", label: "Sources" },
            { href: "/timeline", label: "Timeline" },
            { href: "/archive", label: "Archive" },
            { href: "/search", label: "Search" },
            { href: "/about", label: "About" },
            { href: "/case-study", label: "Case Study" },
          ].map((item) => (
            <Link
              key={item.href}
              href={item.href}
              style={{
                fontFamily: "var(--font-franklin)",
                fontSize: "0.7rem",
                letterSpacing: "0.1em",
                textTransform: "uppercase",
                color: "var(--black)",
                textDecoration: "underline",
                textUnderlineOffset: "3px",
                display: "inline-block",
                padding: "0.65rem 0",
              }}
            >
              {item.label}
            </Link>
          ))}
        </nav>
      </header>

      <section style={{ width: "100%", maxWidth: "760px", padding: "4rem 2rem" }}>
        <p
          style={{
            fontFamily: "var(--font-franklin)",
            fontSize: "1rem",
            lineHeight: "1.8",
            color: "var(--gray)",
            marginBottom: "3.5rem",
          }}
        >
          Definitions for style and aesthetic terms that have recurred across the archive.
          This page defines the terms themselves; the Taxonomy page defines the
          classification system used to sort them. Entries are drawn only from terms that
          have appeared in an archived report. This glossary does not cover source sectors
          or confidence/volatility labels (e.g. flash, microtrend, revival) — for that
          vocabulary, see{" "}
          <Link href="/taxonomy" style={{ color: "var(--black)", textDecoration: "underline" }}>
            Taxonomy
          </Link>
          .
        </p>

        <dl style={{ display: "flex", flexDirection: "column", margin: 0 }}>
          {terms.map((t) => (
            <div
              key={t.term}
              style={{
                display: "grid",
                gridTemplateColumns: "220px 1fr",
                gap: "1.5rem",
                padding: "1.1rem 0",
                borderBottom: "1px solid var(--border)",
                alignItems: "start",
              }}
            >
              <dt
                style={{
                  fontFamily: "var(--font-franklin)",
                  fontSize: "0.85rem",
                  letterSpacing: "0.02em",
                  color: "var(--black)",
                  paddingTop: "0.15rem",
                  textTransform: "capitalize",
                }}
              >
                {t.term}
              </dt>
              <dd
                style={{
                  fontFamily: "var(--font-franklin)",
                  fontSize: "0.95rem",
                  lineHeight: "1.6",
                  color: "var(--gray)",
                  margin: 0,
                }}
              >
                {t.def}
              </dd>
            </div>
          ))}
        </dl>
      </section>

      <footer
        style={{
          width: "100%",
          borderTop: "1px solid var(--border)",
          padding: "2rem",
          textAlign: "center",
        }}
      >
        <p
          style={{
            fontFamily: "var(--font-franklin)",
            fontSize: "0.85rem",
            lineHeight: "1.7",
            color: "var(--gray)",
            maxWidth: "560px",
            margin: "0 auto",
          }}
        >
          ARI3LLA INDEX is an independent style signal archive. Reports are generated from public
          source material and structured for historical reference. No purchasing recommendation is
          implied.
        </p>
      </footer>
    </main>
  );
}
