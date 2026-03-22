from tavily import TavilyClient
from focused_research_agent.config.search_config import get_search_config
from focused_research_agent.interfaces.search_interface import (
    SearchProvider,
    SearchResult,
)
import logging

logger = logging.getLogger(__name__)


class TavilySearchClient(SearchProvider):
    """Tavily-backed implementation of the search provider contract."""

    def __init__(self):
        """Initialize the Tavily search client using validated config."""
        self.search_config = get_search_config()
        self.tavily_client = TavilyClient(api_key=self.search_config["api_key"])

    def search(self, queries: list[str]) -> list[SearchResult]:
        """Run Tavily searches and return normalized search results.

        Args:
            queries: A list of validated search queries.

        Returns:
            list[SearchResult]: Deduplicated and normalized search results.

        Raises:
            ValueError: If the query list is invalid or Tavily returns an
            unexpected response structure.
        """

        if not isinstance(queries, list):
            raise ValueError("TavilySearchClient: queries must be a list")

        if len(queries) == 0:
            raise ValueError("TavilySearchClient: No queries provided")

        for query in queries:
            if not isinstance(query, str):
                raise ValueError("TavilySearchClient: Query must be a string")

            if not query.strip():
                raise ValueError("TavilySearchClient: Query must not be empty")

        search_client = self.tavily_client
        search_config = self.search_config

        final_search_results = []
        seen_urls = set()

        for each_query in queries:
            response = search_client.search(
                query=each_query,
                search_depth="basic",
                max_results=search_config["max_results"],
            )

            if (
                isinstance(response, dict)
                and ("results" in response)
                and isinstance(response["results"], list)
            ):
                response_results = response["results"]
                for each_result in response_results:
                    if not isinstance(each_result, dict):
                        raise ValueError(
                            f"TavilySearchClient: Invalid result item returned for query: {each_query}"
                        )
                    title = (each_result.get("title") or "").strip()
                    url = (each_result.get("url") or "").strip()
                    snippet = (each_result.get("content") or "").strip()
                    score = each_result.get("score")

                    if not title or not url:
                        raise ValueError(
                            f"TavilySearchClient: Result missing title or url for query: {each_query}"
                        )

                    if score is None:
                        raise ValueError(
                            f"TavilySearchClient: Result missing score for query: {each_query}"
                        )

                    try:
                        score = float(score)
                    except (TypeError, ValueError):
                        raise ValueError(
                            f"TavilySearchClient: Invalid score in result for query: {each_query}"
                        )

                    if url in seen_urls:
                        continue

                    normalized_result: SearchResult = {
                        "title": title,
                        "url": url,
                        "snippet": snippet,
                        "source": search_config["provider"],
                        "score": score,
                    }

                    seen_urls.add(url)
                    final_search_results.append(normalized_result)
            else:
                raise ValueError(
                    "search_client: Tavily response missing valid results: {}".format(
                        each_query
                    )
                )
        return final_search_results
