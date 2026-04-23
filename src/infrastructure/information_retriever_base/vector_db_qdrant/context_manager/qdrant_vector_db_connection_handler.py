import os
from qdrant_client import AsyncQdrantClient
from src.infrastructure.information_retriever_base.vector_db_qdrant.exceptions.qdrant_vector_db_exception import (
    QdrantVectorDBException,
)

from src.config.logger_config import setup_logger
logger = setup_logger(name="QdrantVectorDBConnectionHandler")


class QdrantVectorDBConnectionHandler:
    def __init__(self) -> None:
        self.__url = "http://qdrant:6333"

        self.client = self.__create_db_client()

    def __create_db_client(self) -> AsyncQdrantClient:
        try:
            return AsyncQdrantClient(
                url=self.__url,
                prefer_grpc=True,
                timeout=60
            )
        except Exception as exception:
            message = "Exceção ao gerar conexão com banco de dados vetorial Qdrant."
            logger.exception(
                f"QdrantVectorDBConnectionHandler: {message}",
                exc_info=exception,
            )
            raise QdrantVectorDBException(message) from exception

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.close()
