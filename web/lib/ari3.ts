// lib/ari3.ts
// The ARI3 research notebook: experiment registry, release names, project state
// and research principles. Every value is copied from a committed manifest or a
// commit. An experiment entry is permanent. Corrections are added as new notes.

export const REPO = "https://github.com/arikthehacker/fashion-trend-crawler";

export type Metric = { name: string; a?: number; b: number; format: "pct" | "num"; lowerIsBetter?: boolean; note?: string };
export type Hypothesis = { id: string; claim: string; test: string; result: string; verdict: "Supported" | "Not supported" | "Pending" };

export type Experiment = {
  id: string;
  slug: string;
  version: string;
  name: string;
  motto: string;
  status: "Frozen" | "Pre-registered";
  headline: string;
  summary: string[];
  meta: { label: string; value: string; href?: string; mono?: boolean }[];
  question: string;
  preregistered: string;
  hypotheses?: Hypothesis[];
  why?: string[];
  method: string[];
  held: string[];
  changed: string[];
  threats: string[];
  compare?: { a: string; b: string; n: number };
  metrics: Metric[];
  benefits: string[];
  costs: string[];
  surprises: string[];
  engineering: string[];
  log: { step: string; text: string }[];
  lessons: string[];
  openQuestions: string[];
  reproduce: { text: string; commands: string };
};

const ENV_001 = "Python 3.13.2, numpy 2.5.0, scikit-learn 1.9.1, sentence-transformers 6.1.0";

