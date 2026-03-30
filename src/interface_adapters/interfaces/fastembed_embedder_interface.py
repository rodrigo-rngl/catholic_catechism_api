from abc import ABC, abstractmethod
from typing import List, Generic

from src.application.DTOs.QueryEmbedding import QueryEmbeddingType
from src.application.DTOs.IngestionEmbeddings import IngestionEmbeddingsType


class FastembedEmbedderInterface(ABC, Generic[IngestionEmbeddingsType, QueryEmbeddingType]):
    @abstractmethod
    async def embed_ingestion(self, texts: List[str]) -> IngestionEmbeddingsType:
        pass

    @abstractmethod
    async def embed_query(self, query: str) -> QueryEmbeddingType:
        pass
