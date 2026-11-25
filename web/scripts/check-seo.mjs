// scripts/check-seo.mjs
// Runs after `next build` (locally, in CI and in Vercel's build) and fails the
// build when a page is missing what sharing, search and agents need
// (design/SITE_SPEC_photocopy.md §8.6). Reads only the built files in out/.

import fs from "node:fs";
import path from "node:path";

const OUT = path.join(process.cwd(), "out");
const SITE = process.env.NEXT_PUBLIC_SITE_URL || "https://www.ari3lla.com";
const errors = [];
const warnings = [];
const err = (page, msg) => errors.push(`${page}: ${msg}`);
const warn = (page, msg) => warnings.push(`${page}: ${msg}`);

if (!fs.existsSync(OUT)) {
  console.error("check-seo: out/ does not exist; run `next build` first");
  process.exit(1);
}

const reportsDir = process.env.ARI3_REPORTS_DIR || path.join(process.cwd(), "..", "data", "reports");
const reportDates = fs.existsSync(reportsDir)
  ? fs.readdirSync(reportsDir).filter((f) => /^\d{4}-\d{2}-\d{2}\.json$/.test(f)).map((f) => f.slice(0, 10)).sort().reverse()
  : [];

const attr = (html, re) => (html.match(re) || [])[1];
const metaContent = (html, key) =>
  attr(html, new RegExp(`<meta[^>]+(?:name|property)="${key}"[^>]+content="([^"]*)"`)) ??
  attr(html, new RegExp(`<meta[^>]+content="([^"]*)"[^>]+(?:name|property)="${key}"`));
const decode = (s) => (s ?? "").replace(/&amp;/g, "&").replace(/&#x27;|&#39;/g, "'").replace(/&quot;/g, '"').replace(/&lt;/g, "<").replace(/&gt;/g, ">");

function outFileFor(url) {
  const p = decode(url).replace(SITE, "").replace(/^https?:\/\/[^/]+/, "").split("?")[0];
  const candidates = [p, `${p}.png`, `${p}.html`, path.join(p, "index.html")];
  return candidates.map((c) => path.join(OUT, c)).find((f) => fs.existsSync(f) && fs.statSync(f).isFile());
}

function checkPage(rel, { report } = {}) {
  const file = path.join(OUT, rel);
  if (!fs.existsSync(file)) return err(rel, "page was not built");
  const html = fs.readFileSync(file, "utf8");
  const page = `/${rel.replace(/\.html$/, "").replace(/^index$/, "")}`;

  const title = decode(attr(html, /<title>([^<]*)<\/title>/));
  if (!title) err(page, "no <title>");
  else if (title.length > 100) warn(page, `title is ${title.length} characters`);

  const desc = decode(metaContent(html, "description"));
  if (!desc) err(page, "no meta description");
  else if (desc.length < 50 || desc.length > 170) warn(page, `description is ${desc.length} characters`);

  const canonical = attr(html, /<link[^>]+rel="canonical"[^>]+href="([^"]+)"/);
  if (!canonical) err(page, "no canonical URL");
  else if (!canonical.startsWith(SITE)) err(page, `canonical ${canonical} is not on ${SITE}`);

  for (const k of ["og:title", "og:description", "og:url", "og:image", "og:image:alt", "twitter:card", "twitter:image"]) {
    if (!metaContent(html, k)) err(page, `no ${k}`);
  }
  if (metaContent(html, "twitter:card") && metaContent(html, "twitter:card") !== "summary_large_image") err(page, "twitter:card is not summary_large_image");
  const og = metaContent(html, "og:image");
  if (og && !outFileFor(og)) err(page, `og:image ${og} has no built file`);

  const h1s = (html.match(/<h1[\s>]/g) || []).length;
  if (h1s !== 1) err(page, `${h1s} <h1> elements (expected 1)`);
  if (!/<html[^>]+lang="en"/.test(html)) err(page, "no lang attribute");
  if (!/<main[^>]+id="main-content"/.test(html)) err(page, "no <main id=main-content> for the skip link");

  for (const block of html.matchAll(/<script type="application\/ld\+json">([\s\S]*?)<\/script>/g)) {
    try {
      const data = JSON.parse(block[1]);
      if (report) {
        const graph = data["@graph"] || [data];
        const article = graph.find((x) => x["@type"] === "NewsArticle");
        if (!article) err(page, "no NewsArticle JSON-LD");
        else if (!article.headline || /^In the window/.test(article.headline)) err(page, "NewsArticle headline is missing or is the summary's first sentence");
        if (!graph.find((x) => x["@type"] === "Dataset")) err(page, "no Dataset JSON-LD");
      }
    } catch (e) {
      err(page, `JSON-LD does not parse: ${e.message}`);
    }
  }
  if (report) {
    const alt = attr(html, /<link[^>]+rel="alternate"[^>]+type="application\/json"[^>]+href="([^"]+)"/) ?? attr(html, /<link[^>]+type="application\/json"[^>]+href="([^"]+)"/);
    if (!alt) err(page, "no JSON alternate link");
    else if (!outFileFor(alt)) err(page, `JSON alternate ${alt} has no built file`);
  }
  return desc;
}

