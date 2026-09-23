#############################################################
# ingest_rss.py
# feeds -> the item store (src/item_store.py). the first real data
# pipeline: every item it stores has a URL, a publish date and a
# content hash (docs/PROJECT_ANALYSIS_2026-09-22.md, Pillar 1).
#
# - respects robots.txt and the crawler's hard fetch deadline
#   (reuses src/crawler.py), identifies itself honestly, and waits
#   between requests to the same host
# - stores title + link + dates only, never article text
# - an entry without a publish date is skipped and counted: an
#   undated item can't be evidence
#
# usage:
#   python src/ingest_rss.py discover [--limit N] [--domain D ...]
#       find feeds for outlets in taxonomy.DOMAIN_SECTOR_MAP and
#       write data/feeds.json (review it before relying on it)
#   python src/ingest_rss.py ingest [--db PATH] [--limit N]
#       fetch every feed in data/feeds.json into the item store
#############################################################

import argparse
import json
import os
import re
import sys
import time
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from urllib.parse import urljoin, urlparse

from crawler import HEADERS, get_with_hard_deadline, is_allowed
from item_store import DEFAULT_DB, connect, migrate, upsert_item, utc_now
from taxonomy import DOMAIN_SECTOR_MAP, classify_source

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FEEDS_FILE = os.path.join(ROOT, "data", "feeds.json")

PER_HOST_DELAY = 1.0  # seconds between requests to the same host
FALLBACK_PATHS = ("/feed", "/rss", "/feed/", "/rss.xml", "/atom.xml", "/index.xml")
FEED_TYPES = ("application/rss+xml", "application/atom+xml", "application/feed+xml")

NS = {
    "atom": "http://www.w3.org/2005/Atom",
    "dc": "http://purl.org/dc/elements/1.1/",
}

_last_hit = {}


def polite_get(url):
    """robots-checked, rate-limited GET with the crawler's hard deadline.
    returns the response, or None when robots.txt disallows the URL."""
    if not is_allowed(url):
        return None
    host = urlparse(url).netloc
    wait = PER_HOST_DELAY - (time.monotonic() - _last_hit.get(host, 0))
    if wait > 0:
        time.sleep(wait)
    _last_hit[host] = time.monotonic()
    return get_with_hard_deadline(url, headers=HEADERS, timeout=15)


# ---------------------------------------------------------------- parsing

def to_utc(value: str):
    """parse an RSS (RFC 822) or Atom/dc (ISO 8601) date to a
    'YYYY-MM-DDTHH:MM:SSZ' string, or None if unparseable."""
    if not value:
        return None
    value = value.strip()
    dt = None
    try:
        dt = parsedate_to_datetime(value)
    except (TypeError, ValueError, IndexError):
        try:
            dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return None
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)  # feeds without an offset: assume UTC
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _text(el, path):
    found = el.find(path, NS)
    return (found.text or "").strip() if found is not None and found.text else ""


def parse_feed(xml_text: str, feed_url: str) -> list:
    """return [{url, title, published_at, summary}] for every entry that has
    a link, in feed order. published_at is None when the entry has no
    usable date (the caller skips those)."""
    # some feeds prepend whitespace or a BOM before the XML declaration
    root = ET.fromstring(xml_text.lstrip("﻿ \t\r\n").encode("utf-8"))
    entries = []
    if root.tag == f"{{{NS['atom']}}}feed":
        for e in root.findall("atom:entry", NS):
            link = None
            for l in e.findall("atom:link", NS):
                if l.get("rel", "alternate") == "alternate" and l.get("href"):
                    link = l.get("href")
                    break
            if not link:
                continue
            date = _text(e, "atom:published") or _text(e, "atom:updated")
            entries.append({
                "url": urljoin(feed_url, link),
                "title": _text(e, "atom:title"),
                "published_at": to_utc(date),
                "summary": _text(e, "atom:summary"),
            })
    else:
        for item in root.iter("item"):
            link = _text(item, "link") or _text(item, "guid")
            if not link.startswith(("http://", "https://")):
                continue
            date = _text(item, "pubDate") or _text(item, "dc:date")
            entries.append({
                "url": urljoin(feed_url, link),
                "title": _text(item, "title"),
                "published_at": to_utc(date),
                "summary": _text(item, "description"),
            })
    return entries


