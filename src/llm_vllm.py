"""vLLM adapter behind llm_provider's interface, over plain HTTP.

vLLM serves a local model through an OpenAI-compatible endpoint
(`vllm serve <model>` listens on http://localhost:8000/v1 by default). The request is the
same chat-completions shape the DeepSeek adapter sends, with JSON output through
response_format json_object. There is no API key and no per-call cost.

Safety:
- No request is sent unless the provider was created with allow_live=True. A local
  model costs nothing per call, so the ARI3_LIVE_LLM gate for paid calls does not apply.
- Requests go only to base_url, which defaults to localhost. A base_url on any other host is
  refused unless the provider was created with allow_remote=True, because the messages
  carry stored article excerpts and those must not leave the machine by accident.
- Timeouts, at most `max_retries` retries on timeouts, connection errors, 429 and 5xx,
  and no retry on other 4xx.
"""

import time
from urllib.parse import urlparse

import requests

from llm_provider import LiveCallNotAllowed, LLMResult, ProviderError

DEFAULT_BASE_URL = "http://localhost:8000/v1"
LOCAL_HOSTS = {"localhost", "127.0.0.1", "::1"}


class VLLMProvider:
    name = "vllm"

    def __init__(self, model, base_url=DEFAULT_BASE_URL, temperature=0.0, top_p=1.0, max_tokens=1000,
                 timeout=120.0, max_retries=2, allow_live=False, session=None, sleep=time.sleep, allow_remote=False):
        self.model = model
        self.base_url = base_url.rstrip("/")
        host = urlparse(self.base_url).hostname
        if host not in LOCAL_HOSTS and not allow_remote:
            raise ValueError(f"vLLM base_url must be on this machine (got host {host!r}); pass allow_remote=True to override")
        self.temperature = temperature
        self.top_p = top_p
        self.max_tokens = max_tokens
        self.timeout = timeout
        self.max_retries = max_retries
        self.allow_live = allow_live
        self.session = session or requests.Session()
        self.sleep = sleep

    def config(self):
        return {"provider": self.name, "model": self.model, "base_url": self.base_url,
                "temperature": self.temperature, "top_p": self.top_p, "max_tokens": self.max_tokens,
                "timeout_s": self.timeout, "max_retries": self.max_retries, "response_format": "json_object"}

    def _payload(self, messages):
        return {"model": self.model, "messages": messages, "temperature": self.temperature, "top_p": self.top_p,
                "max_tokens": self.max_tokens, "response_format": {"type": "json_object"}, "stream": False}

    def generate_json(self, messages):
        if not self.allow_live:
            raise LiveCallNotAllowed("vLLM calls need allow_live=True")
        t0 = time.perf_counter()
        last = "no attempt made"
        for attempt in range(1, self.max_retries + 2):
            try:
                r = self.session.post(f"{self.base_url}/chat/completions", json=self._payload(messages),
                                      timeout=self.timeout)
            except (requests.Timeout, requests.ConnectionError) as e:
                last = f"network error ({type(e).__name__})"
            else:
                if r.status_code == 200:
                    return self._result(r, attempt, time.perf_counter() - t0)
                try:
                    detail = str(r.json().get("message") or r.json().get("error", {}).get("message", ""))
                except (ValueError, AttributeError):
                    detail = ""
                last = f"HTTP {r.status_code}: {detail[:200]}".rstrip(": ")
                if r.status_code != 429 and r.status_code < 500:
                    raise ProviderError(f"vLLM {last}")
            if attempt <= self.max_retries:
                self.sleep(2 ** (attempt - 1))
        raise ProviderError(f"vLLM failed after {self.max_retries + 1} attempts: {last}")

    def _result(self, r, attempt, latency):
        try:
            data = r.json()
            choice = data["choices"][0]
            text = choice["message"]["content"]
        except (ValueError, KeyError, IndexError, TypeError):
            raise ProviderError("vLLM returned a response without a message") from None
        usage = {k: v for k, v in (data.get("usage") or {}).items() if isinstance(v, (int, float))}
        return LLMResult(text=text or "", provider=self.name, model=data.get("model", self.model), usage=usage,
                         latency_s=latency, request_id=data.get("id"), finish_reason=choice.get("finish_reason"),
                         attempts=attempt)
