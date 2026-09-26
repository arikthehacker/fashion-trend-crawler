// lib/ari3_cards.ts
// Model cards, the dataset card, the public decision log and the research timeline
// for the ARI3 notebook. Counts carry the time they were measured.

export type ModelCard = {
  version: string;
  name: string;
  exp: string;
  status: string;
  purpose: string;
  inputs: string;
  outputs: string;
  training: string;
  metrics: { name: string; value: string }[];
  limitations: string[];
  failureModes: string[];
  intendedUse: string;
  notFor: string;
};

export const MODEL_CARDS: ModelCard[] = [
  {
    version: "v0.0.2",
    name: "DISCIPLINA",
    exp: "exp-002",
    status: "Current",
    purpose: "Decide whether a news item is about style, and say when it is not sure.",
    inputs: "A news item's headline and feed excerpt, joined and cut to 1,000 characters, in any language the embedder covers.",
    outputs: "A calibrated probability that the item is about style, and a conformal set: {yes}, {no}, or {yes, no} when it is not sure (target coverage 90%).",
    training: "229 labels by the editor: 194 random and 35 chosen by active learning. Calibrated on 45 random labels. Tested on 61 random labels. Architecture unchanged from v0.0.1.",
    metrics: [
      { name: "Accuracy (61 held-out items)", value: "0.902, 95% CI 0.80–0.95" },
      { name: "Calibration error after scaling", value: "0.025" },
      { name: "Conformal coverage", value: "0.967" },
      { name: "Confident (single-answer) share", value: "0.754" },
      { name: "Confident mistakes", value: "2 of 61" },
    ],
    limitations: [
      "Trained and tested on one editor's labels.",
      "Mostly English-tagged training items. Other languages are barely tested.",
      "Reads headlines and excerpts only, never full articles.",
      "Most labeled items were published in September 2026.",
    ],
    failureModes: [
      "Articles that sit next to style, such as beauty or retail business news, are where it errs most.",
      "More decisive than v0.0.1, and it made 2 confident mistakes where v0.0.1 made none.",
    ],
    intendedUse: "Filtering collected items before counting, with not-sure items meant for the editor.",
    notFor: "Judging individual articles or outlets, or any use outside the index.",
  },
  {
    version: "v0.0.1",
    name: "INDUSTRIA",
    exp: "exp-001",
    status: "Superseded by v0.0.2, kept frozen",
    purpose: "Decide whether a news item is about style, and say when it is not sure.",
    inputs: "A news item's headline and feed excerpt, joined and cut to 1,000 characters.",
    outputs: "A calibrated probability and a conformal set at 90% target coverage.",
    training: "82 random labels by the editor. Calibrated on 29. Tested on 34.",
    metrics: [
      { name: "Accuracy (34 held-out items)", value: "0.882, 95% CI 0.73–0.95" },
      { name: "Calibration error after scaling", value: "0.088" },
      { name: "Conformal coverage", value: "1.000" },
      { name: "Confident (single-answer) share", value: "0.559" },
      { name: "Confident mistakes", value: "0 of 34" },
    ],
    limitations: [
      "Very small training, calibration and test sets.",
      "Cautious: most unlabeled items received the not-sure answer.",
    ],
    failureModes: [
      "Half its test mistakes were beauty trade coverage, before the beauty scope rule existed.",
    ],
    intendedUse: "The baseline for later versions.",
    notFor: "Current use. v0.0.2 replaces it.",
  },
];

export const ARCHITECTURE = [
  { part: "Embedder", value: "paraphrase-multilingual-MiniLM-L12-v2, revision e8f8c21, 384 dimensions, frozen", source: "Reimers & Gurevych 2019, 2020" },
  { part: "Classifier", value: "Logistic regression, L2, C = 1.0", source: "" },
  { part: "Calibration", value: "Temperature scaling on a held-out calibration split", source: "Guo et al. 2017" },
  { part: "Uncertainty", value: "Split conformal prediction, score 1 − p(true label), α = 0.10", source: "Angelopoulos & Bates 2021" },
];

