"""Tests for the vLLM adapter. No server is needed: a fake session stands in for HTTP."""

import requests

import llm_vllm
from llm_provider import LiveCallNotAllowed, ProviderError

MESSAGES = [{"role": "user", "content": "return json"}]


class FakeResponse:
    def __init__(self, status, body):
        self.status_code = status
        self.body = body

    def json(self):
        if isinstance(self.body, Exception):
            raise self.body
        return self.body


class FakeSession:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def post(self, url, json=None, timeout=None):
        self.calls.append({"url": url, "json": json, "timeout": timeout})
        r = self.responses.pop(0)
        if isinstance(r, Exception):
            raise r
        return r


def ok(text='{"claims": []}'):
    return FakeResponse(200, {"id": "cmpl-1", "model": "qwen", "choices": [{"message": {"content": text},
                              "finish_reason": "stop"}], "usage": {"prompt_tokens": 10, "completion_tokens": 5}})


def provider(responses, **kw):
    return llm_vllm.VLLMProvider("qwen", allow_live=kw.pop("allow_live", True), session=FakeSession(responses),
                                 sleep=lambda s: None, **kw)


def test_refuses_without_allow_live():
    p = provider([ok()], allow_live=False)
    try:
        p.generate_json(MESSAGES)
    except LiveCallNotAllowed:
        assert p.session.calls == []
        return
    raise AssertionError("expected LiveCallNotAllowed")


def test_sends_openai_chat_request_to_base_url():
    p = provider([ok()], base_url="http://localhost:8000/v1/")
    r = p.generate_json(MESSAGES)
    call = p.session.calls[0]
    assert call["url"] == "http://localhost:8000/v1/chat/completions"
    assert call["json"]["response_format"] == {"type": "json_object"}
    assert call["json"]["temperature"] == 0.0 and call["json"]["stream"] is False
    assert r.text == '{"claims": []}' and r.provider == "vllm" and r.usage["completion_tokens"] == 5
    assert r.finish_reason == "stop" and r.attempts == 1


def test_retries_5xx_and_connection_errors_then_succeeds():
    p = provider([FakeResponse(503, {}), requests.ConnectionError(), ok()])
    assert p.generate_json(MESSAGES).attempts == 3


def test_no_retry_on_4xx():
    p = provider([FakeResponse(400, {"message": "prompt too long"}), ok()])
    try:
        p.generate_json(MESSAGES)
    except ProviderError as e:
        assert "400" in str(e) and len(p.session.calls) == 1
        return
    raise AssertionError("expected ProviderError")


def test_gives_up_after_max_retries():
    p = provider([FakeResponse(500, {})] * 3, max_retries=2)
    try:
        p.generate_json(MESSAGES)
    except ProviderError:
        assert len(p.session.calls) == 3
        return
    raise AssertionError("expected ProviderError")


def test_refuses_a_server_on_another_machine_unless_allowed():
    for url in ("http://192.168.1.20:8000/v1", "https://api.example.com/v1", "http://localhost.example.com/v1"):
        try:
            provider([], base_url=url)
        except ValueError:
            continue
        raise AssertionError(f"expected ValueError for {url}")
    assert provider([], base_url="http://127.0.0.1:8000/v1").base_url == "http://127.0.0.1:8000/v1"
    assert provider([], base_url="http://192.168.1.20:8000/v1", allow_remote=True).base_url.startswith("http://192.168")


def test_config_has_no_secrets_and_names_the_server():
    c = provider([]).config()
    assert c["provider"] == "vllm" and c["base_url"] == "http://localhost:8000/v1"
    assert "key" not in " ".join(c).lower()


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print("ok", name)
