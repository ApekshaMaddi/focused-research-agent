from focused_research_agent.state import ResearchState
from focused_research_agent.services.search_client import search

def search_web(state: ResearchState) -> dict:
    queries = state.get("queries")

    if not isinstance(queries, list):
        raise ValueError("search_web: queries must be a list")

    if not queries:
        raise ValueError("search_web: No queries found")

    search_results =  search(queries)

    return {"sources": search_results, "status": "searched"}