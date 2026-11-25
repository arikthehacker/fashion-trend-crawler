# Contributing to ARI3LLA INDEX

ARI3LLA INDEX is a weekly, source-linked record of the style language public fashion coverage uses. It records what coverage is naming, where, and from which kinds of outlets. It is not a trend forecast or a shopping guide. The site is [ari3lla.com](https://www.ari3lla.com).

Corrections, source suggestions and code are welcome. Everything goes through GitHub issues and pull requests, so the whole record stays public.

## Report a correction

If a published report gets something wrong, open a [correction issue](https://github.com/arikthehacker/fashion-trend-crawler/issues/new?template=correction.yml). Include:

- **the report and signal**: the report's address, and the signal's link if it is about one signal (every signal has its own link, ending in `#signal-<name>`);
- **what is wrong**: quote the sentence, count or label;
- **why**: a link to the article or record that shows it. Counts and claims in a report rest on the dated articles listed under each signal, so a correction is strongest when it points to one of them.

What happens next:

- The editor reviews every correction.
- A published report is never silently edited. A confirmed error gets a dated correction note in the report, saying what was wrong and what changed, and the original entry is kept beside it.
- The outcome is recorded on the issue, including when no change is made and why.

## Suggest a source

Open an [issue](https://github.com/arikthehacker/fashion-trend-crawler/issues/new) with the outlet's name and its feed address. ARI3 collects only public, dated feeds (RSS or Atom) that allow automated reading. It does not scrape social platforms (TikTok, Instagram, Pinterest, Reddit) and never rehosts images, including runway images. Titles, outlets, dates and links are stored, not full articles.

## Contribute code

Pull requests to the site (`web/`) and the pipeline (`src/`) are welcome. Open an issue first for anything larger than a small fix, so the approach can be agreed before work starts.

Before opening a pull request, run the checks that CI and the site's build run:

```bash
python -m py_compile src/*.py
python src/validate_all_reports.py
cd web && npm ci && npx eslint . && npx next build && node scripts/check-seo.mjs
```

Rules that apply to every change:

- **Evidence.** Every claim in a report traces to a fetched, dated source with its URL. Nothing is invented, and "not found" is written when evidence is missing.
- **Published reports.** Files in `data/reports/` are changed only through the correction process above.
- **Editor's notes.** The `human_editor_note` field is written by the editor alone. Code and contributors never write it.
- **Voice** for anything public (pages, reports, README): no first person, no hype ("must-have", "everyone is wearing"), no shopping advice, uncertainty stated plainly.
- **No secrets.** Never commit keys, `.env` files or local databases.
- **Social platforms.** Official APIs or manual sampling only, never scraping.

## Terms

The index's own text and data are published under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Contributions to them are accepted on the same terms. The linked articles belong to their publishers. The repository does not yet include a software license, so ask in an issue before reusing code elsewhere.

Be respectful in issues and reviews. Disagreement about a claim is welcome, and it is settled by evidence.
