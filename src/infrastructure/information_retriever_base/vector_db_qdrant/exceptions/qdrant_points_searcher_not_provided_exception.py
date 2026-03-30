from src.infrastructure.information_retriever_base.vector_db_qdrant.exceptions.qdrant_vector_db_exception import (
    QdrantVectorDBException,
)


class QdrantPointsSearcherNotProvidedException(QdrantVectorDBException):
    def __init__(self, message: str) -> None:
        super().__init__(message)
