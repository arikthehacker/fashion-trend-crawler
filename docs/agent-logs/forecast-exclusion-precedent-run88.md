# Forecast-exclusion precedent review (run 88)

## Task

Run 86's `docs/agent-logs/real-report-2028-01-03.md` excluded two year-ahead
trend-forecast pieces (WWD, Vogue, both "2028 predictions" content) from
`top_signals`, reasoning that a prediction of future discourse is not evidence
of present designer intent, editorial interpretation, retail adoption, or
social amplification. It explicitly flagged this as a candidate 14th
precedent but declined to formalize it unilaterally. This run does the actual
thinking and makes a decision.

## The counter-argument, taken seriously

Is a widely-covered trade-press forecast itself a real "editorial
interpretation" event — the forecast existing and being covered is an actual
thing that happened this week, even if its predictive content is speculative?
Put concretely: is there a meaningful difference between

- (a) "Vogue says gingham will be big in 2028" (one outlet's speculative
  op-ed), and
- (b) "Three independent trade outlets (WWD, Vogue, BoF) all independently
  forecast the same specific trend the same week" (an industry-consensus
  event, arguably notable regardless of whether the prediction pans out)?

This is a real distinction, not a rhetorical one. (b) has a property (a)
number does not: independent convergence is itself observable, in-window
discourse — three outlets responding to the same underlying set of resort
collections, ad campaigns, or industry signals and reaching the same read.
That convergence is a fact about December 2027, not a claim about 2028.

## Does `origin_classification` already have a home for this?

Checked `src/taxonomy.py`'s `origin_classification` vocabulary:
`designer_originated`, `editorial_amplified`, `retail_adopted`,
`social_amplified`, `platform_native`, `archive_revival`. Every one of these
describes the origin of an aesthetic choice that has actually manifested
somewhere (a runway, a retail floor, a feed, an archive) and is being
picked up/amplified/adapted from that point. None of them describes "an
outlet's own forward-looking editorial judgment about what will manifest."
`editorial_amplified` specifically means editorial coverage amplifying an
aesthetic that a designer/retailer/platform already originated — it
presupposes an existing thing to amplify. A pure forecast piece has no
antecedent origin event to amplify; it *is* the origin, of a claim, not of a
look. So there is no clean existing slot for "the forecast itself, as a
discourse event" inside the current six-value enum — this is a genuine gap,
not a case of the agent failing to look hard enough.

## Prior practice check: has this project handled forecast/prediction content before?

Searched `data/reports/*.json` for `forecast`/`predict` and
`docs/agent-logs/` for the same.

- **`data/reports/2026-12-28.json`** (year-end window) is the clearest prior
  instance. Its `executive_summary` explicitly states the agent searched for
  "genuine, dated year-end 'best of 2026' retrospective coverage... distinct
  from evergreen or forward-looking 2026 trend-forecast listicles," found
  only forward-looking pieces with no retrospective framing, and treated
  those as **not qualifying** — logged as thin/no signal, same disposition
  as run 86's call. This was applied a full year before run 86's case and
  reached the same conclusion by the same reasoning, without ever being
  written down as a named precedent.
- `docs/agent-logs/forecast-calibration-check-run29.md` is a different thing
  entirely — it's about whether *this project's own* confidence/volatility
  labels are calibrated against later outcomes, not about whether to log
  external trend-forecast journalism. Not on point.
- No report anywhere in the 79-plus-file archive logs an external
  forecast/prediction piece as a `top_signals` entry or treats forecast
  convergence as its own signal type. Every touchpoint (2026-12-28, 2028-01-03)
  independently excluded forward-looking content.

So the practice is not "inconsistent" — it's consistently applied every time
it has come up, just never written down. Two independent agents, a year
apart, reached the identical judgment without coordination. That is itself
evidence the underlying reasoning is sound and durable, and exactly the kind
of repeated-but-undocumented judgment this precedents file exists to capture
(cf. precedent 13's own origin: flagged as a candidate in one report, then
formalized the next run after dedicated review — the same shape as this
case).

## Decision

Formalize **precedent 14**, with the boundary the counter-argument actually
earns:

1. **The core rule stands as run 86 applied it.** A forecast/prediction about
   a *future* season is not evidence of present designer intent, editorial
   interpretation of existing work, retail adoption, or social amplification,
   and must not be folded into `top_signals` as if it were an observed
   trend. This is now supported by two independent applications
   (2026-12-28, 2028-01-03) a year apart, not just one.
2. **The narrower carve-out the counter-argument surfaces is real but has
   never actually been triggered.** Multiple independent trade outlets
   converging on the same specific forecast in the same window is a
   different, narrower kind of event — the *existence and convergence of the
   forecasting activity itself* — and is not automatically excluded by this
   rule the way a single outlet's forward-looking op-ed is. But logging it
   would require: (a) genuine independent corroboration of the convergence
   itself (not one PR wire feeding multiple outlets — precedent 4's
   downstream-republication logic applies here too), and (b) framing it
   explicitly as coverage of a present discourse event ("three outlets
   forecast X this week," a fact about now) rather than smuggling it in as
   though the forecast's *content* were an observed trend. Even then, it
   could not carry a garment/silhouette/aesthetic `top_signals` entry
   implying present adoption — at most a distinctly labeled, narrowly scoped
   note about forecasting-activity-as-event. No existing `origin_classification`
   value fits this (see taxonomy gap above); inventing one is not warranted
   by a single hypothetical case, so this is recorded as an open boundary
   condition, not a new enum value.
3. **Applied to the actual 2028-01-03 facts:** two outlets (WWD, Vogue)
   ran separate forecast pieces the same week. That is exactly two, not
   the "multiple independently converging" case the carve-out requires, and
   run 86's report did not describe them as independently arriving at the
   *same specific* prediction — just as two outlets each doing their own
   year-ahead piece. So the carve-out does not apply here, and run 86's
   plain exclusion was the correct call under precedent 14, not an
   overcautious one.

Precedent 14 has been added to `docs/confidence-discipline-precedents.md`,
matching the existing numbered format (First established / Rule / Reasoning
/ Worked example), citing both the 2026-12-28 and 2028-01-03 instances and
the taxonomy-gap analysis above for the carve-out boundary.