const pages = ["index.html", "archive.html", "signals.html", "search.html", "methodology.html", "about.html", "ari3.html", "glossary.html", "sources.html", "taxonomy.html", "timeline.html"];
const descriptions = new Map();
for (const p of pages) { const d = checkPage(p); if (d) descriptions.set(d, [...(descriptions.get(d) || []), p]); }
for (const date of reportDates) {
  const d = checkPage(`reports/${date}.html`, { report: true });
  if (d) descriptions.set(d, [...(descriptions.get(d) || []), `reports/${date}`]);
}
const signalDir = path.join(OUT, "signals");
for (const f of fs.existsSync(signalDir) ? fs.readdirSync(signalDir).filter((x) => x.endsWith(".html")) : []) {
  const d = checkPage(`signals/${f}`);
  if (d) descriptions.set(d, [...(descriptions.get(d) || []), `signals/${f}`]);
}
for (const [d, ps] of descriptions) if (ps.length > 1) err(ps.join(", "), `share the description "${d.slice(0, 60)}..."`);

// Site-wide files agents and crawlers read.
const need = (rel, test, msg) => {
  const f = path.join(OUT, rel);
  if (!fs.existsSync(f)) return err(rel, "missing");
  if (test && !test(fs.readFileSync(f, "utf8"))) err(rel, msg);
};
need("404.html");
need("robots.txt", (t) => /Sitemap:/i.test(t), "names no sitemap");
need("sitemap.xml", (t) => reportDates.every((d) => t.includes(`/reports/${d}`)), "does not list every report");
need("rss.xml", (t) => reportDates.slice(0, 50).every((d) => t.includes(`/reports/${d}`)), "does not list every recent report");
need("llms.txt", (t) => reportDates.every((d) => t.includes(`/reports/${d}`)), "does not list every report");
need("llms-full.txt");
need("data/reports/index.json", (t) => { try { const j = JSON.parse(t); return reportDates.every((d) => j.reports.some((r) => r.report_date === d)); } catch { return false; } }, "does not list every report");
need("data/search.json");
for (const date of reportDates) {
  need(`data/reports/${date}.json`);
  need(`md/reports/${date}.md`, (t) => t.startsWith("---") && t.includes("## Cite as"), "has no front matter or citation");
}
need("llms.txt", (t) => t.includes("## For AI agents") && t.includes("/md/reports/"), "has no agent section or Markdown links");

for (const w of warnings) console.warn(`warn  ${w}`);
if (errors.length) {
  for (const e of errors) console.error(`FAIL  ${e}`);
  console.error(`check-seo: ${errors.length} problem(s) across ${reportDates.length} reports`);
  process.exit(1);
}
console.log(`check-seo: OK (${reportDates.length} reports, ${pages.length} site pages, ${warnings.length} warning(s))`);
