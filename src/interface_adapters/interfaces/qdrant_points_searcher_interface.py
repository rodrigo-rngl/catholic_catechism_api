from typing import List, Generic
from abc import ABC, abstractmethod

from src.application.DTOs.SearchOutput import SearchOutput
from src.application.DTOs.QueryEmbedding import QueryEmbeddingType


class QdrantPointsSearcherInterface(ABC, Generic[QueryEmbeddingType]):
    @abstractmethod
    async def search(self, collection_name: str, embedding: QueryEmbeddingType, top_k: int) -> List[SearchOutput]:
        pass
