# AI-in-journalism standards vs. ARI3LLA INDEX practice — gap analysis

Research-only, no code changed.

## Sources reviewed
- AP generative AI guidelines — treats AI output as "unvetted source material," bars AI from generating publishable text/images outright, plans quarterly policy review. ([Lessons from AP AI guidelines](https://www.warc.com/content/feed/lessons-from-the-associated-press-ai-guidelines/en-GB/8543), [Popular Science](https://www.popsci.com/technology/ap-ai-news-guidelines/), [Decrypt](https://decrypt.co/152873/associated-press-limits-how-journalists-use-generative-ai))
- Poynter's 2025 updated newsroom AI ethics guidelines — transparency on when/how audiences are told AI was used, "human-in-the-loop" with **clearly assigned oversight roles**, explicit bias-guarding for AI-driven products. ([Poynter, June 2025](https://www.poynter.org/ethics-trust/2025/a-lot-has-changed-since-we-created-ai-ethics-guidelines-for-newsrooms-heres-what-you-need-to-know-now/))
- Reuters Trust Principles / AI guidance — AI use requires "rigorous oversight by newsroom editors," a hard red line on AI-generated imagery, robust disclosure with senior-editor approval for AI-processed visuals. ([Talking Biz News](https://talkingbiznews.com/media-news/what-reuters-is-telling-its-journalists-about-using-artificial-intelligence/))

## Where ARI3LLA INDEX lines up
- **Disclosure exists and is specific**, not boilerplate: methodology's "How AI Is Used" and "AI Involvement" sections, plus about page's "Independence, Corrections, AI Use" block, match Poynter's transparency requirement and AP/Reuters' "AI is a tool, not an author" framing.
- **AI output treated as unvetted material requiring human judgment** — matches AP directly ("Final classification depends on the Index taxonomy and human review").
- **No AI-authored final classification** — taxonomy/origin decisions and cluster interpretation are reserved for a human, matching Reuters' "rigorous editor oversight" and AP's ban on AI making final calls.
- **Corrections policy** (dated, non-silent, original preserved) matches standard wire-service correction practice broadly.

## Gaps against real newsroom standards
1. **No per-report/per-signal sign-off log.** `human_editor_note` is a free-text field on the report, not an auditable record of *who* reviewed, *when*, and *what specifically* they checked. Poynter's "clearly assigned oversight roles" implies traceable accountability, not just a note field that could in principle be left thin or generic.
2. **No prompt version-control / changelog for the summarization prompt itself.** `summarize.py`'s Claude prompt is treated as ordinary code, not as an editorial instrument. AP's quarterly-review cadence and Reuters' "same standards and safeguards" language imply prompts should be reviewed/versioned the way editorial standards are, not just linted with code.
3. **No stated bias-audit practice.** Poynter's 2025 update explicitly flags guarding against AI-model bias in classification/products — the project has no periodic check for systematic skew (e.g., always upgrading certain source sectors, English-language/Western-media bias in crawled sources).
4. **No explicit "AI does not generate publishable prose unsupervised" gate.** AP's line is that AI must not produce publishable content directly — ARI3LLA's summaries are AI-drafted and the pipeline doesn't document a required human edit-and-approve step before a report file is considered "published" (vs. merely generated and saved).

## Recommendations (flagged for a future run, not implemented)
- Add a lightweight structured review record per report (reviewer name/role, date, checklist of what was verified) alongside `human_editor_note`, rather than free text alone.
- Track `summarize.py` prompt changes in the changelog like any editorial-standard change, with rationale.
- Add a periodic (e.g. quarterly) bias-check note to methodology, describing what's checked and when.
- Document explicitly that a saved report file is "draft" until a human review step flips it to "published," closing the AP-style unvetted-material gap.
