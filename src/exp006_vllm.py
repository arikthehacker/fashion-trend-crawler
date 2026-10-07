"""EXP-006: local serving with vLLM against the DeepSeek API on the same frozen inputs.

The run sends the 30 frozen EXP-005 holdout packets (same questions, same retrieved
context, same Prompt v2, same schema and one-retry rule) to a model served locally by
vLLM, through exp005_holdout_c2.generate, so the only thing that changes from the C2 run
is the provider. Nothing in EXP-005 is read for tuning or written to.

usage:
  vllm serve <model> ...                               # in WSL, see the run notes
  python src/exp006_vllm.py preflight --model <model>  # no generation call
                                                       # (fails until experiments/exp-006-local-serving/README.md,
                                                       #  the protocol, is committed and pushed)
  python src/exp006_vllm.py run --model <model>        # once
  python src/exp006_vllm.py compare                    # C2 (DeepSeek) vs vLLM, from the frozen files
"""

import argparse
import json
import os
import statistics
import subprocess
import sys

import requests

import exp005 as v1
import exp005_holdout as h
import exp005_holdout_c2 as c2
import exp005_holdout_freeze as fz
import exp005_v2 as v2
from llm_vllm import DEFAULT_BASE_URL, VLLMProvider

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXP_DIR = os.path.join(ROOT, "experiments", "exp-006-local-serving")
RUN_DIR = os.path.join(EXP_DIR, "runs", "vllm-v1")
OUTPUTS = os.path.join(RUN_DIR, "outputs.jsonl")
PREFLIGHT = os.path.join(RUN_DIR, "preflight.json")
RUN_MANIFEST = os.path.join(RUN_DIR, "run_manifest.json")
COMPARISON = os.path.join(EXP_DIR, "comparison_v1.json")
PROTOCOL = os.path.join(EXP_DIR, "README.md")  # what is measured, on what, and that it runs once


def gpu_info():
    try:
        out = subprocess.run(["nvidia-smi", "--query-gpu=name,memory.total,driver_version", "--format=csv,noheader"],
                             capture_output=True, text=True, timeout=10).stdout.strip()
        return out or "unknown"
    except (OSError, subprocess.SubprocessError):
        return "unknown (nvidia-smi not found from this shell)"


def server_info(base_url):
    root = base_url.rsplit("/v1", 1)[0]
    models = requests.get(f"{base_url}/models", timeout=10).json()
    try:
        version = requests.get(f"{root}/version", timeout=10).json().get("version")
    except (requests.RequestException, ValueError):
        version = None
    return {"served_models": [m["id"] for m in models.get("data", [])], "vllm_version": version}


def preflight(model, base_url):
    missing = [p for p in (h.PACKETS, h.SNAPSHOT) if not os.path.exists(p)]
    if missing:
        return {"checked_at": c2._now(), "passed": False, "checks": {"local_c1_files_present": False},
                "missing": missing, "note": "run this from the machine that holds the C1 packets and store snapshot"}
    checks = {}
    with open(h.MANIFEST, encoding="utf-8") as f:
        m = json.load(f)
    checks["packets_match_c2_manifest"] = h.sha256_json(m["packets"]) == m["packets_sha256"] == c2.EXPECTED["packets"]
    checks["local_packets_unchanged"] = fz.packets_unchanged(m)
    checks["store_snapshot_sha256"] = h.sha256_file(h.SNAPSHOT) == m["store_snapshot"]["sha256"]
    deck, packets = h.load_deck(), h.load_packets()
    with open(v2.PROMPT_V2, encoding="utf-8") as f:
        prompt_text = f.read()
    checks["first_attempt_messages_rebuild_from_frozen_context"] = all(
        h.sha256_json(v1.build_messages(h.app_question(q), p["context"], prompt_text)) == p["messages_sha256"]
        for q, p in zip(deck, packets) if p["status"] == "packet_built")
    checks["c2_run_exists"] = os.path.exists(c2.RUN_MANIFEST)
    import rag_select as rs
    checks["protocol_committed_and_pushed"] = os.path.exists(PROTOCOL) and rs.rule_is_committed_and_pushed(PROTOCOL)[0]
    checks["not_run_before"] = not os.path.exists(RUN_DIR)
    try:
        server = server_info(base_url)
        checks["server_up_and_serving_model"] = model in server["served_models"]
    except (requests.RequestException, ValueError, KeyError) as e:
        server, checks["server_up_and_serving_model"] = {"error": f"{type(e).__name__}"}, False
    return {"checked_at": c2._now(), "passed": all(checks.values()), "checks": checks, "server": server,
            "gpu": gpu_info(), "base_url": base_url, "model": model,
            "protocol_sha256": h.sha256_file(PROTOCOL) if os.path.exists(PROTOCOL) else None}


