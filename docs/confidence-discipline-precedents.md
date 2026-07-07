# Confidence-discipline precedents

This document consolidates every manual override/exception to the mechanical
`derive_confidence()` formula that report-writing agents have established across the
report archive (`data/reports/*.json`) and their working logs
(`docs/agent-logs/*.md`). It exists so future runs don't have to re-read dozens of old
logs to know what's already been decided.

## The mechanical formula (`src/report_schema.py::derive_confidence()`)

- **high** = `source_corroboration_count >= 2` AND sources span `>= 2` distinct
  `source_sectors`
- **medium** = `source_corroboration_count >= 2` from a single sector, OR
  `source_corroboration_count == 1` from a sector in `HIGH_RELIABILITY_SECTORS`
  (`editorial`, `designer_origin`, `institutional`, `independent_criticism` — the last
  added at run 19)
- **low** = everything else
- **archival** = manually flagged, passed through unchanged by the formula

Every precedent below is a case where an agent judged the mechanical output to be
wrong for the specific evidence and manually overrode it (`confidence_source:
"manual"`), with reasoning recorded in the report's `human_editor_note` and/or an
agent-log. None of these change the code — they are editorial judgment calls applied
on top of it, and later runs are expected to keep applying the same judgment to
structurally similar cases.

Ordered chronologically by first establishment.

---

### 1. A single source spanning multiple sectors is not independent corroboration

**First established:** pre-run-6, `docs/agent-logs/confidence-audit.md`, applied to
`data/reports/2026-07-13.json` signal `resale-growth`.

**Rule:** if the mechanical "2+ distinct sectors" test is satisfied only because one
underlying source got tagged under multiple sector labels (e.g. institutional framing
reused editorially), that is not real cross-sector corroboration — corroboration
requires genuinely separate sources, not one source's classification spanning
categories.

**Reasoning:** `confidence-audit.md`: "a single-source signal promoted to 'high' on
the strength of institutional/editorial framing rather than independent
corroboration."

**Worked example:** `resale-growth` in `2026-07-13.json`. Rather than downgrading, the
agent found a genuinely independent second source (GlobalData) — see
`docs/agent-logs/confidence-resolution.md`. Confidence was kept at the mechanically
correct tier once real corroboration existed, rather than left inflated on the
original single-source basis.

---

### 2. Republication within the same sector does not become cross-sector corroboration no matter how many outlets repeat it

**First established:** `data/reports/2027-01-25.json` (run 38), signal
`wales-bonner-hermes-debut`.

**Rule:** raw corroboration count going up is not the same as sector diversity going
up. If ten outlets cover a story but they're all `editorial`, the signal stays capped
at `medium` — it does not cross into `high` on volume alone.

**Reasoning:** `2027-01-25.json` `human_editor_note`: "confidence itself does not move
to high because all three are a single source_sector (editorial)."

