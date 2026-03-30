from src.infrastructure.information_retriever_base.vector_db_qdrant.collection_creators.exceptions.qdrant_collection_creator_factory_exception import (
    QdrantCollectionCreatorFactoryException,
)


class QdrantCollectionCreatorNotImplementedException(QdrantCollectionCreatorFactoryException):
    def __init__(self, message: str) -> None:
        super().__init__(message)
