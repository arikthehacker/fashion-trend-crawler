"""DeepSeek in thinking mode, keeping the reasoning text (EXP-007, reader 3).

The frozen adapter (llm_deepseek.py, fingerprinted by EXP-005) keeps only the final answer,
so this subclass leaves it untouched and adds two things to each result:
  reasoning_content  choices[0].message.reasoning_content (the thinking text)
  usage              plus reasoning_tokens from usage.completion_tokens_details

Docs read 2026-11-24 (api-docs.deepseek.com, thinking_mode and create-chat-completion):
thinking is switched on with {"thinking": {"type": "enabled"}}; temperature has no effect in
thinking mode; top_p for deepseek-flash is effective between 0.95 and 1.0; the reasoning
text is returned in non-streaming responses; it is not sent back in later messages.
"""

from llm_deepseek import DeepSeekProvider
from llm_provider import ProviderError

DOCS_CHECKED_THINKING = "2026-11-24"


class DeepSeekThinkingProvider(DeepSeekProvider):
    def __init__(self, **kw):
        kw["thinking"] = "enabled"
        super().__init__(**kw)

    def config(self):
        return dict(super().config(), thinking="enabled", temperature_note="no effect in thinking mode",
                    docs_checked_thinking=DOCS_CHECKED_THINKING)

    def _result(self, r, attempt, latency, key):
        result = super()._result(r, attempt, latency, key)
        try:
            data = r.json()
            message = data["choices"][0]["message"]
        except (ValueError, KeyError, IndexError, TypeError):
            raise ProviderError("DeepSeek returned a response without a message") from None
        details = (data.get("usage") or {}).get("completion_tokens_details") or {}
        if isinstance(details.get("reasoning_tokens"), (int, float)):
            result.usage["reasoning_tokens"] = details["reasoning_tokens"]
        reasoning = message.get("reasoning_content") or ""
        result.reasoning_content = reasoning.replace(key, "[redacted]") if key else reasoning
        return result
