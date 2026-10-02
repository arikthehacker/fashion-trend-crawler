# Aborted attempt, 2026-10-02 00:58 UTC: no provider call was made

The first `python src/exp005_schema.py run` stopped every question with `ProviderError: DEEPSEEK_API_KEY is not set`. The adapter reads the key from the process environment, and the launching process had not loaded the git-ignored root `.env`.

- Requests sent to DeepSeek: 0. Tokens: 0. Cost: 0.
- Model outputs: none. Nothing about either prompt's behaviour was seen.
- Retrieval ran, and all 8 pairs received identical evidence.

The two files are kept unchanged. They were moved out of the run path so that the one-time guard allows the real run. The rerun uses the same frozen protocol, prompts, batch and code (`0280f1a`), with the key loaded into the launching process only. It stays inside the authorized scope of 16 initial generations.
