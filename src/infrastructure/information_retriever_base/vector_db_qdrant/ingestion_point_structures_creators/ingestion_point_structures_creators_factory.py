from src.application.DTOs.IngestionEmbeddings import IngestionEmbeddingsBase, IngestionHybridEmbeddings, IngestionDenseEmbeddings

from src.infrastructure.information_retriever_base.vector_db_qdrant.ingestion_point_structures_creators.dense_ingestion_point_structures_creator import DenseIngestionPointStructuresCreator
from src.infrastructure.information_retriever_base.vector_db_qdrant.ingestion_point_structures_creators.hybrid_ingestion_point_structures_creator import HybridIngestionPointStructuresCreator
from src.infrastructure.information_retriever_base.vector_db_qdrant.ingestion_point_structures_creators.exceptions.ingestion_embeddings_not_supported_exception import IngestionEmbeddingsNotSupportedException

from src.interface_adapters.interfaces.ingestion_point_structures_creators_interface import IngestionPointStructuresCreatorsInterface


class IngestionPointStructuresCreatorsFactory:
    def __init__(self, embeddings: IngestionEmbeddingsBase) -> None:
        self.embeddings = embeddings

    def produce(self) -> IngestionPointStructuresCreatorsInterface:
        if isinstance(self.embeddings, IngestionHybridEmbeddings):
            return HybridIngestionPointStructuresCreator(embeddings=self.embeddings)
        if isinstance(self.embeddings, IngestionDenseEmbeddings):
            return DenseIngestionPointStructuresCreator(embeddings=self.embeddings)
        else:
            raise IngestionEmbeddingsNotSupportedException(
                'Não há implementação para o tipo de IngestorEmbeddigs fornecido.')
