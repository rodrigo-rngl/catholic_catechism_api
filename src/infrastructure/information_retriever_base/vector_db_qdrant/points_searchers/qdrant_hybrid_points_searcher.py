from typing import List
from qdrant_client.http.models import Prefetch, SparseVector, QueryResponse
from src.application.DTOs.SearchOutput import SearchOutput
from src.application.DTOs.QueryEmbedding import QueryHybridEmbedding
from src.interface_adapters.interfaces.qdrant_points_searcher_interface import QdrantPointsSearcherInterface
from src.infrastructure.information_retriever_base.vector_db_qdrant.context_manager.qdrant_vector_db_connection_handler import QdrantVectorDBConnectionHandler
from src.infrastructure.information_retriever_base.vector_db_qdrant.points_searchers.exceptions import (
    QdrantPointsSearcherException,
)

from src.config.logger_config import setup_logger
logger = setup_logger(name="QdrantHybridPointsSearcher")


class QdrantHybridPointsSearcher(QdrantPointsSearcherInterface[QueryHybridEmbedding]):
    async def search(self, collection_name: str, embedding: QueryHybridEmbedding, top_k: int) -> List[SearchOutput]:
        async with QdrantVectorDBConnectionHandler() as qdrant:
            try:
                search_result = await qdrant.client.query_points(
                    collection_name=collection_name,
                    prefetch=[
                        Prefetch(
                            query=embedding.dense,
                            using="dense",
                            limit=20,
                        ),
                        Prefetch(
                            query=SparseVector(
                                **embedding.sparse.model_dump()),
                            using="sparse",
                            limit=20,
                        ),
                    ],
                    query=embedding.late,
                    using="colbertv2.0",
                    with_payload=True,
                    limit=top_k
                )

                return self.__create_search_outputs(search_result)

            except Exception as exception:
                message = f"Exceção ao realizar busca híbrida na coleção '{collection_name}'."
                logger.exception(
                    f"QdrantHybridPointsSearcher: {message}",
                    exc_info=exception,
                )
                raise QdrantPointsSearcherException(message) from exception

    @classmethod
    def __create_search_outputs(cls, search_result: QueryResponse) -> List[SearchOutput]:
        search_outputs_list = [SearchOutput(
            text=point.payload['text'],
            localization=point.payload['localization'],
            similarity_score=point.score
        ) for point in search_result.points if point.payload != None]

        return search_outputs_list
