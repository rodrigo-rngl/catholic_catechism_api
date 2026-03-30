from typing import Literal
import asyncio
from dotenv import load_dotenv
from src.application.services.CatechismParagraphsScrapper import CatechismParagraphsScrapper
from src.application.services.CatechismParagraphsCollectionIngestor import CatechismParagraphsCollectionIngestor
from src.infrastructure.information_retriever_base.qdrant.qdrant_information_retriever_base_repository import QdrantVectorDBRepository
from src.infrastructure.fastembed_embedder.fastembed_embedder_factory import FastembedEmbedderFactory
from src.infrastructure.information_retriever_base.qdrant.collection_creators. qdrant_collection_creator_factory import QdrantCollectionCreatorFactory


load_dotenv()


async def ingest() -> None:
    scrapper = CatechismParagraphsScrapper()
    payloads = scrapper.scrape()

    collection_name = "Parágrafos do Catecismo (Hybrid Search)"
    search_type: Literal["Semântica", "Híbrida"] = "Híbrida"

    collection_creator = QdrantCollectionCreatorFactory(
        search_type=search_type).produce()

    repository = QdrantVectorDBRepository(
        collection_name=collection_name, collection_creator=collection_creator)
    await repository.create_collection()

    embedder = FastembedEmbedderFactory(search_type=search_type).produce()

    ingestor = CatechismParagraphsCollectionIngestor(
        embedder=embedder, repository=repository)
    await ingestor.ingest(payloads=payloads, batch_size=5)

asyncio.run(ingest())
