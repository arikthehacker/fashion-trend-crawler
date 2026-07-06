#############################################################
# summarize.py
# last edited: 07/06/2026
# reads trends_raw.json, sends headlines to claude api,
# and saves a structured, dated ARI3LLA INDEX style signal
# report to data/reports/<report_date>.json
#
# ways to use:###############################################
#    python src/summarize.py
# run this after crawler.py
#############################################################
from dotenv import load_dotenv
load_dotenv()
import json
import os
from datetime import date, timedelta
from anthropic import Anthropic

from taxonomy import (
    SOURCE_SECTORS,
    CONFIDENCE_LEVELS,
    VOLATILITY_LABELS,
    ORIGIN_CLASSIFICATIONS,
    classify_source,
)
from report_schema import save_report, report_path, SchemaValidationError

client = Anthropic()


def load_trends(path="trends_raw.json"):
    # load the raw crawled data
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def compute_sector_breakdown(pages):
    """count pages per source sector using taxonomy.classify_source"""
    breakdown = {}
    for page in pages:
        sector = classify_source(page["url"])
        breakdown[sector] = breakdown.get(sector, 0) + 1
    return breakdown


def build_prompt(pages, report_date, window_start, window_end):
    # flatten all headlines into one block for claude to read, tagged with
    # both the domain and the source sector so the model has source-incentive
    # context per section 21 of docs/ARI3LLA INDEX.txt
    all_headlines = []
    for page in pages:
        domain = page["url"].split("/")[2].replace("www.", "")
        sector = classify_source(page["url"])
        for title in page["titles"]:
            all_headlines.append(f"[{domain} | {sector}] {title}")

    headlines_text = "\n".join(all_headlines)
    items_collected = sum(len(p["titles"]) for p in pages)

    return f"""You are ARI3LLA INDEX, a weekly style signal report.

Analyze the provided source material objectively. Do not write as a stylist, influencer, marketer, or brand forecaster. Do not recommend purchases. Do not hype trends. Do not use first person.

Classify observed style signals by recurrence, source diversity, volatility, visual coherence, historical/aesthetic context, and source incentive.

Use only the provided source material. Do not invent trends, brands, or claims. Focus on repeated language, recurring visual references, garments, silhouettes, colors, materials, styling behaviors, and cultural/aesthetic terms.

Treat TikTok/social signals as high-noise by default. Identify them, but classify them as volatile unless supported by non-social evidence across multiple reporting periods.

Do not treat editorial sources as neutral confirmation. Classify each source by incentive context: designer-originated, editorial, commerce, social, retail, independent criticism, or institutional archive.

Independent criticism (named-author, attributed commentary) and editorial coverage are both curated, attributed commentary, not raw social volume. When assigning confidence, do not let source sector alone push independent criticism lower than editorial at an equal corroboration count — evaluate both on the same evidentiary basis. This is not a case for treating independent criticism as more reliable than editorial; it is a case for not treating it as less reliable by default.

Distinguish between style as lived practice and trend as market instruction. Do not recommend adoption. Do not describe signals as must-have, essential, or the next big thing.

Do not use evaluative or editorializing verbs such as "declared," "revealed," or "proves." Use measured, attribution-anchored verbs instead, such as "said," "reported," "noted," or "showed."

Avoid vague, unsupported claims of ubiquity such as "everyone is wearing" or "everywhere right now." If evidence is thin, limited to one source sector, or contradictory, state that plainly in the evidence or index_note field rather than smoothing it over or omitting it.

When a signal continues an existing signal_id carried forward from a prior report, keep garment/material terminology describing it consistent with prior usage unless the change is genuine — in which case note it explicitly (e.g. "garment description updated from X to Y because...") rather than letting the terminology silently drift.

If a headline is in a language other than English, do not silently translate and classify it as if it were equivalent to English-language coverage. You may interpret it to extract the signal, but note in the evidence or index_note field that the source material was non-English (name the language if identifiable) and that the term/description is a translation, not a direct quote.

If the source material yields only a small number of genuinely distinct, well-supported signals, do not stretch, duplicate, or manufacture additional signals to appear more comprehensive. Instead, set "collection_status" to "thin" and use "thin_week_note" to state plainly that this reporting period had limited signal volume, so the report reflects the actual state of coverage rather than an inflated one. Use "collection_status": "normal" and leave "thin_week_note" empty when signal volume is adequate.

Each headline below is tagged as [domain | source_sector]. Valid source sectors are: {", ".join(SOURCE_SECTORS)}.
Valid confidence levels are: {", ".join(CONFIDENCE_LEVELS)}.
Valid volatility labels are: {", ".join(VOLATILITY_LABELS)}.
Valid origin classifications are: {", ".join(ORIGIN_CLASSIFICATIONS)}.

Return your response as JSON with exactly this structure (no markdown, no backticks, no preamble):
{{
  "report_date": "{report_date}",
  "collection_window": {{"start": "{window_start}", "end": "{window_end}"}},
  "sources_scanned": {len(pages)},
  "items_collected": {items_collected},
  "source_sector_breakdown": {{}},
  "executive_summary": "3-5 sentences, objective, research-report tone.",
  "top_signals": [
    {{
      "name": "signal name",
      "type": "garment | silhouette | color | material | styling_behavior | cultural_term",
      "source_sectors": ["editorial", "retail"],
      "confidence": "low | medium | high | archival",
      "volatility": "stable | emerging | seasonal | volatile | flash | microtrend | recurring | revival | long_tail | saturated | declining",
      "origin_classification": "designer_originated | editorial_amplified | retail_adopted | social_amplified | platform_native | archive_revival | unclear",
      "evidence": "one sentence describing what the data shows, citing source sectors, not opinion.",
      "index_note": "one sentence of methodological context, e.g. why this confidence/volatility was assigned."
    }}
  ],
  "repeated_keywords": [],
  "garments": [],
  "silhouettes": [],
  "materials": [],
  "colors": [],
  "aesthetic_terms": [],
  "cultural_references": [],
  "limitations": ["note any gaps, e.g. limited source sectors, small sample size, single reporting period"],
  "archive_tags": [],
  "collection_status": "normal | thin",
  "thin_week_note": "if collection_status is 'thin', explain why in one sentence; otherwise leave empty"
}}

Leave source_sector_breakdown as an empty object; it is computed separately from the raw data.

Headlines:
{headlines_text}

Return only valid JSON. No markdown, no backticks, no preamble."""


