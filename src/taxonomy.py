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
    # added run 100 -- B2B commercial trend-forecasting / retail-analytics
    # vendors (e.g. wgsn.com, trendalytics.co, stylearcade.com) that publish
    # public trend-report blog content as marketing for a paid forecasting/
    # merchandising-intelligence product. Distinct incentive structure from
    # every existing bucket: not journalism (editorial), not brand voice
    # (designer_origin), not a nonprofit/governing body (institutional), not
    # a product storefront (retail) -- it's a vendor selling *predictions* as
    # a subscription product, with a commercial incentive to make trends
    # sound bigger/more certain than editorial or independent criticism
    # would. See docs/agent-logs/taxonomy-gap-fix-run100.md for the full
    # reasoning and the three domains that motivated this addition; this is
    # a bigger structural change than a routine domain mapping, flagged here
    # for easy human review/reversal. NOT added to
    # report_schema.HIGH_RELIABILITY_SECTORS -- the commercial incentive to
    # inflate trend certainty is a noise-profile risk comparable to
    # unvetted social/UGC sources, not comparable to editorial/independent
    # criticism's noise profile.
    "trade_intelligence",
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

    # added run (2028-03-13 report) -- same first-party-collection-drop
    # pattern as khaite.com/proenzaschouler.com/simonerocha.com: miumiu.com
    # and loewe.com are each house's own official site, first crawled for
    # their Fall/Winter 2028 Paris Fashion Week runway lookbooks.
    "miumiu.com": "designer_origin",
    "loewe.com": "designer_origin",

    # added run 96 -- closing the next tier of run 93/94's gap backlog
    # (docs/agent-logs/taxonomy-gap-fix-run96.md), each verified via
    # WebSearch before classifying: fashionista.com is a staffed fashion
    # news site (Breaking Media, est. 2007, named EIC/editorial team);
    # fashionnetwork.com is FashionNetwork.com, an independent French
    # fashion-business trade news outlet (est. 2001, ~60 editors
    # worldwide) -- trade press, same pattern as wwd.com/
    # businessoffashion.com; fashionunited.com is the global edition of
    # the FashionUnited business-news/jobs platform, matching the
    # already-mapped fashionunited.in; graziadaily.co.uk is Grazia UK's
    # website (Bauer Media, launched 2005/web 2008, staffed glossy
    # magazine); stylist.co.uk is Stylist magazine (UK, est. 2009, named
    # EIC, owned by The Stylist Group/DC Thomson); thefashionlaw.com is
    # a legal/business fashion-industry trade journalism site founded by
    # attorney Julie Zerbo (2012), analytical trade reporting in the same
    # bucket as businessoffashion.com/wwd.com rather than a personal
    # opinion blog; theimpression.com is a NYC-based fashion-industry
    # trade site covering runway/marketing/business news, membership
    # model. hellobeautiful.com is a staffed Black-women's fashion/
    # beauty/lifestyle editorial site under Urban One (Radio One's media
    # division) -- a legitimate media company property, not a PR mill.
    "fashionista.com": "editorial",
    "fashionnetwork.com": "editorial",
    "fashionunited.com": "editorial",
    "graziadaily.co.uk": "editorial",
    "stylist.co.uk": "editorial",
    "thefashionlaw.com": "editorial",
    "theimpression.com": "editorial",
    "hellobeautiful.com": "editorial",

    # added run 98 -- continuing to close run 93/94/96's gap backlog
    # (docs/agent-logs/taxonomy-gap-fix-run98.md), each verified via
    # WebSearch before classifying: artnews.com is ARTnews, a staffed
    # visual-arts trade/editorial publication tracking art since 1902
    # (fashion-adjacent art-world coverage); asiae.co.kr is The Asia
    # Business Daily, a staffed South Korean economic newspaper (est.
    # 1988, listed KOSDAQ) -- general business press, geographic-
    # diversity editorial in the same vein as scmp.com/tribune.com.pk;
    # bricksmagazine.co.uk is BRICKS Magazine, an independent UK
    # publication (10+ years, named team/masthead) covering fashion,
    # music, and culture; clashmusic.com is Clash, a UK music magazine
    # (launched 2004/web 2008) whose coverage explicitly spans fashion
    # alongside music; complex.com is Complex, a staffed digital media
    # outlet (founded 2002, corporate-owned, editorial masthead) with a
    # long-running style/style-history vertical, same bucket as
    # hypebeast.com/highsnobiety.com; essence.com is ESSENCE, the
    # historic (est. 1970) staffed lifestyle/fashion/beauty magazine for
    # Black women, Black-owned since 2018; hellomagazine.com is HELLO!,
    # a staffed UK celebrity/royal/fashion weekly (launched 1988, web
    # 2001); hollywoodreporter.com is The Hollywood Reporter, a staffed
    # entertainment trade publication (founded 1930, Penske Media) whose
    # coverage includes red-carpet/fashion business reporting;
    # interviewmagazine.com is Interview, the staffed culture/fashion
    # magazine founded 1969 (Andy Warhol/John Wilcock); papermag.com is
    # PAPER, a staffed independent NYC fashion/culture magazine founded
    # 1984, still operating with a named editor-in-chief.
    #
    # Skipped (not added), all researched but not clearing the bar:
    # cafedelhomme.com -- WebSearch shows this is the website for Café
    # de l'Homme, a Paris restaurant near the Trocadero; its "fashion"
    # content is incidental Fashion Week dining coverage, not a fashion
    # editorial source. chicstylecollective.com -- a single-editor-run
    # affordable-luxury lifestyle blog (fashion/beauty/horoscopes mixed
    # together, "must-have"/shopping-guide framing); ambiguous enough
    # (like modernluxury.com in run 96) that it doesn't clearly clear
    # the bar for a staffed editorial title, left for a closer look.
    # ecostylia.com -- a small independently-funded French/English
    # magazine mixing fashion with astrology/horoscopes and general
    # culture; genuine editorial standard unclear, left unclassified
    # rather than forced, same caution as modernluxury.com.
    "artnews.com": "editorial",
    "asiae.co.kr": "editorial",
    "bricksmagazine.co.uk": "editorial",
    "clashmusic.com": "editorial",
    "complex.com": "editorial",
    "essence.com": "editorial",
    "hellomagazine.com": "editorial",
    "hollywoodreporter.com": "editorial",
    "interviewmagazine.com": "editorial",
    "papermag.com": "editorial",

    # added run 99 -- closing more of run 96's 32-domain backlog
    # (docs/agent-logs/taxonomy-gap-fix-run98.md), each verified via
    # WebSearch before classifying (see
    # docs/agent-logs/taxonomy-gap-fix-run99.md): fashionunited.uk is the
    # UK edition of the FashionUnited B2B trade-news/jobs platform,
    # matching the already-mapped fashionunited.in/fashionunited.com;
    # fzine.com (F ZINE Singapore, formerly FEMALE magazine since 1974)
    # is a staffed youth-culture/fashion editorial platform with a named
    # editor-in-chief; imfirenzedigest.com is I'M FIRENZE DIGEST, an
    # editorial trend/culture magazine published by Istituto Marangoni
    # Firenze -- a magazine publication in its own right (fashion/art/
    # beauty features), distinct from the school's own institutional site
    # (istitutomarangoni.com, already institutional); insidehook.com is a
    # staffed men's lifestyle outlet (12 full-time editors, named
    # editorial policy) with a style vertical; lamag.com is Los Angeles
    # magazine (est. 1961, named EIC, National Magazine Award winner)
    # covering fashion among its city-lifestyle beat; lofficielusa.com is
    # the US edition of L'Officiel, a major fashion/culture title founded
    # in Paris in 1921 with 30 national editions; news.sbs.co.kr is the
    # news portal of SBS, a major staffed South Korean broadcast network
    # -- general/geographic-diversity press in the same vein as
    # asiae.co.kr/scmp.com/tribune.com.pk; numero.com is Numero, a
    # staffed international fashion/art magazine (founded 1998, named
    # EIC); parisselectbook.com is Paris Select, a 17-year-running
    # Paris luxury/lifestyle magazine with a named editor-in-chief and
    # journalist-written content; pursuitist.com is an independent,
    # ad-free luxury lifestyle publication (founded 2008, named EIC,
    # cited by NYT/WSJ/Forbes) with a dedicated Style vertical;
    # robbreport.com is Robb Report, a staffed luxury-lifestyle magazine
    # (founded 1976, Penske Media-owned, same publisher family as
    # hollywoodreporter.com) with a Style/fashion vertical; soccerbible.com
    # is a staffed football-culture publisher (founded 2006) whose
    # coverage includes footwear/apparel design content, fashion-adjacent
    # in the same way artnews.com is art-adjacent; thezoereport.com is a
    # staffed fashion/beauty/lifestyle title (launched 2009, named
    # editorial director and masthead) under BDG; vmagazine.com is V
    # Magazine, a major fashion/pop-culture title running since 1999;
    # vogueadria.com is Vogue Adria, Conde Nast's Balkan-region regional
    # Vogue edition (launched 2024, named EIC), matching the
    # voguearabia.com/voguescandinavia.com pattern; whitewall.art is
    # Whitewall, an independent art/fashion/design magazine (launched
    # 2006) with a named editorial team; wionews.com is WION, a staffed
    # global news network (India-headquartered) with named journalists --
    # geographic-diversity editorial in the same vein as wionews.com's
    # South Asian peers already mapped; yourcoffeebreak.co.uk is Your
    # Coffee Break, a staffed lifestyle magazine for professional women
    # (founded 2012, London-based with multi-city bureaus) covering
    # fashion/beauty; euronews.com is Euronews, a major staffed
    # pan-European news network (400 journalists) -- geographic-diversity
    # general press, same bucket as scmp.com/asiae.co.kr.
    "fashionunited.uk": "editorial",
    "fzine.com": "editorial",
    "imfirenzedigest.com": "editorial",
    "insidehook.com": "editorial",
    "lamag.com": "editorial",
    "lofficielusa.com": "editorial",
    "news.sbs.co.kr": "editorial",
    "numero.com": "editorial",
    "parisselectbook.com": "editorial",
    "pursuitist.com": "editorial",
    "robbreport.com": "editorial",
    "soccerbible.com": "editorial",
    "thezoereport.com": "editorial",
    "vmagazine.com": "editorial",
    "vogueadria.com": "editorial",
    "whitewall.art": "editorial",
    "wionews.com": "editorial",
    "yourcoffeebreak.co.uk": "editorial",
    "euronews.com": "editorial",

    # added run 99 -- wardrobeoxygen.com is a long-running (since 2005,
    # full-time since 2017) single-author personal style blog by Alison
    # Gary, featured in the Washington Post/NYT/US News -- same
    # single-voice, long-running, independently-credible pattern as
    # dieworkwear.com/throwingfits.com, not a staffed masthead.
    "wardrobeoxygen.com": "independent_criticism",

    # added run 100 -- see docs/agent-logs/taxonomy-gap-fix-run100.md.
    # modernluxury.com is Modern Luxury, the largest US city-regional
    # luxury-lifestyle magazine publisher (65+ city titles), covering
    # fashion alongside dining/design/travel -- same
    # general-lifestyle-magazine-with-a-fashion-vertical pattern as
    # lamag.com/robbreport.com, already editorial.
    "modernluxury.com": "editorial",

    # chicstylecollective.com is Chic Style Collective, a staffed fashion/
    # beauty/lifestyle site with a named editor-in-chief (Natalie Dixon,
    # 15+ years fashion/beauty/lifestyle journalism) and a claimed 4.5M
    # readership. Monetizes via affiliate links/shopping content, but that
    # commerce layer doesn't disqualify it any more than it would other
    # editorial outlets with shopping verticals -- named masthead + regular
    # published output clears the same bar as fzine.com/lamag.com.
    "chicstylecollective.com": "editorial",

    # ecostylia.com is Ecostylia, an independently-funded French online
    # press outlet (founder/editor Pierre-Antoine Tsady) covering arts,
    # society, sustainable fashion, and Paris Fashion Week, including
    # original designer interviews. General-interest with real, regular
    # fashion coverage -- same bucket as other small independent editorial
    # outlets (whitewall.art).
    "ecostylia.com": "editorial",

    # added run 100 -- new trade_intelligence sector, see SOURCE_SECTORS
    # comment above for full reasoning. All three confirmed via WebSearch
    # to publish public seasonal/runway trend-report blog content (not just
    # gated SaaS product pages) as top-of-funnel marketing for a paid B2B
    # forecasting/retail-analytics product -- that public content is what
    # the crawler is picking up.
    "wgsn.com": "trade_intelligence",
    "trendalytics.co": "trade_intelligence",
    "stylearcade.com": "trade_intelligence",
    # EDITED (retail pricing/assortment analytics); its blog is a public feed
    # (added 2026-09-22 for sector coverage in src/ingest_rss.py)
    "edited.com": "trade_intelligence",
    # Added 2026-09-23 with feeds verified by src/ingest_rss.py (>= 5 dated
    # entries, newest within 60 days) to widen sector and language coverage.
    "fashionweekonline.com": "runway",
    "fashionmuseum.co.uk": "institutional",
    "globenewswire.com": "designer_origin",  # brand press releases (clothing & accessories category feed)
    "permanentstyle.com": "independent_criticism",
    "footwearnews.com": "trade_intelligence",
    "glossy.co": "trade_intelligence",
    "just-style.com": "trade_intelligence",
    "apparelresources.com": "trade_intelligence",
    "drapersonline.com": "trade_intelligence",
    "theindustry.fashion": "trade_intelligence",
    "beautyindependent.com": "trade_intelligence",
    "cosmeticsbusiness.com": "trade_intelligence",
    "theguardian.com": "editorial",
    "vogue.co.uk": "editorial",
    "hypebae.com": "editorial",
    "nylon.com": "editorial",
    "refinery29.com": "editorial",
    "allure.com": "editorial",
    "elle.com.au": "editorial",
    "harpersbazaar.com.au": "editorial",
    "bellanaija.com": "editorial",
    "fashionsnap.com": "editorial",
    "lemonde.fr": "editorial",
    "vogue.fr": "editorial",
    "vogue.it": "editorial",
    "vogue.es": "editorial",
    "vogue.de": "editorial",
    "grazia.it": "editorial",
    "gqitalia.it": "editorial",
    "elle.com.br": "editorial",

    # Skipped (not added) this run, all researched but not clearing the
    # bar, or found not to be fashion sources at all:
    # ipowerrichmond.com -- WebSearch shows this is iPower 92.1/104.1 FM,
    # a Richmond VA hip-hop/R&B radio station, not a fashion source at
    # all. wkzo.com -- a Kalamazoo, Michigan AM/FM talk radio station
    # (conservative syndicated programming), also not a fashion source at
    # all. uraniumwaves.com (carried forward from run 96, re-verified run
    # 100) -- an independent Canadian music label/blog (artist submissions,
    # mixing/mastering services, merch store), not a fashion source.
    # cafedelhomme.com (carried forward from run 98, re-verified run 100)
    # -- Cafe de l'Homme, a high-end Paris restaurant at the Trocadero, not
    # a fashion source. All four are the same wrong-domain pattern: a
    # plausible-sounding domain that turns out to be an unrelated business.
    # outfittrends.com -- a 2009-founded "outfit ideas" content site with a
    # rotating team of non-journalist contributors (doctors/teachers/
    # engineers writing style posts) and shopping-guide framing; ambiguous,
    # left unclassified rather than forced.
    # yahoo.com -- a general news/search portal aggregating wire and
    # syndicated content across many verticals under no single editorial
    # identity, unlike a staffed masthead; genuinely ambiguous the way
    # google.com is handled separately (visual_archive, a narrower usage
    # pattern) rather than a comparable case. Not a trade_intelligence fit
    # either -- it's a general consumer portal, not a B2B forecasting
    # vendor -- so the new sector doesn't resolve this one.
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