**Worked example:** `wales-bonner-hermes-debut` was tracked across **8 consecutive
report windows** (2027-01-25 through 2027-03-08) with the same single-sector cap
applied identically each time, closed out compliant. The same discipline was then
applied to: `chanel-cruise-2027-biarritz-debut` (2027-05-03, "nine outlets, same
sector"), `royal-purple-color-trend` (2027-06-14), `blokecore-...` and
`tomato-red-color-trend` (2027-06-21), `wimbledon-tenniscore-polka-dot` (2027-06-28),
`couture-fw27-designer-debuts` (2027-07-05), and `margiela-raw-edge-retail-buy`
(2027-10-11, two retailers both mapping to `retail`).

---

### 3. An "unclear" domain-map gap must not be counted as a real distinct sector

**First established:** `data/reports/2027-05-24.json` (run 55), signal
`cannes-2027-architectural-red-carpet`.

**Rule:** `derive_confidence()` counts whatever `source_sectors` the domain map
resolved to. If most of those domains actually resolve to `"unclear"` (not yet mapped
in `taxonomy.py`'s domain-sector map), that is a taxonomy coverage gap, not genuine
sector diversity, and must not be allowed to mechanically produce `high`.

**Reasoning:** `2027-05-24.json` `human_editor_note`: "derive_confidence() would land
this at 'high' on raw corroboration count (5 sources), but only two of those domains
... resolve to a mapped sector ... Holding this at 'medium' rather than overriding."

**Worked example / extended application:** the same "unclear" gap caveat was applied
across at least ten later signals through 2027-10-04 — `beaded-jewelry-revival`
(2027-06-07), `bubble-hem-revival` and `royal-purple-color-trend` (2027-06-14),
`blokecore-...`/`tomato-red-color-trend` (2027-06-21), `wimbledon-tenniscore-polka-dot`
(2027-06-28), `couture-fw27-designer-debuts` (2027-07-05),
`ragebait-runway-casting` (2027-08-09), `chanel-acquires-charvet` (2027-08-16),
`martens-margiela-debut` (2027-08-23), `gucci-demna-debut-reception` (2027-08-30),
`pfw-ss28-calendar-confirmed` (2027-09-06), `margiela-raw-edge-tailoring-preview`
(2027-09-20), and `margiela-raw-edge-retail-buy` (2027-10-04). A related edge case,
`lv-waterfall-heatwave-backlash` (2027-07-26), had *all five* sources resolve to
`unclear` and was held at medium on the same basis.

**Important companion ruling — taxonomy fixes are not retroactive:**
`docs/agent-logs/confidence-recompute-2027-09-06-run72.md` explicitly considered
whether closing the domain-map gap (adding `fhcm.paris`/`laforma.club` to
`DOMAIN_SECTOR_MAP`) should retroactively flip a past confidence call to `high`, and
concluded it should not — a later taxonomy expansion does not retroactively re-derive
a substantive editorial judgment made under the taxonomy as it stood at the time.

---

### 4. A downstream reprint/aggregator republishing a primary source is not independent second-sector confirmation

**First established:** `data/reports/2027-04-12.json` (run 49), signal
`glamoratti-revival`.

**Rule:** if a "new" corroborating outlet is really an SEO/content-marketing site
re-describing the same underlying primary source (rather than independently
reporting/confirming the fact), counting it as corroboration rewards volume of
reprinting, not additional evidence, and must not raise the confidence tier.

**Reasoning:** `2027-04-12.json` `human_editor_note`: "the new outlets here are
downstream SEO/content-marketing sites re-describing the same Pinterest Predicts data
point ... Counting republication as corroboration [would reward volume of reprinting,
not additional evidence]."

**Worked example:** most fully reasoned instance is
`docs/agent-logs/confidence-recompute-2027-09-06-run72.md`, re: signal
`pfw-ss28-calendar-confirmed` (`data/reports/2027-09-06.json`) — `laforma.club` had
"independently republished" `fhcm.paris`'s own announcement of the same fact. This was
explicitly distinguished from genuine cross-sector corroboration even after a taxonomy
fix would have mechanically produced `high` (see precedent 3's companion ruling).

---

### 5. The `independent_criticism` high-reliability exception covers genuine independent reporting, not a citation-free rehash

**First established:** `data/reports/2027-11-08.json` (run 78), signal
`bogota-waist-tailoring-independent-criticism-synthesis`.

**Rule:** `independent_criticism`'s membership in `HIGH_RELIABILITY_SECTORS` (added
run 19) exists to let one genuinely independent piece of critical reporting register
at `medium` on its own. It does not extend to a piece that is a citation-free
rehash/synthesis of material already logged from other sectors in the same signal
thread — that gets manually held down to `low`.

**Reasoning:** `2027-11-08.json` `human_editor_note`: "the HIGH_RELIABILITY_SECTORS
exception exists for genuine independent [reporting], not a citation-free rehash" —
manually overridden `medium` → `low`, `confidence_source: "manual"`.

**Worked example:** re-applied verbatim, citing this exact precedent, at
`opera-gloves-awards-season-independent-criticism-synthesis`
(`data/reports/2027-11-29.json`, run 81): "manually overridden down to 'low' ... for
the same reason [as] the 2027-11-08 Dieworkwear entry."

**Boundary cases confirming genuine independent reporting is NOT downgraded:**
- `margiela-raw-edge-critical-reception` (`2027-10-11.json`, run 74, dieworkwear.com) —
  adopted at `high` as computed, no override.
- `bogota-waist-tailoring-designer-intent-bof` (`2027-11-15.json`, run 79) — BoF's own
  interviews, explicitly contrasted against the 2027-11-08 Dieworkwear override as the
  "genuine" case.
- `resort-2028-obi-sash-cocoon-coat` (`2027-12-06.json`, run 82) — Vogue's account
  judged "not a citation-free rehash of Chanel's lookbook," left uncorrected.

---

### 6. Same-week co-occurrence of two distinct signals is not cross-sector corroboration between them

**First established:** `data/reports/2027-11-22.json` (run 80), signal
`opera-gloves-awards-season-editorial`.

**Rule:** if two related but analytically distinct signals happen to surface in the
same collection window, that timing coincidence must not be treated as one signal
corroborating the other. Each signal's confidence is derived from sources that
actually address it, not from a sibling signal that merely occurred the same week.

**Reasoning:** `2027-11-22.json` `human_editor_note`: "net-a-porter.com's stocking
increase (logged separately below) occurred in the same window, it is a different
sector's independent claim, not corroboration of Vogue's specific styling framing, so
cross-sector corroboration of this signal itself does not yet exist."

**Worked example:** documented at the changelog level too —
`docs/changelog-entries/run-80.md`: "A new opera-gloves awards-season thread split
into two distinct signals ... with their same-week co-occurrence correctly NOT treated
as cross-sector corroboration between them."

---

### 7. A nominal sector tag can mislabel what's really the same underlying sector — check the actual sourcing, not just the tag

**First established:** `data/reports/2027-06-07.json` (run 57), signal
`sleepwear-as-outerwear-relaxed-tailoring`.

**Rule:** a source tagged `runway` or `designer_origin` may really be an editorial
outlet describing a runway show secondhand, not an independent designer-origin
statement. The mechanical sector count should be checked against what the source
actually is, not the label alone — cross-sector diversity can be thinner in practice
than the raw tag count implies.

**Reasoning:** `2027-06-07.json` `human_editor_note`: "the runway sector citation here
is really editorial outlets describing runway shows secondhand ... not an independent
designer-origin statement, so the cross-sector diversity is thinner in practice than
the raw tag count implies."

**Worked example:** reinforced at `royal-purple-color-trend` (`2027-06-14.json`, run
58): "all three corroborating sources are editorial synthesis pieces reporting on
those shows rather than independent designer-origin statements."

---

### 8. Commercial/service-journalism verticals get an extra discount even within "editorial"

**First established:** `data/reports/2027-06-07.json` (run 57), signal
`beaded-jewelry-revival`.

**Rule:** outlets/verticals that also run shopping-recommendation or service content
(e.g. jewelry/beauty service verticals within otherwise-editorial outlets) carry a
higher risk that "trend" coverage is partly commercially motivated. Even when the
mechanical formula computes `high` (count 4, 2+ sectors), this is a reason to hold the
signal at `medium`.

**Reasoning:** `2027-06-07.json` `human_editor_note`: "three of the four corroborating
outlets ... are enthusiast/service-jewelry verticals within the same outlets that also
run shopping-recommendation content, which raises the risk that 'trend' coverage here
is partly commercial."

---

### 9. Signals driven by an external calendar event are held down until tracked past that event

**First established:** `data/reports/2027-06-21.json` (run 59), signal
`blokecore-world-cup-jersey-styling`.

**Rule:** a signal whose entire discourse volume is calendar-driven by an external
event (a sporting tournament, an awards ceremony) has genuinely unknown durability
until it's been tracked past the event's conclusion. This is a reason to hold
confidence down independent of raw corroboration count/sector spread.

**Reasoning:** `2027-06-21.json` `human_editor_note`: "the entire signal is
calendar-driven by an external sporting event rather than an independent
fashion-cycle development — real discourse, but its durability is genuinely unknown
until it's tracked past the tournament."

---

### 10. General-news/wire-syndicated pickup is not fashion-trade-press corroboration

**First established:** `data/reports/2027-07-26.json` (run 64), signal
`lv-waterfall-heatwave-backlash`.

**Rule:** coverage from general/broadcast news or wire syndication (not fashion trade
press) is treated as thin, single-sector-equivalent corroboration even if it
technically spans multiple outlets — it is not treated as validating the story the way
genuine trade-press coverage (Vogue/WWD/BoF) would.

**Reasoning:** `2027-07-26.json` `human_editor_note`: sources were general-news/
broadcast/wire (SBS, WION, an AP affiliate), explicitly not fashion trade press;
treated as thin corroboration (all resolving to `unclear`) rather than genuine
trade-press validation, while noting that the absence of trade-press pickup is itself
a meaningful data point.

---

### 11. Attention-economics/casting discourse is a categorization call, not automatically a style signal

**First established:** `data/reports/2027-08-09.json` (run 65), signal
`ragebait-runway-casting`.

**Rule:** coverage about the attention economics of a casting decision is not, by
itself, coverage of a garment, silhouette, or aesthetic the brand designed. This is a
categorization judgment distinct from confidence tier — don't fold "industry discourse
about fashion" into a style-signal frame just because it's fashion-adjacent and well
corroborated.

**Reasoning:** `2027-08-09.json` `human_editor_note`: "this is coverage about the
attention economics of casting, not about a garment, silhouette, or aesthetic the
brand designed. Folding it under a style signal would misrepresent it." (Its
confidence tier itself was separately held at `medium` under precedent 3, `unclear`
domains.)

---

### 12. Structured/controlled-vocabulary fields are correctable retroactively; editorial prose fields are not

**First established:** `docs/agent-logs/godet-skirt-backfill-decision-run68.md` (run
68), re: `data/reports/2026-07-20.json`.

**Rule:** garment/silhouette tags and other controlled-vocabulary structured fields are
treated as data to be kept internally consistent, and can be corrected retroactively
if found wrong. `human_editor_note`/`evidence` prose fields, by contrast, are never
retroactively rewritten to reflect later editorial judgment — they're a preserved
record of what the agent reasoned at the time, even if it's since been superseded or
found imperfect.

**Reasoning/example:** `docs/agent-logs/human-editor-note-quality-audit-run49.md`
found two verbatim-duplicate `human_editor_note` entries (`2026-07-13.json` and
`2026-11-09.json`) and explicitly declined to rewrite them, instead flagging them for
a human/future run to consider. This governs precedent 4's reasoning in
`confidence-recompute-2027-09-06-run72.md` (a taxonomy/structured-data fix does not
license rewriting a past prose judgment call).

---

### 13. Resale-platform sourcing reflects supply/discard behavior, not demand, and a platform's own "trending" framing does not become genuine demand corroboration just because corroboration count rises

**First established:** `data/reports/2027-12-20.json` (run 84), signal
`bogota-waist-tailoring-resale-holiday-demand`, flagged as an open candidate in that
report's `limitations` field; formalized here at run 85 after dedicated research
(`docs/agent-logs/resale-platform-precedent-research-run85.md`).

**Rule:** `resale` (`therealreal.com`, `vestiairecollective.com`, `depop.com`,
`grailed.com`, `poshmark.com` in `taxonomy.py`'s `DOMAIN_SECTOR_MAP`) is deliberately
**not** in `HIGH_RELIABILITY_SECTORS`, and this precedent affirms that placement rather
than overriding it. Two independent reasons compound, both grounded in how resale
platforms are actually used in trade coverage rather than in trend forecasting proper:

1. **Resale listing/sell-through volume is a supply-side/discard signal, not a
   demand signal.** What appears on a resale platform reflects what current owners
   are choosing to part with, which correlates with novelty-seeking and rapid
   turnover as much as with rising demand for a look. Treating "items in category X
   are being resold at volume" as equivalent to "category X is newly desired"
   conflates the two.
2. **A resale platform's own "trending"/demand-signal framing (a marketing page,
   press-cited internal trend report, or self-reported search/sell-through spike) is
   self-promotional in the same way Pinterest's own Trends/Predicts reports are
   (`docs/manual-sampling-workflow.md`'s "platform marketing is not organic signal"
   rule) — it is the platform's own commercial interest describing its own inventory,
   not a neutral third party measuring demand.

Because of this, `resale`-sector corroboration should be held at the mechanically
correct tier or lower, and should **not** be manually upgraded even in a future case
where a resale-sector signal happens to reach `count >= 2` from a single sector
(mechanically "medium" under the formula) — that is two supply-side listings/reports,
not demand evidence, and the same discount applies at that tier too. A resale signal
should only be treated as confirming genuine demand once corroborated by a
demand-side source (search/interest data, a non-resale retailer's sell-through or
waitlist figures, or editorial/independent-criticism coverage of the demand itself),
consistent with how other single/thin-sector cases here require genuine independent
corroboration rather than volume within one sector (precedents 2, 8).

**Reasoning:** research conducted for this precedent
(`docs/agent-logs/resale-platform-precedent-research-run85.md`) found the trade
literature genuinely split: some resale-analytics vendors market resale listing data
as a *leading* indicator of upcoming primary-market trends, while separate consumer-
behavior research found secondhand purchasing supplements rather than substitutes for
new purchasing, and that frequent secondhand buyers discard items faster in pursuit of
novelty — i.e., a resale spike can just as plausibly reflect people discarding a look
as it can reflect people newly wanting it. Given that split evidence, holding the
mechanical low/medium tier rather than inventing an upward override is the correct
conservative call, not a decided fact that resale data is worthless.

**Worked example:** `bogota-waist-tailoring-resale-holiday-demand`
(`data/reports/2027-12-20.json`, run 84): `therealreal.com`, `corroboration_count=1`,
`confidence=low`, `confidence_source=derived`. Left as computed; the mechanical "low"
was correct and no exception was invented, per the reasoning above.

---

### 14. A forecast/prediction about a future season is not evidence of a present signal, unless independently-converging forecasting activity itself becomes the (narrowly framed) event

**First established:** implicitly at `data/reports/2026-12-28.json` (year-end
window, forward-looking "2026 trends" listicles excluded from a "best of
2026" retrospective search); flagged as a candidate precedent at
`data/reports/2028-01-03.json`/`docs/agent-logs/real-report-2028-01-03.md`
(run 86, WWD/Vogue 2028 year-ahead forecast pieces); formalized here at run 88
after dedicated review (`docs/agent-logs/forecast-exclusion-precedent-run88.md`).

**Rule:** a trend-forecast or prediction piece about a *future* season is not,
by itself, evidence of designer intent, editorial interpretation of existing
work, retail adoption, or social amplification that has actually occurred —
it is a claim about the future, not an observation about the present, and
must not be folded into `top_signals` as if it were an observed trend. None
of `taxonomy.py`'s `origin_classification` values (`designer_originated`,
`editorial_amplified`, `retail_adopted`, `social_amplified`,
`platform_native`, `archive_revival`) fit a pure forecast piece either — all
six presuppose an aesthetic that has already manifested somewhere and is
being amplified/adapted from that point; a forecast has no such antecedent
event to amplify, so this is a genuine taxonomy gap, not a case of failing to
look hard enough for the right label.

A narrower carve-out exists but has never yet been triggered: if multiple
genuinely independent trade outlets converge on the *same specific*
prediction in the same window (not one wire/PR feed reaching multiple
outlets — precedent 4's downstream-republication logic applies), the
convergence itself is a present-tense discourse event (outlets responding to
this week's signals and reaching the same read) distinct from the
speculative content of the prediction. Logging that would require framing it
explicitly as coverage of the forecasting activity itself ("N outlets
forecast X this week," a fact about now), never as though the forecast's
content were an observed trend, and it still could not carry a
garment/silhouette/aesthetic `top_signals` entry implying present adoption.
No new `origin_classification` enum value has been added for this
hypothetical case — inventing one is not warranted until it actually occurs.

**Reasoning:** `docs/agent-logs/forecast-exclusion-precedent-run88.md`: two
independent agents a year apart (`2026-12-28.json`, `2028-01-03.json`)
reached the identical exclusion without coordination, which is itself
evidence the underlying judgment is sound and durable rather than
inconsistent improvisation — exactly the "flagged once, formalized after
review" shape precedent 13 also followed.

**Worked example:** `data/reports/2028-01-03.json` (run 86): two outlets
(wwd.com, vogue.com) each ran separate 2028 year-ahead forecast pieces the
same window. Recorded as collected (`items_collected: 2`,
`source_sector_breakdown: {"editorial": 2}`) but excluded from
`top_signals`, with `top_signals: []` and `collection_status: "thin"`. This
is exactly two outlets, not independently-converging-on-the-same-specific-
prediction, so the narrower carve-out above does not apply — plain exclusion
was the correct call. `data/reports/2026-12-28.json` (run in the archive's
first year): explicitly searched for genuine dated year-end retrospective
coverage, found only "generic forward-looking '2026 trends' pieces with no
publication date tying them to this window or framing them as a retrospective
of the year just ending," and excluded them on the same reasoning, a year
before run 86's case.

---

### 15. A signal whose content is a claim about a relationship between two other already-logged signals ("editorial synthesis") is a distinct category, gated by stricter requirements than an ordinary multi-source signal, and must never retroactively touch the signals it references

**First established:** `data/reports/2028-03-20.json` (run 97), signal
`fw28-season-wrap-unfinished-edge-editorial-synthesis`, flagged as a candidate in
that report's `limitations` field; formalized here at run 98 after dedicated review
(`docs/agent-logs/editorial-synthesis-precedent-run98.md`).

**Rule:** an "editorial synthesis" signal is one whose evidentiary content is not a new
garment/aesthetic observation but a *claim of relationship* between two (or more)
signals that already exist as their own logged `signal_id`s in the archive. This is a
different, stronger kind of claim than an ordinary observation, so logging it requires
clearing a gate first, not just running it through `derive_confidence()` directly:

1. **Both/all referenced antecedent signals must already exist as their own logged
   `signal_id`s, independently sourced and confidence-tiered before the synthesis piece
   appeared.** A "connection" drawn between one archived fact and a claim invented in
   the same wave of coverage is not synthesis of prior signals — see precedent 1's
   "one source's classification spanning categories is not two sources," applied here
   to signals rather than sectors.
2. **At least two outlets must independently perform the synthesis, and neither may
   cite the other for the connective claim itself.** If one synthesis piece credits or
   links to the other for the cross-signal read, that is precedent 4's downstream-
   reprint case applied to the synthesis layer, and it must be logged as a
   single-source synthesis claim, not independently-converged synthesis.
3. **The synthesis must cite the underlying archived facts, not merely assert the
   pattern.** A piece asserting a trend without naming the specific prior
   garments/shows being connected is an ordinary trend-observation piece, evaluated on
   its own terms (including precedent 5's citation-free-rehash test), not a synthesis
   signal.

**Two illegitimate patterns to check for explicitly, not assume away:**

- **A single outlet's opinion piece dressed up as a discovered pattern** — caught by
  requirement 2. A solo synthesis piece may still be logged as its own signal, but never
  at more than single-source-equivalent confidence, and its `index_note` must state
  plainly the pattern claim is one outlet's read, not a corroborated observation.
- **A single house's PR narrative echoed by two outlets** — precedent 5's citation-free-
  rehash logic applied to the synthesis layer. If both outlets' "independent" synthesis
  actually traces to the same seeded talking point (a lookbook press note, a designer
  interview asserting the lineage first, a stylist's framing distributed to press),
  that is one source wearing two bylines, not independent editorial judgment, and must
  be manually held down (e.g. to `low`), the same mechanism precedent 5 used for the
  Dieworkwear/opera-gloves overrides. The test is whether each outlet independently
  argued the connection from the archive facts themselves, versus each reporting a
  connection a design house's own communications asserted first.

**Confidence still runs through the normal formula and precedent 2 once the gate is
cleared:** two outlets independently synthesizing is still two sources in one sector
(`editorial`) unless a genuinely distinct sector also corroborates the same connective
claim — precedent 2's "volume within one sector does not become cross-sector
corroboration" applies at the synthesis layer exactly as at the observation layer.

**Retroactivity: original signals are never touched.** A synthesis signal must not
retroactively edit, tag, or re-tier the antecedent signals it references — no added
`archive_tags`, no prose edit to `human_editor_note`/`evidence`/`index_note`, no
confidence or classification change on the original signal records. This extends
precedent 12 (structured fields correctable, prose fields never retroactively rewritten
to reflect later judgment): the antecedent signals' prose is a preserved record of what
was known and reasoned at their own authoring time, and rewriting it to reflect a later
discovered connection would make that historical record look more prescient than it
was. The synthesis signal's own record (its own `signal_id`, `evidence` field naming
both antecedents, and its own `/signals/[slug]` page) is sufficient for the connection
to be discoverable via archive/search/timeline surfaces without altering either
original entry.

**Reasoning:** `docs/agent-logs/editorial-synthesis-precedent-run98.md` — checked
carefully against precedent 4 (does not apply: the two outlets are not restating each
other's reporting of the same fact, they are independently performing the same
analytical act) and precedent 6 (does not apply: this is not two signals coincidentally
co-occurring in the same window, it is one new signal whose entire content is an
explicit claim of relationship between two prior signals). Neither precedent, nor any
of the other 13, states a rule for a signal whose subject is a relationship between two
other archived signals, confirming a genuine categorization gap rather than a case
already covered by careful reading.

**Worked example:** `fw28-season-wrap-unfinished-edge-editorial-synthesis`
(`data/reports/2028-03-20.json`, run 97): wwd.com and vogue.com each independently
published a season-wrap piece connecting the already-logged
`miu-miu-raw-hem` signal (2028-03-13) and the closed-out `margiela-raw-edge` thread
(2027-10-18) into a claimed recurring unfinished-edge construction idiom. Passes all
three gate requirements (both antecedents pre-existing and independently sourced;
neither outlet cites the other for the connective claim; both cite the underlying
runway lookbooks/reviews directly) and shows no sign of the PR-echo pattern. Correctly
kept as its own distinct `signal_id` (not merged into either antecedent), correctly
capped at `medium` under precedent 2 (both sources resolve to `editorial`), and
correctly left the Miu Miu and Margiela report entries completely unedited.

---

### 16. Prose must never describe a single-outlet signal's sourcing in the plural

**First established as an audit finding:** `docs/agent-logs/journalism-standards-check-run71.md`
(spot-check only, not previously codified as a durable rule); formalized here at run 99
after dedicated journalism-standards benchmarking research
(`docs/agent-logs/journalism-standards-review-run99.md`).

**Rule:** `evidence`/`human_editor_note`/`index_note` prose must never describe a signal
backed by `source_corroboration_count == 1` using plural language ("sources report...",
"outlets are covering...") — attribution language must match the actual number of
independent outlets behind a claim. This is a prose-discipline companion to precedent 1
(a single source spanning multiple sector tags is not real corroboration): precedent 1
governs the mechanical confidence tier, this rule governs how the sourcing is *described*
in prose, independent of what tier it lands on.

**Reasoning:** Reuters' published sourcing conventions state plainly that a report should
never "cite sources in the plural when only one source exists" — treated as a core
sourcing-integrity rule, not a stylistic nicety, because inflating apparent corroboration
in the prose itself misleads a reader even when the structured `confidence` field is
correct. ([Reuters Handbook of Journalism](https://www.mediareform.org.uk/wp-content/uploads/2015/12/Reuters_Handbook_of_Journalism.pdf))

**Status:** run 71's spot-check of the two most recent reports at the time found this
already being followed in practice. This entry exists so the rule is checkable going
forward against the actual written record rather than re-verified informally each time —
per this project's own recurring "documented once in an agent-log, never carried into the
durable ruleset" bug class (SKILL.md workflow convention #9's underlying pattern, applied
here to a prose convention rather than a schema field).

---

## Related, non-override background (for context, not confidence exceptions themselves)

- **`independent_criticism` added to `HIGH_RELIABILITY_SECTORS`** — proposed
  `docs/agent-logs/bias-audit-run16.md`, reinforced `docs/agent-logs/bias-audit-run18.md`,
  implemented run 19. Structurally unreachable in practice until `dieworkwear.com` was
  added to `FASHION_SOURCES` at run 54
  (`docs/agent-logs/independent-criticism-source-investigation-run54.md`). This is a
  formula change (not a manual override), but precedents 5 and 9 above only make sense
  in light of it.
- **3-consecutive-quiet-window dormancy close-out threshold** — established
  2026-08-24, `docs/agent-logs/confidence-dormancy-review-run15.md` and `-run23.md`
  (`sheer-layering`, `soft-tailoring`, `off-duty-varsity`, `peplum-waist-revival` all
  closed after 3 consecutive quiet windows). This governs when a signal is retired
  entirely, not what confidence tier it gets — a sibling discipline to the precedents
  above, not itself a confidence-derivation exception.
- **Domain-map coverage expansions** (`docs/agent-logs/domain-classification-run56.md`,
  `-run70.md`, `source-diversity-expansion*.md`, `source-diversity-research-run73.md`)
  are the mechanism that periodically shrinks precedent 3's "unclear" gap over time —
  context for why that pattern recurs and then partially resolves, not a precedent of
  its own.
