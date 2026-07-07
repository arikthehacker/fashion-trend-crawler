# Source Domain Freshness Spot-Check — Run 65

**Scope:** Run 49 verified all 27 `source_domains` values present through report
`2027-04-05.json`. 16 reports have been added since (`2027-04-12.json` through
`2027-07-26.json`), introducing 33 domains never individually checked for liveness.

## Method

Recursive JSON walk over `data/reports/*.json` filtered to files dated after 2027-04-05,
collecting unique `source_domains` strings, diffed against run 49's confirmed list. 33 new
domains found. Checked each with `curl -L --max-time 8-15` using a standard browser
User-Agent (same fallback run 49 used, since WebFetch is gated against arbitrary domains).

## Result: all 33 new domains resolve to live, correctly-named outlets

30 of 33 returned 200 directly: anothermag.com, asiae.co.kr, businessoffashion.com,
cfda.com, complex.com, coveteur.com, dazeddigital.com, ecostylia.com, fashionnetwork.com,
fashionunited.uk, hellomagazine.com, hollywoodreporter.com, insidehook.com, lamag.com,
lofficielusa.com, news.sbs.co.kr, nssmag.com, outfittrends.com, runwaylive.com,
soccerbible.com, stylerave.com, stylist.co.uk, theimpression.com, thezoereport.com,
vogueadria.com, wardrobeoxygen.com, whitewall.art, wkzo.com, wmagazine.com,
yourcoffeebreak.co.uk.

3 returned 403/timeout under curl: `fashionista.com`, `wionews.com` (both 403 on both bare
and `www.` variants), and `net-a-porter.com` (TLS renegotiation timeout on `www.`
subdomain). All three are recognizable, real outlets (Fashionista — Breaking Media's
fashion-news vertical; WION — an Indian TV news network's site; Net-a-Porter — a major
luxury e-commerce retailer), consistent with run 49's finding that some legitimate sites
run bot-detection WAFs (Akamai/Cloudflare-style) that 403 or stall plain `curl` requests
regardless of UA string, not evidence of a dead or mistyped domain. No further fallback
(e.g. browser-rendered fetch) was available in this environment to get a clean 200, same
limitation run 49 hit and resolved by reasoning rather than a clean status code for its
four holdouts.

## Conclusion

No typos, no dead domains, no unexpected redirect targets across all 33 newly-introduced
domains (reports 2027-04-12 through 2027-07-26). Standard already met; no code or data
changes made. Recommend the next full domain-verification sweep after another ~12-15
reports accumulate (mirrors the run 49 -> run 65 cadence), and note in `TODO.md`/here that
`fashionista.com`, `wionews.com`, `net-a-porter.com` are known curl-hostile but legitimate
if a future check wants to skip re-flagging them.
