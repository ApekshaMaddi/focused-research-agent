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

    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")
