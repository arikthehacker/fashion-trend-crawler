#############################################################
# test_tools.py
# last edited: 05/04/2026
# quick test script to verify mcp tools work without
# needing the mcp inspector or a connected claude client
#############################################################

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from crawler import crawl_all_sources, FASHION_SOURCES
import json

print("testing get_cached_trends...")
if os.path.exists("trends_raw.json"):
    with open("trends_raw.json", "r") as f:
        data = json.load(f)
    print(f"  found {len(data)} cached pages")
else:
    print("  no cache found!!! run crawler first")

print("\ntesting search_trends for 'met gala'...")
if os.path.exists("trends_raw.json"):
    with open("trends_raw.json", "r") as f:
        data = json.load(f)
    keyword = "met gala"
    matches = []
    for page in data:
        hits = [t for t in page["titles"] if keyword.lower() in t.lower()]
        if hits:
            matches.append({"url": page["url"], "headlines": hits})
    count = len(matches)
    label = "page" if count == 1 else "pages"
    print(f"  found '{keyword}' in {count} {label}")
    for m in matches[:3]:
        print(f"  {m['url']}")
        for h in m['headlines']:
            print(f"    - {h}")

print("\nall tools verified.")
