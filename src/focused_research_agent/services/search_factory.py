from focused_research_agent.config.search_config import get_search_config
from focused_research_agent.interfaces.search_interface import SearchProvider
from focused_research_agent.services.search_client_tavily import TavilySearchClient


def get_search_provider() -> SearchProvider:
    search_config = get_search_config()
    provider = search_config["provider"]

    if provider == "tavily":
        return TavilySearchClient()

    raise ValueError(f"Unsupported search provider: {provider}")