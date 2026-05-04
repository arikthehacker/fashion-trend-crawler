#############################################################
# crawler.py
# last edited: 05/04/2026
# general purpose web crawler
#  1. starts from one or more seed urls
#  2. checks robots.txt before crawling anything
#  3. follows links up to specified depth
#  4. extracts headlines
#  5. saves results to a json file to analyze later
#
# ways to use:###############################################
# use default fashion sources i already have (i like fashion)
#    python src/crawler.py
# point it at anything
#    python src/crawler.py https://reuters.com
# or job listings, or art sites, or whatever
#    python src/crawler.py https://www.nike.com
#############################################################

import requests
from bs4 import BeautifulSoup
from collections import deque
from urllib.parse import urljoin, urlparse, urldefrag
from urllib.robotparser import RobotFileParser
import json
import time
import sys

# default sources that you can override later (see beginning note block)
FASHION_SOURCES = [
    "https://www.vogue.com/fashion",
    "https://www.whowhatwear.com",
    "https://hypebeast.com/fashion",
]

# identifying ourselves honestly instead of pretending to be a browser
HEADERS = {
    "User-Agent": "fashion-trend-crawler/1.0 (educational project)"
}

# cache robots parsers by domain so we dont re-fetch the same robots.txt repeatedly
robots_cache = {}

def get_robots_parser(base_url):
    domain = urlparse(base_url).netloc

    # already fetched this one, just return it
    if domain in robots_cache:
        return robots_cache[domain]

    # build the robots.txt url and try to read it
    robots_url = f"{urlparse(base_url).scheme}://{domain}/robots.txt"
    parser = RobotFileParser()
    parser.set_url(robots_url)

    try:
        parser.read()
    except Exception:
        # if we cant read it just assume we're allowed
        pass

    robots_cache[domain] = parser
    return parser

def is_allowed(url):
    # ask the robots parser if we're allowed to visit this url
    parser = get_robots_parser(url)
    return parser.can_fetch(HEADERS["User-Agent"], url)

def is_same_domain(url, base):
    # only follow links that stay on the same site
    return urlparse(url).netloc == urlparse(base).netloc

def crawl(start_url, max_depth=2, max_pages=20):
    visited = set()  # track what we've already seen so we don't loop
    queue = deque([(start_url, 0)])  # bfs queue (url, current depth)
    results = []

    while queue and len(results) < max_pages:
        url, depth = queue.popleft()
        # strip url fragments (#main-content etc) so we dont crawl the same page twice
        url, _ = urldefrag(url)

        # skip if already visited or too deep
        if url in visited or depth > max_depth:
            continue

        # skip if robots.txt says no
        if not is_allowed(url):
            print(f"[blocked by robots.txt] {url}")
            visited.add(url)
            continue

        visited.add(url)

        try:
            response = requests.get(url, headers=HEADERS, timeout=8)

            # skip anything that didn't load cleanly
            if response.status_code != 200:
                continue

            soup = BeautifulSoup(response.text, "html.parser")

            # pull headline text from h1/h2/h3 tags
            # filter short strings that are probably nav links not articles
            titles = []
            for tag in soup.find_all(["h1", "h2", "h3"]):
                text = tag.get_text(strip=True)
                if len(text) > 20:
                    titles.append(text)

            # only save pages that actually had headlines
            if titles:
                results.append({
                    "url": url,
                    "depth": depth,
                    "titles": titles[:5]  # cap at 5 per page for neatness
                })
                count = len(titles)
                label = "headline" if count == 1 else "headlines"
                print(f"[depth {depth}] {url} -♡♥♡- {count} {label} found")

            # queue up links to follow if we haven't hit max depth yet
            if depth < max_depth:
                for link in soup.find_all("a", href=True):
                    full_url, _ = urldefrag(urljoin(url, link["href"]))
                    # skip language switcher pages (same content diff locales) 
                    if "/change-language" in full_url:
                        continue
                    if is_same_domain(full_url, start_url) and full_url not in visited:
                        queue.append((full_url, depth + 1))

            # niceness level
            time.sleep(1)

        except Exception as e:
            # log any error & continue
            print(f"error crawling {url}: {e}")
            continue

    return results

def crawl_all_sources(sources, output_file="trends_raw.json"):
    # run the crawler against every source in the list
    all_results = []
    for source in sources:
        print(f"\nCrawling {source}...")
        results = crawl(source, max_depth=1, max_pages=10)
        all_results.extend(results)

    # dump everything to json for tools to pick up later
    with open(output_file, "w") as f:
        json.dump(all_results, f, indent=2)

    print(f"\nDone. {len(all_results)} pages crawled. Saved to {output_file}")
    return all_results

if __name__ == "__main__":
    # if urls passed as arguments use those, otherwise fall back to defaults
    # usage: python src/crawler.py https://site1.com https://site2.com
    sources = sys.argv[1:] if len(sys.argv) > 1 else FASHION_SOURCES
    crawl_all_sources(sources)
