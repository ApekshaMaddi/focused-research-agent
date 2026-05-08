"""
LLM provider factory for the Focused Research Agent.

This module contains the factory function responsible for instantiating
the correct LLM provider implementation based on the LLM_PROVIDER
environment variable.

Currently supported providers:
- groq: GroqLLMProvider using LangChain's init_chat_model
- ollama: OllamaLLMProvider using the Ollama client library

Adding a new LLM provider requires:
- Implementing the LLMProvider interface
- Adding a new branch in get_llm_provider

No other files need to change — all callers go through this factory.
The ollama import is intentionally local to avoid importing the ollama
package when it is not the active provider.

Architecturally, this module belongs to the services layer and implements
the Factory pattern. It keeps provider selection logic in one place and
decouples the rest of the application from concrete provider classes.
"""

from focused_research_agent.config.llm_config import get_llm_config
from focused_research_agent.interfaces.llm_interface import LLMProvider
from focused_research_agent.services.llm_provider_groq import GroqLLMProvider


def get_llm_provider() -> LLMProvider:
    """Return the active LLM provider implementation.

    Returns:
        LLMProvider: The configured LLM provider instance.

    Raises:
        ValueError: If the configured provider is unsupported.
    """
    llm_config = get_llm_config()
    provider = llm_config["provider"]

    if provider == "groq":
        return GroqLLMProvider()

    if provider == "ollama":
        from focused_research_agent.services.llm_provider_ollama import (
            OllamaLLMProvider,
        )

        return OllamaLLMProvider()

    raise ValueError(f"Unsupported LLM provider: {provider}")
