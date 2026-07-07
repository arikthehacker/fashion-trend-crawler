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

    # added run (2028-02-21 report) -- khaite.com is the brand's own official
    # site, first crawled for its Fall/Winter 2028 New York Fashion Week
    # lookbook; same first-party-collection-drop pattern as the other
    # designer_origin entries above
    "khaite.com": "designer_origin",

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

    # added run 39 -- East Asian (Hong Kong) and Middle Eastern (UAE) fashion
    # press, both English-language but genuine geographic diversity; see
    # docs/agent-logs/source-diversity-run39.md
    "scmp.com": "editorial",

    # added run 56 -- verified via WebSearch/WebFetch before classifying (see
    # docs/agent-logs/domain-classification-run56.md): runwaylive.com is
    # RUNWAY Magazine, a CFDA-accredited US fashion/beauty/lifestyle
    # publication est. 1989; stylerave.com is Style Rave NG LLC, a
    # Nigeria-based fashion/lifestyle editorial title with staff bylines and
    # an affiliate shopping section (same pattern as okayafrica.com/
    # nataal.com -- editorial content plus a commerce layer, not a pure
    # retailer or content farm)
    "runwaylive.com": "editorial",
    "stylerave.com": "editorial",

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

    # added run 70 -- verified via WebSearch before classifying (see
    # docs/agent-logs/domain-classification-run70.md): fhcm.paris is the
    # Fédération de la Haute Couture et de la Mode, the official governing
    # body that coordinates Paris Fashion Week and Haute Couture Week
    # (confirmed official site, mirrors cfda.com/britishfashioncouncil.co.uk)
    "fhcm.paris": "institutional",

    # added run 74 -- Inexmoda (Instituto para la Exportacion y la Moda),
    # Colombia's nonprofit fashion/textile industry institute; runs
    # Colombiatex/Colombiamoda trade fairs, publishes trend/research
    # reports, provides training -- genuine institutional body, not a PR/
    # event-management site (unlike SPFW, re-checked and re-rejected this
    # same run). See docs/agent-logs/spfw-institutional-recheck-run74.md.
    "inexmoda.org.co": "institutional",

    # added run 70 -- laforma.club is an independent fashion-calendar/
    # editorial outlet (fashion week schedules, designer/bag guides,
    # documentary lists), not a governing body -- same editorial-plus-content
    # pattern as okayafrica.com/stylerave.com, not institutional
    "laforma.club": "editorial",

    # added run 73 -- ffw.com.br (FFW) is an independent Brazilian
    # fashion/culture editorial platform, the first South American source
    # in FASHION_SOURCES; see docs/agent-logs/source-diversity-research-run73.md
    "ffw.com.br": "editorial",

    # added run 75 -- voguearabia.com (Vogue Arabia) is a Condé Nast-owned,
    # Dubai-based regional Vogue edition covering Arab fashion/pop culture,
    # the first genuine Middle East source in FASHION_SOURCES (scmp.com,
    # run 39, is Hong Kong/East Asia, not Middle East); see
    # docs/agent-logs/middle-east-source-research-run75.md
    "voguearabia.com": "editorial",

    # added run 93 -- verified via WebSearch before classifying (see
    # docs/agent-logs/taxonomy-gap-fix-run93.md): proenzaschouler.com is the
    # house's own official site (proenzaschouler.com/pages/<season>, e.g.
    # fall-2024, spring-2026), publishing seasonal runway lookbook pages
    # alongside its shop -- same designer-owned-site-plus-commerce pattern as
    # chanel.com/dior.com/louisvuitton.com/gucci.com/prada.com, not a pure
    # e-commerce-only domain. Cited as a designer_origin source in the
    # 2028-02-14 report (Fall/Winter 2028 NYFW runway lookbook), flagged as a
    # candidate gap in that report's own agent log.
    "proenzaschouler.com": "designer_origin",

    # added run 94 -- closing the top of run 93's 58-domain gap backlog
    # (docs/agent-logs/taxonomy-gap-fix-run93.md), each verified via WebSearch
    # before classifying (see docs/agent-logs/taxonomy-gap-fix-run94.md):
    # voguescandinavia.com is Vogue Scandinavia, Conde Nast's Nordic-region
    # local Vogue edition (launched 2021, same publisher family as vogue.com/
    # voguearabia.com); wallpaper.com is a Future plc-owned British design/
    # architecture/fashion/art monthly (est. 1996); marieclaire.com is the
    # US edition of the long-running Marie Claire women's magazine (est.
    # 1937 in France, now Future plc); wmagazine.com is W Magazine, a
    # fashion/film/art/culture title (est. 1993, now Bustle Digital Group);
    # anothermag.com is AnOther Magazine, published by Dazed Media (the same
    # independent publisher as dazeddigital.com, already editorial) -- all
    # five are genuine staffed editorial titles with bylines, not retailers.
    "voguescandinavia.com": "editorial",
    "wallpaper.com": "editorial",
    "marieclaire.com": "editorial",
    "wmagazine.com": "editorial",
    "anothermag.com": "editorial",

    # added run 94 -- nssmag.com (nss magazine) is a Milan-based streetwear/
    # culture editorial title, a registered newspaper publication (est. 2012,
    # official status 2022) with investigative/feature journalism plus a
    # "shopping" vertical -- same editorial-plus-commerce-layer pattern
    # already accepted for okayafrica.com/stylerave.com, not a pure
    # retailer; coveteur.com is a staffed multimedia editorial brand (est.
    # 2011, relaunched 2025 under Gallery Media Group/VaynerX) covering
    # fashion/beauty/lifestyle with a named editorial policy barring
    # pay-for-play coverage -- editorial-led despite a "shopping" section,
    # matching the same pattern rather than the pure-transactional retailers
    # (net-a-porter.com, ssense.com, etc.) already in this map.
    "nssmag.com": "editorial",
    "coveteur.com": "editorial",

    # added run 94 -- istitutomarangoni.com is Istituto Marangoni, a
    # genuine higher-education institution (founded 1935, campuses in
    # Milan/Paris/London/Florence/Shanghai, QS-ranked fashion/design/luxury
    # schools) -- an institutional/educational body, not a designer house
    # or editorial outlet, matching fitnyc.edu's pattern rather than the
    # editorial or designer_origin sectors.
    "istitutomarangoni.com": "institutional",

    # added run (2028-02-28 report) -- verified via WebSearch before
    # classifying, same convention as domain-classification-run56/run70/
    # run93/run94: simonerocha.com is the house's own official site, first
    # crawled for its Fall/Winter 2028 London Fashion Week lookbook; same
    # first-party-collection-drop pattern as khaite.com/proenzaschouler.com.
    # cameramoda.it is Camera Nazionale della Moda Italiana, the official
    # governing body that organizes Milan Fashion Week, confirmed official
    # site, mirrors cfda.com/britishfashioncouncil.co.uk/fhcm.paris.
    "simonerocha.com": "designer_origin",
    "cameramoda.it": "institutional",
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
