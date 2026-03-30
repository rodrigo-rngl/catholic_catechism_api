from qdrant_client.http.models import VectorParams, Distance

from src.infrastructure.information_retriever_base.vector_db_qdrant.context_manager.qdrant_vector_db_connection_handler import QdrantVectorDBConnectionHandler

from src.interface_adapters.interfaces.qdrant_collection_creator_interface import QdrantCollectionCreatorInterface

from src.infrastructure.information_retriever_base.vector_db_qdrant.collection_creators.exceptions import QdrantCollectionCreatorException

from src.config.logger_config import setup_logger
logger = setup_logger(name="QdrantDenseCollectionCreator")


class QdrantDenseCollectionCreator(QdrantCollectionCreatorInterface):
    async def create(self, collection_name: str) -> None:
        async with QdrantVectorDBConnectionHandler() as qdrant:
            try:
                logger.info(
                    f"QdrantDenseCollectionCreator: Criando a coleção '{collection_name}'..."
                )
                await qdrant.client.create_collection(
                    collection_name=collection_name,
                    vectors_config={
                        "dense": VectorParams(size=384, distance=Distance.COSINE)}
                )

                logger.info(
                    f"QdrantDenseCollectionCreator: A coleção '{collection_name}' foi criada com sucesso."
                )

            except Exception as exception:
                message = f"Exceção ao criar a coleção '{collection_name}' no Qdrant."
                logger.exception(
                    f"QdrantDenseCollectionCreator: {message}",
                    exc_info=exception,
                )
                raise QdrantCollectionCreatorException(message) from exception
