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
from concurrent.futures import TimeoutError as FutureTimeoutError
import threading
import queue as _queue
from urllib.parse import urljoin, urlparse, urldefrag
from urllib.robotparser import RobotFileParser
import json
import time
import sys

# per-call hard wall-clock deadline, independent of requests' own timeout=.
# requests' timeout only bounds gaps *between* bytes, not total transfer
# time -- a host that trickles data can stall forever without ever
# tripping that per-read timeout. This bounds the whole call.
# See docs/agent-logs/crawler-hang-research-run71.md and
# docs/agent-logs/crawler-hang-fix-run72.md.
HARD_FETCH_DEADLINE = 20  # seconds, wall clock, per HTTP call

def get_with_hard_deadline(url, **kwargs):
    """requests.get() wrapped with a total wall-clock deadline.

    Runs the blocking call in a worker thread so a slow-trickling host
    cannot hang the crawler indefinitely -- the caller gets control back
    after HARD_FETCH_DEADLINE seconds even though the worker thread (and
    its socket) may still be alive in the background until the OS or
    requests' own low-level timeout eventually cleans it up.
    """
    # NOTE: deliberately not using ThreadPoolExecutor here. Its internal
    # worker threads are non-daemon by default (and Python's
    # ThreadPoolExecutor does not expose a daemon= kwarg), so a leaked
    # worker -- e.g. one still blocked in requests.get() on a trickling
    # host after this function has already given up and returned -- keeps
    # the whole interpreter alive at process exit until that socket is
    # cleaned up. A plain daemon thread has the same "leak until the
    # request resolves" behavior but never blocks process exit, since
    # daemon threads are killed outright when the main thread ends.
    result_q = _queue.Queue(maxsize=1)

    def _worker():
        try:
            result_q.put(("ok", requests.get(url, **kwargs)))
        except Exception as exc:
            result_q.put(("error", exc))

    thread = threading.Thread(target=_worker, daemon=True)
    thread.start()
    try:
        status, value = result_q.get(timeout=HARD_FETCH_DEADLINE)
    except _queue.Empty:
        # deadline hit -- the worker thread may still be alive in the
        # background, but being a daemon thread it will not prevent the
        # process from exiting.
        raise FutureTimeoutError(
            f"get_with_hard_deadline: {url} did not complete within "
            f"{HARD_FETCH_DEADLINE}s"
        )
    if status == "error":
        raise value
    return value

# default sources that you can override later (see beginning note block)
FASHION_SOURCES = [
    "https://www.vogue.com/fashion",
    "https://www.whowhatwear.com",
    "https://hypebeast.com/fashion",
    # added run 17 (bias-audit run 16 follow-up) to broaden geographic/cultural
    # coverage beyond English-language Western editorial/retail -- see
    # docs/agent-logs/source-diversity-expansion.md
    "https://nataal.com",
    "https://www.okayafrica.com",
    "https://fashionunited.in",
    "https://tokyofashion.com",
    # added run 19 -- filling the local-for-local gap flagged in run 17/18
    # (nataal/okayafrica/fashionunited.in are still diaspora- or Western-
    # audience-adjacent) -- see docs/agent-logs/source-diversity-expansion-2.md
    "https://www.vogue.mx",
    "https://tribune.com.pk/fashion",
    "https://www.savoirflair.com",
    # added run 20 -- first genuinely crawlable Southeast Asian source found
    # after run 19 left the region open (vogue.ph blocked by a Cloudflare JS
    # challenge); see docs/agent-logs/southeast-asia-source-attempt.md
    "https://www.dewimagazine.com",
    # added run 39 -- East Asia and Middle East were still uncovered gaps;
    # both verified reachable (no Cloudflare block); see
    # docs/agent-logs/source-diversity-run39.md. Still English-language --
    # geographic, not linguistic, diversification.
    "https://www.scmp.com/lifestyle/fashion-beauty",
    # thenationalnews.com added run 39, removed run 41: fetches fine and
    # passes robots.txt, but its fashion section is client-side rendered --
    # 0 headlines via static-HTML scraping across repeated checks (see
    # docs/agent-logs/new-source-crawl-verification-run40.md and
    # docs/agent-logs/thenationalnews-decision-run41.md). Not worth adding
    # JS-rendering complexity for one source; crawler.py stays static-HTML.
    # dieworkwear.com added run 54 -- this is the root-cause fix for the
    # long-standing "independent_criticism sources never reappear" carry-
    # forward: DOMAIN_SECTOR_MAP already classified dieworkwear.com/
    # throwingfits.com/blackbirdspyplane.com/substack.com as
    # independent_criticism, but NONE of them were ever seeded in
    # FASHION_SOURCES, and crawl() only follows same-domain links
    # (is_same_domain()), so the sector was structurally unreachable
    # regardless of what summarize.py's WebSearch step did. Verified via
    # WebFetch: dieworkwear.com is a real, independently-run static-HTML
    # menswear/workwear criticism blog (not a major-outlet property, not
    # PR-adjacent), robots.txt is fully permissive ("Disallow:" empty), and
    # the homepage renders real headline links without JS. throwingfits.com
    # was also tried and rejected -- it 302-redirects to a Patreon login
    # gate, not independently fetchable. See
    # docs/agent-logs/independent-criticism-source-investigation-run54.md.
    "https://dieworkwear.com",
    # added run 73 -- South America was a genuine 0-source gap (vogue.mx is
    # Mexico/North America, not South America). ffw.com.br is FFW, an
    # independent Brazilian fashion/culture editorial platform (est. 2009,
    # ~15+ years running, staff bylines, not PR-adjacent or a content mill).
    # Verified: robots.txt only disallows /wp-admin/ (fully permissive
    # otherwise); both the root domain and /materias/ return HTTP 200 via
    # curl with this project's own User-Agent and render real static-HTML
    # headline links (<h1>/<h2> article titles, /category/moda/ fashion
    # section) with no JS rendering required. See
    # docs/agent-logs/source-diversity-research-run73.md.
    "https://ffw.com.br",
    # added run 74 -- second look at the run-73 institutional-sector gap.
    # SPFW (spfw.com.br) re-verified and re-rejected: WebFetch confirms it's
    # event-management/PR content (designer showcase + ticketing via
    # Eventim, run by IMM/INMODE/F2), not a governing body -- run 73's call
    # stands. Inexmoda (inexmoda.org.co), Colombia's Instituto para la
    # Exportacion y la Moda, is a private nonprofit institute (est. 1987)
    # that runs the Colombiatex/Colombiamoda trade fairs, publishes
    # industry trend/research reports, and provides training -- an actual
    # institutional/research body, not an event-PR site. Verified: robots.txt
    # explicitly allows AI crawlers and search engines (only disallows
    # /wp-admin/, /xmlrpc.php); WebFetch on the root got HTTP 403 but curl
    # with this project's own User-Agent returned HTTP 200 with real
    # static-HTML headline markup (<h1>"INFORME DE TENDENCIAS",
    # <h2>"PROYECCIONES PARA LA INDUSTRIA DE LA MODA!") -- no JS rendering
    # required. First genuine second institutional-sector source alongside
    # cfda.com/fhcm.paris/britishfashioncouncil.co.uk. See
    # docs/agent-logs/spfw-institutional-recheck-run74.md.
    "https://inexmoda.org.co",
]