export const DATASETS = [
  {
    name: "ARI3 item corpus",
    version: "Live, counted 2026-09-26 16:33 UTC",
    rows: [
      { k: "What it is", v: "Dated news items collected from public RSS and Atom feeds about fashion and style." },
      { k: "Sources", v: "97 feeds from 97 outlets, each mapped to a sector. The outlets are listed on the Sources page." },
      { k: "Collection", v: "Every 4 hours. robots.txt is checked, requests to the same host wait one second, and items without a publish date are skipped." },
      { k: "What is stored", v: "URL, title, publish time, fetch time, a content hash, feed language, and the feed's own summary capped at 500 characters. Full article text is never stored." },
      { k: "Size", v: "5,655 items, 5,246 with an excerpt. Publish dates run from 2015-01-09 to 2026-09-26. The first item was fetched 2026-09-23." },
      { k: "Sectors", v: "Editorial 87.3%, trade 4.2%, independent criticism 2.5%, retail 2.4%, visual archive 1.5%, institutional 0.8%, runway 0.6%, designer origin 0.5%, resale 0.2%." },
      { k: "Languages", v: "By feed metadata, 77% English-tagged and 16% untagged. The rest include Japanese, Italian, French and Portuguese." },
      { k: "Excluded", v: "Social platforms are never scraped. Runway images are never stored." },
      { k: "Known biases", v: "Editorial outlets dominate. Feeds keep only recent items, so older coverage is thin. Outlets with no feed are missing." },
      { k: "License and access", v: "The items belong to their publishers. The corpus is kept locally for research and is not redistributed. The site shows links and short metadata only." },
    ],
  },
  {
    name: "ARI3 style labels (is_style_signal)",
    version: "350 labels, fingerprint sha256 20ca8e4a…, 2026-09-26",
    rows: [
      { k: "Question", v: "Is this item about style: what people wear, how, and what it is called?" },
      { k: "Scope rule", v: "Yes: garments, silhouettes, materials, colors, styling, aesthetic terms, collections, clothing collaborations, nails. No: beauty (makeup, skincare, fragrance, hair, packaging), earnings, deals, executive moves, store openings, celebrity news with no clothing content." },
      { k: "Annotator", v: "One: the editor. Labeled one item at a time with the ARI3 review app." },
      { k: "Sampling", v: "300 items drawn in turn from each sector (seed 7), so small sectors appear. 50 more chosen by active learning from items v0.0.1 was least sure about." },
      { k: "Balance", v: "Random labels: 166 yes, 134 no. Active-learning labels: 14 yes, 36 no." },
      { k: "Splits", v: "Fixed by a SHA-256 hash of each item at labeling time: 65% train, 15% calibration, 20% test. Active-learning labels are kept out of calibration and testing." },
      { k: "Versions", v: "145 labels (2026-09-23, used by v0.0.1). 350 labels (2026-09-26, used by v0.0.2)." },
      { k: "Known biases", v: "One annotator. 300 of 350 items are English-tagged. 276 of 350 were published in September 2026." },
      { k: "Access", v: "Not published yet. The fingerprints let later releases prove which labels were used." },
    ],
  },
];

export type Decision = { id: string; date: string; title: string; decision: string; why: string; alternatives: string; tradeoff: string; exp?: string };

