from qdrant_client import models
from qdrant_client.http.models import VectorParams, Distance
from src.interface_adapters.interfaces.qdrant_collection_creator_interface import QdrantCollectionCreatorInterface
from src.infrastructure.information_retriever_base.vector_db_qdrant.context_manager.qdrant_vector_db_connection_handler import QdrantVectorDBConnectionHandler
from src.infrastructure.information_retriever_base.vector_db_qdrant.collection_creators.exceptions import (
    QdrantCollectionCreatorException
)

from src.config.logger_config import setup_logger
logger = setup_logger(name="QdrantHybridCollectionCreator")


class QdrantHybridCollectionCreator(QdrantCollectionCreatorInterface):
    async def create(self, collection_name: str) -> None:
        async with QdrantVectorDBConnectionHandler() as qdrant:
            try:
                logger.info(
                    f"QdrantHybridCollectionCreator: Criando a coleção '{collection_name}'..."
                )
                await qdrant.client.create_collection(
                    collection_name=collection_name,
                    vectors_config={
                        "dense": VectorParams(size=384, distance=Distance.COSINE),
                        "colbertv2.0": VectorParams(
                            size=128,
                            distance=Distance.COSINE,
                            multivector_config=models.MultiVectorConfig(
                                comparator=models.MultiVectorComparator.MAX_SIM,
                            ),
                        ),
                    },
                    sparse_vectors_config={
                        "sparse": models.SparseVectorParams(modifier=models.Modifier.IDF),
                    },
                )

                logger.info(
                    f"QdrantHybridCollectionCreator: A coleção '{collection_name}' foi criada com sucesso."
                )

            except Exception as exception:
                message = f"Exceção ao criar a coleção híbrida '{collection_name}' no Qdrant."
                logger.exception(
                    f"QdrantHybridCollectionCreator: {message}",
                    exc_info=exception,
                )
                raise QdrantCollectionCreatorException(message) from exception
