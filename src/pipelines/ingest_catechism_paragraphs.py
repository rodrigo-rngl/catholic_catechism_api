import asyncio

from typing import Literal

from src.application.services.CatechismParagraphsScrapper import CatechismParagraphsScrapper
from src.application.services.CatechismParagraphsCollectionIngestor import CatechismParagraphsCollectionIngestor
from src.infrastructure.information_retriever_base.vector_db_qdrant.qdrant_vector_db_repository import QdrantVectorDBRepository
from src.infrastructure.information_retriever_base.fastembed_embedder.fastembed_embedder_factory import FastembedEmbedderFactory
from src.infrastructure.information_retriever_base.vector_db_qdrant.collection_creators.qdrant_collection_creator_factory import QdrantCollectionCreatorFactory


async def ingest() -> None:
    collection_name = "Parágrafos do Catecismo (Hybrid Search)"
    search_type: Literal["Semântica", "Híbrida"] = "Híbrida"

    collection_creator = QdrantCollectionCreatorFactory(
        search_type=search_type).produce()

    repository = QdrantVectorDBRepository(
        collection_name=collection_name, collection_creator=collection_creator)

    await repository.create_collection()

    if await repository.collection_already_populated():
        print("A coleção já populada, ingestão ignorada!")
        return None

    scrapper = CatechismParagraphsScrapper()
    payloads = scrapper.scrape()

    embedder = FastembedEmbedderFactory(search_type=search_type).produce()

    ingestor = CatechismParagraphsCollectionIngestor(
        embedder=embedder, repository=repository)

    await ingestor.ingest(payloads=payloads, batch_size=10)

    print("Ingestão finalizada com sucesso!")

asyncio.run(ingest())
