#############################################################
# taxonomy.py
# constants + classification helpers for ARI3LLA INDEX
#
# defines the controlled vocabularies used across the pipeline:
#   - source sectors (section 11 of docs/ARI3LLA INDEX.txt)
#   - confidence levels (section 14)
#   - volatility labels (section 15)
#   - origin classifications (section 12)
# plus a lightweight classify_source(url) helper that maps a
# domain to a source sector so reports can compute
# source_sector_breakdown without manual tagging.
#############################################################

from urllib.parse import urlparse

# ---------------------------------------------------------------
# source sectors
# ---------------------------------------------------------------
SOURCE_SECTORS = [
    "designer_origin",
    "runway",
    "editorial",
    "retail",
    "social",
    "visual_archive",
    "independent_criticism",
    "institutional",
    "street_ugc",
    "resale",
]

# ---------------------------------------------------------------
# confidence levels (section 14)
# ---------------------------------------------------------------
CONFIDENCE_LEVELS = [
    "low",
    "medium",
    "high",
    "archival",
]

# ---------------------------------------------------------------
# volatility labels (section 15)
# ---------------------------------------------------------------
VOLATILITY_LABELS = [
    "stable",
    "emerging",
    "seasonal",
    "volatile",
    "flash",
    "microtrend",
    "recurring",
    "revival",
    "long_tail",
    "saturated",
    "declining",
]

# ---------------------------------------------------------------
# origin classifications (section 12)
# ---------------------------------------------------------------
ORIGIN_CLASSIFICATIONS = [
    "designer_originated",
    "editorial_amplified",
    "retail_adopted",
    "social_amplified",
    "platform_native",
    "archive_revival",
    "unclear",
]

# ---------------------------------------------------------------
# domain -> sector map (section 11 detailed source types)
# add to this as new sources are crawled
# ---------------------------------------------------------------
DOMAIN_SECTOR_MAP = {
    # designer origin sources (brand-owned sites, first-party collection drops)
    "chanel.com": "designer_origin",
    "dior.com": "designer_origin",
    "gucci.com": "designer_origin",
    "louisvuitton.com": "designer_origin",
    "prada.com": "designer_origin",

    # runway / editorial / magazine sources
    "vogue.com": "editorial",
    "wwd.com": "editorial",
    "businessoffashion.com": "editorial",
    "gq.com": "editorial",
    "harpersbazaar.com": "editorial",
    "elle.com": "editorial",
    "i-d.co": "editorial",
    "dazeddigital.com": "editorial",
    "highsnobiety.com": "editorial",
    "hypebeast.com": "editorial",
    "thecut.com": "editorial",
    "nytimes.com": "editorial",

    # added run 17 -- non-Western/geographically-broadening editorial sources
    # (bias-audit run 16 finding: prior seeds were all English-language Western
    # editorial/retail; see docs/agent-logs/source-diversity-expansion.md)
    "nataal.com": "editorial",
    "okayafrica.com": "editorial",
    "fashionunited.in": "editorial",
    "tokyofashion.com": "editorial",

    # added run 19 -- local-for-local outlets (published primarily for a
    # local/regional audience, not diaspora or Western-expat-facing) filling
    # the Latin American / South Asian / Southeast Asian / Middle Eastern
    # gap flagged in run 17's log; see
    # docs/agent-logs/source-diversity-expansion-2.md
    "vogue.mx": "editorial",
    "tribune.com.pk": "editorial",
    "savoirflair.com": "editorial",

    # added run 20 -- Southeast Asia, home-grown Indonesian fashion/lifestyle
    # title (Bahasa Indonesia editorial, not a Western edition), the first
    # genuinely crawlable candidate found for this region; see
    # docs/agent-logs/southeast-asia-source-attempt.md
    "dewimagazine.com": "editorial",

    # retail / commerce sources
    "whowhatwear.com": "retail",
    "net-a-porter.com": "retail",
    "ssense.com": "retail",
    "farfetch.com": "retail",
    "nordstrom.com": "retail",
    "shopbop.com": "retail",
    "revolve.com": "retail",

    # resale / secondhand market sources
    "thereal-real.com": "resale",
    "therealreal.com": "resale",
    "depop.com": "resale",
    "vestiairecollective.com": "resale",
    "grailed.com": "resale",
    "poshmark.com": "resale",

    # social / platform sources
    "tiktok.com": "social",
    "instagram.com": "social",
    "youtube.com": "social",
    "reddit.com": "social",
    "pinterest.com": "social",

    # visual archive / search sources
    "google.com": "visual_archive",
    "worn-on.com": "visual_archive",
    "firstview.com": "visual_archive",
    "nowfashion.com": "visual_archive",
    "gettyimages.com": "visual_archive",
    "fashionanthology.com": "visual_archive",

    # independent criticism
    "substack.com": "independent_criticism",
    "blackbirdspyplane.com": "independent_criticism",
    "dieworkwear.com": "independent_criticism",
    "throwingfits.com": "independent_criticism",

    # institutional / historical sources
    "fitnyc.edu": "institutional",
    "metmuseum.org": "institutional",
    "vam.ac.uk": "institutional",
    "cfda.com": "institutional",
    "kci.or.jp": "institutional",
    "britishfashioncouncil.co.uk": "institutional",
}


def _strip_www(netloc: str) -> str:
    return netloc[4:] if netloc.startswith("www.") else netloc


def classify_source(url: str) -> str:
    """
    map a source url (or bare domain) to a source sector.

    matches on registered domain and known subdomains (e.g. a
    substack.com subdomain like someone.substack.com still maps
    to independent_criticism). falls back to "unclear" if the
    domain isn't in DOMAIN_SECTOR_MAP.
    """
    if not url:
        return "unclear"

    # allow bare domains (no scheme) to be passed in directly
    netloc = urlparse(url).netloc
    if not netloc:
        netloc = url

    netloc = _strip_www(netloc.lower()).split(":")[0]  # drop port if present

    if netloc in DOMAIN_SECTOR_MAP:
        return DOMAIN_SECTOR_MAP[netloc]

    # check suffix match for subdomains, e.g. someone.substack.com
    for domain, sector in DOMAIN_SECTOR_MAP.items():
        if netloc.endswith("." + domain):
            return sector

    return "unclear"