def summarize(pages=None, revision_reason=None, corrected_at=None):
    if pages is None:
        print("loading trends...")
        pages = load_trends()

    today = date.today()
    report_date = today.isoformat()
    window_start = (today - timedelta(days=6)).isoformat()
    window_end = report_date

    print(f"sending {sum(len(p['titles']) for p in pages)} headlines to claude...")
    prompt = build_prompt(pages, report_date, window_start, window_end)

    # 4000 (raised from 2000 in run 8) covers today's thin-week reports (1-8
    # signals, e.g. 2026-07-20.json's 8 signals ran close to ~3.8k tokens
    # of completion) but leaves little headroom. Each signal costs ~400-450
    # tokens of JSON; a genuinely busy fashion-week window (NYFW/LFW/MFW/PFW
    # from Sept 8, 2026, per docs/EDITORIAL_CALENDAR.md) could plausibly
    # surface 15+ signals, which extrapolates to ~6000-7000 tokens plus
    # overhead -- past 4000. Raised to 8000 for headroom; see
    # docs/agent-logs/busy-week-readiness-run18.md.
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=8000,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = response.content[0].text.strip()

    # parse, fill in the sector breakdown computed from real crawl data
    # (rather than trusting the model to count it), then save as a dated report
    report = json.loads(raw)
    report["source_sector_breakdown"] = compute_sector_breakdown(pages)

    try:
        path = save_report(
            report, revision_reason=revision_reason, corrected_at=corrected_at
        )
    except SchemaValidationError as e:
        if os.path.exists(report_path(report_date)) and not revision_reason:
            print(
                f"a report for {report_date} already exists with different content.\n"
                "refusing to overwrite it silently. re-run with an explicit "
                "correction reason, e.g.:\n"
                "    python src/summarize.py --revision-reason \"<why this changed>\" "
                "--corrected-at YYYY-MM-DD"
            )
            return
        raise

    print(f"saved report to {path}")
    print(f"\nexecutive summary: {report['executive_summary']}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--revision-reason",
        default=None,
        help="required if today's report already exists with different content",
    )
    parser.add_argument(
        "--corrected-at",
        default=None,
        help="ISO date string for the correction (required alongside --revision-reason)",
    )
    args = parser.parse_args()

    summarize(revision_reason=args.revision_reason, corrected_at=args.corrected_at)
