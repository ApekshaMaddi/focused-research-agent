from focused_research_agent.services.search_factory import get_search_provider
from focused_research_agent.state import ResearchState


def search_web(state: ResearchState) -> dict:
    queries = state.get("queries")

    if not isinstance(queries, list):
        raise ValueError("search_web: queries must be a list")

    if not queries:
        raise ValueError("search_web: No queries found")

    search_provider = get_search_provider()
    search_results = search_provider.search(queries)

    return {"sources": search_results, "status": "searched"}
