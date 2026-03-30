from typing import List

from src.application.DTOs.SearchOutput import SearchOutput

from src.application.DTOs.SearchPipelineResult import SearchSuccess
from src.application.services.QueryContextValidator import QueryContextValidator

from src.infrastructure.information_retriever_base.vector_db_qdrant.qdrant_vector_db_repository import QdrantVectorDBRepository

from src.interface_adapters.interfaces.fastembed_embedder_interface import FastembedEmbedderInterface

from src.config.logger_config import setup_logger
logger = setup_logger(name="CatholicCatechismParagraphsSearcher")


class CatholicCatechismParagraphsSearcher:
    def __init__(self,
                 embedder: FastembedEmbedderInterface,
                 repository: QdrantVectorDBRepository) -> None:
        self.repository = repository
        self.embedder = embedder

    async def search(self, query: str, top_k: int) -> SearchSuccess:
        logger.info(
            "CatholicCatechismParagraphsSearcher: Iniciando busca de parágrafos do catecismo da Igreja Católica..."
        )
        query_validation = await QueryContextValidator().validate(query=query)

        query_embedding = await self.embedder.embed_query(
            query=query)

        search_outputs: List[SearchOutput] = await self.repository.search_points(
            embedding=query_embedding, top_k=top_k)

        return SearchSuccess(search_outputs=search_outputs, query_validation=query_validation)