# -------------------------------------------------------------- discovery

_LINK_TAG = re.compile(r"<link\b[^>]*>", re.I)
_ATTR = re.compile(r'(\w[\w-]*)\s*=\s*["\']([^"\']*)["\']')


def autodiscover(html: str, page_url: str) -> list:
    """feed URLs advertised by <link rel="alternate" type="...rss/atom...">."""
    found = []
    for tag in _LINK_TAG.findall(html):
        attrs = {k.lower(): v for k, v in _ATTR.findall(tag)}
        if "alternate" in attrs.get("rel", "").lower() and attrs.get("type", "").lower() in FEED_TYPES and attrs.get("href"):
            url = urljoin(page_url, attrs["href"])
            if "comments" not in url.lower() and url not in found:
                found.append(url)
    return found


def is_working_feed(url: str) -> bool:
    try:
        resp = polite_get(url)
        if resp is None or resp.status_code != 200:
            return False
        entries = parse_feed(resp.text, url)
        return any(e["published_at"] for e in entries)
    except Exception:
        return False


def discover_domain(domain: str):
    """return the first working feed URL for a domain, or None."""
    home = f"https://{domain}/"
    candidates = []
    try:
        resp = polite_get(home)
        if resp is not None and resp.status_code == 200:
            candidates += autodiscover(resp.text, resp.url)
    except Exception:
        pass
    candidates += [urljoin(home, p) for p in FALLBACK_PATHS]
    for url in candidates:
        if is_working_feed(url):
            return url
    return None


# ------------------------------------------------- section feeds (relevance)

# rough topical filter for choosing between an outlet's feeds; not used to
# classify items. multilingual because many outlets in the taxonomy aren't
# English-language.
_STYLE_WORDS = re.compile(
    r"fashion|style|runway|catwalk|collection|designer|couture|menswear|womenswear|wear\b|"
    r"dress|outfit|jacket|coat|knit|denim|sneaker|shoe|boot|bag|jewel|watch|beauty|makeup|"
    r"skincare|fragrance|hair|nail|vintage|resale|thrift|luxury|label|boutique|tailor|"
    r"silhouette|aesthetic|-core\b|trend|spring 20|fall 20|resort 20|pre-fall|met gala|"
    r"mode\b|défilé|defile|tendance|moda\b|desfile|estilo|tendencia|tendência|passerella|sfilata",
    re.I,
)
SECTION_NAMES = ("fashion", "style", "moda", "mode", "lifestyle/fashion", "style/fashion", "beauty")


def style_share(entries: list) -> float:
    if not entries:
        return 0.0
    hits = sum(bool(_STYLE_WORDS.search(f"{e['title']} {e['url']}")) for e in entries)
    return hits / len(entries)


def feed_entries(url: str) -> list:
    try:
        resp = polite_get(url)
        if resp is None or resp.status_code != 200:
            return []
        return [e for e in parse_feed(resp.text, url) if e["published_at"]]
    except Exception:
        return []


def find_section_feed(domain: str, current_url: str):
    """look for a fashion/style section feed that is more on-topic than the
    outlet's current feed. returns (url, share, current_share); url is None
    when nothing better exists."""
    current_share = style_share(feed_entries(current_url))
    home = f"https://{domain}/"
    candidates = []
    for name in SECTION_NAMES:
        section = urljoin(home, f"{name}/")
        try:
            resp = polite_get(section)
            if resp is not None and resp.status_code == 200:
                candidates += autodiscover(resp.text, resp.url)
        except Exception:
            pass
        candidates += [urljoin(home, p) for p in (
            f"{name}/feed/", f"{name}/feed", f"{name}/rss", f"{name}/rss.xml",
            f"category/{name}/feed/", f"rss/{name}", f"feed/{name}",
        )]
    best, best_share = None, current_share
    for url in dict.fromkeys(candidates):
        if url.rstrip("/") == current_url.rstrip("/"):
            continue
        entries = feed_entries(url)
        if len(entries) < 3:
            continue
        share = style_share(entries)
        # require a clear improvement, not a coin-flip difference
        if share >= best_share + 0.2 and share >= 0.6:
            best, best_share = url, share
            if share >= 0.9:
                break
    return best, best_share, current_share