def run(model, base_url):
    from rag_corpus import open_corpus
    pre = preflight(model, base_url)
    if not pre["passed"]:
        print(json.dumps({"stopped_before_first_call": True,
                          "failed": sorted(k for k, v in pre["checks"].items() if not v)}, indent=1))
        return 1
    os.makedirs(RUN_DIR)
    with open(PREFLIGHT, "x", encoding="utf-8", newline="\n") as f:
        json.dump(pre, f, indent=1, ensure_ascii=False)
        f.write("\n")
    p = v1.PROVIDER_SETTINGS
    provider = VLLMProvider(model, base_url=base_url, temperature=p["temperature"], top_p=p["top_p"],
                            max_tokens=p["max_tokens"], max_retries=p["transport_retries"], allow_live=True)
    deck, packets = h.load_deck(), h.load_packets()
    with open(v2.PROMPT_V2, encoding="utf-8") as f:
        prompt_text = f.read()
    corpus = open_corpus(h.SNAPSHOT)
    budget, records, started = c2.Budget(cap=float("inf")), [], c2._now()
    with open(OUTPUTS, "x", encoding="utf-8", newline="\n") as out:
        for q, pk in zip(deck, packets):
            r = c2.generate(q, pk, provider, corpus, prompt_text, budget, cost_fn=None)
            r.update(run="vllm-v1", packet_messages_sha256=pk.get("messages_sha256"))
            out.write(json.dumps(r, ensure_ascii=False) + "\n")
            out.flush()
            records.append(r)
    corpus.close()
    body = {"version": "exp006-vllm-run-v1", "run": "vllm-v1", "started_at": started, "ended_at": c2._now(),
            "inputs": {"packets_sha256": c2.EXPECTED["packets"], "prompt_v2_sha256": c2.EXPECTED["prompt_v2"],
                       "schema_v2_sha256": c2.EXPECTED["schema_v2"], "preflight_sha256": h.sha256_file(PREFLIGHT),
                       "protocol_sha256": pre["protocol_sha256"]},
            "provider": provider.config(), "server": pre["server"], "gpu": pre["gpu"],
            "summary": c2.summarize(records, budget), "outputs_sha256": h.sha256_file(OUTPUTS)}
    with open(RUN_MANIFEST, "x", encoding="utf-8", newline="\n") as f:
        json.dump(body, f, indent=1, ensure_ascii=False)
        f.write("\n")
    print(json.dumps(body, indent=1, ensure_ascii=False))
    return 0


def _pct(values, q):
    s = sorted(values)
    return s[min(len(s) - 1, int(round(q * (len(s) - 1))))] if s else None


def _median(values):
    return round(statistics.median(values), 1) if values else None