export const EXPERIMENTS: Experiment[] = [
  {
    id: "EXP-002",
    slug: "exp-002",
    version: "v0.0.2",
    name: "DISCIPLINA",
    motto: "The method emerges.",
    status: "Frozen",
    headline: "35 hard cases raised confident predictions from 66% to 82% at equal training size.",
    summary: [
      "ARI3 v0.0.2 kept every design choice of v0.0.1 and changed only the training data, adding 155 random labels and 50 hard cases chosen by active learning.",
      "The plan and its five pass criteria were committed publicly before any v0.0.2 label existed, so the result could not be tuned after the fact.",
      "All five hypotheses were supported. The clear gains were in confident answers and calibration, accuracy moved within noise, and the model made 2 confident mistakes where v0.0.1 made none.",
    ],
    meta: [
      { label: "Experiment", value: "EXP-002" },
      { label: "Run", value: "2026-09-26 19:25 UTC" },
      { label: "Pre-registration", value: "79e95bc, 2026-09-24 01:08 UTC", href: `${REPO}/blob/79e95bc918c3bf523a8ae58e3d7eca6a4ac6471f/models/ari3-v0.0.2/PREREGISTRATION.md`, mono: true },
      { label: "Release commit", value: "ec788a0", href: `${REPO}/commit/ec788a0d9e2cbb8a7d6b2d954f8761db42e1b762`, mono: true },
      { label: "Dataset", value: "350 labels by the editor: 300 random, 50 active learning" },
      { label: "Dataset fingerprint", value: "sha256 20ca8e4a1344f81e6c38527935c57542cfa9ff39f61fbb4981560abf10698765", mono: true },
      { label: "Model", value: "ari3-v0.0.2 (perception, is_style_signal)", mono: true },
      { label: "Weights", value: "sha256 f6b25eb421e2766cc2681f9b2a6816330ab50569bae752a73b231ed7fe282f09", mono: true },
      { label: "Manifest", value: "manifest_sha256 d1cad506d6c9326e77a7729970261a0bb8a0ace3e834b0735530a98e0214e055", mono: true },
      { label: "Embedder", value: "paraphrase-multilingual-MiniLM-L12-v2 @ e8f8c21", mono: true },
      { label: "Environment", value: "Not recorded in this manifest. The run used the same machine as EXP-001. Future manifests record it." },
      { label: "Random seeds", value: "Label queue: 7. H5 subsets: 0 to 19. Model fitting is deterministic." },
      { label: "Runtime", value: "Not recorded. Future manifests record it." },
    ],
    question: "Does adding intentionally difficult human labels improve perception more than labeling the same number of randomly chosen articles?",
    preregistered: "Yes. Five hypotheses with pass criteria were committed before any v0.0.2 label existed.",
    hypotheses: [
      { id: "H1", claim: "More decisive", test: "Single-answer share on the test set ≥ 0.70", result: "0.754", verdict: "Supported" },
      { id: "H2", claim: "Coverage holds", test: "Conformal coverage ≥ 0.90", result: "0.967", verdict: "Supported" },
      { id: "H3", claim: "Accuracy does not drop", test: "v0.0.2 accuracy ≥ v0.0.1 on the same items", result: "0.902 vs 0.869", verdict: "Supported" },
      { id: "H4", claim: "Calibration stays good", test: "Calibration error after scaling ≤ 0.10", result: "0.025", verdict: "Supported" },
      { id: "H5", claim: "Hard cases beat random labels", test: "At equal training size, the active-learning arm beats the random arm", result: "Accuracy 0.898 vs 0.885. Single-answer share 0.820 vs 0.656", verdict: "Supported" },
    ],
    why: [
      "A classifier learns where to draw the line between two answers. Items far from that line teach it little, because it already gets them right. Items the model is torn about sit near the line, so labeling them shows where the line belongs. Choosing those items on purpose is uncertainty sampling, a standard active-learning method (Settles 2009).",
      "More calibration labels should also help. Split conformal prediction pads its threshold to guarantee coverage on small calibration sets, and the padding shrinks as the set grows. A smaller threshold means fewer not-sure answers without breaking the guarantee (Angelopoulos & Bates 2021).",
    ],
    method: [
      "350 labels by the editor",
      "Split fixed by a hash of each item: train, calibration, test",
      "Hard cases removed from calibration and test",
      "Multilingual sentence embeddings, frozen",
      "Logistic regression on 229 training labels",
      "Temperature scaling on 45 calibration labels",
      "Split conformal threshold at α = 0.10",
      "Scored with v0.0.1 on the same 61 test items",
    ],
    held: [
      "Embedding model and revision",
      "Tokenizer (the embedder's own)",
      "Feature extraction: headline plus excerpt, up to 1,000 characters, normalized",
      "Classifier and regularization (C = 1.0)",
      "Temperature scaling procedure",
      "Conformal method and α",
      "Split rule",
      "Evaluation metrics",
      "The labeling question and its scope rule",
    ],
    changed: [
      "+155 random labels",
      "+50 hard cases chosen by active learning (35 landed in training)",
      "H5 separates the two: both arms train on 194 labels, and one swaps 35 random labels for the 35 hard cases",
    ],
    threats: [
      "Small test set. 61 items, so a 2-item difference is within noise.",
      "One annotator. Every label reflects one editor's judgment, and no agreement rate between labelers exists yet.",
      "Source bias. About 87% of stored items come from editorial outlets, so small sectors have few examples.",
      "Language. By feed metadata, 300 of the 350 labeled items are tagged English and 10 French, so accuracy on other languages is essentially untested.",
      "Time. 276 of the 350 labeled items were published in September 2026, so the model is barely tested on older or newer language.",
      "Class balance. 55% of random labels are yes.",
      "The test set excludes hard cases, so it does not measure performance on the hardest items.",
      "Two analysis choices were not in the pre-registration. Hard cases were also kept out of calibration, and H5 was run at equal size by swapping labels. Both are listed in the manifest.",
    ],
    compare: { a: "v0.0.1", b: "v0.0.2", n: 61 },
    metrics: [
      { name: "Accuracy", a: 0.869, b: 0.902, format: "pct", note: "95% intervals 0.76–0.93 and 0.80–0.95 overlap" },
      { name: "Confident answers", a: 0.574, b: 0.754, format: "pct" },
      { name: "Coverage (target ≥ 0.90)", a: 1.0, b: 0.967, format: "pct" },
      { name: "Calibration error", a: 0.088, b: 0.025, format: "num", lowerIsBetter: true, note: "5-bin expected calibration error after temperature scaling" },
      { name: "Precision", a: 0.85, b: 0.917, format: "pct" },
      { name: "Recall", a: 0.944, b: 0.917, format: "pct" },
    ],
    benefits: [
      "+18 percentage points of confident answers (0.574 → 0.754)",
      "Calibration error 3.5× lower (0.088 → 0.025), measured on 61 items",
      "At equal training size, hard cases raised confident answers from 0.656 to 0.820",
    ],
    costs: [
      "2 confident mistakes on the test set, where v0.0.1 made none",
      "Coverage fell from 1.00 to 0.967, still above the 0.90 target",
      "Recall fell from 0.944 to 0.917",
    ],
    surprises: [
      "Only 14 of the 50 hard cases were about style. The items v0.0.1 found hardest were mostly non-style articles that read like style coverage.",
      "Active learning changed confidence far more than accuracy.",
    ],
    engineering: [
      "Touch and keyboard labeling app with a separate hard-case deck (src/ari3_review.pyw)",
      "Hard-case labels are tagged in the database so they can be kept out of testing",
      "One-shot experiment runner that refuses to run twice (src/ari3_v002_run.py)",
      "Scope rule for beauty coverage written into the labeling screen",
    ],
    log: [
      { step: "Observation", text: "v0.0.1 answered not-sure for 1,648 of 2,472 unlabeled items." },
      { step: "Idea", text: "The items it is most torn about should teach it the most." },
      { step: "Experiment", text: "EXP-002, pre-registered, 50 hard cases plus 155 random labels." },
      { step: "Result", text: "Confident answers rose clearly. Accuracy moved within noise. 2 confident mistakes appeared." },
      { step: "New question", text: "Does the confident-mistake rate grow as the model becomes more decisive?" },
    ],
    lessons: [
      "Expected: hard cases would mainly raise accuracy. Observed: they mainly raised confidence.",
      "Decisiveness has a price, and it has to be reported beside the gain.",
      "Pre-registration required the weak results to be published.",
    ],
    openQuestions: [
      "How do accuracy and confident answers change as labels grow (a learning curve)?",
      "Should the confident-mistake rate become a pass criterion of its own?",
      "Does performance hold on items newer than the training data?",
      "Does a second labeler agree with the first, and how often?",
    ],
    reproduce: {
      text: "The code, weights and manifest are public. The labels live in the project's local database and are not published yet, so an outside rerun is not possible yet. The published hashes let anyone confirm the weights are the ones committed.",
      commands: `git clone ${REPO}.git
cd fashion-trend-crawler
git show ec788a0:models/ari3-v0.0.2/weights.npz | sha256sum
# with the label database present:
git checkout ec788a0
pip install -r requirements.txt -r requirements-ml.txt
python src/ari3_v002_run.py`,
    },
  },
  {
    id: "EXP-001",
    slug: "exp-001",
    version: "v0.0.1",
    name: "INDUSTRIA",
    motto: "The work begins.",
    status: "Frozen",
    headline: "The first ARI3 model made no confident mistakes on its 34 held-out items.",
    summary: [
      "ARI3 v0.0.1 is the first model trained on the editor's own judgments, 145 labels saying whether a news item is about style.",
      "It pairs a small classifier with calibrated probabilities and conformal prediction, so it can say when it is not sure.",
      "It reached 0.882 held-out accuracy against a 0.529 baseline, and all 4 of its mistakes came with a not-sure answer.",
    ],
    meta: [
      { label: "Experiment", value: "EXP-001" },
      { label: "Run", value: "2026-09-23, frozen 08:55 UTC" },
      { label: "Release commit", value: "9c296bd", href: `${REPO}/commit/9c296bd72a10915969b5808b0d6bc4e41e2ac4a9`, mono: true },
      { label: "Dataset", value: "145 random labels by the editor" },
      { label: "Dataset fingerprint", value: "sha256 3f09bf6fe74b66102b4a154d5a75eb607f71292fc695cb84155bebb0c2a3978f", mono: true },
      { label: "Model", value: "ari3-v0.0.1 (perception, is_style_signal)", mono: true },
      { label: "Weights", value: "sha256 78ddaf3383eaa141687133e8d6993ff12a6568452a1747bd862c0955572b76be", mono: true },
      { label: "Manifest", value: "manifest_sha256 f9f2c44bb06dad0fc3672c29dfcacfa39d2ce503dc28c38457206dac5ccb0213", mono: true },
      { label: "Embedder", value: "paraphrase-multilingual-MiniLM-L12-v2 @ e8f8c21", mono: true },
      { label: "Environment", value: ENV_001 },
      { label: "Random seeds", value: "Label queue: 7. Model fitting is deterministic." },
      { label: "Runtime", value: "Not recorded." },
    ],
    question: "Can a small model trained on one editor's labels tell style coverage from adjacent news, and know when it is unsure?",
    preregistered: "No. EXP-001 was exploratory. Its result became the baseline that EXP-002 was pre-registered against.",
    method: [
      "145 labels by the editor",
      "Split fixed by a hash of each item: 82 train, 29 calibration, 34 test",
      "Multilingual sentence embeddings, frozen",
      "Logistic regression",
      "Temperature scaling",
      "Split conformal threshold at α = 0.10",
      "Scored on 34 held-out items",
    ],
    held: [
      "One labeling question for every item",
      "Split fixed before training by a hash of each item",
    ],
    changed: ["First version. No earlier model to compare against."],
    threats: [
      "Very small test set. 34 items, so accuracy has a 22-point interval.",
      "One annotator, one pass.",
      "Source bias. About 85% of stored items came from editorial outlets at the time.",
      "Only 29 calibration items, which makes the conformal threshold cautious.",
      "Not pre-registered. The analysis was chosen by the people who ran it.",
    ],
    metrics: [
      { name: "Accuracy", b: 0.882, format: "pct", note: "Majority-answer baseline 0.529" },
      { name: "Confident answers", b: 0.559, format: "pct" },
      { name: "Coverage (target ≥ 0.90)", b: 1.0, format: "pct" },
      { name: "Calibration error, before scaling", b: 0.234, format: "num", lowerIsBetter: true },
      { name: "Calibration error, after scaling", b: 0.088, format: "num", lowerIsBetter: true },
      { name: "Precision", b: 0.833, format: "pct" },
      { name: "Recall", b: 0.938, format: "pct" },
    ],
    benefits: [
      "35 points above the majority-answer baseline",
      "Temperature scaling cut calibration error by 62%",
      "No confident mistakes on the test set",
    ],
    costs: [
      "The not-sure answer was common: 1,648 of 2,472 unlabeled items received it",
    ],
    surprises: [
      "The fitted temperature was 0.40, meaning the raw classifier was underconfident. Deep networks are usually the reverse (Guo et al. 2017).",
      "The share of items that were about style ranged from about a quarter to all of a sector's feeds, so raw item counts overstate style activity.",
      "Beauty trade coverage caused half the test mistakes, which led to a written scope rule before the next experiment.",
    ],
    engineering: [
      "Database migration 0002: feed excerpts, a labels table with hash-fixed splits, and an append-only prediction log",
      "Keyboard labeling tool (src/label_tool.py)",
      "Freeze script that refuses to overwrite a frozen version (src/ari3_freeze.py)",
    ],
    log: [
      { step: "Observation", text: "Feeds mix style coverage with business and celebrity news, and raw counts cannot tell them apart." },
      { step: "Idea", text: "Train a small model on the editor's own judgment of what counts as style." },
      { step: "Experiment", text: "EXP-001, 145 labels, calibrated and conformal." },
      { step: "Result", text: "0.882 accuracy and no confident mistakes, but many not-sure answers." },
      { step: "New question", text: "Can hard examples make it more decisive? That became EXP-002." },
    ],
    lessons: [
      "Expected: feed counts could stand in for style activity. Observed: style share varies nearly fourfold by sector.",
      "On the test set, the not-sure answer flagged every one of the model's mistakes for the editor.",
    ],
    openQuestions: [
      "Where does the model's boundary sit, and which items sit on it?",
      "Is beauty a separate category? (Answered before EXP-002: yes, with nails counted as style.)",
    ],
    reproduce: {
      text: "The weights and manifest are public. The labels are in the project's local database and not published yet. The freeze script refuses to refit a frozen version, so a rerun needs a new version name.",
      commands: `git clone ${REPO}.git
cd fashion-trend-crawler
git show 9c296bd:models/ari3-v0.0.1/weights.npz | sha256sum`,
    },
  },
];

