import logging

from tavily import TavilyClient

from focused_research_agent.config.search_config import get_search_config
from focused_research_agent.interfaces.search_interface import (
    SearchProvider,
    SearchResult,
)

logger = logging.getLogger(__name__)


class TavilySearchClient(SearchProvider):
    """Tavily-backed implementation of the search provider contract."""

    def __init__(self):
        """Initialize the Tavily search client using validated config."""
        self.search_config = get_search_config()
        self.tavily_client = TavilyClient(api_key=self.search_config["api_key"])

    # ------------------------------------------------------------------
    # Static helpers — pure validation functions that operate only on
    # their arguments and do not read or modify any instance state.
    # @staticmethod signals this explicitly and prevents accidental
    # coupling to self.
    # ------------------------------------------------------------------

    @staticmethod
    def _validate_queries(queries: list[str]) -> list[str]:
        """Validate and clean incoming search queries.

        Args:
            queries: Raw list of search queries.

        Returns:
            list[str]: Cleaned non-empty query strings.

        Raises:
            ValueError: If queries is not a non-empty list of non-empty
                strings.
        """
        if not isinstance(queries, list):
            raise ValueError("TavilySearchClient: queries must be a list")

        if len(queries) == 0:
            raise ValueError("TavilySearchClient: No queries provided")

        cleaned_queries = []

        for query in queries:
            if not isinstance(query, str):
                raise ValueError("TavilySearchClient: Query must be a string")

            cleaned_query = query.strip()
            if not cleaned_query:
                raise ValueError("TavilySearchClient: Query must not be empty")

            cleaned_queries.append(cleaned_query)

        return cleaned_queries

    @staticmethod
    def _validate_tavily_response(response: object, query: str) -> list[dict]:
        """Validate the Tavily API response shape for a single query.

        Args:
            response: Raw response returned by Tavily.
            query: The query used for the Tavily call.

        Returns:
            list[dict]: Raw Tavily result items.

        Raises:
            ValueError: If the response is not a dict or does not contain
                a valid "results" list.
        """
        if not isinstance(response, dict) or "results" not in response:
            raise ValueError(
                f"search_client: Tavily response missing valid results: {query}"
            )

        results = response["results"]

        if not isinstance(results, list):
            raise ValueError(
                f"search_client: Tavily response missing valid results: {query}"
            )

        return results

    # ------------------------------------------------------------------
    # Instance methods — these use self.search_config or
    # self.tavily_client and must remain as instance methods.
    # ------------------------------------------------------------------

    def _normalize_result(self, item: dict, query: str) -> SearchResult:
        """Normalize one Tavily result item into the shared SearchResult shape.

        Args:
            item: A raw Tavily result item.
            query: The query that produced this result, used in error messages.

        Returns:
            SearchResult: Normalized result dict matching the SearchResult shape.

        Raises:
            ValueError: If the result item is malformed or missing required
                fields.
        """
        if not isinstance(item, dict):
            raise ValueError(
                f"TavilySearchClient: Invalid result item returned for query: {query}"
            )

        title = (item.get("title") or "").strip()
        url = (item.get("url") or "").strip()
        snippet = (item.get("content") or "").strip()
        score = item.get("score")

        if not title or not url:
            raise ValueError(
                f"TavilySearchClient: Result missing title or url for query: {query}"
            )

        if score is None:
            raise ValueError(
                f"TavilySearchClient: Result missing score for query: {query}"
            )

        try:
            score = float(score)
        except (TypeError, ValueError):
            raise ValueError(
                f"TavilySearchClient: Invalid score in result for query: {query}"
            )

        normalized_result: SearchResult = {
            "title": title,
            "url": url,
            "snippet": snippet,
            "source": self.search_config["provider"],  # requires self
            "score": score,
        }

        return normalized_result

    def _search_single_query(self, query: str) -> list[SearchResult]:
        """Run Tavily search for one query and normalize the returned results.

        Args:
            query: A single validated search query.

        Returns:
            list[SearchResult]: Normalized results for that query.

        Raises:
            ValueError: If the Tavily response shape is invalid or a result
                item is malformed.
        """
        response = self.tavily_client.search(
            query=query,
            search_depth=self.search_config["search_depth"],
            max_results=self.search_config["max_results"],
        )

        response_results = self._validate_tavily_response(response, query)

        normalized_results: list[SearchResult] = []

        for item in response_results:
            normalized_results.append(self._normalize_result(item, query))

        return normalized_results

    def search(self, queries: list[str]) -> list[SearchResult]:
        """Run Tavily searches and return normalized, deduplicated results.

        Args:
            queries: A list of validated search queries.

        Returns:
            list[SearchResult]: Deduplicated and normalized search results.

        Raises:
            ValueError: If the query list is invalid or Tavily returns an
                unexpected response structure.
        """
        cleaned_queries = self._validate_queries(queries)

        final_search_results: list[SearchResult] = []
        seen_urls: set[str] = set()

        for query in cleaned_queries:
            query_results = self._search_single_query(query)

            for result in query_results:
                if result["url"] in seen_urls:
                    continue

                seen_urls.add(result["url"])
                final_search_results.append(result)

        return final_search_results