# default cache output path, pulled out as a named constant so future callers
# (summarize.py, server.py, etc.) can reference/override it consistently
# instead of each hardcoding the "trends_raw.json" string. Behavior/default
# unchanged: crawl_all_sources() still writes here unless a caller passes
# a different output_file explicitly.
DEFAULT_OUTPUT_FILE = "trends_raw.json"

# identifying ourselves honestly instead of pretending to be a browser
HEADERS = {
    "User-Agent": "fashion-trend-crawler/1.0 (educational project)"
}
# some hosts (e.g. dieworkwear.com, found run 55) respond with Brotli
# (Content-Encoding: br) regardless of Accept-Encoding -- confirmed by
# testing (the server ignores an Accept-Encoding: gzip, deflate override
# and sends br anyway). requests only decodes Brotli if the `brotli` (or
# `brotlicffi`) package is installed; without it response.text comes back
# garbled and crawl() silently finds 0 headlines with no error. Fixed by
# adding brotli as a real dependency (see requirements.txt) rather than
# fighting the server's encoding choice. See
# docs/agent-logs/dieworkwear-crawl-verification-run55.md.

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
        # use requests with our identifying HEADERS instead of RobotFileParser's
        # built-in read() (bare urllib, default "Python-urllib/x.x" user-agent).
        # found run 17: some hosts (e.g. tokyofashion.com, behind Cloudflare)
        # 403 that default UA on /robots.txt specifically, and RobotFileParser
        # treats a 403 as "disallow everything" -- even though the real
        # robots.txt (confirmed via curl/requests with our own UA) allows
        # crawling. Fetching robots.txt with the same headers we use for
        # every other request avoids that false "blocked" result.
        resp = get_with_hard_deadline(robots_url, headers=HEADERS, timeout=8)
        if resp.status_code == 200:
            parser.parse(resp.text.splitlines())
        elif resp.status_code in (401, 403):
            parser.disallow_all = True
        else:
            # missing/other error -> assume allowed, matching RobotFileParser's
            # own default behavior for non-401/403 errors
            parser.allow_all = True
    except (Exception, FutureTimeoutError):
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
            response = get_with_hard_deadline(url, headers=HEADERS, timeout=8)

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
                print(f"[depth {depth}] {url} -- {count} {label} found")

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

        except (Exception, FutureTimeoutError) as e:
            # log any error & continue
            print(f"error crawling {url}: {e}")
            continue

    return results

def crawl_all_sources(sources, output_file=DEFAULT_OUTPUT_FILE):
    # run the crawler against every source in the list
    all_results = []
    for source in sources:
        print(f"\nCrawling {source}...")
        results = crawl(source, max_depth=1, max_pages=10)
        all_results.extend(results)

        # flush after every source, not just at the very end -- if a slow/
        # unresponsive host later in the list stalls or the process gets
        # killed (found run 62/65/66: crawler.py can hang indefinitely on a
        # host that trickles bytes slowly enough that no single read ever
        # exceeds the per-request timeout), progress from sources already
        # crawled is preserved on disk instead of discarded. See
        # docs/agent-logs/real-pipeline-e2e-attempt-run65.md and
        # docs/agent-logs/crawler-hang-investigation-run67.md.
        with open(output_file, "w") as f:
            json.dump(all_results, f, indent=2)

    print(f"\nDone. {len(all_results)} pages crawled. Saved to {output_file}")
    return all_results

if __name__ == "__main__":
    # if urls passed as arguments use those, otherwise fall back to defaults
    # usage: python src/crawler.py https://site1.com https://site2.com
    sources = sys.argv[1:] if len(sys.argv) > 1 else FASHION_SOURCES
    crawl_all_sources(sources)
