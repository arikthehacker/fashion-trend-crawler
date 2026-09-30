"""DeepSeek chat-completions adapter behind llm_provider's interface, over plain HTTP.

Checked against api-docs.deepseek.com on 2026-09-30 (read through a summarizer, so
re-check the raw pages before the first live call): OpenAI-compatible endpoint
https://api.deepseek.com/chat/completions, models `deepseek-flash` (V4.1 Flash) and
`deepseek-v4-pro`, JSON output mode, a `thinking` request parameter, and prices that
differ between peak hours (01:00 to 04:00 and 06:00 to 10:00 UTC, Monday to Friday) and
off-peak hours. Rate limits were not found.

Safety:
- The key comes only from the DEEPSEEK_API_KEY environment variable. It is never
  logged, returned, put in an exception or included in config().
- No request is sent unless the provider was created with allow_live=True AND the
  environment variable ARI3_LIVE_LLM is set to "approved". Otherwise LiveCallNotAllowed
  is raised before any network activity. The owner sets the gate. Code never sets it.
- Timeouts, at most `max_retries` retries on timeouts, connection errors, 429 and 5xx,
  and no retry on other 4xx.
- Error messages keep the HTTP status and at most 200 characters of the provider's
  error text, with anything that looks like a key removed.
"""

import os
import re
import time
from datetime import datetime, timezone

import requests

from llm_provider import LiveCallNotAllowed, LLMResult, ProviderError

BASE_URL = "https://api.deepseek.com"
DEFAULT_MODEL = "deepseek-flash"
DOCS_CHECKED = "2026-09-30"
GATE_VARIABLE = "ARI3_LIVE_LLM"
# USD per million tokens, from the pricing page on DOCS_CHECKED: (off-peak, peak).
PRICING = {"deepseek-flash": {"input_cache_hit": (0.003, 0.006), "input_cache_miss": (0.15, 0.30),
                              "output": (0.60, 1.20)},
           "deepseek-v4-pro": {"input_cache_hit": (0.022, 0.044), "input_cache_miss": (0.66, 1.32),
                               "output": (1.98, 3.96)}}
SECRET_SHAPES = re.compile(r"sk-[A-Za-z0-9_-]{8,}|Bearer\s+\S+", re.I)


def is_peak(at):
    return at.weekday() < 5 and (1 <= at.hour < 4 or 6 <= at.hour < 10)


def estimate_cost(model, usage, at=None):
    """Estimated USD for one call, or None when the model has no recorded price."""
    prices = PRICING.get(model)
    if prices is None:
        return None
    col = 1 if is_peak(at or datetime.now(timezone.utc)) else 0
    hit = usage.get("prompt_cache_hit_tokens", 0) or 0
    miss = usage.get("prompt_cache_miss_tokens", (usage.get("prompt_tokens", 0) or 0) - hit) or 0
    out = usage.get("completion_tokens", 0) or 0
    return round((hit * prices["input_cache_hit"][col] + miss * prices["input_cache_miss"][col]
                  + out * prices["output"][col]) / 1_000_000, 8)


def sanitize(text, key=None):
    text = str(text or "")
    if key:
        text = text.replace(key, "[redacted]")
    return SECRET_SHAPES.sub("[redacted]", text)[:200]


class DeepSeekProvider:
    name = "deepseek"

    def __init__(self, model=DEFAULT_MODEL, temperature=0.0, max_tokens=1200, timeout=60.0, max_retries=2,
                 thinking="disabled", allow_live=False, session=None, sleep=time.sleep):
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout = timeout
        self.max_retries = max_retries
        self.thinking = thinking
        self.allow_live = allow_live
        self.session = session or requests.Session()
        self.sleep = sleep

    def config(self):
        return {"provider": self.name, "model": self.model, "base_url": BASE_URL, "temperature": self.temperature,
                "max_tokens": self.max_tokens, "timeout_s": self.timeout, "max_retries": self.max_retries,
                "thinking": self.thinking, "response_format": "json_object", "docs_checked": DOCS_CHECKED}

    def _payload(self, messages):
        body = {"model": self.model, "messages": messages, "temperature": self.temperature,
                "max_tokens": self.max_tokens, "response_format": {"type": "json_object"}, "stream": False}
        if self.thinking:
            body["thinking"] = {"type": self.thinking}
        return body

    def generate_json(self, messages):
        if not self.allow_live or os.environ.get(GATE_VARIABLE) != "approved":
            raise LiveCallNotAllowed(f"live DeepSeek calls need allow_live=True and {GATE_VARIABLE}=approved")
        key = os.environ.get("DEEPSEEK_API_KEY", "")
        if not key:
            raise ProviderError("DEEPSEEK_API_KEY is not set")
        headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
        t0 = time.perf_counter()
        last = "no attempt made"
        for attempt in range(1, self.max_retries + 2):
            try:
                r = self.session.post(f"{BASE_URL}/chat/completions", json=self._payload(messages), headers=headers,
                                      timeout=self.timeout)
            except (requests.Timeout, requests.ConnectionError) as e:
                last = f"network error ({type(e).__name__})"
            else:
                if r.status_code == 200:
                    return self._result(r, attempt, time.perf_counter() - t0, key)
                try:
                    detail = r.json().get("error", {}).get("message", "")
                except ValueError:
                    detail = ""
                last = f"HTTP {r.status_code}: {sanitize(detail, key)}".rstrip(": ")
                if r.status_code != 429 and r.status_code < 500:
                    raise ProviderError(f"DeepSeek {last}")
            if attempt <= self.max_retries:
                self.sleep(2 ** (attempt - 1))
        raise ProviderError(f"DeepSeek failed after {self.max_retries + 1} attempts: {last}")

    def _result(self, r, attempt, latency, key):
        try:
            data = r.json()
            choice = data["choices"][0]
            text = choice["message"]["content"]
        except (ValueError, KeyError, IndexError, TypeError):
            raise ProviderError("DeepSeek returned a response without a message") from None
        usage = {k: v for k, v in (data.get("usage") or {}).items() if isinstance(v, (int, float))}
        return LLMResult(text=text or "", provider=self.name, model=data.get("model", self.model), usage=usage,
                         latency_s=latency, request_id=sanitize(data.get("id"), key) or None,
                         finish_reason=choice.get("finish_reason"), attempts=attempt)
