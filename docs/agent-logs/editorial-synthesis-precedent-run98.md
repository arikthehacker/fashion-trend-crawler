# Editorial-synthesis-of-prior-signals precedent review (run 98)

## Task

Run 97's `data/reports/2028-03-20.json` logged
`fw28-season-wrap-unfinished-edge-editorial-synthesis`: wwd.com and vogue.com
each independently published a season-wrap piece drawing the same cross-house
comparison between the already-archived Miu Miu raw-hem signal
(2028-03-13) and the already-closed Margiela raw-edge thread
(2027-10-18), reading them together as a recurring unfinished-edge
construction idiom. The report flagged this as a candidate 15th precedent
because no existing precedent addresses a signal whose *content* is a claim
about a relationship between two other already-logged signals, rather than a
claim about a garment/aesthetic itself. This log does the actual precedent
review the run 97 report asked a future agent to do.

## 1. Is there a genuine gap, or does this reduce to an existing precedent?

Checked against the two precedents run 97 explicitly distinguished from,
plus the rest of the doc:

- **Precedent 4 (downstream reprint is not independent corroboration).**
  Does not apply here. Precedent 4 is about a *second outlet restating a
  first outlet's own reporting of the same fact* (fhcm.paris announcement,
  laforma.club republishing it). Here, WWD and Vogue are not restating each
  other's copy about the *same* fact — each is independently performing the
  same *analytical act* (comparing two separate archive entries and drawing
  a relationship). That's a different thing from reprinting: two people
  independently noticing the same pattern in data they can both see is not
  one of them copying the other's writeup. Precedent 4's test (does source B
  add reporting, or just restate source A's) is the right lens, but it
  answers "yes, independent" here, it doesn't classify the pattern.

- **Precedent 6 (same-week co-occurrence of two distinct signals is not
  cross-signal corroboration).** Does not apply either, and for a
  precise reason worth stating plainly: precedent 6 governs two signals that
  merely *co-occur in the same window* with no claimed relationship between
  them (opera-gloves editorial framing + net-a-porter stocking increase,
  same week, unrelated claims). The new signal here is not two signals
  coincidentally occurring together — it is a *single new signal* whose
  entire evidentiary content *is* an explicit claim of relationship between
  two prior signals, sourced independently by two outlets. Precedent 6 would
  apply if a future agent were tempted to treat the Miu Miu and Margiela
  signals as *corroborating each other*; that's not what happened here, and
  the run 97 report correctly kept them as three distinct signal_ids rather
  than merging or cross-corroborating any pair.

- **Precedent 5 (independent_criticism exception is for genuine
  independent reporting, not citation-free rehash)** and **precedent 1 (one
  source spanning multiple sector tags isn't real corroboration)** are the
  closest analogues in spirit — both are about distinguishing genuine
  independent judgment from something dressed up to look like it — but
  neither's *rule* covers a signal whose content is a claim about a pattern
  across two other signals. They inform the boundary conditions below but
  don't resolve the categorization question by themselves.

- **Precedent 14 (forecast exclusion)** was already correctly checked and
  ruled out by run 97 (backward-looking interpretation of shows that already
  happened, not a claim about a future season). Re-confirmed here — not
  relevant to the gap question, just correctly cleared.

None of the 14 precedents, individually or combined, states a rule for *a
signal whose subject matter is a relationship between two other archived
signals*, as opposed to a rule for *how many/what kind of sources support a
single observational claim*. That's a real categorization gap, not just an
unindexed case of an existing rule. Verdict: **genuinely novel — formalize
precedent 15.**

## 2. Boundary conditions: legitimate synthesis vs. illegitimate synthesis

A synthesis signal is a claim about a *pattern*, which is a stronger kind of
claim than an observation, so it needs a higher bar than an ordinary signal,
not the same bar. Working through what actually distinguishes the
legitimate case from the illegitimate ones named in the task:

**Required, all of the following, to log a synthesis signal at all
(gate, not a confidence adjustment):**

1. **Both/all referenced antecedent signals must already exist as their own
   logged `signal_id`s in the archive**, each independently sourced and
   confidence-tiered *before* the synthesis piece appeared. If the
   "connection" is being drawn between one archived fact and one thing that
   only exists because this same wave of coverage asserted it, this isn't
   synthesis of prior signals, it's just a new single-sector signal
   dressed up with an extra citation. (This is precedent 1's logic —
   "one source's classification spanning categories is not two sources" —
   applied to signals instead of sectors: one *new* claim citing itself
   twice is not two antecedent facts.)

2. **At least two outlets must independently perform the synthesis, and
   neither may cite the other for the connective claim itself** — i.e. the
   comparative/pattern claim (not the underlying facts, which may of course
   both cite the same runway shows) must be arrived at separately. If outlet
   B's synthesis piece links to or credits outlet A's synthesis piece for
   the cross-house read, that is precedent 4's downstream-reprint case
   applied to the synthesis layer, and it must be logged as a single-source
   synthesis claim (effectively `corroboration_count=1`), not as
   independently-converged synthesis.

3. **The synthesis must cite the underlying archived facts, not just
   assert the pattern.** A piece that says "there's a raw-edge trend this
   season" without naming the specific prior garments/shows being connected
   is not synthesis of logged signals — it's an ordinary trend-observation
   piece and should be evaluated as one (and checked against precedent 5's
   citation-free-rehash test on its own terms).

**Explicitly named illegitimate patterns to watch for, matching the task's
examples:**

- **A single outlet's opinion piece dressed up as a discovered pattern.**
  Caught by requirement 2 (needs 2+ independently-arrived-at instances).
  A solo synthesis piece may still be logged as its own signal if it clears
  the normal bar for a single-source claim, but never as a "recurring idiom
  across houses" pattern-signal at more than `low`/single-source-equivalent
  confidence, and its `index_note` must say plainly that the pattern claim
  is one outlet's read, not a corroborated observation.

- **A single house's PR narrative echoed by two outlets.** This is
  precedent 5's citation-free-rehash logic, applied to the synthesis layer:
  if both outlets' "independent" synthesis actually traces back to the same
  seeded talking point (a lookbook press note, a designer interview
  quote asserting the lineage themselves, a stylist's framing distributed to
  press), that is one source wearing two bylines, not independent editorial
  judgment, and must be held down accordingly (manual override to `low`,
  same mechanism precedent 5 used for the Dieworkwear/opera-gloves case).
  The test: did each outlet independently notice/argue the connection from
  the archive facts themselves, or did each outlet report a connection that
  a design house's own communications asserted first? The run 97 case
  passes this test as documented (`human_editor_note` states neither piece
  cites the other and each cites the underlying runway lookbooks/reviews
  independently) but this must be checked explicitly every time, not
  assumed from outlet reputation.

- **Confidence ceiling stays capped by precedent 2 regardless of how the
  synthesis was reached.** Two outlets independently synthesizing is still
  two sources in one sector (`editorial`) unless a non-editorial sector
  (e.g. `designer_origin` confirming the lineage, or `independent_criticism`
  under precedent 5's genuine-independent-reporting carve-out) also
  corroborates the same connective claim. Precedent 2's "volume within one
  sector does not become cross-sector corroboration" applies at the
  synthesis layer exactly as it does at the observation layer — run 97
  applied this correctly.

## 3. Should a synthesis signal retroactively touch the original signals it cites?

No. Original signals remain a frozen historical record; only the new
synthesis signal carries the cross-reference. Reasoning, extending
precedent 12 (structured fields correctable, prose fields never
retroactively rewritten to reflect later judgment):

- The Miu Miu and Margiela signals' `human_editor_note`/`evidence`/
  `index_note` prose is a preserved record of what was known and reasoned
  *at the time* those signals were logged (2028-03-13 and 2027-10-18
  respectively). Neither agent could have known in advance that a later
  synthesis piece would connect them. Rewriting that prose after the fact to
  say "later linked to X" would be exactly the kind of retroactive
  prose-rewrite precedent 12 forbids — it would make the historical record
  look more prescient/connected than it actually was at authoring time.
- This is different from precedent 3's companion ruling (a later taxonomy
  fix does not retroactively re-derive a past confidence call) only in
  degree, not in kind: both say the record of a past judgment stands as
  made, and new information is layered on as new records, not backfilled
  into old ones.
- A **structured, additive, non-destructive pointer** is a different
  question from rewriting prose, and is consistent with precedent 12's
  "structured fields are correctable" half — but the run 97 report already
  achieved the right effect without needing to touch the old signals at
  all: `signal_id: "fw28-season-wrap-unfinished-edge-editorial-synthesis"`
  is itself a new, independently-discoverable structured record that names
  both antecedents in its own `evidence` field, and `/signals/[slug]` page
  generation means anyone landing on the Miu Miu or Margiela signal pages
  can find this via the archive/search/timeline surfaces without either
  original record being touched. So the rule is: **do not add or edit
  fields on the original signals' report entries** (no retroactive
  `archive_tags` addition, no confidence/classification change, no prose
  edit) — the synthesis signal's own record is sufficient and keeps the
  frozen-record guarantee intact for every past report file.

## 4. Decision

**Formalized as precedent 15** in
`docs/confidence-discipline-precedents.md`, following the existing format
(First established / Rule / Reasoning / Worked example), using
`fw28-season-wrap-unfinished-edge-editorial-synthesis`
(`data/reports/2028-03-20.json`, run 97) as the first worked example. This
was not added reflexively just because run 97 flagged it as a candidate —
section 1 above shows precedents 4 and 6 were checked carefully and neither
resolves the categorization question, so the gap is real. The rule is
written narrowly (four gating requirements plus the two named illegitimate
patterns) so it applies only to signals whose content is itself a claim
about a relationship between two prior archived signals, not to ordinary
multi-source observational signals, which precedents 1-14 already cover.
