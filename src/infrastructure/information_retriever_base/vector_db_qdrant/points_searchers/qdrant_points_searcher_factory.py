from typing import Literal
from src.interface_adapters.interfaces.qdrant_points_searcher_interface import QdrantPointsSearcherInterface
from src.infrastructure.information_retriever_base.vector_db_qdrant.points_searchers.qdrant_dense_points_searcher import QdrantDensePointsSearcher
from src.infrastructure.information_retriever_base.vector_db_qdrant.points_searchers.qdrant_hybrid_points_searcher import QdrantHybridPointsSearcher
from src.infrastructure.information_retriever_base.vector_db_qdrant.points_searchers.exceptions.qdrant_points_searcher_not_implemented_exception import (
    QdrantPointsSearcherNotImplementedException,
)

from src.config.logger_config import setup_logger
logger = setup_logger(name="QdrantPointsSearcherFactory")


class QdrantPointsSearcherFactory:
    def __init__(self, search_type: Literal['Semântica', 'Esparsa', 'Híbrida']) -> None:
        self.search_type = search_type

    def produce(self) -> QdrantPointsSearcherInterface:
        if self.search_type == 'Híbrida':
            return QdrantHybridPointsSearcher()
        if self.search_type == 'Semântica':
            return QdrantDensePointsSearcher()
        else:
            raise QdrantPointsSearcherNotImplementedException(
                f"Não há implementação de Buscador de Pontos Vetoriais para o tipo de busca '{self.search_type}'.")