def discover(domains) -> list:
    feeds = []
    for i, domain in enumerate(domains, 1):
        url = discover_domain(domain)
        print(f"[{i}/{len(domains)}] {domain}: {url or 'no working feed'}")
        if url:
            feeds.append({"domain": domain, "sector": classify_source(domain),
                          "feed_url": url, "discovered_at": utc_now()[:10]})
    return feeds


# ---------------------------------------------------------------- ingest

def ingest_feed(con, feed: dict, fetched_at: str = None) -> dict:
    counts = {"inserted": 0, "updated": 0, "unchanged": 0, "undated": 0, "future": 0, "error": ""}
    try:
        resp = polite_get(feed["feed_url"])
        if resp is None:
            counts["error"] = "disallowed by robots.txt"
            return counts
        if resp.status_code != 200:
            counts["error"] = f"HTTP {resp.status_code}"
            return counts
        entries = parse_feed(resp.text, feed["feed_url"])
    except Exception as exc:  # one bad feed never stops the run
        counts["error"] = f"{type(exc).__name__}: {exc}"[:200]
        return counts
    fetched_at = fetched_at or utc_now()
    with con:
        for e in entries:
            if not e["published_at"]:
                counts["undated"] += 1
                continue
            if e["published_at"] > fetched_at:
                counts["future"] += 1  # a feed claiming a future date is not evidence
                continue
            _, status = upsert_item(con, url=e["url"], title=e["title"], published_at=e["published_at"],
                                    fetched_at=fetched_at, source_method="rss", ts_precision="exact",
                                    hash_basis=e["summary"])
            counts[status] += 1
    return counts


def load_feeds(path=FEEDS_FILE) -> list:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="RSS/Atom feeds -> item store")
    ap.add_argument("command", choices=["discover", "sections", "ingest"])
    ap.add_argument("--db", default=DEFAULT_DB)
    ap.add_argument("--limit", type=int, default=0, help="only the first N domains/feeds")
    ap.add_argument("--domain", action="append", help="discover only these domains")
    args = ap.parse_args(argv)

    if args.command == "discover":
        domains = args.domain or sorted(DOMAIN_SECTOR_MAP)
        if args.limit:
            domains = domains[: args.limit]
        feeds = discover(domains)
        existing = load_feeds() if os.path.exists(FEEDS_FILE) else []
        merged = {f["domain"]: f for f in existing}
        merged.update({f["domain"]: f for f in feeds})
        os.makedirs(os.path.dirname(FEEDS_FILE), exist_ok=True)
        with open(FEEDS_FILE, "w", encoding="utf-8") as f:
            json.dump(sorted(merged.values(), key=lambda x: x["domain"]), f, indent=2)
            f.write("\n")
        print(f"{len(feeds)} of {len(domains)} domains have a working feed; {len(merged)} feeds in {FEEDS_FILE}")
        return 0

    if args.command == "sections":
        feeds = load_feeds()
        targets = [f for f in feeds if not args.domain or f["domain"] in args.domain]
        for f in targets:
            url, share, before = find_section_feed(f["domain"], f["feed_url"])
            f["style_share"] = round(share if url else before, 2)
            if url:
                f.setdefault("site_feed_url", f["feed_url"])
                f["feed_url"] = url
                f["section_found_at"] = utc_now()[:10]
            print(f"{f['domain']}: {before:.0%} -> " + (f"{share:.0%} via {url}" if url else "no better section feed"))
        with open(FEEDS_FILE, "w", encoding="utf-8") as fh:
            json.dump(feeds, fh, indent=2)
            fh.write("\n")
        return 0

    con = connect(args.db)
    migrate(con)
    feeds = load_feeds()
    if args.limit:
        feeds = feeds[: args.limit]
    totals = {"inserted": 0, "updated": 0, "unchanged": 0, "undated": 0, "future": 0, "failed_feeds": 0}
    for feed in feeds:
        c = ingest_feed(con, feed)
        for k in ("inserted", "updated", "unchanged", "undated", "future"):
            totals[k] += c[k]
        totals["failed_feeds"] += bool(c["error"])
        print(f"{feed['domain']}: +{c['inserted']} new, {c['updated']} updated, {c['unchanged']} unchanged, "
              f"{c['undated']} undated, {c['future']} future" + (f"  ERROR {c['error']}" if c["error"] else ""))
    print("totals:", totals)
    return 0


if __name__ == "__main__":
    sys.exit(main())
