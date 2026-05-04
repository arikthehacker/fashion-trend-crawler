#############################################################
# server.py
# last edited: 05/04/2026
# mcp server that exposes the crawler as a tool
# so claude (or any mcp client) can call it directly
#
# ways to use:###############################################
# run the server
#    python src/server.py
# stop it when done
#    ctrl+c
#############################################################

from mcp.server.fastmcp import FastMCP
from crawler import crawl_all_sources, FASHION_SOURCES
import json
import os
import sys

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))

mcp = FastMCP("fashion-trend-crawler")

sys.stderr.write("fashion-trend-crawler mcp server running\n")
sys.stderr.flush()

@mcp.tool()
def crawl_fashion_trends(urls: list[str] = None) -> str:
    """
    crawls fashion pages and returns headline data as json.
    if no urls provided, uses default fashion sources.
    """
    sources = urls if urls else FASHION_SOURCES
    results = crawl_all_sources(sources, output_file="trends_raw.json")
    return json.dumps(results, indent=2)

@mcp.tool()
def get_cached_trends() -> str:
    """
    returns the last crawled trends from the json file
    without re-crawling anything. fast if you already ran the crawler.
    """
    if not os.path.exists("trends_raw.json"):
        return json.dumps({"error": "no cached trends found. are you in the right folder? run crawler.py first, then try again."})

    with open("trends_raw.json", "r") as f:
        return f.read()

@mcp.tool()
def search_trends(keyword: str) -> str:
    """
    searches cached trends for a specific keyword.
    returns all headlines that contain the keyword.
    """
    if not os.path.exists("trends_raw.json"):
        return json.dumps({"error": "no cached trends found. are you in the right folder? run crawler.py first, then try again."})

    with open("trends_raw.json", "r") as f:
        data = json.load(f)

    matches = []
    keyword_lower = keyword.lower()
    for page in data:
        matching_titles = [t for t in page["titles"] if keyword_lower in t.lower()]
        if matching_titles:
            matches.append({
                "url": page["url"],
                "matching_headlines": matching_titles
            })

    count = len(matches)
    label = "page" if count == 1 else "pages"
    return json.dumps({
        "keyword": keyword,
        "found_in": f"{count} {label}",
        "results": matches
    }, indent=2)

if __name__ == "__main__":
    mcp.run()