export const DECISIONS: Decision[] = [
  {
    id: "D-09", date: "2026-09-26", title: "Keep ambiguous lexicon terms, with sense checks",
    decision: "Lexicon v1 keeps all 73 terms the editor reviewed. Seven words that often mean something else (western, brat, demure, lace, bow, glamour, sustainable) carry a note that each match needs a sense check.",
    why: "Dropping them would hide real style uses. Counting them blindly would count the wrong meanings.",
    alternatives: "Drop the ambiguous terms, or count them without notes.",
    tradeoff: "Counts for those seven words are provisional until a sense check exists.",
  },
  {
    id: "D-08", date: "2026-09-26", title: "Keep hard cases out of calibration as well as testing",
    decision: "Active-learning labels were used only for training in EXP-002.",
    why: "Split conformal prediction assumes calibration items look like test items. Items chosen for being hard do not.",
    alternatives: "Use them in calibration as their hash placed them.",
    tradeoff: "7 labels went unused. The choice was not in the pre-registration and is disclosed as such.",
    exp: "exp-002",
  },
  {
    id: "D-07", date: "2026-09-24", title: "Pre-register every experiment that compares versions",
    decision: "EXP-002's question, hypotheses and pass criteria were committed publicly before any of its labels existed.",
    why: "Criteria chosen after seeing results can make any result look good.",
    alternatives: "Report results and explain them afterwards.",
    tradeoff: "Weak or failed results have to be published as they are.",
    exp: "exp-002",
  },
  {
    id: "D-06", date: "2026-09-23", title: "Beauty is separate from style, nails count",
    decision: "Makeup, skincare, fragrance, hair and beauty packaging are labeled not style. Nails are style.",
    why: "Beauty trade coverage caused half of v0.0.1's test mistakes, so the boundary had to be written down before more labeling.",
    alternatives: "Count all beauty as style, or none of it.",
    tradeoff: "Beauty coverage is not measured until it gets a task of its own.",
    exp: "exp-002",
  },
  {
    id: "D-05", date: "2026-09-23", title: "Fix each label's split when it is written",
    decision: "A SHA-256 hash of the item and task decides whether a label is for training, calibration or testing, and it never changes.",
    why: "A test item that ever reaches training makes every later score look better than it is.",
    alternatives: "Re-split randomly for each experiment.",
    tradeoff: "Split sizes are only approximately 65/15/20.",
    exp: "exp-001",
  },
  {
    id: "D-04", date: "2026-09-23", title: "Collect every 4 hours",
    decision: "Feeds are read six times a day.",
    why: "Measured: 28 of 65 feeds held under 7 days of items, and the fastest held about 8 hours. Weekly collection would miss items.",
    alternatives: "Weekly, daily or every 12 hours.",
    tradeoff: "More requests to each outlet, kept polite by robots.txt checks and a one-second delay per host.",
  },
  {
    id: "D-03", date: "2026-09-22", title: "Every claim needs a dated article link",
    decision: "A report cannot be published if any claim lacks a link to a specific dated article, or links only to a homepage, or cites something published after the report date. Continuous integration enforces this.",
    why: "A reader has to be able to open the source behind each claim and check it.",
    alternatives: "Allow outlet-level citations.",
    tradeoff: "Fewer, slower reports.",
  },
  {
    id: "D-02", date: "2026-09-22", title: "Split what one person can build from what needs partners",
    decision: "Each capability is either Viable (buildable on public data by one person) or Frontier (needs private data, real-world experiments or a team). Moving one across the line needs its own recorded decision.",
    why: "The line stops the site from claiming capabilities the project cannot yet support.",
    alternatives: "One undivided roadmap.",
    tradeoff: "Frontier ideas wait, however interesting.",
  },
  {
    id: "D-01", date: "Standing rule", title: "No scraping of social platforms",
    decision: "Social data may come only from official APIs or hand sampling. Runway images are linked, never stored.",
    why: "Scraping breaks platform terms and collects people's posts without their consent.",
    alternatives: "Scrape public posts.",
    tradeoff: "Social signals are missing until API access is granted.",
  },
];

export type TimelineEvent = { date: string; title: string; detail: string; href?: string; planned?: boolean };

export const TIMELINE: TimelineEvent[] = [
  { date: "2026-05-04", title: "Repository started", detail: "A headline crawler and a tool server for querying it." },
  { date: "2026-05-18", title: "First real crawl", detail: "96 headlines from two outlets. It later became the first published report." },
  { date: "2026-09-23", title: "Dated collection begins", detail: "RSS collection every 4 hours into a local database. The evidence gate runs on every change." },
  { date: "2026-09-23", title: "First sourced report", detail: "The 2026-05-18 crawl, re-checked against the articles behind it, published with every claim linked.", href: "/reports/2026-05-18" },
  { date: "2026-09-23", title: "First human labels, INDUSTRIA trained", detail: "145 labels by the editor. v0.0.1 reaches 0.882 held-out accuracy.", href: "/ari3/exp-001" },
  { date: "2026-09-24", title: "INDUSTRIA committed, EXP-002 pre-registered", detail: "v0.0.1 (frozen the day before) and the next experiment's pass criteria committed publicly, one second apart.", href: "/ari3/exp-002" },
  { date: "2026-09-26", title: "DISCIPLINA frozen", detail: "350 labels, 50 of them hard cases. All five pre-registered hypotheses supported.", href: "/ari3/exp-002" },
  { date: "2026-09-26", title: "Lexicon v1 decided", detail: "73 style terms chosen by the editor. Not yet loaded." },
  { date: "Next", title: "INTEGRITAS", detail: "The evidence can be trusted.", planned: true },
  { date: "Later", title: "PROVIDENTIA", detail: "The system begins looking forward.", planned: true },
  { date: "Later", title: "CONCORDIA", detail: "Independent models act in concert.", planned: true },
];
