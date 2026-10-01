# Schema capacity: a separate finding (2026-10-01)

**Status:** recorded only. The schema and Prompt v2 are unchanged, and no experiment has run.

## What happened

Fresh first-attempt schema validity was 2/5, and 3/6 with the q013 probe. Each failure took the one permitted retry, and every final output was valid.

| Question | First-attempt violation | Size of first attempt | Retry |
|---|---|---|---|
| q005 | 6 claims (cap 4) | claims 120–221 chars, 3 limitations | 4 claims, valid |
| q020 | claim 3 was 722 chars (cap 400), citing 7 items | other claims 134–250 chars | claim 3 was 349 chars, valid |
| q023 | limitation 0 was 333 chars (cap 300) | abstention with 1 limitation | 282 chars, valid |

All the failures are about size. None is a malformed structure. Every first attempt parsed as JSON with the right fields and ended with `finish_reason` = `stop`.

## Observations

- **The caps are not all stated in the prompt.** Prompt v2 states the 4-claim cap and the citation counts. It does not state the 400-character claim cap or the 300-character limitation cap. Two of the three failures broke a cap the prompt never stated.
- **The coverage rule pushes against the length cap.** Rule 14 tells the model to group related findings into one claim rather than drop them. In q020, a single grouped claim citing 7 items ran to 722 characters.
- **The retry is doing real work.** Three of six first attempts needed it. Its cost is small at this scale (the whole batch cost 0.0059 USD), but it hides a mismatch between the prompt and the schema.

## A future controlled experiment (not run)

**Question:** which change raises first-attempt schema validity without lowering claim support or completeness?

**Arms**, each changing one thing against Prompt v2:
1. State every cap in the prompt.
2. Raise the claim cap to 600 characters, with the prompt unchanged.
3. Allow up to 6 claims, with the prompt unchanged.

**Design:**
- Fresh DEV questions not used in batches 1 or 2. Never TEST.
- The same frozen retriever, serializer and provider settings.
- Pre-registered before any output.

**Measures:**
- first-attempt schema validity;
- final validity;
- retries;
- claim support precision and completeness, under the context-only rule.

This needs a new protocol, the owner's go-ahead, and live-call authorization. Nothing is prepared beyond this sketch.
