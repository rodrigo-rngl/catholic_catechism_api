import asyncio
from typing import List, Any
from fastembed import TextEmbedding

from src.application.DTOs.QueryEmbedding import QueryDenseEmbedding
from src.application.DTOs.IngestionEmbeddings import IngestionDenseEmbeddings

from src.interface_adapters.interfaces.fastembed_embedder_interface import FastembedEmbedderInterface
from src.infrastructure.information_retriever_base.fastembed_embedder.exceptions.fastembed_dense_invalid_texts_type_exception import (
    FastembedDenseInvalidTextsTypeException,
)
from src.infrastructure.information_retriever_base.fastembed_embedder.exceptions.fastembed_embedder_exception import (
    FastembedEmbedderException,
)

from src.config.logger_config import setup_logger
logger = setup_logger(name="FastembedDenseEmbedder")


class FastembedDenseEmbedder(FastembedEmbedderInterface[IngestionDenseEmbeddings, QueryDenseEmbedding]):
    def __init__(self) -> None:
        self.embedding_models = self.__initialize_embedding_models()

    async def embed_ingestion(self, texts: List[str]) -> IngestionDenseEmbeddings:
        logger.info(
            f"FastembedDenseEmbedder: Transformando {len(texts)} parágrafos em embeddings..."
        )

        dense_vecs = await asyncio.to_thread(self.generate_dense_embedding, texts)

        logger.info("FastembedDenseEmbedder: Embeddings criados com sucesso!")
        return IngestionDenseEmbeddings(
            dense=dense_vecs
        )

    async def embed_query(self, query: str) -> QueryDenseEmbedding:
        logger.info(
            "FastembedDenseEmbedder: Transformando query em embeddings..."
        )

        dense_vec = await asyncio.to_thread(self.generate_dense_embedding, query)

        logger.info("FastembedDenseEmbedder: Embeddings criados com sucesso!")
        return QueryDenseEmbedding(
            dense=dense_vec)

    @classmethod
    def __initialize_embedding_models(cls) -> TextEmbedding:
        logger.info(
            "FastembedDenseEmbedder: Inicializando modelo de embeddings para busca semântica..."
        )

        logger.info("FastembedDenseEmbedder: Inicializando o modelo de embedding...")
        dense_embedding_model = TextEmbedding(
            "sentence-transformers/all-MiniLM-L6-v2")
        logger.info("FastembedDenseEmbedder: O modelo foi inicializado com sucesso!")

        return dense_embedding_model

    def generate_dense_embedding(self, texts: str | List[str]) -> List[Any]:
        dense_model = self.embedding_models

        try:
            dense_embedding = dense_model.embed(texts)
        except Exception as exception:
            message = "Exceção ao gerar dense embedding."
            if isinstance(texts, list):
                message = "Exceção ao gerar dense embeddings."

            logger.exception(
                f"FastembedDenseEmbedder: {message}",
                exc_info=exception,
            )
            raise FastembedEmbedderException(message) from exception

        if isinstance(texts, str):
            return next(iter(dense_embedding)).tolist()
        if isinstance(texts, list):
            return [vector.tolist() for vector in dense_embedding]

        raise FastembedDenseInvalidTextsTypeException(
            "O tipo de 'texts' não é válido.")
