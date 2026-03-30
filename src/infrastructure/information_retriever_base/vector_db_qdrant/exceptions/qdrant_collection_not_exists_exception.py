from src.infrastructure.information_retriever_base.vector_db_qdrant.exceptions.qdrant_vector_db_exception import (
    QdrantVectorDBException,
)


class QdrantCollectionNotExistsException(QdrantVectorDBException):
    def __init__(self, message: str) -> None:
        super().__init__(message)


# Compatibilidade com nome usado anteriormente no arquivo.
class QdrantCollectionNotExistsExeception(QdrantCollectionNotExistsException):
    def __init__(self, message: str) -> None:
        super().__init__(message)
