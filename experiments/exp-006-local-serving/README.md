# EXP-006: local serving with vLLM on the frozen EXP-005 holdout packets

**Status:** protocol, written and committed before the run. The run happens once. This file is not edited afterwards. Results and any later notes go in separate files.

## Question

What changes when ARI3's generation step is served by a small model on local consumer hardware, with every input held fixed? The comparison is with the hosted DeepSeek run already frozen as EXP-005 C2.

This is a serving comparison on identical inputs. It is not a model-quality study, and it makes no claim about answer quality.

## What is held fixed

- The 30 frozen EXP-005 holdout packets (all-packets hash `ad67316abfa8306c66ed002036fe4438883409a813bc3a0dfdc0af8eb3d5bc6a`): the same questions, the same retrieved evidence, the same Prompt v2 messages.
- Prompt v2 (`efea461f…`) and schema v2 (`47b747c1…`), unchanged.
- The same generation function as C2 (`exp005_holdout_c2.generate`): one attempt, plus one retry only when the output does not parse into the schema, then the same deterministic validation.
- The same request settings as C2: temperature 0, top_p 1, max_tokens 1000, JSON output (`response_format: json_object`), up to 2 transport retries.
- No retrieval is rerun. The store snapshot (`43f623eb…`) is read only for citation validation.

The only thing that changes is the provider.

## The local side

| Item | Value |
|---|---|
| Model | `Qwen/Qwen2.5-1.5B-Instruct`, revision `989aa7980e4cf806f80c7fef2b1adb7bc71aa306`, Apache 2.0 |
| Precision | fp16 (`--dtype half`) |
| Server | vLLM 0.31.0, PyTorch 2.13.0, in WSL2 (Ubuntu 24.04) on Windows 11 |
| GPU | NVIDIA GeForce RTX 2080, 8 GB |
| Reach | `http://localhost:8000/v1` only. The adapter refuses any other host. |

Server command:

```
vllm serve Qwen/Qwen2.5-1.5B-Instruct --revision 989aa7980e4cf806f80c7fef2b1adb7bc71aa306 --dtype half --max-model-len 6144 --gpu-memory-utilization 0.55 --enforce-eager --host 127.0.0.1 --port 8000
```

**Why this model.** It was chosen before any packet was sent, on two grounds. It fits: other programs hold about 2.7 GB of the card, the 1.5B model loads in about 3 GB, and the 3B model's weights alone are 6.17 GB. Its license is Apache 2.0.

**Server defaults that apply.** vLLM takes sampling defaults from the model's own `generation_config.json`. The request sets temperature 0 and top_p 1, so decoding is greedy. The model's default `repetition_penalty` of 1.1 is not overridden and applies. This is recorded here and is not tuned.

**Warm-up.** Two calls with an unrelated prompt were made after the server started, to confirm JSON output works. The first took 6.4 s and the second 0.8 s. No frozen packet was sent before this protocol was committed.

## What is measured

All figures come from `python src/exp006_vllm.py compare`, which reads the two frozen outputs files and applies the same function to both.

- First-attempt latency per call: median and 95th percentile. Latency is wall time around the provider call, measured the same way in both runs.
- Latency per question including the schema retry: median and 95th percentile.
- Output tokens per second on first attempts: median.
- Schema validity: first attempt, and final after the one allowed retry.
- Final status of each question, and deterministic integrity failures (rejected schema, rejected citation, invalid context, provider error).

## What is not measured

- Answer quality, grounding, completeness and abstention correctness. No human review of these outputs is planned, and they are not compared with the C2 review.
- The local outputs are never evidence and are not used by any report.

## How to read the result

- The hosted latency includes the network and the provider's hardware. The local latency is one consumer GPU with no network. The two models also differ greatly in size. A latency difference therefore describes the two serving paths as they are, not the speed of one model against another on equal hardware.
- A 1.5B model is expected to fail the answer schema more often than the hosted model. That outcome is a finding and is reported as it comes.

## Rules

1. One run, written to `runs/vllm-v1/`. An existing run is never overwritten or repeated.
2. The preflight must pass first: packets and store snapshot match the C2 manifest, first-attempt messages rebuild to their frozen hashes, this protocol is committed and pushed, and the server is serving the named model.
3. No prompt, schema, request setting or server flag changes after the first packet is sent.
4. A provider error or a server failure during the run is recorded as it happens and counts. No question is rerun.
5. Every question is reported, including failures.
