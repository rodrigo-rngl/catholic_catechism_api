from typing import List
from qdrant_client.http.models import QueryResponse

from src.application.DTOs.SearchOutput import SearchOutput
from src.application.DTOs.QueryEmbedding import QueryDenseEmbedding

from src.infrastructure.information_retriever_base.vector_db_qdrant.context_manager.qdrant_vector_db_connection_handler import QdrantVectorDBConnectionHandler

from src.interface_adapters.interfaces.qdrant_points_searcher_interface import QdrantPointsSearcherInterface

from src.infrastructure.information_retriever_base.vector_db_qdrant.points_searchers.exceptions import (
    QdrantPointsSearcherException
)

from src.config.logger_config import setup_logger
logger = setup_logger(name="QdrantDensePointsSearcher")


class QdrantDensePointsSearcher(QdrantPointsSearcherInterface[QueryDenseEmbedding]):
    async def search(self, collection_name: str, embedding: QueryDenseEmbedding, top_k: int) -> List[SearchOutput]:
        async with QdrantVectorDBConnectionHandler() as qdrant:
            try:
                search_result = await qdrant.client.query_points(
                    collection_name=collection_name,
                    query=embedding.dense,
                    using="dense",
                    limit=top_k
                )

            except Exception as exception:
                message = f"Exceção ao realizar busca semântica na coleção '{collection_name}'."
                logger.exception(
                    f"QdrantDensePointsSearcher: {message}",
                    exc_info=exception,
                )
                raise QdrantPointsSearcherException(message) from exception

            return self.__create_search_outputs(search_result)

    @classmethod
    def __create_search_outputs(cls, search_result: QueryResponse) -> List[SearchOutput]:
        search_outputs_list = [SearchOutput(
            text=point.payload['text'],
            similarity_score=point.score
        ) for point in search_result.points if point.payload != None]

        return search_outputs_list
