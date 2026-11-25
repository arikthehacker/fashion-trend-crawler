# EXP-008: an AI-written taste profile of the editor, tested leave one week out

**Status:** pre-registered 2026-11-25, before any model call. This replaces the few-shot plan proposed on 2026-11-24, which never ran. The frozen details (fingerprints of this file, the subagent instructions, the prompt change, the profile inputs, the decks, the definitions, the code and the settings) are in `protocol/protocol_v1.json`. The runner is `src/exp008.py`.

## Question

EXP-007 found that a zero-shot AI labeler barely tracks the editor on the weekly report decisions. It reached decision agreement 0.681 and Cohen's kappa 0.079 on 216 signal cards, below the always-keep baseline of 0.694. It kept far more than the editor did.

EXP-008 asks whether a short profile of the editor's judgment, written by another AI from her decisions in other weeks, closes that gap. This follows the constitution-style idea in RLAIF (Lee et al., ICML 2024; Bai et al., 2022), where written principles steer an AI labeler, except that here the principles are induced from one human's own labels.

## Step 1: the seven profiles

- **Leave one week out.** For each of the seven weeks W (report dates 2026-10-11 to 2026-11-22), one profile is written from the other six weeks only. A card in week W is later labeled with profile W, so no profile has seen the editor's answers for the cards it is used on.
- **The writer.** Each profile is written by a fresh Claude Code general-purpose subagent (model `claude-opus-5-5`). It starts with no conversation history, so it has never seen EXP-007's results, the AI answers or this session's discussion. Its standing context (the project `CLAUDE.md` files and the local memory index) was checked on 2026-11-25 and holds no EXP-007 results.
- **What it reads.** Six input files, one per other week, built by `exp008.py build-inputs` from the decks and from the editor's decision logs, which EXP-007 already fingerprinted. Each file holds every required card exactly as ARI3 Review's card text shows it (title, counts, sectors, dates, weaknesses and the evidence headlines with outlet, date and sector), followed by the editor's answer: decision, merge target, volatility, confidence, any type, origin or name change, the number of items removed, and her thoughts. The files stay local. Their SHA-256 values are frozen.
- **The instructions** are `protocol/profile_instructions_v1.md`, filled in with the six file paths, the output path and the banned words. In short:
  - general rules only, about 350 to 550 words;
  - what makes the editor keep, drop, watchlist or merge, count duplicates once or separately, and pick a volatility label;
  - no trend, style or garment term, brand, person, outlet, event or headline, and no counts from the files;
  - Read and Write only, nothing else opened.
- **Unedited.** The subagent writes the profile file itself. The file is never edited. The main session does not read it, and neither does the editor until the comparison is committed.
- **Software checks**, in `exp008.py check-profile`, which prints only the names of matched words and never the profile text:
  1. **Transcript audit:** the subagent's own transcript shows Read calls on exactly its six input files, one Write to its profile path, and no other tool call.
  2. **Leak check:** none of the 48 signal names from the seven decks, in any plural or spacing; none of the outlet domains or their name parts; no run of 5 words copied from any evidence headline; at most 800 words and not empty.
- **One retry.** If a week's profile fails a check, a new fresh subagent gets the same instructions once. If that one fails too, nothing runs, and the owner decides. Every failed attempt is listed, with its problems only, in the sealed profile manifest.
- **Sealing.** `exp008.py seal-profiles` commits the SHA-256 of all seven profiles (`runs/sealed_profiles.json`) before any DeepSeek call.

## Step 2: the rerun

- **Reader:** EXP-007's thinking-off reader, unchanged. DeepSeek `deepseek-flash` with temperature 0, top_p 1, max_tokens 1000, thinking disabled and JSON output. The same 226 required cards (218 signal, 8 duplicate), both option orders (app order and every option list reversed), 452 first calls, and one retry only when the app's save rules reject an answer.
- **The only change** is the prompt, which adds the held-out week's profile after the definitions, as specified in `protocol/prompt_v2.md`.
- **Sealed outputs** go to `data/store/blind/exp008/`, which is local and never printed. A committed manifest holds their SHA-256 and counts only.
- **Running cost cap:** 1.00 USD (see Cost).

