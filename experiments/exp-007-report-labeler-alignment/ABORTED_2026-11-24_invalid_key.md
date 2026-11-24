# Aborted attempt, 2026-11-24: no provider call succeeded

The first `python src/exp007.py run`, started after the protocol was frozen and pushed (`2775bd1`), was stopped after 40 records. Every request returned HTTP 401: the configured DeepSeek API key was rejected as invalid.

- Successful calls: 0. Tokens: 0. Cost: 0.
- AI decisions: none. Nothing about any card was produced or seen.
- The 40 error records are kept locally, unchanged, in `data/store/blind/exp007/aborted-2026-11-24-invalid-key/`. They were moved out of the run path so the one-time guard allows the real run.

The rerun uses the same frozen protocol, definitions, decks and code. Only the key in the local `.env` changes, and the editor sets it herself.
