# Retention & versioning design — corrections vs. content_hash

Design proposal only — no code changed. Touches `src/report_schema.py` core logic
deliberately, per instructions.

## Research findings

**(a) Post-publication errors.** `web/app/methodology/page.tsx`'s existing "Corrections"
section (added last run) already states the right policy in prose: affected reports are
not silently edited, a dated correction note is appended, and the original entry is
preserved alongside it. This matches journalism convention (Ethics and Journalism, ONA
Ethics, Trusting News): corrections are always labeled as such, never euphemized as
"updates" or "fixes," and form a permanent, public part of the item's revision history —
not deleted or hidden after the fact.

**(b) Removal vs. retention.** SAA's *Guidelines for Reappraisal and Deaccessioning*
confirm archival science treats deaccessioning (removal) as a distinct, rare, documented
act separate from correction — done only for scope/duplication/legal reasons, always with
a record of what was removed and why, never as a way to erase an error. The general
convention for factual/classification errors is annotate, don't delete: the erroneous
state stays visible as part of the record's history.

**(c) Fixity/versioning for structured data.** Digital preservation practice (DPC/NDSA,
already cited in this project's `content_hash` implementation) ties fixity checksums to
an audit trail of preservation actions, not just a single current-state checksum. A
checksum alone tells you *whether* content changed; it doesn't tell you *when* or *why*.
For a corrected report, the old `content_hash` should be preserved as an audit-trail
entry, not overwritten and forgotten.

## The gap

`report_schema.py`'s `save_report()` (line 315) recomputes `content_hash` and overwrites
the file unconditionally on every call for a given date. There is no `revision_history`
field, so calling `save_report()` twice for the same date leaves no trace that anything
changed — this contradicts the Corrections section's own claim that "the original entry
is preserved alongside the correction."

## Recommendation

Yes — add a `revision_history: list` field to `Report`, populated by `save_report()`
itself when it detects it's overwriting an existing file with a different `content_hash`,
not left to callers to remember.

Sketch:

```python
revision_history: list = field(default_factory=list)
# each entry: {
#   "previous_content_hash": str,   # sha256 of the prior version
#   "corrected_at": str,            # ISO 8601 UTC timestamp
#   "reason": str,                  # required, human-authored, non-empty
# }
```

`save_report()` behavior change (design only, not implemented): before overwriting an
existing report file, load the old version; if its `content_hash` differs from the newly
computed one, require a non-empty `reason` argument and append an entry to
`revision_history` before writing. Raise if a correction is attempted with no reason —
mirrors the existing `human_editor_note` non-empty enforcement pattern in
`manual_sample.py`, so it's consistent with how this codebase already enforces
accountability fields.

This is a schema + `save_report()` change touching validation and the CLI/summarize
call sites, which is why it's deliberately deferred to a dedicated future run rather than
bundled here.
