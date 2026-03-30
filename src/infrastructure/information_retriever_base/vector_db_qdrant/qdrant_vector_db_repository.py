from typing import List
from qdrant_client.http.models import PointStruct
from datetime import datetime, timedelta, timezone

from src.application.DTOs.SearchOutput import SearchOutput
from src.application.DTOs.RetrieveOutput import RetrieveOutput
from src.application.DTOs.QueryEmbedding import QueryEmbeddingBase

from src.infrastructure.information_retriever_base.vector_db_qdrant.context_manager.qdrant_vector_db_connection_handler import QdrantVectorDBConnectionHandler

from src.interface_adapters.interfaces.qdrant_points_searcher_interface import QdrantPointsSearcherInterface
from src.interface_adapters.interfaces.qdrant_collection_creator_interface import QdrantCollectionCreatorInterface

from src.infrastructure.information_retriever_base.vector_db_qdrant.exceptions import (
    QdrantCollectionCreatorNotProvidedException,
    QdrantCollectionNotExistsException,
    QdrantCollectionNotPopulatedException,
    QdrantPointsSearcherNotProvidedException,
    QdrantVectorDBException
)

from src.config.logger_config import setup_logger
logger = setup_logger(name="QdrantVectorDBRepository")


class QdrantVectorDBRepository:
    def __init__(
        self,
        collection_name: str,
        collection_creator: QdrantCollectionCreatorInterface | None = None,
        points_searcher: QdrantPointsSearcherInterface | None = None,
    ) -> None:
        self.collection_name = collection_name
        self.collection_creator = collection_creator
        self.points_searcher = points_searcher

    async def create_collection(self, recreate_if_already_populated: bool = False) -> None:
        logger.info(
            "QdrantVectorDBRepository: Iniciando criação/verificação da coleção '%s'. recreate_if_already_populated=%s",
            self.collection_name,
            recreate_if_already_populated,
        )

        if self.collection_creator is None:
            logger.exception(
                "QdrantVectorDBRepository: Criador de coleção não foi informado para a coleção '%s'.",
                self.collection_name,
            )
            raise QdrantCollectionCreatorNotProvidedException(
                "O criador de coleção não foi passado. O criador de coleção não pode ser None."
            )

        if not await self.__collection_already_exist():
            logger.info(
                "QdrantVectorDBRepository: A coleção '%s' será criada.",
                self.collection_name,
            )
            await self.collection_creator.create(collection_name=self.collection_name)
            return None

        if await self.collection_already_populated():
            logger.info(
                "QdrantVectorDBRepository: A coleção '%s' já existe e já possui dados.",
                self.collection_name,
            )

            if recreate_if_already_populated:
                logger.info(
                    "QdrantVectorDBRepository: A coleção '%s' será recriada.",
                    self.collection_name,
                )
                await self.__delete_collection()
                await self.collection_creator.create(collection_name=self.collection_name)
            else:
                logger.info(
                    "QdrantVectorDBRepository: recriação desabilitada para '%s'.",
                    self.collection_name,
                )
            return None

        logger.info(
            "QdrantVectorDBRepository: A coleção '%s' já existe, mas está vazia.",
            self.collection_name,
        )

    async def upsert_points(self, ingestion_points: List[PointStruct]) -> None:
        logger.info(
            "QdrantVectorDBRepository: Enviando %s estruturas de pontos de ingestão para '%s'...",
            len(ingestion_points),
            self.collection_name,
        )

        try:
            async with QdrantVectorDBConnectionHandler() as qdrant:
                await qdrant.client.upsert(
                    collection_name=self.collection_name,
                    points=ingestion_points,
                )

                logger.info(
                    "QdrantVectorDBRepository: As estruturas de pontos de ingestão foram enviadas com sucesso para '%s'.",
                    self.collection_name,
                )
        except Exception as exception:
            message = f"Exceção ao inserir estruturas de pontos de ingestão na coleção '{self.collection_name}'"
            logger.exception(
                f"QdrantVectorDBRepository: {message}", exc_info=exception)
            raise QdrantVectorDBException(message) from exception

    async def retrieve_points(self, paragraph_numbers: List[int]) -> List[RetrieveOutput]:
        logger.info(
            "QdrantVectorDBRepository: Iniciando a recuperação de pontos vetoriais...")

        utc_minus_3 = timezone(timedelta(hours=-3))
        start_time = datetime.now(tz=utc_minus_3)

        if not await self.collection_already_populated():
            message = f"A coleção '{self.collection_name}' não possui dados para recuperar pontos vetoriais."
            logger.exception(
                f"QdrantVectorDBRepository: {message}"
            )
            raise QdrantCollectionNotPopulatedException(message)

        try:
            async with QdrantVectorDBConnectionHandler() as qdrant:
                response = await qdrant.client.retrieve(
                    collection_name=self.collection_name,
                    ids=paragraph_numbers,
                )

                retrieve_output = [
                    RetrieveOutput(
                        text=point.payload["text"],
                        localization=point.payload["localization"],
                    )
                    for point in response
                    if point.payload is not None
                ]

                search_time_ms = self.__calculate_search_time(
                    start_time=start_time)

                logger.info(
                    "QdrantVectorDBRepository: Pontos vetoriais foram recuperados com sucesso da coleção '%s'. Tempo de Busca: %sms",
                    self.collection_name,
                    search_time_ms,
                )
                return retrieve_output
        except Exception as exception:
            message = f"Exceção ao recuperar os pontos vetoriais na coleção '{self.collection_name}'."
            logger.exception(
                f"QdrantVectorDBRepository: {message}", exc_info=exception
            )
            raise QdrantVectorDBException(message) from exception

    async def search_points(
        self,
        embedding: QueryEmbeddingBase,
        top_k: int,
    ) -> List[SearchOutput]:
        logger.info(
            "QdrantVectorDBRepository: Iniciando a busca de pontos vetoriais na coleção '%s' com top_k=%s...",
            self.collection_name,
            top_k,
        )

        utc_minus_3 = timezone(timedelta(hours=-3))
        start_time = datetime.now(tz=utc_minus_3)

        if self.points_searcher is None:
            message = f'O buscador de pontos vetoriais não foi passado para a coleção {self.collection_name}. O buscador não pode ser None.'
            logger.exception(f'QdrantVectorDBRepository: {message}')
            raise QdrantPointsSearcherNotProvidedException(message)

        if not await self.collection_already_populated():
            message = f"A coleção '{self.collection_name}' não possui dados para realizar busca de pontos vetoriais."
            logger.exception(f'QdrantVectorDBRepository: {message}')
            raise QdrantCollectionNotPopulatedException(message)

        try:
            search_outputs: List[SearchOutput] = await self.points_searcher.search(
                collection_name=self.collection_name,
                embedding=embedding,
                top_k=top_k,
            )

            search_time_ms = self.__calculate_search_time(
                start_time=start_time)

            logger.info(
                "QdrantVectorDBRepository: Pontos vetoriais retornados com sucesso da coleção '%s'. Tempo de Busca: %sms",
                self.collection_name,
                search_time_ms,
            )

            return search_outputs
        except Exception as exception:
            message = f"Exceção ao buscar os pontos vetoriais na coleção '{self.collection_name}'."
            logger.exception(
                f'QdrantVectorDBRepository: {message}', exc_info=exception)
            raise QdrantVectorDBException(message) from exception

    async def get_collection_points_count(self) -> int:
        logger.info(
            "QdrantVectorDBRepository: Buscando quantidade de pontos da coleção '%s'...",
            self.collection_name)

        if not await self.__collection_already_exist():
            message = f"A coleção '{self.collection_name}' não existe! Com isso, não dá para checar se a mesma está populada."
            logger.exception(f'QdrantVectorDBRepository: {message}')
            raise QdrantCollectionNotExistsException(message)

        try:
            async with QdrantVectorDBConnectionHandler() as qdrant:
                collection_info = await qdrant.client.get_collection(self.collection_name)
                logger.info(
                    "QdrantVectorDBRepository: A coleção '%s' agora possui %s pontos de ingestão.",
                    self.collection_name,
                    collection_info.points_count,
                )
                if collection_info.points_count is None:
                    return 0

                return collection_info.points_count
        except Exception as exception:
            message = f"Exceção ao obter informações sobre a coleção '{self.collection_name}'."
            logger.exception(
                f'QdrantVectorDBRepository: {message}', exc_info=exception)
            raise QdrantVectorDBException(message) from exception

    async def collection_already_populated(self) -> bool:
        logger.info(
            "QdrantVectorDBRepository: Verificando se a coleção '%s' está populada...",
            self.collection_name,
        )

        return bool(await self.get_collection_points_count())

    async def __collection_already_exist(self) -> bool:
        logger.info(
            "QdrantVectorDBRepository: Verificando se a coleção '%s' existe...",
            self.collection_name,
        )

        try:
            async with QdrantVectorDBConnectionHandler() as qdrant:
                exists = await qdrant.client.collection_exists(
                    collection_name=self.collection_name,
                )
                logger.info("QdrantVectorDBRepository: Coleção '%s' existe: %s",
                            self.collection_name, exists)
                return exists
        except Exception as exception:
            message = f"Exceção ao verificar se a coleção '{self.collection_name}' no Qdrant existe."
            logger.exception(
                f'QdrantVectorDBRepository: {message}', exc_info=exception)
            raise QdrantVectorDBException(message) from exception

    async def __delete_collection(self) -> None:
        logger.info(
            "QdrantVectorDBRepository: Excluindo coleção '%s'...", self.collection_name)

        try:
            async with QdrantVectorDBConnectionHandler() as qdrant:
                await qdrant.client.delete_collection(collection_name=self.collection_name)
                logger.info(
                    "QdrantVectorDBRepository: A coleção '%s' foi excluída com sucesso.",
                    self.collection_name,
                )
        except Exception as exception:
            message = f"Exceção ao excluir a coleção '{self.collection_name}' do Qdrant."
            logger.exception(
                f'QdrantVectorDBRepository: {message}', exc_info=exception)
            raise QdrantVectorDBException(message) from exception

    @classmethod
    def __calculate_search_time(cls, start_time: datetime) -> int:
        end_time = datetime.now(tz=start_time.tzinfo)
        return int((end_time - start_time).total_seconds() * 1000)
