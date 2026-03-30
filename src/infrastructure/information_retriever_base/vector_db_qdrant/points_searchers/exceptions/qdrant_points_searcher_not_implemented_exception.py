from src.infrastructure.information_retriever_base.vector_db_qdrant.points_searchers.exceptions.qdrant_points_searcher_factory_exception import (
    QdrantPointsSearcherFactoryException,
)


class QdrantPointsSearcherNotImplementedException(QdrantPointsSearcherFactoryException):
    def __init__(self, message: str) -> None:
        super().__init__(message)
