"""Provider-independent interface for language-model calls in EXP-004.

ARI3 code depends only on this interface. Provider-specific HTTP behavior lives in its
own module (llm_deepseek.py). A provider receives chat messages and returns text that
the caller parses and validates. Providers never see the database and never write to it.

ScriptedProvider returns fixed responses. It is used in tests and for offline dry runs,
so the whole pipeline can be exercised without a network call or an API key.
"""

import time
from dataclasses import dataclass, field
from typing import List, Optional, Protocol


class ProviderError(RuntimeError):
    """A provider call failed. The message is sanitized: it never holds a key, a header
    or a full response body."""


class LiveCallNotAllowed(ProviderError):
    """A live, paid call was attempted without the explicit generation gate."""


@dataclass
class LLMResult:
    text: str
    provider: str
    model: str
    usage: dict = field(default_factory=dict)
    latency_s: float = 0.0
    request_id: Optional[str] = None
    finish_reason: Optional[str] = None
    attempts: int = 1


class LLMProvider(Protocol):
    name: str
    model: str

    def config(self) -> dict:
        """Every setting that affects output (model, temperature, limits), for the audit log.
        Never includes a key."""

    def generate_json(self, messages: List[dict]) -> LLMResult:
        """Send chat messages and return the model's text, which should be one JSON object."""


class ScriptedProvider:
    """Returns the given responses in order. Records every call."""

    name = "scripted"

    def __init__(self, responses, model="scripted-v1"):
        self.responses = list(responses)
        self.model = model
        self.calls = []

    def config(self):
        return {"provider": self.name, "model": self.model}

    def generate_json(self, messages):
        self.calls.append(messages)
        if not self.responses:
            raise ProviderError("scripted provider has no response left")
        response = self.responses.pop(0)
        if isinstance(response, Exception):
            raise response
        t0 = time.perf_counter()
        return LLMResult(text=response, provider=self.name, model=self.model,
                         usage={"prompt_tokens": 0, "completion_tokens": 0}, latency_s=time.perf_counter() - t0)
