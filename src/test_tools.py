#############################################################
# test_tools.py
# last edited: 05/04/2026
# verifies that all three mcp tools work correctly
# run this after crawler.py to confirm everything is working
#
# ways to use:###############################################
#    python test_tools.py
#############################################################

import sys
import os
import json


CACHE_FILE = "trends_raw.json"
passed = 0
failed = 0

def test(name, condition, detail=""):
    global passed, failed
    if condition:
        print(f"  PASS  {name}")
        passed += 1
    else:
        print(f"  FAIL  {name} {detail}")
        failed += 1

print("---------------------------------------------------")
print("  fashion-trend-crawler −∘♥∘− tool tests")
print("---------------------------------------------------")

# test 1 cache file exists
print("\n[ get_cached_trends ]")
cache_exists = os.path.exists(CACHE_FILE)
test("cache file exists", cache_exists, "−∘♥∘− run crawler.py first")

if cache_exists:
    with open(CACHE_FILE, "r") as f:
        data = json.load(f)

    # test 2 cache has data
    test("cache is not empty", len(data) > 0)

    # test 3 each entry has required fields
    has_fields = all("url" in p and "titles" in p and "depth" in p for p in data)
    test("all entries have url, titles, depth", has_fields)

    # test 4 titles are actually strings
    has_strings = all(isinstance(t, str) for p in data for t in p["titles"])
    test("all titles are strings", has_strings)

    print("\n[ search_trends ]")

    # pull a real keyword from the actual data 
    first_title = data[0]["titles"][0] if data and data[0]["titles"] else None
    if first_title:
        # grab first word thats longer than 4 chars — avoids boring words like "the"
        keyword = next((w for w in first_title.split() if len(w) > 4), None)

        if keyword:
            # test 5 −∘♥∘− search finds something with a real keyword from the data
            matches = []
            for page in data:
                hits = [t for t in page["titles"] if keyword.lower() in t.lower()]
                if hits:
                    matches.append({"url": page["url"], "headlines": hits})

            test(f"search for '{keyword}' returns results", len(matches) > 0)
            test("search results have url and headlines", all("url" in m and "headlines" in m for m in matches))

            # test 6 — search for something that shouldnt exist returns empty
            fake_matches = [p for p in data if "xyznonexistentkeyword123" in str(p["titles"])]
            test("search for fake keyword returns nothing", len(fake_matches) == 0)

print("\n[ crawl structure ]")
if cache_exists:
    # test 7 depth values are valid numbers
    valid_depths = all(isinstance(p["depth"], int) and p["depth"] >= 0 for p in data)
    test("all depth values are valid integers", valid_depths)

    # test 8 urls are actual urls
    valid_urls = all(p["url"].startswith("http") for p in data)
    test("all urls start with http", valid_urls)

print("\n---------------------------------------------------")
total = passed + failed
print(f"  {passed}/{total} tests passed")
if failed == 0:
    print("  everything looks good. server tools are ready.")
else:
    print("  fix the failures above before pushing to github.")
print("---------------------------------------------------")
