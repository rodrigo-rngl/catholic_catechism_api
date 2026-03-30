import uuid
from typing import List
from src.application.DTOs.Payload import Payload
from qdrant_client.http.models import PointStruct, SparseVector
from src.application.DTOs.IngestionEmbeddings import IngestionHybridEmbeddings
from src.interface_adapters.interfaces.ingestion_point_structures_creators_interface import IngestionPointStructuresCreatorsInterface
from src.infrastructure.information_retriever_base.vector_db_qdrant.ingestion_point_structures_creators.exceptions import (
    IngestionPointStructuresCreatorException,
)

from src.config.logger_config import setup_logger

logger = setup_logger(name="HybridIngestionPointStructuresCreators")


class HybridIngestionPointStructuresCreator(IngestionPointStructuresCreatorsInterface):
    def __init__(self, embeddings: IngestionHybridEmbeddings) -> None:
        self.embeddings = embeddings

    def create(self, payloads: List[Payload]) -> List[PointStruct]:
        logger.info(
            f"HybridIngestionPointStructuresCreators: Transformando {len(payloads)} payloads e embeddings em estruturas de pontos para ingestão..."
        )

        ingestion_points_list = []

        for sparse, dense, late, payload in zip(self.embeddings.sparse, self.embeddings.dense, self.embeddings.late, payloads):
            try:
                point = PointStruct(
                    id=payload.id,
                    vector={
                        "dense": dense,
                        "colbertv2.0": late,
                        "sparse": SparseVector(indices=sparse.indices,
                                               values=sparse.values)
                    },
                    payload={"text": payload.text,
                             "localization": payload.localization}
                )

                ingestion_points_list.append(point)

            except Exception as exception:
                message = "Exceção ao criar uma estrutura de ponto de ingestão híbrida."
                logger.exception(
                    f"HybridIngestionPointStructuresCreators: {message}",
                    exc_info=exception,
                )
                raise IngestionPointStructuresCreatorException(message) from exception

        logger.info(
            "HybridIngestionPointStructuresCreators: Estruturas de pontos para ingestão criadas com sucesso!"
        )

        return ingestion_points_list
