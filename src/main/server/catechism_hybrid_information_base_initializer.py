import asyncio
import fcntl
from typing import TextIO

from src.application.DTOs.IngestionEmbeddings import IngestionHybridEmbeddings
from src.application.DTOs.QueryEmbedding import QueryHybridEmbedding
from src.application.services.CatechismParagraphsCollectionIngestor import (
    CatechismParagraphsCollectionIngestor,
)
from src.application.services.CatechismParagraphsScrapper import CatechismParagraphsScrapper
from src.infrastructure.information_retriever_base.fastembed_embedder.fastembed_embedder_factory import (
    FastembedEmbedderFactory,
)
from src.infrastructure.information_retriever_base.vector_db_qdrant.collection_creators.qdrant_collection_creator_factory import (
    QdrantCollectionCreatorFactory,
)
from src.infrastructure.information_retriever_base.vector_db_qdrant.qdrant_vector_db_repository import (
    QdrantVectorDBRepository,
)
from src.interface_adapters.interfaces.fastembed_embedder_interface import (
    FastembedEmbedderInterface,
)

from src.config.logger_config import setup_logger

logger = setup_logger(name="CatechismHybridInformationBaseInitializer")

LOCK_PATH = "/tmp/catechism_hybrid_information_base_ingestion.lock"
COLLECTION_NAME = "Parágrafos do Catecismo (Hybrid Search)"
SEARCH_TYPE = "Híbrida"


def __acquire_interprocess_lock(lock_path: str) -> TextIO:
    lock_file = open(lock_path, "w", encoding="utf-8")
    fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
    return lock_file


def __release_interprocess_lock(lock_file: TextIO) -> None:
    fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)
    lock_file.close()


async def initialize_hybrid_catechism_information_base() -> None:
    logger.info(
        "CatechismHybridInformationBaseInitializer: aguardando lock interprocesso em '%s'.",
        LOCK_PATH,
    )
    lock_file = await asyncio.to_thread(__acquire_interprocess_lock, LOCK_PATH)

    try:
        logger.info(
            "CatechismHybridInformationBaseInitializer: lock adquirido, verificando coleção '%s'.",
            COLLECTION_NAME,
        )

        collection_creator = QdrantCollectionCreatorFactory(
            search_type=SEARCH_TYPE
        ).produce()

        repository = QdrantVectorDBRepository(
            collection_name=COLLECTION_NAME,
            collection_creator=collection_creator,
        )

        await repository.create_collection(recreate_if_already_populated=False)

        if await repository.collection_already_populated():
            logger.info(
                "CatechismHybridInformationBaseInitializer: coleção já populada, ingestão ignorada."
            )
            return None

        logger.info(
            "CatechismHybridInformationBaseInitializer: coleção vazia, iniciando scraping e ingestão."
        )
        scrapper = CatechismParagraphsScrapper()
        payloads = await asyncio.to_thread(scrapper.scrape)

        embedder: FastembedEmbedderInterface[
            IngestionHybridEmbeddings, QueryHybridEmbedding
        ] = FastembedEmbedderFactory(search_type=SEARCH_TYPE).produce()

        ingestor = CatechismParagraphsCollectionIngestor(
            embedder=embedder, repository=repository
        )
        await ingestor.ingest(payloads=payloads, batch_size=3)

        logger.info(
            "CatechismHybridInformationBaseInitializer: ingestão concluída para a coleção '%s'.",
            COLLECTION_NAME,
        )
    finally:
        await asyncio.to_thread(__release_interprocess_lock, lock_file)
        logger.info("CatechismHybridInformationBaseInitializer: lock liberado.")
