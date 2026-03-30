from typing import List
from qdrant_client.http.models import PointStruct

from src.application.DTOs.Payload import Payload
from src.application.DTOs.IngestionEmbeddings import IngestionDenseEmbeddings

from src.interface_adapters.interfaces.ingestion_point_structures_creators_interface import IngestionPointStructuresCreatorsInterface

from src.infrastructure.information_retriever_base.vector_db_qdrant.ingestion_point_structures_creators.exceptions import IngestionPointStructuresCreatorException

from src.config.logger_config import setup_logger
logger = setup_logger(name="DenseIngestionPointStructuresCreators")


class DenseIngestionPointStructuresCreator(IngestionPointStructuresCreatorsInterface):
    def __init__(self, embeddings: IngestionDenseEmbeddings) -> None:
        self.embeddings = embeddings

    def create(self, payloads: List[Payload]) -> List[PointStruct]:
        logger.info(
            f"DenseIngestionPointStructuresCreators: Transformando {len(payloads)} payloads e embeddings em estruturas de pontos para ingestão..."
        )

        ingestion_points_list = []

        for dense, payload in zip(self.embeddings.dense, payloads):
            try:
                point = PointStruct(
                    id=payload.id,
                    vector={
                        "dense": dense
                    },
                    payload={"text": payload.text,
                             "localization": payload.localization}
                )

                ingestion_points_list.append(point)

            except Exception as exception:
                message = "Exceção ao criar uma estrutura de ponto de ingestão densa."
                logger.exception(
                    f"DenseIngestionPointStructuresCreators: {message}",
                    exc_info=exception,
                )
                raise IngestionPointStructuresCreatorException(
                    message) from exception

        logger.info(
            "DenseIngestionPointStructuresCreators: Estruturas de pontos para ingestão criadas com sucesso!"
        )

        return ingestion_points_list