## Metrics and hypotheses

Comparisons use the app order, the editor's latest answers (fingerprinted by EXP-007) and EXP-007's exclusions. The two cards decided before EXP-007's plan, and any card marked `[looked up]`, are reported separately.

- **H1 (primary):** Cohen's kappa between the editor and the AI on the four signal decisions is higher with the profile than in EXP-007's thinking-off run (0.0793). The test is a paired bootstrap over signal cards (10,000 resamples, seed 8008, 95% percentile interval) of the kappa difference:
  - a lower bound above 0 means **supported**;
  - an interval that contains 0 means **not supported**;
  - an upper bound below 0 means **reversed**.
- **H2:** the same test for keep against anything else (EXP-007: kappa 0.1882).
- **Reported beside them, with no pass criteria:**
  - decision agreement against the always-keep baseline (0.694);
  - an exact McNemar test on cards each run got right and the other got wrong;
  - the number of AI drops against the editor's;
  - volatility agreement on cards both kept (EXP-007: 0.3605);
  - duplicate collapse agreement (8 cards, descriptive);
  - position bias, the share of cards whose decision changes under the order swap (EXP-007: 0.115);
  - per-week kappa and kept-set Jaccard;
  - the number of decisions the profile changed against EXP-007.
- **Outputs.** The metrics are committed in `runs/comparison.json`. The card-by-card detail, with the editor's thoughts and both AI readers' thoughts, stays local in `data/store/blind/exp008/comparison_detail.md`.

## Known limits, stated before the results

- **Small sample.** About 216 signal cards, with 7 weeks too few to resample by week. Cards within a week are not independent, so the bootstrap interval is optimistic.
- **No length-matched control.** A change could come from a longer prompt rather than from what the profile says.
- **Recurring candidates.** The same terms recur across weeks, so the profile writer has seen the editor's answers on other weeks' cards for many of the same terms. The ban on names in the profile limits what can carry over, but rules stated generally ("keeps a term that spans many outlets") still apply to those cards.
- **No measured run-to-run noise.** The profiles are not reproducible, since a second subagent would write a different one, and DeepSeek at temperature 0 is not guaranteed to be deterministic. The order-swap change rate in EXP-007 (11.5%) is the only noise reference.
- **Two different models.** The profile writer (Claude) and the labeler (DeepSeek) differ, so the result says nothing about Claude as a labeler.

## Cost

| What runs | Calls | Estimate |
|---|---|---|
| Step 1: 7 Claude subagents | 7 | Billed to the Claude plan, not DeepSeek. Each reads about 300,000 characters (about 75,000 tokens) and writes about one page |
| Step 2: DeepSeek rerun | 452 first calls | Expected about 0.25 USD off-peak and about 0.50 USD at peak, scaled from EXP-007's actual 0.18 USD for the same calls with about 760 more prompt tokens each |
| Step 2 worst case | 904 at most | 5.37 USD: every character a token, two attempts each, full output, peak prices, with an 800-word profile |

The worst case is above the remaining DeepSeek balance (about 4.37 USD after EXP-007's 0.63 USD). The run therefore stops itself once its running estimated cost reaches 1.00 USD, which is about four times the expected cost, and records that it stopped.

## Order of work

1. Commit this file, the instructions, the prompt spec, the code and the frozen protocol, before any call.
2. With the owner's "LIVE DEV GENERATION AUTHORIZED" for EXP-008: push, write and check the seven profiles, seal them, commit and push.
3. Run the DeepSeek rerun, seal it, commit and push.
4. Compare, commit and push the metrics. Only then may anyone read the profiles.
