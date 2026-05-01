from types import SimpleNamespace

import pytest

import focused_research_agent.services.llm_provider_groq as llm_provider_module
import focused_research_agent.services.search_provider_tavily as search_provider_module
from focused_research_agent.services.llm_provider_groq import GroqLLMProvider
from focused_research_agent.services.search_provider_tavily import TavilySearchClient

"""
Unit tests for external provider implementations.

What is tested:
- GroqLLMProvider JSON parsing and validation behavior
- TavilySearchClient input validation, normalization, and deduplication

How it is tested:
- external SDK dependencies are replaced with fake classes
- provider methods are exercised with controlled fake responses
- expected exceptions are asserted for invalid cases

Why it matters:
- verifies the reliability of code that interacts with external systems
- ensures provider-level parsing and normalization are robust
"""


class FakeLLM:
    def __init__(self, content: str):
        self._content = content

    def invoke(self, prompt: str):
        return SimpleNamespace(content=self._content)


class FakeTavilyClient:
    def __init__(self, responses: list[dict]):
        self._responses = responses
        self.calls = []

    def search(self, query: str, search_depth: str, max_results: int):
        self.calls.append(
            {
                "query": query,
                "search_depth": search_depth,
                "max_results": max_results,
            }
        )
        return self._responses.pop(0)


def fake_llm_config():
    return {
        "provider": "groq",
        "model": "fake-model",
        "temperature": 0.0,
        "max_retries": 2,
        "api_key": "fake-key",
    }


def fake_search_config():
    return {
        "provider": "tavily",
        "api_key": "fake-key",
        "max_results": 5,
        "search_depth": "basic",
    }


def fake_init_chat_model_with_valid_json(**kwargs):
    return FakeLLM('{"ok": true}')


def fake_init_chat_model_with_fenced_json(**kwargs):
    return FakeLLM('```json\n{"answer": "ok"}\n```')


def fake_init_chat_model_with_surrounding_text(**kwargs):
    return FakeLLM('Here is the result: {"answer": "ok"} Thanks!')


def fake_init_chat_model_with_no_json(**kwargs):
    return FakeLLM("plain text without any json structure")


def build_fake_tavily_client(responses: list[dict]):
    def fake_tavily_client(api_key: str):
        return FakeTavilyClient(responses)

    return fake_tavily_client


def build_shared_fake_tavily_client(fake_client: FakeTavilyClient):
    def fake_tavily_client(api_key: str):
        return fake_client

    return fake_tavily_client


def test_groq_generate_json_rejects_empty_prompt(monkeypatch):
    monkeypatch.setattr(llm_provider_module, "get_llm_config", fake_llm_config)
    monkeypatch.setattr(
        llm_provider_module,
        "init_chat_model",
        fake_init_chat_model_with_valid_json,
    )

    provider = GroqLLMProvider()

    with pytest.raises(ValueError, match="GroqLLMProvider: No prompt provided!"):
        provider.generate_json("   ")


def test_groq_generate_json_parses_markdown_fenced_json(monkeypatch):
    monkeypatch.setattr(llm_provider_module, "get_llm_config", fake_llm_config)
    monkeypatch.setattr(
        llm_provider_module,
        "init_chat_model",
        fake_init_chat_model_with_fenced_json,
    )

    provider = GroqLLMProvider()
    result = provider.generate_json("test prompt")

    assert result == {"answer": "ok"}


def test_groq_generate_json_parses_json_from_surrounding_text(monkeypatch):
    monkeypatch.setattr(llm_provider_module, "get_llm_config", fake_llm_config)
    monkeypatch.setattr(
        llm_provider_module,
        "init_chat_model",
        fake_init_chat_model_with_surrounding_text,
    )

    provider = GroqLLMProvider()
    result = provider.generate_json("test prompt")

    assert result == {"answer": "ok"}


def test_groq_generate_json_raises_when_no_json_found(monkeypatch):
    monkeypatch.setattr(llm_provider_module, "get_llm_config", fake_llm_config)
    monkeypatch.setattr(
        llm_provider_module,
        "init_chat_model",
        fake_init_chat_model_with_no_json,
    )

    provider = GroqLLMProvider()

    with pytest.raises(ValueError, match="LLM did not return JSON"):
        provider.generate_json("test prompt")


def test_tavily_search_rejects_non_list_queries(monkeypatch):
    monkeypatch.setattr(search_provider_module, "get_search_config", fake_search_config)
    monkeypatch.setattr(
        search_provider_module,
        "TavilyClient",
        build_fake_tavily_client([]),
    )

    provider = TavilySearchClient()

    with pytest.raises(ValueError, match="queries must be a list"):
        provider.search("not-a-list")


def test_tavily_search_rejects_empty_query_string(monkeypatch):
    monkeypatch.setattr(search_provider_module, "get_search_config", fake_search_config)
    monkeypatch.setattr(
        search_provider_module,
        "TavilyClient",
        build_fake_tavily_client([]),
    )

    provider = TavilySearchClient()

    with pytest.raises(ValueError, match="Query must not be empty"):
        provider.search(["valid query", "   "])


def test_tavily_search_deduplicates_urls(monkeypatch):
    responses = [
        {
            "results": [
                {
                    "title": "First result",
                    "url": "https://example.com/a",
                    "content": "Snippet A",
                    "score": 0.95,
                },
                {
                    "title": "Duplicate result",
                    "url": "https://example.com/a",
                    "content": "Duplicate snippet",
                    "score": 0.90,
                },
            ]
        },
        {
            "results": [
                {
                    "title": "Second unique result",
                    "url": "https://example.com/b",
                    "content": "Snippet B",
                    "score": 0.85,
                }
            ]
        },
    ]

    fake_client = FakeTavilyClient(responses)

    monkeypatch.setattr(search_provider_module, "get_search_config", fake_search_config)
    monkeypatch.setattr(
        search_provider_module,
        "TavilyClient",
        build_shared_fake_tavily_client(fake_client),
    )

    provider = TavilySearchClient()
    result = provider.search(["query one", "query two"])

    assert len(result) == 2
    assert result[0]["url"] == "https://example.com/a"
    assert result[1]["url"] == "https://example.com/b"
    assert result[0]["source"] == "tavily"


def test_tavily_search_raises_on_invalid_response_shape(monkeypatch):
    responses = [
        {"unexpected_key": []},
    ]

    monkeypatch.setattr(search_provider_module, "get_search_config", fake_search_config)
    monkeypatch.setattr(
        search_provider_module,
        "TavilyClient",
        build_fake_tavily_client(responses),
    )

    provider = TavilySearchClient()

    with pytest.raises(ValueError, match="Tavily response missing valid results"):
        provider.search(["query one"])


def test_tavily_search_raises_when_score_missing(monkeypatch):
    responses = [
        {
            "results": [
                {
                    "title": "Result without score",
                    "url": "https://example.com/a",
                    "content": "Snippet A",
                }
            ]
        }
    ]

    monkeypatch.setattr(search_provider_module, "get_search_config", fake_search_config)
    monkeypatch.setattr(
        search_provider_module,
        "TavilyClient",
        build_fake_tavily_client(responses),
    )

    provider = TavilySearchClient()

    with pytest.raises(ValueError, match="Result missing score"):
        provider.search(["query one"])