export const RELEASE_NAMES = [
  { version: "v0.0.1", name: "INDUSTRIA", motto: "The work begins.", status: "Released", exp: "exp-001" },
  { version: "v0.0.2", name: "DISCIPLINA", motto: "The method emerges.", status: "Released", exp: "exp-002" },
  { version: "v0.0.3", name: "INTEGRITAS", motto: "The evidence can be trusted.", status: "Planned" },
  { version: "v0.0.4", name: "PROVIDENTIA", motto: "The system begins looking forward.", status: "Planned" },
  { version: "v0.0.5", name: "CONCORDIA", motto: "Independent models act in concert.", status: "Planned" },
  { version: "v1.0", name: "FIDES", motto: "The system earns trust.", status: "Planned" },
  { version: "v2.0", name: "AUCTORITAS", motto: "Others build upon it.", status: "Planned" },
];

export type StateItem = { area: string; detail: string };
export const PROJECT_STATE: { status: string; mark: "full" | "half" | "dashed" | "empty"; items: StateItem[] }[] = [
  {
    status: "Completed", mark: "full", items: [
      { area: "Dated collection", detail: "97 feeds read every 4 hours into a local database, respecting robots.txt" },
      { area: "Evidence gate", detail: "No report is published without a dated article link for every claim" },
      { area: "Perception v0.0.1 and v0.0.2", detail: "Frozen, hashed and public" },
      { area: "Pre-registration", detail: "First experiment with public pass criteria committed before its data" },
    ],
  },
  {
    status: "In progress", mark: "half", items: [
      { area: "Lexicon v1", detail: "73 style terms chosen by the editor, 12 with usage notes. Not yet loaded" },
      { area: "Forecast ledger", detail: "Database tables built. No forecast has been made" },
    ],
  },
  {
    status: "Research", mark: "dashed", items: [
      { area: "Term extraction", detail: "Counting lexicon terms across stored articles, with sense checks for ambiguous words" },
      { area: "Style R₀", detail: "A Hawkes process model of how terms spread between sectors. Designed, not built" },
      { area: "Latent salience", detail: "A Kalman filter estimate of attention beneath each source's noise. Designed, not built" },
    ],
  },
  {
    status: "Not started", mark: "empty", items: [
      { area: "Flow between sectors", detail: "Optimal transport" },
      { area: "Event lift", detail: "Synthetic control" },
      { area: "Adaptive collection", detail: "A reinforcement learning crawler" },
    ],
  },
];

export const PRINCIPLES = [
  { title: "Version everything", body: "Every model, dataset and experiment has a version and a hash. A frozen version is never changed." },
  { title: "Measure everything", body: "A claim about ARI3 comes with the number behind it and the size of the sample it came from." },
  { title: "Never hide failures", body: "Every pre-registered hypothesis is reported, including those that fail, and every gain is shown beside its cost." },
  { title: "Pre-register experiments", body: "Questions and pass criteria are committed publicly before the data that answers them exists." },
  { title: "Separate hypothesis from hindsight", body: "Analysis choices made after seeing data are listed as such, apart from the pre-registered plan." },
  { title: "Prefer reproducibility over novelty", body: "Every result lists the code, data fingerprint and hashes behind it, and says plainly what an outsider cannot yet rerun." },
  { title: "Human judgment is data", body: "The editor's labels are the ground truth ARI3 learns from and is tested against, and they are versioned like code." },
  { title: "Models should admit uncertainty", body: "An ARI3 model says when it is not sure, and those items are meant for a person instead of an automatic count." },
];
