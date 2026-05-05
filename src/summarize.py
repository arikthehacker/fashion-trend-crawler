#############################################################
# summarize.py
# last edited: 05/04/2026
# reads trends_raw.json, sends headlines to claude api,
# saves a human-readable trend summary to trends_summary.json
#
# ways to use:###############################################
#    python src/summarize.py
# run this after crawler.py
#############################################################
from dotenv import load_dotenv
load_dotenv()
import json
import os
from anthropic import Anthropic

client = Anthropic()

def load_trends():
    # load the raw crawled data
    with open("trends_raw.json", "r", encoding="utf-8") as f:
        return json.load(f)

def build_prompt(pages):
    # flatten all headlines into one block for claude to read
    all_headlines = []
    for page in pages:
        domain = page["url"].split("/")[2].replace("www.", "")
        for title in page["titles"]:
            all_headlines.append(f"[{domain}] {title}")

    headlines_text = "\n".join(all_headlines)

    return f"""You are a fashion trend analyst. Based on these headlines crawled today from Vogue, Who What Wear, and Hypebeast, write a sharp, editorial trend summary.

Format your response as JSON with exactly this structure:
{{
  "the_moment": "One punchy sentence: the single biggest thing happening in fashion right now.",
  "summary": "Two to three sentences. What is the dominant trend or cultural moment? What are the undercurrents? Write like a Vogue editor who is talking to their best friend about what they've been overhearing in the designers room.",
  "trends": [
    {{"trend": "trend name", "signal": "one sentence on what the data shows"}},
    {{"trend": "trend name", "signal": "one sentence on what the data shows"}},
    {{"trend": "trend name", "signal": "one sentence on what the data shows"}}
  ],
  "sources_summary": {{
    "vogue.com": "one sentence on what vogue is covering most",
    "whowhatwear.com": "one sentence on what wwwear is covering most",
    "hypebeast.com": "one sentence on what hypebeast is covering most"
  }}
}}

Headlines:
{headlines_text}

Return only valid JSON. No markdown, no backticks, no preamble."""

def summarize():
    print("loading trends...")
    pages = load_trends()

    print(f"sending {sum(len(p['titles']) for p in pages)} headlines to claude...")
    prompt = build_prompt(pages)

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}]
    )

    raw = response.content[0].text.strip()

    # parse and save
    summary = json.loads(raw)
    with open("trends_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print("saved to trends_summary.json")
    print(f"\nthe moment: {summary['the_moment']}")

if __name__ == "__main__":
    summarize()
