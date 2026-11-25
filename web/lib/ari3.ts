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

// Committed experiment folders, for the entries that have no release version.
const EXP_DIR = `${REPO}/blob/master/experiments`;

const ENV_001 = "Python 3.13.2, numpy 2.5.0, scikit-learn 1.9.1, sentence-transformers 6.1.0";

export const EXPERIMENTS: Experiment[] = [
  {
    id: "EXP-009",
    slug: "exp-009",
    version: "",
    kicker: "ARI3 walk-forward experiment, with no release version",
    name: "Predictors of the editor's decisions",
    motto: "",
    status: "Closed",
    headline: "On 185 signal cards, the editor's own past decisions predicted her next keep-or-drop call far better than DeepSeek reading the card: kappa 0.542 for \"same as last time\" and 0.515 for a small taste model, against 0.182.",
    summary: [
      "EXP-007 and EXP-008 found that an LLM reading a report card does not track the editor's keep-or-drop decisions, with or without a written profile of her taste. EXP-009 asks which kind of predictor does best: her own past decisions, a small model trained on them, or the LLM, with and without a memory of her earlier calls on the same term.",
      "Five methods guessed each of the 185 signal cards in weeks 2 to 7, each using only what was known before that card's week. This is a walk-forward evaluation, also called time-series cross-validation. The editor's decisions were already known when the design was written, so this is not a blind test like EXP-007. Every method, feature, rule and threshold was fixed and committed before any score was computed.",
      "H1 and H2 were supported. The taste model beat DeepSeek by +0.333 in kappa, and a memory of the editor's earlier calls raised DeepSeek's kappa from 0.182 to 0.436. H3 was not supported: the taste model tied the plain rule \"do what she did last time\", with a difference of -0.027 and an interval from -0.188 to +0.135.",
    ],
    meta: [
      { label: "Experiment", value: "EXP-009, with no release version" },
      { label: "Pre-registration", value: "2026-11-25, before any score was computed and before any new model call", href: `${EXP_DIR}/exp-009-editor-taste-predictors/PREREGISTRATION.md` },
      { label: "Protocol", value: "protocol_v2.json. It supersedes v1, under which nothing ran", href: `${EXP_DIR}/exp-009-editor-taste-predictors/protocol/protocol_v2.json`, mono: true },
      { label: "Results", value: "2026-11-25", href: `${EXP_DIR}/exp-009-editor-taste-predictors/RESULTS.md` },
      { label: "Target cards", value: "185 signal cards, weeks 2 to 7 (report dates 2026-10-18 to 2026-11-22), none excluded. The editor kept 130" },
      { label: "History only", value: "Week 1 (2026-10-11), used as history and training data, never as a target" },
      { label: "DeepSeek calls", value: "185 for M4, all valid on the first attempt, estimated cost 0.17 USD, under a running 0.50 USD stop" },
      { label: "Bootstrap", value: "Paired over cards, 10,000 resamples, seed 9009, 95% percentile interval" },
      { label: "Metrics", value: "runs/comparison.json, with the taste model's weights", href: `${EXP_DIR}/exp-009-editor-taste-predictors/runs/comparison.json`, mono: true },
    ],
    question: "Which kind of predictor best matches the editor's keep-or-drop decisions on the weekly report cards: her own past decisions, a small model trained on them, or an LLM, with and without a memory of her earlier calls on the same term?",
    preregistered: "Yes. The five methods, the taste model's features and settings, the three hypotheses and the bootstrap test were committed on 2026-11-25, before any score was computed. Protocol v2 replaced v1, under which nothing ran, because v1's freeze check refused the run on a type mismatch.",
    hypotheses: [
      { id: "H1", claim: "The taste model (M2) beats DeepSeek (M3)", test: "Paired bootstrap of the kappa difference, keep against not-keep: lower bound above 0", result: "+0.333 [+0.136, +0.524]", verdict: "Supported" },
      { id: "H2", claim: "DeepSeek with memory (M4) beats DeepSeek (M3)", test: "The same test", result: "+0.254 [+0.063, +0.440]", verdict: "Supported" },
      { id: "H3", claim: "The taste model (M2) beats same as last time (M1)", test: "The same test", result: "-0.027 [-0.188, +0.135]", verdict: "Not supported" },
    ],
    why: [
      "In RLHF terms (Christiano et al., 2017; Ouyang et al., 2022), a model learned from one person's labels is a first reward model. Lee et al. (ICML 2024) ask whether AI feedback can replace that human signal. EXP-009 scores both kinds of predictor on the same cards.",
      "Most terms recur from week to week, so the editor's earlier call on the same term may carry much of the signal. M1 tests that rule on its own, and M4 gives the same history to the LLM.",
    ],
    method: [
      "Walk-forward split: a card in week k is predicted from weeks 1 to k-1 only. Week 1 is history and training data, never a target",
      "M0, always keep: every card is kept",
      "M1, same as last time: the editor's decision on the same term in the most recent earlier week with a card for it. A term with no earlier card is kept",
      "M2, taste model: a logistic regression (Cox, 1958) on card features (items, outlets, sectors, days covered, weaknesses, baseline confidence, card type) and history features (seen before, last decision was keep, share of earlier cards kept, number of earlier cards). L2 penalty 0.1, batch gradient descent from zero for 2,000 iterations, keep when the probability is at least 0.5",
      "M3, DeepSeek: EXP-007's sealed thinking-off answers in the app's option order, with no new calls",
      "M4, DeepSeek with memory: EXP-007's prompt and settings, plus the editor's decision, volatility and any confidence she set on the same term in every earlier week. Decisions and labels only, none of her thoughts",
      "Scored as Cohen's kappa on keep against not-keep, compared by a paired bootstrap over cards",
    ],
    held: [
      "The 185 target cards and the walk-forward split",
      "EXP-007's prompt, definitions and reader settings, for M3 and M4",
      "Every method, feature, rule and threshold, committed before scoring",
    ],
    changed: [
      "What each method knows: nothing (M0), the editor's last call on the term (M1), a model fitted on earlier weeks (M2), the card alone (M3), the card plus the term's history (M4)",
    ],
    threats: [
      "185 cards from six weeks, and cards within a week are not independent, so the intervals are optimistic.",
      "Only 15 new terms, so results on new terms are descriptive.",
      "The editor's decisions were known before the design. Every method and feature was fixed and committed before scoring, but this is not a blind test.",
      "The first taste model learns from the 33 cards of week 1, which have no history features, so its early weeks are weak.",
      "One editor, and one LLM.",
    ],
    compare: { a: "Agreement", b: "Kappa", n: 185 },
    resultsIntro: "Keep against not-keep on the 185 target cards. The editor kept 130. Kappa on terms seen before covers 170 cards, and on new terms 15.",
    metrics: [
      { name: "M0 always keep", a: 0.703, b: 0, format: "pct", note: "Keeps all 185. Kappa is 0 by definition" },
      { name: "M1 same as last time", a: 0.822, b: 0.542, format: "pct", note: "Keeps 143. Kappa 0.632 on terms seen before, 0.000 on new terms" },
      { name: "M2 taste model", a: 0.822, b: 0.515, format: "pct", note: "Keeps 153. Kappa 0.503 on terms seen before, 0.500 on new terms" },
      { name: "M3 DeepSeek", a: 0.735, b: 0.182, format: "pct", note: "Keeps 173. Kappa 0.170 on terms seen before, 0.186 on new terms" },
      { name: "M4 DeepSeek with memory", a: 0.8, b: 0.436, format: "pct", note: "Keeps 159. Kappa 0.452 on terms seen before, 0.286 on new terms" },
    ],
    benefits: [
      "The plain rule and the taste model both reached kappa above 0.5, the first predictors in this series to track the editor's keep-or-drop calls clearly",
      "Memory of the editor's earlier calls more than doubled DeepSeek's kappa, from 0.182 to 0.436",
      "The taste model is readable: each target week's fitted weights are committed. The last model's largest weights are the share of earlier cards kept and whether the last one was kept, then item count, outlet count and days covered",
      "M4's 185 calls were all valid on the first attempt, at an estimated 0.17 USD",
    ],
    costs: [
      "The taste model did not beat the plain rule (H3 not supported)",
      "Even with memory, DeepSeek stayed below the plain rule. M1 led M4 by +0.106, with an interval from -0.035 to +0.248, so the difference is not significant",
      "The taste model was weak in early weeks: kappa 0.129 for the week ending 2026-10-18 and 0.000 for 2026-11-01",
      "Not a blind test, because the editor's decisions were known before the design",
    ],
    surprises: [
      "The taste model was the only method with clear agreement on terms the editor had never seen, kappa 0.500 against 0.000 for the plain rule. That rests on 15 cards, so it is descriptive only.",
      "The first taste model, trained on 33 cards with no history, put its largest weights on card type and baseline confidence. By the last week, the history features carried the most weight.",
    ],
    engineering: [
      "A pure-Python logistic regression with fixed settings, so every fit is deterministic (`src/exp009.py`)",
      "A freeze check that refuses to run when the frozen protocol does not match. It refused v1 on a type mismatch, and v2 fixed it",
      "A running cost stop at 0.50 USD for the M4 calls",
    ],
    log: [
      { step: "Observation", text: "Two LLM readers, with and without a written taste profile, barely tracked the editor's report decisions." },
      { step: "Idea", text: "Compare the LLM with predictors built from her own past decisions, walking forward one week at a time." },
      { step: "Experiment", text: "EXP-009: five methods on 185 cards, three pre-registered hypotheses." },
      { step: "Result", text: "H1 and H2 supported, H3 not supported. Her own history predicts her next calls best." },
      { step: "New question", text: "Does the taste model pull ahead of the plain rule as more weeks accumulate, and on new terms?" },
    ],
    lessons: [
      "The editor's own past decisions predicted her next ones better than an LLM reading the card.",
      "A memory of her earlier calls on the term was the main thing the LLM lacked.",
      "A plain rule is a strong baseline. A learned model has to beat it, not only the LLM.",
    ],
    openQuestions: [
      "Does the taste model's lead on new terms hold beyond 15 cards?",
      "Would the taste model beat the plain rule with more weeks of training data?",
    ],
    reproduce: {
      text: "The pre-registration, both protocol files, the sealed-output manifest, the metrics and the taste model's weights are public. The card-by-card predictions and the editor's decision logs stay local, so outsiders can check the fingerprints but cannot rerun the comparison.",
      commands: `git clone ${REPO}.git
cd fashion-trend-crawler
cat experiments/exp-009-editor-taste-predictors/runs/comparison.json`,
    },
  },
  {
    id: "EXP-008",
    slug: "exp-008",
    version: "",
    kicker: "ARI3 labeler experiment, with no release version",
    name: "Taste profile",
    motto: "",
    status: "Closed",
    headline: "A written profile of the editor's judgment, induced by a Claude subagent from her other weeks, did not bring DeepSeek's report decisions closer to hers: kappa 0.086 against 0.079. Neither hypothesis was supported.",
    summary: [
      "EXP-007 found that a zero-shot AI reader barely tracks the editor on the weekly report decisions. EXP-008 asks whether a short written profile of her judgment closes that gap. It follows the constitution-style idea in RLAIF (Lee et al., ICML 2024; Bai et al., 2022), where written principles steer an AI labeler, except that here the principles are induced from one person's own decisions.",
      "For each of the seven weeks, a fresh Claude subagent wrote a profile of about 350 to 550 words from the editor's decisions in the other six weeks only, with no signal, brand, outlet or headline named. Software checked each profile for leaks, and all seven were sealed by SHA-256 before any DeepSeek call. EXP-007's thinking-off reader then decided the same 226 cards again, with the held-out week's profile added to its prompt.",
      "Neither pre-registered hypothesis was supported. Four-way kappa moved from 0.079 to 0.086, with an interval from -0.076 to +0.092. Keep-against-anything-else kappa fell from 0.188 to 0.082, with an interval from -0.231 to +0.016. The profile made the AI drop 4 cards, all of which the editor also dropped, but it also stopped the AI from using the watchlist, and the AI kept 212 of 216 cards. The editor kept 150.",
    ],
    meta: [
      { label: "Experiment", value: "EXP-008, with no release version" },
      { label: "Pre-registration", value: "2026-11-25, before any model call", href: `${EXP_DIR}/exp-008-taste-profile/PREREGISTRATION.md` },
      { label: "Amendment 1", value: "2026-11-25, the subagent's reply channel, before any profile was sealed or read", href: `${EXP_DIR}/exp-008-taste-profile/AMENDMENT_2026-11-25_handback.md` },
      { label: "Amendment 2", value: "2026-11-25, self-edits and short replies, the owner's decision, before any profile was sealed or read", href: `${EXP_DIR}/exp-008-taste-profile/AMENDMENT_2026-11-25_self_edits.md` },
      { label: "Results", value: "2026-11-25", href: `${EXP_DIR}/exp-008-taste-profile/RESULTS.md` },
      { label: "Profile writer", value: "A fresh Claude Code general-purpose subagent per held-out week, model claude-opus-5-5" },
      { label: "Reader", value: "DeepSeek deepseek-flash, thinking off, temperature 0, top_p 1, max_tokens 1000, as in EXP-007" },
      { label: "Cards", value: "226 required cards (218 signal, 8 duplicate), in app order and with every option list reversed: 452 calls, all valid on the first attempt" },
      { label: "Cost", value: "Estimated 0.45 USD for the DeepSeek rerun, under a running 1.00 USD stop" },
      { label: "Bootstrap", value: "Paired over signal cards, 10,000 resamples, seed 8008, 95% percentile interval" },
      { label: "Metrics", value: "runs/comparison.json", href: `${EXP_DIR}/exp-008-taste-profile/runs/comparison.json`, mono: true },
    ],
    question: "Does a short profile of the editor's judgment, written by another AI from her decisions in other weeks, bring an AI reader's report decisions closer to hers?",
    preregistered: "Yes. Both hypotheses, the bootstrap test and the profile checks were committed on 2026-11-25, before any model call. Two amendments followed the same day, before any profile was sealed or read and before any DeepSeek call. The first allowed the reply every subagent must send. The second allowed a subagent to edit its own draft and send a short reply, and for held-out weeks 2026-10-11 and 2026-11-08 the second-attempt profile was used.",
    hypotheses: [
      { id: "H1", claim: "The profile raises kappa on the four signal decisions", test: "Paired bootstrap of the kappa difference against EXP-007 (0.079): lower bound above 0", result: "0.086, difference +0.006 [-0.076, +0.092]", verdict: "Not supported" },
      { id: "H2", claim: "The profile raises kappa on keep against anything else", test: "The same test against EXP-007 (0.188)", result: "0.082, difference -0.106 [-0.231, +0.016]", verdict: "Not supported" },
    ],
    why: [
      "EXP-007's zero-shot reader reached kappa 0.079 on the four signal decisions and kept far more cards than the editor. Its prompt held her definitions but nothing from her past decisions.",
      "In RLAIF, written principles steer an AI labeler (Bai et al., 2022; Lee et al., ICML 2024). EXP-008 tests principles induced from one editor's own decisions, held out by week, so that no profile has seen her answers for the cards it is used on.",
    ],
    method: [
      "Leave one week out: for each of the seven weeks, one profile written from the other six weeks only",
      "Each profile written by a fresh Claude subagent with no conversation history, reading only six input files: every card as the app shows it, followed by the editor's answer and thoughts",
      "The instructions asked for general rules only, about 350 to 550 words, with no trend, style or garment term, brand, person, outlet, event, headline or count",
      "Software checks on every profile: an audit of the subagent's tool calls, and a leak check for the 48 signal names, outlet names, any 5-word run from a headline, and an 800-word cap",
      "All seven profiles sealed by SHA-256 before any DeepSeek call. No one read them until the comparison was committed",
      "EXP-007's thinking-off reader rerun on the same 226 cards in both option orders, with the held-out week's profile added after the definitions",
      "Paired bootstrap over signal cards for H1 and H2, with an exact McNemar test reported beside them",
    ],
    held: [
      "The reader: deepseek-flash, thinking off, temperature 0, top_p 1, max_tokens 1000, JSON output",
      "The 226 cards, both option orders and the one-retry rule",
      "The editor's definitions and her decisions, as fingerprinted in EXP-007",
      "EXP-007's exclusions. The 2 cards decided before its plan are reported separately",
    ],
    changed: [
      "The prompt only: the held-out week's profile, added after the definitions (`protocol/prompt_v2.md`)",
    ],
    threats: [
      "About 216 signal cards, and cards within a week are not independent, so the bootstrap interval is optimistic.",
      "No length-matched control. Some of the changes could come from a longer prompt rather than from what the profile says.",
      "The same terms recur across weeks. The ban on names limits what carries over, but general rules learned from other weeks still apply to the same terms.",
      "The profiles are not reproducible: a second subagent would write a different one, and DeepSeek at temperature 0 is not guaranteed to be deterministic.",
      "Two weeks used second-attempt profiles (amendment 2): 2026-10-11 and 2026-11-08. The 2026-11-08 week, which shows the highest kappa, is one of them.",
      "The profile writer (Claude) and the reader (DeepSeek) are different models, so the result says nothing about Claude as a labeler.",
    ],
    compare: { a: "No profile (EXP-007)", b: "Profile", n: 216 },
    resultsIntro: "The same reader on the same 216 signal cards in app order, without and with the profile. The editor kept 150 and dropped 53. Order-swap counts cover all 226 cards.",
    metrics: [
      { name: "Kappa, four signal decisions", a: 0.079, b: 0.086, format: "pct", note: "Difference +0.006 [-0.076, +0.092]. H1 not supported" },
      { name: "Kappa, keep against anything else", a: 0.188, b: 0.082, format: "pct", note: "Difference -0.106 [-0.231, +0.016]. H2 not supported" },
      { name: "Decision agreement", a: 0.681, b: 0.713, format: "pct", note: "Always-keep baseline 0.694" },
      { name: "Cards the AI kept, of 216", a: 202, b: 212, format: "num", note: "The editor kept 150" },
      { name: "Cards the AI dropped", a: 0, b: 4, format: "num", note: "The editor dropped 53, including all 4" },
      { name: "Watchlist or merge choices", a: 14, b: 0, format: "num" },
      { name: "Volatility agreement on cards both kept", a: 0.361, b: 0.413, format: "pct", note: "n 147 and 150" },
      { name: "Duplicate collapse agreement", a: 0.625, b: 0.625, format: "pct", note: "8 cards, descriptive" },
      { name: "Decisions changed by the order swap, of 226", a: 26, b: 8, format: "num", note: "11.5% and 3.5%" },
    ],
    benefits: [
      "On the four-way decision, 7 cards went from wrong to right with the profile and none went from right to wrong (exact McNemar, p = 0.016): the 4 correct drops and 3 cards the editor kept that EXP-007 had put on the watchlist",
      "The AI's answers became much less sensitive to option order: the swap changed 8 of 226 decisions, against 26 in EXP-007. Not a pre-registered hypothesis",
      "Volatility agreement rose slightly, from 0.361 to 0.413. Not a pre-registered hypothesis",
      "All 452 calls were valid on the first attempt, at an estimated 0.45 USD",
    ],
    costs: [
      "Keep-against-anything-else kappa fell from 0.188 to 0.082, though the interval includes 0",
      "The AI stopped using the watchlist, and it kept 212 of 216 cards",
      "Per-week kappa was 0 in five of the seven weeks, because the AI kept almost every card",
      "Two weeks needed a second profile attempt and an amendment to the transcript audit",
    ],
    surprises: [
      "The pre-registered transcript audit allowed only Read and Write, so no subagent could pass it: the harness makes every subagent return its final reply through one more tool call. Amendment 1 allowed that reply when it holds only a word count.",
      "Three of the four failed attempts edited their own profile, one of them 16 times, and two replied with a sentence instead of a bare number. All four read only their six allowed input files and passed the leak check.",
      "The only week with clear kappa, 2026-11-08 at 0.315, used a second-attempt profile.",
    ],
    engineering: [
      "A profile checker that prints only the names of matched words, never the profile text (`src/exp008.py check-profile`)",
      "An audit of each subagent's tool calls from its own transcript, amended twice, with tests",
      "Profile sealing that records each week's attempts, the checks run and the audit rules in force",
      "A running cost stop at 1.00 USD",
    ],
    log: [
      { step: "Observation", text: "EXP-007's AI reader kept far more cards than the editor and barely tracked her decisions." },
      { step: "Idea", text: "Give the reader a written profile of her judgment, induced from her other weeks." },
      { step: "Experiment", text: "EXP-008: seven leave-one-week-out profiles, checked and sealed, then the same 452 calls with the profile added." },
      { step: "Result", text: "H1 and H2 not supported. Fewer order flips and 4 correct drops, but no watchlist use." },
      { step: "New question", text: "Do the editor's own past decisions predict her next ones better than any AI reader? That became EXP-009." },
    ],
    lessons: [
      "A profile of general rules did not move the AI's keep-or-drop judgment toward the editor's.",
      "Changes that were mostly right can still leave kappa unchanged, because the AI went on keeping almost every card.",
      "A pre-registered audit has to be checked against the tools it runs in. The first version could not be passed by any subagent.",
    ],
    openQuestions: [
      "Would a prompt of the same length without the profile produce the same changes?",
      "Would a memory of the editor's calls on each term help more than general rules? EXP-009 tested this.",
    ],
    reproduce: {
      text: "The pre-registration, both amendments, the protocol fingerprints, the sealed manifests and the metrics are public. The profiles, their input files, the AI answers and the card-by-card detail stay local, so outsiders can check the fingerprints but cannot rerun the comparison.",
      commands: `git clone ${REPO}.git
cd fashion-trend-crawler
cat experiments/exp-008-taste-profile/runs/comparison.json`,
    },
  },
  {
    id: "EXP-007",
    slug: "exp-007",
    version: "",
    kicker: "ARI3 measurement of AI labelers, with no release version",
    name: "AI labeler alignment",
    motto: "",
    status: "Closed",
    headline: "On 216 signal cards, a zero-shot DeepSeek reader matched the editor's report decisions with kappa 0.079, and its agreement of 0.681 fell below the 0.694 of always answering keep. Letting it think first did not help.",
    summary: [
      "EXP-007 asks whether an LLM can stand in for the editor on ARI3LLA's weekly report decisions. It adapts the AI labeler alignment measure of Lee et al. (ICML 2024, RLAIF vs RLHF) from pairwise preferences to the editor's categorical decisions: keep, drop, merge or watchlist for each signal card, and collapse or not for each duplicate card.",
      "Three readers decided the same 226 required cards from seven prepared weeks, report dates 2026-10-11 to 2026-11-22: the editor in the ARI3 Review app, DeepSeek deepseek-flash with thinking off, and the same model with thinking on. The AI readers saw the card text, options and the editor's definitions word for word as the app shows them, with no links, article text, examples or earlier decisions. Their answers were sealed by SHA-256, and the comparison ran only after the editor's decision logs were fingerprinted.",
      "Neither AI reader tracked the editor. The thinking-off reader reached decision agreement 0.681 and kappa 0.079, and the thinking-on reader 0.667 and 0.071, both below the always-keep baseline of 0.694. Both kept far more than she did: the editor kept 150 of 216 signal cards, the thinking-off reader 202 and the thinking-on reader 196. EXP-007 was a measurement with no pass criteria.",
    ],
    meta: [
      { label: "Experiment", value: "EXP-007, a measurement with no release version" },
      { label: "Pre-registration", value: "2026-11-24, before any provider call and before the editor's backlog decisions", href: `${EXP_DIR}/exp-007-report-labeler-alignment/PREREGISTRATION.md` },
      { label: "Protocol v1 frozen", value: "2775bd1", href: `${REPO}/commit/2775bd1`, mono: true },
      { label: "Amendment", value: "2026-11-24, three readers, written before any AI answer existed", href: `${EXP_DIR}/exp-007-report-labeler-alignment/AMENDMENT_2026-11-24_three_readers.md` },
      { label: "Cards", value: "226 required cards from seven weeks, report dates 2026-10-11 to 2026-11-22: 218 signal and 8 duplicate" },
      { label: "Readers", value: "The editor. DeepSeek deepseek-flash with thinking off, in app order and reversed. The same model with thinking on, in app order only" },
      { label: "AI settings", value: "Thinking off: temperature 0, top_p 1, max_tokens 1000, JSON output. Thinking on: top_p 1, max_tokens 16000, reasoning text kept and sealed" },
      { label: "Compared", value: "2026-11-25 01:41 UTC", href: `${EXP_DIR}/exp-007-report-labeler-alignment/runs/comparison.json` },
      { label: "Runner", value: "src/exp007.py, sha256 c385e4f1d2e9f67840ecb644ea73ab34d8a90e383822b407788213b2cef21115", mono: true },
    ],
    question: "Can an LLM stand in for the editor on ARI3LLA's weekly report decisions?",
    preregistered: "Yes. The cards, readers, prompt, sealing rules and metrics were committed on 2026-11-24, before any provider call and before the editor decided the backlog cards. An amendment the same day added the thinking-on reader before any AI answer existed. EXP-007 is a measurement, with no pass criteria.",
    why: [
      "Lee et al. (ICML 2024) call the match between an AI labeler and human labels AI labeler alignment, and measure it on pairwise preferences. EXP-007 adapts it to the categorical decisions the editor makes on every weekly report.",
      "The thinking-on reader follows the chain-of-thought question in the same paper: does letting the labeler reason first change its agreement with the human?",
    ],
    method: [
      "226 required cards from seven prepared weeks: 218 signal cards (keep, drop, merge or watchlist) and 8 duplicate cards (collapse yes or no)",
      "The editor decided every card in ARI3 Review without opening evidence links, because the AI could not",
      "Each AI reader saw the title, card text, form fields and option lists the app shows, word for word, and the editor's definitions file, plus a short opening paragraph and the JSON output format",
      "Zero-shot only: no worked examples, no earlier weeks, no article text and no outside search",
      "Thinking off ran in app order and again with every option list reversed, to measure position bias. Thinking on ran in app order only",
      "One retry only when an answer could not be saved",
      "AI answers sealed by SHA-256 in a committed manifest. The editor's decision logs fingerprinted and committed before unsealing",
      "Measured: decision agreement and Cohen's kappa beside the majority-class baseline, keep against anything else, volatility on cards both kept, merge targets, duplicate collapse, kept-set overlap per week and position bias",
    ],
    held: [
      "The 226 cards, from frozen deck files",
      "The editor's 35 definitions, written and approved by her on 2026-11-24, shown word for word in the app and in the prompt",
      "The prompt (`protocol/prompt_v1.md`) and the one-retry rule, for both AI readers",
      "No links for any reader",
    ],
    changed: [
      "Thinking mode, off or on, between the two AI readers",
      "Option order, app order or reversed, for the thinking-off reader",
    ],
    threats: [
      "One editor, so agreement is with one person's judgment.",
      "The always-keep baseline is 0.694, so raw agreement says little on its own. Kappa corrects for chance agreement.",
      "Per-week kappa rests on about 30 cards and is noisy.",
      "No card was merged by both the editor and an AI reader, so merge-target agreement could not be measured.",
      "Duplicate results rest on 8 cards and are descriptive.",
      "Two cards decided before the plan existed (`signal:sneaker` and `signal:denim`, week of 2026-10-11) were decided without the definitions panel and are reported separately. The editor and both AI readers kept both.",
      "Zero-shot only. A reader taught from the editor's past decisions could behave differently, which is a separate experiment.",
    ],
    compare: { a: "Thinking off", b: "Thinking on", n: 216 },
    resultsIntro: "Each AI reader against the editor, in app order, on the 216 signal cards (the 8 duplicate cards for the duplicate row). No card was excluded.",
    metrics: [
      { name: "Decision agreement, four ways", a: 0.6806, b: 0.6667, format: "pct", note: "Always-keep baseline 0.694" },
      { name: "Decision kappa, four ways", a: 0.0793, b: 0.0711, format: "pct" },
      { name: "Keep against anything else, agreement", a: 0.7315, b: 0.7037, format: "pct", note: "Always-keep baseline 0.694" },
      { name: "Keep against anything else, kappa", a: 0.1882, b: 0.1325, format: "pct" },
      { name: "Volatility agreement on cards both kept", a: 0.3605, b: 0.3475, format: "pct", note: "n 147 and 141. Majority-label baselines 0.340 and 0.333" },
      { name: "Volatility kappa on cards both kept", a: 0.2255, b: 0.2349, format: "pct" },
      { name: "Duplicate collapse agreement", a: 0.625, b: 0.75, format: "pct", note: "8 cards. Majority baseline 0.750" },
      { name: "Cards the AI kept, of 216", a: 202, b: 196, format: "num", note: "The editor kept 150" },
      { name: "Cards the AI dropped, of 216", a: 0, b: 7, format: "num", note: "The editor dropped 53" },
    ],
    benefits: [
      "A first measured baseline for AI feedback on the report decisions, with agreement, kappa and kept-set overlap for every week",
      "No card was excluded: every card had a valid answer from each AI reader and a decision from the editor",
      "The editor's 35 definitions now exist in her own words, approved one by one, and the app shows them beside every card",
      "The thinking-off reader's position bias is measured: the order swap changed 26 of 226 decisions (0.115)",
    ],
    costs: [
      "Both AI readers fell below the always-keep baseline on the four-way decision",
      "The thinking-off reader never answered drop. The editor dropped 53 cards",
      "Thinking lowered keep-against-anything-else kappa from 0.188 to 0.133",
      "About 0.63 USD of DeepSeek credit in all. The thinking-off run's 452 calls cost about 0.18 USD (both figures from EXP-008's pre-registration)",
    ],
    surprises: [
      "Of the thinking-off reader's 14 answers other than keep, 13 watchlist and 1 merge, 11 were on cards the editor dropped.",
      "Thinking changed 26 of 218 decisions, the same number the order swap changed for the thinking-off reader.",
      "The two AI readers agreed on volatility far more with each other (0.606, kappa 0.490) than either did with the editor (0.361 and 0.348).",
    ],
    engineering: [
      "A runner that seals AI answers by SHA-256 and never opens the editor's decision folder, enforced by a test (`src/exp007.py`)",
      "A thinking-mode adapter that leaves the adapter EXP-005 froze untouched (`src/llm_deepseek_thinking.py`)",
      "An append-only log of the editor's definitions, rebuilt into one file with her text exactly as typed, and an approval deck in ARI3 Review",
      "A run stops at once on an authentication or balance error (HTTP 401 or 402)",
      "Cost gates: a 3.81 USD worst case under a 5 USD cap for thinking off, and a running 3.00 USD stop for thinking on",
    ],
    log: [
      { step: "Observation", text: "Each prepared week has about 30 signal cards, and the editor decides every one by hand." },
      { step: "Idea", text: "Measure whether an LLM reading the same card makes the same call, as AI labeler alignment." },
      { step: "Experiment", text: "EXP-007: 226 cards, three readers, AI answers sealed before the comparison." },
      { step: "Result", text: "Kappa 0.079 with thinking off and 0.071 with thinking on. Both AI readers kept far more cards than the editor." },
      { step: "New question", text: "Does a written profile of the editor's judgment close the gap? That became EXP-008." },
    ],
    lessons: [
      "Raw agreement near 0.68 looks moderate. Beside an always-keep baseline of 0.694 and a kappa near 0.08, it is close to chance.",
      "Letting the reader think first did not bring it closer to the editor.",
      "The editor's definitions alone were not enough for the AI to drop what she drops.",
    ],
    openQuestions: [
      "Would a written profile of the editor's judgment change the AI's decisions? EXP-008 tested this.",
      "Would a memory of the editor's earlier calls on the same term help? EXP-009 tested this.",
    ],
    reproduce: {
      text: "The pre-registration, the amendment, the protocol fingerprints, the sealed-output manifests and the comparison metrics are public. The definitions file, the editor's decisions, the AI answers and the card-by-card detail stay local, and only their fingerprints are published, so outsiders can check the hashes but cannot rerun the comparison.",
      commands: `git clone ${REPO}.git
cd fashion-trend-crawler
cat experiments/exp-007-report-labeler-alignment/runs/comparison.json`,
    },
  },
  {
    id: "EXP-006",
    slug: "exp-006",
    version: "",
    name: "Local serving",
    motto: "",
    status: "Closed",
    headline: "On the same 30 frozen evidence packets, a 1.5B model on a local RTX 2080 took a median 4.6 s per call against 1.7 s for hosted DeepSeek, and never abstained. Answer quality was not measured.",
    summary: [
      "EXP-006 asks what changes when ARI3's answer-generation step runs on a small model on local consumer hardware, with every input held fixed. The comparison is the hosted DeepSeek run already frozen as EXP-005 C2: the same 30 holdout packets, the same Prompt v2 messages, the same schema and the same validation.",
      "The local side was Qwen2.5-1.5B-Instruct in fp16, served by vLLM 0.31.0 on one NVIDIA GeForce RTX 2080 (8 GB) in WSL2, reachable only on localhost. The model was chosen before any packet was sent because it fits the card and is Apache 2.0 licensed.",
      "This is a serving comparison, not a quality study. The hosted latency includes the network and the provider's hardware, and the two models differ greatly in size, so the numbers describe the two serving paths as they are.",
    ],
    meta: [
      { label: "Status", value: "Closed 2026-10-07. One run" },
      { label: "Protocol", value: "09e0436, committed and pushed before the first packet", href: `${EXP_DIR}/exp-006-local-serving/README.md` },
      { label: "Results", value: "57188b0", href: `${EXP_DIR}/exp-006-local-serving/comparison_v1.json` },
      { label: "Local model", value: "Qwen/Qwen2.5-1.5B-Instruct, revision 989aa798, fp16, Apache 2.0", mono: true },
      { label: "Server", value: "vLLM 0.31.0, PyTorch 2.13.0, WSL2 (Ubuntu 24.04), localhost only" },
      { label: "GPU", value: "NVIDIA GeForce RTX 2080, 8 GB" },
      { label: "Packets", value: "30 frozen EXP-005 holdout packets, sha256 ad67316abfa8306c66ed002036fe4438883409a813bc3a0dfdc0af8eb3d5bc6a", mono: true },
    ],
    question: "What changes when ARI3's generation step is served by a small model on local consumer hardware, with every input held fixed?",
    preregistered: "Yes. The protocol was committed and pushed before the first packet was sent, and the run happened once. EXP-006 had no pass criteria.",
    method: [
      "The 30 frozen EXP-005 holdout packets, sent unchanged: same questions, same retrieved evidence, same Prompt v2 messages",
      "The same generation function as the hosted run: one attempt, one retry only when the output does not parse, then the same deterministic validation",
      "The same request settings: temperature 0, top_p 1, max_tokens 1000, JSON output",
      "One run, compared with the frozen hosted run by the same comparison code",
    ],
    held: ["The packets, prompt, schema, validation and request settings", "No retrieval was rerun"],
    changed: ["Only the provider: a local 1.5B model on vLLM in place of hosted DeepSeek"],
    threats: [
      "Answer quality, grounding, completeness and abstention correctness were not measured, and no human review of the local outputs is planned.",
      "The hosted latency includes the network and the provider's hardware; the local latency is one consumer GPU with no network.",
      "The model's default repetition penalty of 1.1 applied and was not tuned.",
    ],
    compare: { a: "Hosted DeepSeek (EXP-005 C2)", b: "Local Qwen2.5-1.5B", n: 30 },
    resultsIntro: "Both runs on the same 30 packets. Latency is wall time per provider call, measured the same way in both.",
    metrics: [
      { name: "First-attempt latency, median (ms)", a: 1658.7, b: 4644.9, format: "num", lowerIsBetter: true },
      { name: "First-attempt latency, p95 (ms)", a: 2624.0, b: 5975.7, format: "num", lowerIsBetter: true },
      { name: "Output tokens per second, median", a: 145.1, b: 26.6, format: "num" },
      { name: "First-attempt schema validity", a: 0.867, b: 0.967, format: "pct", note: "26 of 30 against 29 of 30" },
      { name: "Final schema validity", a: 1.0, b: 1.0, format: "pct", note: "30 of 30 both, after the one allowed retry" },
      { name: "Questions answered", a: 24, b: 30, format: "num", note: "The hosted model abstained on 6; the local model never abstained" },
      { name: "Integrity failures", a: 0, b: 0, format: "num", lowerIsBetter: true },
    ],
    benefits: ["The local model passed the schema on the first attempt more often (29 of 30)", "No integrity failures, and nothing leaves the machine"],
    costs: ["Median first-attempt latency was about 2.8 times the hosted run", "Output speed was 26.6 tokens per second against 145.1", "The local model answered every question, including ones the hosted model declined; whether those answers are grounded is unknown"],
    surprises: ["The 1.5B model failed the answer schema less often than the hosted model, the opposite of what the protocol expected"],
    engineering: ["A loopback-only vLLM provider adapter that refuses any other host (src/llm_vllm.py)", "A preflight that checks packets, the store snapshot and message hashes before the run (src/exp006_vllm.py)"],
    log: [
      { step: "Observation", text: "Every answer call went to a hosted API." },
      { step: "Experiment", text: "EXP-006: the same frozen packets, served locally by a small model, one run." },
      { step: "Result", text: "Slower and never abstaining, with schema validity as good or better; quality unmeasured." },
    ],
    lessons: ["A local model can carry the format of ARI3's answers; whether it carries the grounding needs the human review that EXP-006 did not include."],
    openQuestions: ["Are the local model's answers grounded in the evidence packets, judged the same way as EXP-005?"],
    reproduce: {
      text: "The protocol, the comparison and both outputs' hashes are public. Running it again needs the frozen packets, which stay local, and a GPU with vLLM.",
      commands: `git clone ${REPO}.git
cd fashion-trend-crawler
cat experiments/exp-006-local-serving/comparison_v1.json`,
    },
  },
  {
    id: "EXP-005",
    slug: "exp-005",
    version: "",
    name: "Grounded generation",
    motto: "",
    status: "In progress",
    headline: "On five fresh development questions, Prompt v2's answers made 10 of 10 supported claims and all 5 were grounded when judged on the evidence they were given. The final holdout review of 163 answer cards is still open.",
    summary: [
      "EXP-005 asks whether a language model, given evidence retrieved by ARI3's frozen EXP-004 retriever, can produce useful answers without claiming more than that evidence supports. Retrieval is not tuned here. Generated text is written only to the experiment's folder and never enters the item store, labels or any report.",
      "Prompt v1 was run once on five development questions: 17 of 18 claims were supported and 4 of 5 answers were grounded. The failure was a free-text summary that added a fact, so Prompt v2 removed the summary and added coverage and limitation rules. On five fresh development questions, judged only on the exact evidence packet each answer received, Prompt v2 made 10 of 10 supported claims and 5 of 5 grounded answers.",
      "A schema-capacity comparison (SC-1) found Prompt v2 and a variant equally valid, 8 of 8 on the first attempt each, so the frozen rule gave inconclusive and Prompt v2 stayed. The final test is a fresh holdout of 30 frozen questions, already answered once by DeepSeek; the editor's review of those 163 answer cards has not been done, so no holdout result exists yet.",
    ],
    meta: [
      { label: "Status", value: "In progress. The holdout review (163 cards) is open" },
      { label: "Protocol v1", value: "ca33507, frozen before any output", href: `${EXP_DIR}/exp-005-grounded-generation/README.md` },
      { label: "Prompt v2", value: "04ea296 (protocol v2 b6636fa)" },
      { label: "Evidence boundary", value: "Amendment 2026-10-01: answers are judged only against the exact packet they received", href: `${EXP_DIR}/exp-005-grounded-generation/AMENDMENT_2026-10-01_evidence_boundary.md` },
      { label: "Context-grounded score", value: "bd9ca06" },
      { label: "SC-1", value: "Protocol 0280f1a, outputs ec47f9c, scored 58ad98f: inconclusive" },
      { label: "Retriever", value: "The frozen EXP-004 hybrid retriever, top 10" },
      { label: "Model cost", value: "0.0041 USD (batch 1), 0.0059 USD (batch 2), 0.0080 USD (SC-1)" },
    ],
    question: "Given evidence retrieved by ARI3's frozen retriever, can a language model produce useful answers without claiming more than the supplied evidence supports?",
    preregistered: "Yes, step by step. Protocol v1 was frozen before any output, Prompt v2 before its batch, and the SC-1 protocol before its outputs. The holdout questions and packets are frozen; their review is not done.",
    method: [
      "Question, then the frozen EXP-004 hybrid retriever (top 10), then a context check; an empty context gives an abstention with no model call",
      "The model answers in a fixed JSON schema with cited claims; one retry only if the output does not parse",
      "Deterministic validation of every citation, the corpus, time and filters",
      "Human review in ARI3 Review, judged only against the exact evidence packet",
      "Development on EXP-004 development questions; the final evaluation on a fresh, frozen holdout",
    ],
    held: ["The frozen EXP-004 retriever", "The context serializer, provider settings and retry policy across prompt versions"],
    changed: ["Prompt v1 to Prompt v2: no free-text summary, coverage rules, limitations that cite their items"],
    threats: [
      "Development scores rest on five questions per batch.",
      "One person reviews every answer.",
      "Stored records hold a headline and a 500-character feed summary, not full articles, so some questions cannot be answered from the stored text.",
    ],
    resultsIntro: "Development results so far. The holdout result does not exist yet.",
    metrics: [
      { name: "Claim support, Prompt v1", b: 0.944, label: "dev batch 1", format: "pct", note: "17 of 18 claims" },
      { name: "Grounded answer rate, Prompt v1", b: 0.8, label: "dev batch 1", format: "pct", note: "4 of 5 answers" },
      { name: "Claim support, Prompt v2, judged on the packet only", b: 1.0, label: "dev batch 2", format: "pct", note: "10 of 10 claims" },
      { name: "Grounded answer rate, Prompt v2, judged on the packet only", b: 1.0, label: "dev batch 2", format: "pct", note: "5 of 5 answers; 0.60 when outside content was used in review" },
      { name: "First-attempt schema validity, SC-1", b: 1.0, label: "SC-1", format: "pct", note: "8 of 8 for both prompts" },
    ],
    benefits: ["Every Prompt v2 claim on fresh development questions was supported by the cited evidence", "Every abstention in the context-grounded score was correct"],
    costs: ["Prompt v2's first-attempt schema validity on fresh development questions was 2 of 5 before SC-1", "Some questions cannot be answered because stored records hold only headlines and short summaries"],
    surprises: ["Judging answers against the full articles instead of the packet the model saw changed the grounded rate from 1.00 to 0.60, which is why the evidence boundary was fixed by amendment"],
    engineering: ["A generation pipeline with deterministic citation validation", "Blind answer-review and adjudication decks in ARI3 Review"],
    log: [
      { step: "Observation", text: "EXP-004 finds the right records; an answer must not claim more than they say." },
      { step: "Experiment", text: "Prompt v1 on five development questions, then Prompt v2 after failure analysis." },
      { step: "Result so far", text: "Prompt v2 grounded on fresh development questions; the holdout review is open." },
    ],
    lessons: ["A free-text summary cannot be checked automatically for added facts, so it was removed rather than restricted."],
    openQuestions: ["How does Prompt v2 do on the frozen holdout, once the editor has reviewed its 163 answer cards?"],
    reproduce: {
      text: "The protocols, prompts, frozen questions and scores are public. The item store stays local, so outsiders can check hashes but cannot rerun retrieval or generation.",
      commands: `git clone ${REPO}.git
cd fashion-trend-crawler
ls experiments/exp-005-grounded-generation`,
    },
  },
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
      { area: "v0.0.3", detail: "Released 2026-10-03. Both parts of EXP-003 ran once, and the results include a failed accuracy criterion and a failed forecast detector" },
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
