from src.infrastructure.information_retriever_base.vector_db_qdrant.ingestion_point_structures_creators.exceptions.ingestion_point_structures_creator_factory_exception import (
    IngestionPointStructuresCreatorFactoryException,
)


class IngestionEmbeddingsNotSupportedException(IngestionPointStructuresCreatorFactoryException):
    def __init__(self, message: str) -> None:
        super().__init__(message)
