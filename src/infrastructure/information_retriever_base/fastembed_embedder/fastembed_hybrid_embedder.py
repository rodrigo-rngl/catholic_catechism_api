import asyncio
import numpy as np
from typing import Tuple, List, Any
from fastembed import TextEmbedding
from fastembed.sparse.bm25 import Bm25
from fastembed.late_interaction import LateInteractionTextEmbedding

from src.application.DTOs.QueryEmbedding import QueryHybridEmbedding
from src.application.DTOs.QueryEmbedding import SparseDict as QuerySparseDict
from src.application.DTOs.IngestionEmbeddings import IngestionHybridEmbeddings
from src.application.DTOs.IngestionEmbeddings import SparseDict as IngestionSparseDict

from src.interface_adapters.interfaces.fastembed_embedder_interface import FastembedEmbedderInterface
from src.infrastructure.information_retriever_base.fastembed_embedder.exceptions.fastembed_hybrid_dense_invalid_texts_type_exception import (
    FastembedHybridDenseInvalidTextsTypeException,
)
from src.infrastructure.information_retriever_base.fastembed_embedder.exceptions.fastembed_hybrid_late_invalid_texts_type_exception import (
    FastembedHybridLateInvalidTextsTypeException,
)
from src.infrastructure.information_retriever_base.fastembed_embedder.exceptions.fastembed_hybrid_sparse_invalid_texts_type_exception import (
    FastembedHybridSparseInvalidTextsTypeException,
)
from src.infrastructure.information_retriever_base.fastembed_embedder.exceptions.fastembed_embedder_exception import (
    FastembedEmbedderException,
)


from src.config.logger_config import setup_logger
logger = setup_logger(name="FastembedHybridEmbedder")


class FastembedHybridEmbedder(FastembedEmbedderInterface[IngestionHybridEmbeddings, QueryHybridEmbedding]):
    def __init__(self) -> None:
        self.embedding_models = self.__initialize_embedding_models()

    async def embed_ingestion(self, texts: List[str]) -> IngestionHybridEmbeddings:
        logger.info(
            f"FastembedHybridEmbedder: Transformando {len(texts)} parágrafos em embeddings..."
        )

        dense_task = asyncio.to_thread(self.generate_dense_embedding, texts)
        sparse_task = asyncio.to_thread(self.generate_sparse_embedding, texts)
        late_task = asyncio.to_thread(self.generate_late_embedding, texts)

        dense_vecs, sparse_dicts, late_mats = await asyncio.gather(
            dense_task, sparse_task, late_task
        )

        logger.info("FastembedHybridEmbedder: Embeddings criados com sucesso!")
        return IngestionHybridEmbeddings(
            dense=dense_vecs,
            sparse=sparse_dicts,
            late=late_mats
        )

    async def embed_query(self, query: str) -> QueryHybridEmbedding:
        logger.info(
            "FastembedHybridEmbedder: Transformando query em embeddings..."
        )

        dense_task = asyncio.to_thread(self.generate_dense_embedding, query)
        sparse_task = asyncio.to_thread(self.generate_sparse_embedding, query)
        late_task = asyncio.to_thread(self.generate_late_embedding, query)

        dense_vec, sparse_dict, late_mat = await asyncio.gather(
            dense_task, sparse_task, late_task
        )

        logger.info("FastembedHybridEmbedder: Embeddings criados com sucesso!")
        return QueryHybridEmbedding(
            dense=dense_vec,
            sparse=sparse_dict,
            late=late_mat
        )

    @classmethod
    def __initialize_embedding_models(cls) -> Tuple[TextEmbedding, Bm25, LateInteractionTextEmbedding]:
        logger.info(
            "FastembedHybridEmbedder: Inicializando modelos de embeddings híbridos..."
        )

        logger.info("FastembedHybridEmbedder: Inicializando o dense embedding...")
        dense_embedding_model = TextEmbedding(
            "sentence-transformers/all-MiniLM-L6-v2")
        logger.info("FastembedHybridEmbedder: O dense embedding foi inicializado com sucesso!")

        logger.info("FastembedHybridEmbedder: Inicializando o sparse embedding...")
        sparse_embedding_model = Bm25("Qdrant/bm25")
        logger.info("FastembedHybridEmbedder: O sparse embedding foi inicializado com sucesso!")

        logger.info("FastembedHybridEmbedder: Inicializando o late interaction embedding...")
        late_embedding_model = LateInteractionTextEmbedding(
            "colbert-ir/colbertv2.0")
        logger.info(
            "FastembedHybridEmbedder: O late interaction embedding foi inicializado com sucesso!"
        )

        return dense_embedding_model, sparse_embedding_model, late_embedding_model

    def generate_dense_embedding(self, texts: str | List[str]) -> List[Any]:
        dense_model, _, _ = self.embedding_models

        try:
            dense_embedding = dense_model.embed(texts)
        except Exception as exception:
            message = "Exceção ao gerar dense embedding."
            if isinstance(texts, list):
                message = "Exceção ao gerar dense embeddings."

            logger.exception(
                f"FastembedHybridEmbedder: {message}",
                exc_info=exception,
            )
            raise FastembedEmbedderException(message) from exception

        if isinstance(texts, str):
            return next(iter(dense_embedding)).tolist()
        if isinstance(texts, list):
            return [vector.tolist() for vector in dense_embedding]

        raise FastembedHybridDenseInvalidTextsTypeException(
            "O tipo de 'texts' não é válido.")

    def generate_sparse_embedding(self, texts: str | List[str]) -> Any:
        _, sparse_model, _ = self.embedding_models

        try:
            sparse_embedding = sparse_model.embed(texts)
        except Exception as exception:
            message = "Exceção ao gerar sparse embedding."
            if isinstance(texts, list):
                message = "Exceção ao gerar sparse embeddings."

            logger.exception(
                f"FastembedHybridEmbedder: {message}",
                exc_info=exception,
            )
            raise FastembedEmbedderException(message) from exception

        if isinstance(texts, str):
            sparse_dict_raw: dict[str, np.ndarray] = next(
                iter(sparse_embedding)).as_object()
            sparse_dict = {k: v.tolist() for k, v in sparse_dict_raw.items()}
            return QuerySparseDict(indices=sparse_dict['indices'], values=sparse_dict["values"])

        if isinstance(texts, list):
            sparse_dicts_raw = [dictionary.as_object()
                                for dictionary in sparse_embedding]
            sparse_dicts = []
            for dictionary in sparse_dicts_raw:
                sparse_dict = {k: v.tolist() for k, v in dictionary.items()}
                sparse_dicts.append(IngestionSparseDict(
                    indices=sparse_dict['indices'], values=sparse_dict["values"]))
            return sparse_dicts

        raise FastembedHybridSparseInvalidTextsTypeException(
            "O tipo de 'texts' não é válido.")

    def generate_late_embedding(self, texts: str | List[str]) -> List[List[Any]]:
        _, _, late_model = self.embedding_models

        try:
            late_embedding = late_model.embed(texts)
        except Exception as exception:
            message = "Exceção ao gerar late embedding."
            if isinstance(texts, list):
                message = "Exceção ao gerar late embeddings."

            logger.exception(
                f"FastembedHybridEmbedder: {message}",
                exc_info=exception,
            )
            raise FastembedEmbedderException(message) from exception

        if isinstance(texts, str):
            return next(iter(late_embedding)).tolist()
        if isinstance(texts, list):
            return [matrix.tolist() for matrix in late_embedding]

        raise FastembedHybridLateInvalidTextsTypeException(
            "O tipo de 'texts' não é válido.")