def stats(path):
    """Descriptive figures for one run's outputs file. A question whose provider call never
    returned has no recorded attempt: it counts in `questions` and `statuses`, not in the
    latency or schema figures, and `called` says how many did return."""
    with open(path, encoding="utf-8") as f:
        rows = [json.loads(line) for line in f if line.strip()]
    called = [r for r in rows if r["attempts"]]
    first = [r["attempts"][0] for r in called]
    lat = [a["latency_ms"] for a in first]
    total = [sum(a["latency_ms"] for a in r["attempts"]) for r in called]
    tps = [(a.get("usage") or {}).get("completion_tokens", 0) / (a["latency_ms"] / 1000) for a in first if a["latency_ms"]]
    statuses = {}
    for r in rows:
        statuses[r["status"]] = statuses.get(r["status"], 0) + 1
    return {"questions": len(rows), "called": len(called),
            "first_attempt_latency_ms": {"median": _median(lat), "p95": _pct(lat, 0.95)},
            "per_question_latency_ms_with_retries": {"median": _median(total), "p95": _pct(total, 0.95)},
            "output_tokens_per_s_median": _median(tps),
            "first_attempt_schema_valid": f"{sum(a['schema_valid'] for a in first)}/{len(called)}",
            "final_schema_valid": f"{sum(any(a['schema_valid'] for a in r['attempts']) for r in called)}/{len(called)}",
            "schema_retries": sum(1 for r in called if len(r["attempts"]) > 1),
            "statuses": statuses,
            "integrity_failures": sum(statuses.get(k, 0) for k in c2.DETERMINISTIC_FAILURES)}


def compare(outputs=None, manifest_path=None, comparison=None):
    """C2 (DeepSeek) against the vLLM run, from the two frozen outputs files. Written once."""
    outputs, manifest_path, comparison = outputs or OUTPUTS, manifest_path or RUN_MANIFEST, comparison or COMPARISON
    for path, what in ((c2.OUTPUTS, "the C2 outputs"), (outputs, "the vLLM run"), (manifest_path, "the vLLM run manifest")):
        if not os.path.exists(path):
            print(json.dumps({"compared": False, "reason": f"{what} not found: {path}"}, indent=1))
            return 1
    if os.path.exists(comparison):
        print(json.dumps({"compared": False, "reason": f"already written: {comparison}"}, indent=1))
        return 1
    with open(manifest_path, encoding="utf-8") as f:
        manifest = json.load(f)
    if h.sha256_file(outputs) != manifest["outputs_sha256"]:
        print(json.dumps({"compared": False, "reason": "the vLLM outputs changed after the run"}, indent=1))
        return 1
    body = {"computed_at": c2._now(),
            "inputs": {"deepseek_c2_outputs_sha256": h.sha256_file(c2.OUTPUTS), "vllm_v1_outputs_sha256": manifest["outputs_sha256"],
                       "packets_sha256": manifest["inputs"]["packets_sha256"]},
            "deepseek_c2": {"model": "deepseek-flash (hosted API)", **stats(c2.OUTPUTS)},
            "vllm_v1": {"model": manifest["provider"]["model"], "gpu": manifest.get("gpu"),
                        "vllm_version": (manifest.get("server") or {}).get("vllm_version"), **stats(outputs)},
            "note": "latency is wall time per provider call, measured the same way in both runs. The hosted figure "
                    "includes the network and the provider's hardware, the local figure one consumer GPU, and the two "
                    "models differ in size. Answer quality is not compared here and needs human review."}
    with open(comparison, "x", encoding="utf-8", newline="\n") as f:
        json.dump(body, f, indent=1, ensure_ascii=False)
        f.write("\n")
    print(json.dumps(body, indent=1, ensure_ascii=False))
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["preflight", "run", "compare"])
    ap.add_argument("--model")
    ap.add_argument("--base-url", default=DEFAULT_BASE_URL)
    a = ap.parse_args(argv)
    if a.cmd == "compare":
        return compare()
    if not a.model:
        ap.error("--model is required for preflight and run")
    if a.cmd == "preflight":
        print(json.dumps(preflight(a.model, a.base_url), indent=1, ensure_ascii=False))
        return 0
    return run(a.model, a.base_url)


if __name__ == "__main__":
    sys.exit(main())
