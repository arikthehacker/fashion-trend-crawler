// lib/ari3.ts
// The ARI3 research notebook: experiment registry, release names, project state
// and research principles. Every value is copied from a committed manifest or a
// commit. An experiment entry is permanent. Corrections are added as new notes.

export const REPO = "https://github.com/arikthehacker/fashion-trend-crawler";

export type Metric = { name: string; a?: number; b: number; label?: string; format: "pct" | "num"; lowerIsBetter?: boolean; note?: string };
export type Hypothesis = { id: string; claim: string; test: string; result: string; verdict: "Supported" | "Not supported" | "Pending" };

export type Experiment = {
  id: string;
  slug: string;
  version: string;
  kicker?: string;
  name: string;
  motto: string;
  status: string;
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
  resultsIntro?: string;
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
    id: "EXP-004",
    slug: "exp-004",
    version: "",
    kicker: "ARI3 retrieval experiment, with no release version",
    name: "Grounded retrieval",
    motto: "",
    status: "Closed",
    headline: "On the 12 held-out test questions with a resolved relevant item, the frozen hybrid retriever reached macro Recall@10 0.770 and Hit@10 1.000.",
    summary: [
      "EXP-004 asks whether ARI3 can find the stored records that answer a question, inside the question's date, language, sector and outlet limits. Each record is a headline and the feed's own summary, capped at 500 characters. No full article text is stored, so EXP-004 measures retrieval over ARI3's stored evidence, not over complete articles.",
      "Four retrieval methods were compared on 37 development questions under a selection rule committed before any result. The hybrid method, which combines keyword search and sentence embeddings by reciprocal rank fusion, was chosen and frozen, then run once on 19 held-out test questions.",
      "On the 12 test questions with at least one item the editor judged relevant, macro Recall@10 was 0.770 and Hit@10 was 1.000. This does not mean ARI3 finds 77% of all relevant evidence. Recall is measured against the pool of items the methods retrieved and the editor judged.",
    ],
    meta: [
      { label: "Experiment", value: "EXP-004. It does not imply ARI3 v0.0.4" },
      { label: "Closed", value: "2026-10-01" },
      { label: "Ledger claim", value: "C-0010", href: "/ari3/claims#c-0010" },
      { label: "Questions", value: "56, drafted and reviewed by the editor, frozen 2026-09-30. 37 development, 19 test (seed 4)" },
      { label: "Questions fingerprint", value: "sha256 d1d17cb4cfe34196b05724dd8623ad4c94ce9c69d00420ba9af3290cf73d4ad4", mono: true },
      { label: "Relevance judgments", value: "819 question and item pairs judged by the editor, blind to method, rank and score: 318 relevant, 273 not relevant, 228 unsure" },
      { label: "Judgments fingerprint", value: "sha256 bda481d21f0b551f985d6ba05caa08a704542ec6c64c5baf7896ad9523153822", mono: true },
      { label: "Index", value: "7,955 stored items first seen before 2026-09-30 08:00 UTC, from 94 outlets" },
      { label: "Frozen retriever", value: "44421a5, sha256 3b55fcebbb08ec54b87198ab4a18e2f1b2bd0b922c6677428f525ceeadfd6b21", href: `${REPO}/blob/44421a59654974f803c288f52d9cd52b3a60fde7/experiments/exp-004-grounded-retrieval/frozen/retriever_v1.json`, mono: true },
      { label: "Test result", value: "b9f9e6c, sha256 bf44847928dc7fd53f7c646e0c158ba3005ba1a39f6d1b01a5a6937d7fc87d19", href: `${REPO}/blob/b9f9e6c23275edde98f47c8f7518597df693ba84/experiments/exp-004-grounded-retrieval/results/test-retrieval-v1.json`, mono: true },
      { label: "Embedder", value: "paraphrase-multilingual-MiniLM-L12-v2 @ e8f8c21", mono: true },
    ],
    question: "Can ARI3 find the stored records that answer a question, within the question's date, language, sector and outlet limits?",
    preregistered: "Partly. The rule for choosing a retriever on development questions, and the single run on test questions, were committed before any result. The rule was amended once, before the development run. EXP-004 had no pass criteria.",
    method: [
      "56 questions, reviewed and frozen by the editor",
      "Each method's top 10 pooled and judged by the editor, blind to method, rank and score",
      "Questions split into 37 development and 19 test",
      "Four methods compared on development questions: keyword search with two tokenizers, sentence embeddings, and a hybrid of the two",
      "Hybrid chosen by the committed rule and frozen",
      "Frozen hybrid run once on the test questions",
    ],
    held: [
      "Filters applied before ranking: dates, language, sector, outlet and the time cutoff",
      "The frozen index of 7,955 items",
      "The retriever configuration, frozen before the test run",
    ],
    changed: ["First retrieval experiment. No earlier version to compare against."],
    threats: [
      "Only 12 answerable test questions carry the main metrics.",
      "Recall is measured against the judged pool, the union of each method's top 10, not against every relevant item in the corpus.",
      "Recall@10 is capped for questions with more than 10 relevant items. Two test questions reached the cap.",
      "Retrieval in languages other than English is not established. Most non-English judgments are unsure, and no non-English test question has a resolved relevant item.",
      "Some filtered questions have small candidate sets, 10 to 16 eligible items, where high recall comes close to being guaranteed.",
      "One person judged relevance, and 228 of the 819 judgments are unsure.",
      "Feed language tags contain known errors.",
    ],
    resultsIntro: "The frozen hybrid retriever, run once on the 19 test questions. Hit, recall and reciprocal rank cover the 12 questions with at least one item judged relevant.",
    metrics: [
      { name: "Recall@10", b: 0.77, label: "hybrid", format: "pct", note: "Macro average over 12 questions" },
      { name: "Recall@5", b: 0.438, label: "hybrid", format: "pct" },
      { name: "Hit@10", b: 1.0, label: "hybrid", format: "pct", note: "12 of 12 questions" },
      { name: "Hit@5", b: 1.0, label: "hybrid", format: "pct", note: "12 of 12 questions" },
      { name: "Mean reciprocal rank", b: 0.958, label: "hybrid", format: "num" },
      { name: "Unsure share of the top 10", b: 0.311, label: "hybrid", format: "pct", lowerIsBetter: true, note: "18 questions with results" },
    ],
    benefits: [
      "Each of the 12 answerable test questions had a relevant item in its top 5",
      "Median retrieval time 67.4 ms over the 19 test queries on a local CPU (p95 344.4 ms), retrieval only",
      "No result broke a filter or the time cutoff",
    ],
    costs: [
      "Recall@5 was 0.438, so on average fewer than half of each question's judged relevant items reached the top 5",
      "31% of top-10 results were judged unsure",
    ],
    surprises: [
      "On development questions, hybrid led keyword search by 0.169 in Recall@10, but the 95% interval ran from -0.006 to 0.352. The selection rule's practical-tie clause decided.",
      "Keyword search and sentence embeddings found mostly different items. In the judging pool their top-10 sets have a Jaccard overlap of 0.12, which is why both were pooled and why the hybrid combines them.",
    ],
    engineering: [
      "Read-only retrieval over the SQLite store, with FTS5 keyword search and stored sentence embeddings (src/rag_*.py)",
      "A blind relevance-judging deck in the ARI3 review app",
      "Guards on the test run, which refuses to start without a frozen retriever and refuses to run twice",
    ],
    log: [
      { step: "Observation", text: "Answering questions about the corpus needs the right stored records first, inside each question's limits." },
      { step: "Idea", text: "Combine keyword search and sentence embeddings, and choose between methods by a rule fixed in advance." },
      { step: "Experiment", text: "EXP-004: 56 frozen questions, 819 blind judgments, selection on development questions, one test run." },
      { step: "Result", text: "Hybrid frozen. Test Recall@10 0.770 and Hit@10 1.000 on 12 answerable questions." },
      { step: "New question", text: "Can a language model answer from these records without claiming more than they say? That is EXP-005, in development." },
    ],
    lessons: [
      "Expected: one method would clearly win. Observed: hybrid led, but its lead over keyword search on development questions was within noise.",
      "Non-English relevance could not be judged reliably, so retrieval in other languages stays unmeasured.",
    ],
    openQuestions: [
      "How does retrieval do in languages other than English, judged by someone who reads them?",
      "How should the index be refreshed as the corpus grows? A refreshed index is a new retrieval version with its own check.",
    ],
    reproduce: {
      text: "The questions, judgments, split, frozen retriever and both results are public. The item store and index stay local, so outsiders can check the hashes but cannot rerun retrieval.",
      commands: `git clone ${REPO}.git
cd fashion-trend-crawler
git show 44421a5:experiments/exp-004-grounded-retrieval/frozen/retriever_v1.json | sha256sum
git show b9f9e6c:experiments/exp-004-grounded-retrieval/results/test-retrieval-v1.json | sha256sum`,
    },
  },
  {
    id: "EXP-003",
    slug: "exp-003",
    version: "v0.0.3",
    name: "INTEGRITAS",
    motto: "The evidence can be trusted.",
    status: "Released",
    headline: "Both parts ran once. Frozen v0.0.2 kept its coverage on later articles but missed its accuracy pass mark, 0.833 against 0.85. The forecast detector never flagged a forecast.",
    summary: [
      "EXP-003 asks whether the evidence ARI3 produces can be trusted, in two parts. EXP-003A tested frozen v0.0.2 on articles published after it was frozen. EXP-003B trained a new perception head to tell a prediction from a report.",
      "EXP-003A ran once on 150 items published after the freeze and labeled by the editor. The prediction sets held the right answer for 0.927 of them and the not-sure share was 0.327, so H1 and H3 were supported. Accuracy was 0.833 against a pass mark of 0.85, so H2 was not supported. The model was not refit, recalibrated or retuned, and the evaluation was not rerun.",
      "EXP-003B ran once, as pre-registered. H4 failed: the new head answered \"not a prediction\" for every test item, so its balanced accuracy was 0.50, the same as always answering no. H5 held: coverage was 0.961.",
      "The failed forecast head is frozen and hashed, and it is not used. Forecast articles stay in the mention counts. v0.0.3 was released on 2026-10-03 with a release manifest. The style classifier is still the frozen v0.0.2 model.",
    ],
    meta: [
      { label: "Experiment", value: "EXP-003 (EXP-003A Temporal Generalization, EXP-003B Forecast Detection)" },
      { label: "Pre-registration", value: "2ff1c53, 2026-09-26 22:30 UTC", href: `${REPO}/blob/2ff1c53/models/ari3-v0.0.3/PREREGISTRATION.md`, mono: true },
      { label: "Pre-registration hash", value: "sha256 fa65367d3166cba52903229bfd849ce34022b536e93ae6c62341325e7911aff1", mono: true },
      { label: "EXP-003A run", value: "2026-10-02, once" },
      { label: "EXP-003A record", value: "1c78f56", href: `${REPO}/commit/1c78f56e865a34d044cd092d81a8adb4623233fc`, mono: true },
      { label: "EXP-003A dataset", value: "150 time-holdout labels by the editor (82 yes, 68 no), frozen and committed before the run" },
      { label: "EXP-003A gold fingerprint", value: "sha256 7e15f2a1c9595fce12dffd5558b9e38e1845a32a22052b0664649235676d9b7d", mono: true },
      { label: "EXP-003A model", value: "ari3-v0.0.2, unchanged. Weights sha256 f6b25eb421e2766cc2681f9b2a6816330ab50569bae752a73b231ed7fe282f09", mono: true },
      { label: "EXP-003A eligibility", value: "Amended 2026-09-30, before any label existed", href: `${REPO}/blob/3132885c0e90406e8296f2bfbf98aeeb12f89997/models/ari3-v0.0.3/AMENDMENT_2026-09-30_holdout_eligibility.md` },
      { label: "EXP-003B run", value: "2026-09-26, once" },
      { label: "EXP-003B record", value: "bbbaaf0", href: `${REPO}/commit/bbbaaf0768515d4b37e447813036117950086adb`, mono: true },
      { label: "EXP-003B dataset", value: "250 is_forecast labels by the editor (35 forecasts), made after the pre-registration" },
      { label: "Dataset fingerprint", value: "sha256 ff36351a44866144506dddf9cf58fdf299dd61100ed49238c534f2d75633ec70", mono: true },
      { label: "is_forecast head", value: "Frozen and hashed, not used. manifest_sha256 c39b1f601e7d2fa137a48532ceddea38bb7230cc2b7e0976e4ffcb60b93a6d77", mono: true },
      { label: "Release manifest", value: "2026-10-03, manifest_sha256 846b249dfaa46c0aec920998d8f83e0cc50c10de7974793516fa60fcd894ebc1", href: `${REPO}/blob/master/models/ari3-v0.0.3/manifest.json`, mono: true },
      { label: "Environment", value: "Recorded in the forecast head's manifest and in the EXP-003A result file" },
      { label: "Random seeds", value: "EXP-003B queue: 11. EXP-003A queue: 13. Model fitting is deterministic." },
    ],
    question: "Can the evidence ARI3 produces be trusted: do its judgments hold on articles it could not have seen (EXP-003A), and can it separate predictions from reports (EXP-003B)?",
    preregistered: "Yes. Both parts, their five hypotheses, a reason for each threshold and a failure interpretation for each were committed before any EXP-003 label existed.",
    hypotheses: [
      { id: "H1", claim: "003A: coverage holds on new items", test: "Coverage on the time holdout ≥ 0.90", result: "0.927 (139 of 150)", verdict: "Supported" },
      { id: "H2", claim: "003A: accuracy holds on new items", test: "Accuracy on the time holdout ≥ 0.85", result: "0.833 (125 of 150)", verdict: "Not supported" },
      { id: "H3", claim: "003A: not-sure rate matches the test set", test: "Not-sure share on the time holdout ≤ 0.35", result: "0.327 (49 of 150)", verdict: "Supported" },
      { id: "H4", claim: "003B: the model learns the task", test: "Balanced accuracy ≥ 0.75 and above the majority baseline", result: "0.50, equal to the baseline", verdict: "Not supported" },
      { id: "H5", claim: "003B: coverage holds for the new task", test: "Coverage ≥ 0.90", result: "0.961", verdict: "Supported" },
    ],
    why: [
      "Every earlier test used articles collected before the model was trained. In use, the model meets articles that did not exist when it was frozen, so only post-freeze data shows how it will behave. v0.0.2 answered not-sure for 25% of its test set but 42% of the whole corpus, a first sign that this matters.",
      "An article saying a look \"will be big next season\" is a prediction. Counted as a mention, it feeds the press's forecasts back into the evidence that later trend models will read. A forecast detector has to exist before those models run.",
    ],
    method: [
      "003A: 150 items published after the v0.0.2 freeze, drawn in turn from each sector",
      "003A: labeled by the editor, then frozen and committed",
      "003A: frozen v0.0.2 scored them once, unchanged",
      "003B: 250 is_forecast labels, 150 random and 100 containing a forecast word",
      "003B: split fixed by a hash of each item, 161 train, 38 calibration, 51 test",
      "003B: new logistic regression head on the shared, frozen sentence embeddings",
      "003B: temperature scaling, then a split conformal threshold at α = 0.10",
      "003B: scored on 51 test items, both groups together and separately",
    ],
    held: [
      "The shared perception architecture: embedder, classifier type, calibration, conformal step",
      "Frozen v0.0.2 for EXP-003A, not refit, recalibrated or retuned",
      "Thresholds, datasets, splits, seeds and labeling rules, as committed",
    ],
    changed: [
      "A second perception task, is_forecast, with its own labels and head",
    ],
    threats: [
      "5 forecasts in the EXP-003B test set, so every forecast metric is highly uncertain.",
      "One editor labels every item, with no second labeler.",
      "The 100 forecast-word items are not a random sample.",
      "The EXP-003A sample covers 39 outlets and about 3.3 days of publication, so a later period may behave differently.",
      "EXP-003A measures how v0.0.2 does on newer articles. It does not explain why accuracy fell.",
      "Publish times are the times feeds report, and a feed can report them wrongly.",
      "88.6% of stored items came from the editorial sector on 2026-10-03. The EXP-003A draw rotates through sectors, so its sample is less editorial than the corpus.",
      "Most labeled items are tagged English.",
    ],
    compare: { a: "Always no", b: "is_forecast", n: 51 },
    resultsIntro: "EXP-003A: frozen v0.0.2 scored once on the 150 time-holdout items. EXP-003B: the is_forecast head and always answering no, scored on the same 51 held-out items.",
    metrics: [
      { name: "003A coverage (target ≥ 0.90)", b: 0.927, label: "v0.0.2", format: "pct", note: "139 of 150. Supported" },
      { name: "003A accuracy (pass mark 0.85)", b: 0.833, label: "v0.0.2", format: "pct", note: "125 of 150, 95% interval 0.766 to 0.884. Not supported" },
      { name: "003A not-sure share (limit 0.35)", b: 0.327, label: "v0.0.2", format: "pct", lowerIsBetter: true, note: "49 of 150. Supported" },
      { name: "003B balanced accuracy", a: 0.5, b: 0.5, format: "pct", note: "Pre-registered pass mark 0.75. Not supported" },
      { name: "003B forecasts caught (recall)", a: 0, b: 0, format: "pct", note: "0 of 5 test forecasts" },
      { name: "003B plain accuracy", a: 0.902, b: 0.902, format: "pct", note: "Identical to always answering no" },
      { name: "003B coverage (target ≥ 0.90)", b: 0.961, format: "pct" },
    ],
    benefits: [
      "003A: on newer articles, v0.0.2's prediction sets still held the right answer 92.7% of the time",
      "003A: the not-sure share (0.327) stayed closer to the test set (0.25) than to the whole corpus (0.42)",
      "003B: conformal coverage was 0.961 and met H5, despite the head failing to identify any forecasts. Coverage therefore does not establish useful forecast discrimination",
      "003B: the balanced-accuracy test, chosen in advance, exposed a failure that 90% plain accuracy would have hidden",
    ],
    costs: [
      "003A: accuracy fell from 0.902 on v0.0.2's own test set to 0.833 on newer articles, below the pre-registered 0.85",
      "003A: 11 confident mistakes on 150 items, against 2 on the 61-item test set",
      "003B: no forecast was detected, so forecast articles remain in the mention counts",
    ],
    surprises: [
      "No item scored above 0.41, so the head never reached the 0.50 point needed to answer yes. Forecasts were 11% of its training items, and temperature scaling (T = 1.84) flattened its probabilities further. Post-hoc check, not pre-registered.",
      "The head ranked forecasts almost perfectly on its training items (AUC 0.985) and weakly on test items (0.674 from 5 forecasts). It fit its 18 training forecasts more than it learned the idea. Post-hoc check, not pre-registered.",
    ],
    engineering: [
      "Review app runs any labeling queue, each with its own task, split and group tag",
      "Queue builders for the forecast sample and the time holdout (src/label_tool.py)",
      "One-shot EXP-003B runner that refuses to run twice (src/ari3_exp003b_run.py)",
      "EXP-003A runner that checks every label and eligibility rule, freezes the gold labels, and refuses to score before they are committed and public (src/ari3_exp003a_run.py)",
      "Database migration 0004: write-once first-seen times, so a holdout can show when each item arrived",
      "Manifests now record the environment, runtime and labeling queue fingerprint",
    ],
    log: [
      { step: "Observation", text: "Press predictions were being counted as mentions of the looks they predicted." },
      { step: "Idea", text: "Add a second perception task that tells a prediction from a report." },
      { step: "Experiment", text: "EXP-003B (250 labels) and EXP-003A (150 time-holdout labels), pre-registered, each run once." },
      { step: "Result", text: "003B: H4 failed, the head never answered yes, and H5 held. 003A: coverage and the not-sure share held, and accuracy missed its pass mark." },
      { step: "New question", text: "Which newer articles does v0.0.2 get wrong, and would labels from newer periods fix them? Any fix is a new pre-registered experiment." },
    ],
    lessons: [
      "Expected: the style task's design would transfer to forecasts. Observed: with forecasts at 11% of labels, it never predicted one.",
      "Plain accuracy looked like 90% success. Balanced accuracy showed it was no better than always answering no.",
      "A failed hypothesis still produced a usable record: what failed, the observed failure pattern, and a frozen head that is kept out of the counts.",
      "Expected: v0.0.2 would keep its accuracy on newer articles. Observed: accuracy fell to 0.833 while coverage held at 0.927.",
    ],
    openQuestions: [
      "Which kinds of newer articles does v0.0.2 get wrong, and why?",
      "How many forecast labels would a head need before it separates predictions from reports on new items?",
      "Would more context than a headline and excerpt make forecasts easier to recognize?",
    ],
    reproduce: {
      text: "The pre-registration, both runners, the frozen forecast head, the EXP-003A gold labels (item IDs and labels) and the EXP-003A result are public. The items' text stays in the project's local database, so outsiders can check the hashes but cannot rerun the scoring. Both runners refuse to run a second time.",
      commands: `git clone ${REPO}.git
cd fashion-trend-crawler
git show 2ff1c53:models/ari3-v0.0.3/PREREGISTRATION.md | sha256sum
git show bbbaaf0:models/ari3-v0.0.3/is_forecast/weights.npz | sha256sum
git show 88eb59e:models/ari3-v0.0.3/exp003a/gold_v1.jsonl | sha256sum
git show 1c78f56:models/ari3-v0.0.3/exp003a/result.json | sha256sum`,
    },
  },
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
      "Source bias. About 87% of stored items came from the editorial sector when EXP-002 ran (2026-09-26), so small sectors had few examples.",
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
      "Source bias. Editorial sources already dominated the stored corpus when EXP-001 ran.",
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
  { version: "v0.0.3", name: "INTEGRITAS", motto: "The evidence can be trusted.", status: "Released", exp: "exp-003" },
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
      { area: "Pre-registration", detail: "Every experiment that compares versions commits its pass criteria before its data" },
      { area: "Grounded retrieval (EXP-004)", detail: "A frozen retriever, tested once on held-out questions" },
      { area: "INTEGRITAS (v0.0.3)", detail: "Released 2026-10-03. Both parts of EXP-003 ran once, and the results include a failed accuracy criterion and a failed forecast detector" },
    ],
  },
  {
    status: "In progress", mark: "half", items: [
      { area: "Lexicon v1", detail: "73 style terms chosen by the editor, loaded 2026-09-26 and matched in items stored up to then. Seven ambiguous terms are kept but left out of every count until their uses are checked one by one" },
      { area: "Grounded answers (EXP-005)", detail: "A prompt and answer schema that answer questions only from retrieved ARI3 items are in development. In the two latest development batches, of five and eight questions, every claim was supported by its cited items, judged only against the evidence each answer was given. A side-by-side test of a prompt that states the schema's size limits found no difference from the current prompt, so the current prompt stays. These are development results, not an estimate of general performance. No final evaluation has run" },
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
