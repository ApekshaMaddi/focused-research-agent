from abc import ABC, abstractmethod
from typing import  TypedDict


class SearchResult(TypedDict):
    title: str
    url: str
    snippet: str
    source: str
    score: float


class SearchProvider(ABC):
    @abstractmethod
    def search(self, queries: list[str]) -> list[SearchResult]:
        ...
