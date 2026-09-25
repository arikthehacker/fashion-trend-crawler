// lib/ari3.ts
// The ARI3 release ledger. Each entry mirrors a commit in the public repository.
// Values are copied from models/<version>/manifest.json and the commit itself.
// A release is never edited after it is committed. New facts are new entries.

export const REPO = "https://github.com/arikthehacker/fashion-trend-crawler";

export type Metric = { name: string; value: string; note?: string };
export type Hypothesis = { id: string; claim: string; test: string; status: "pending" | "supported" | "not supported" };

export type Release = {
  version: string;
  status: "frozen" | "pre-registered";
  kind: string;
  committedAt: string; // commit time, UTC
  commit: string;
  files: { path: string; sha256: string; label: string }[];
  summary: string[];
  method?: { stage: string; technique: string; value?: string; source: string }[];
  metrics?: Metric[];
  hypotheses?: Hypothesis[];
  limits: string[];
};

export const RELEASES: Release[] = [
  {
    version: "v0.0.2",
    status: "pre-registered",
    kind: "Perception: is an item about style?",
    committedAt: "2026-09-24T01:08:12Z",
    commit: "79e95bc918c3bf523a8ae58e3d7eca6a4ac6471f",
    files: [
      {
        path: "models/ari3-v0.0.2/PREREGISTRATION.md",
        sha256: "2ed73c43c80ba38721d97540613aab695049fe2c7401dc30bbf3f513440480b1",
        label: "Pre-registration",
      },
    ],
    summary: [
      "The plan and the pass criteria for v0.0.2 were committed before any v0.0.2 label existed. The file must not change after commit, and the repository history would show it if it did. A change of plan requires a new, dated amendment.",
      "Only the training data changes: about 350 human labels instead of 145, including 50 items chosen by active learning (the items v0.0.1 was least sure about). Everything else is held fixed, so any difference between versions comes from the data.",
      "Items chosen by active learning are excluded from the test score, because a model-chosen test set is biased toward hard cases. Both versions are scored on the same held-out items.",
    ],
    hypotheses: [
      { id: "H1", claim: "More decisive", test: "Share of single-answer predictions on the test set reaches at least 0.70", status: "pending" },
      { id: "H2", claim: "Coverage holds", test: "Conformal coverage on the test set is at least 0.90", status: "pending" },
      { id: "H3", claim: "Accuracy does not drop", test: "v0.0.2 accuracy is no lower than v0.0.1 on the same test items", status: "pending" },
      { id: "H4", claim: "Calibration stays good", test: "Expected calibration error after scaling is at most 0.10", status: "pending" },
      { id: "H5", claim: "Active learning beats random labels", test: "v0.0.2 beats a control trained on the same number of random labels", status: "pending" },
    ],
    limits: [
      "Every hypothesis will be reported, including any that fail.",
      "Scope was fixed before labeling (2026-09-23): nails count as style, and makeup, skincare, fragrance, hair and beauty packaging do not.",
    ],
  },
  {
    version: "v0.0.1",
    status: "frozen",
    kind: "Perception: is an item about style?",
    committedAt: "2026-09-24T01:08:13Z",
    commit: "9c296bd72a10915969b5808b0d6bc4e41e2ac4a9",
    files: [
      {
        path: "models/ari3-v0.0.1/weights.npz",
        sha256: "78ddaf3383eaa141687133e8d6993ff12a6568452a1747bd862c0955572b76be",
        label: "Weights",
      },
      {
        path: "models/ari3-v0.0.1/manifest.json",
        sha256: "f9f2c44bb06dad0fc3672c29dfcacfa39d2ce503dc28c38457206dac5ccb0213",
        label: "Manifest",
      },
    ],
    summary: [
      "The first frozen version of ARI3. It reads a news item's headline and feed excerpt, in any of the collected languages, and gives a calibrated probability that the item is about style, plus a set of answers it cannot rule out.",
      "When the set holds both answers, the model is saying it is not sure. Those items are meant for the editor's review, not for automatic counting.",
      "It was trained on 145 labels written by the editor. It is never retrained. Later labels train a later version.",
    ],
    method: [
      { stage: "Represent", technique: "Multilingual sentence embeddings (encoder frozen)", value: "384 dimensions", source: "Reimers & Gurevych, EMNLP 2019 and 2020" },
      { stage: "Classify", technique: "Logistic regression", value: "C = 1.0", source: "" },
      { stage: "Calibrate", technique: "Temperature scaling", value: "T = 0.403", source: "Guo, Pleiss, Sun & Weinberger, ICML 2017" },
      { stage: "Abstain", technique: "Split conformal prediction", value: "α = 0.10, q̂ = 0.837", source: "Angelopoulos & Bates 2021. Romano, Sesia & Candès, NeurIPS 2020" },
    ],
    metrics: [
      { name: "Accuracy", value: "0.882", note: "30 of 34. 95% interval 0.73 to 0.95. Always guessing the majority answer scores 0.53" },
      { name: "Precision / recall", value: "0.83 / 0.94" },
      { name: "Calibration error", value: "0.234 → 0.088", note: "Before and after temperature scaling (5-bin ECE)" },
      { name: "Conformal coverage", value: "1.00", note: "34 of 34. Target at least 0.90" },
      { name: "Errors the model was sure about", value: "0 of 4", note: "All four mistakes came with the not-sure set" },
    ],
    limits: [
      "The test set is 34 items, so every number above has a wide interval.",
      "With 29 calibration items the not-sure set is cautious: 1,648 of 2,472 unlabeled items received it.",
      "Only headlines and feed excerpts are read, never full articles. 85% of the training-time items came from editorial outlets.",
      "The split into training, calibration and test items is fixed by a hash of each item, so no test item was used in training.",
    ],
  },
];
