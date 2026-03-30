from typing import Literal
from functools import lru_cache

from src.infrastructure.information_retriever_base.fastembed_embedder.fastembed_dense_embedder import FastembedDenseEmbedder
from src.infrastructure.information_retriever_base.fastembed_embedder.fastembed_hybrid_embedder import FastembedHybridEmbedder
from src.infrastructure.information_retriever_base.fastembed_embedder.exceptions.fastembed_embedder_not_implemented_exception import (
    FastembedEmbedderNotImplementedException,
)

from src.interface_adapters.interfaces.fastembed_embedder_interface import FastembedEmbedderInterface

from src.config.logger_config import setup_logger
logger = setup_logger(name="FastembedEmbedderFactory")


class FastembedEmbedderFactory:
    def __init__(self, search_type: Literal['Semântica', 'Esparsa', 'Híbrida']) -> None:
        self.search_type = search_type

    def produce(self) -> FastembedEmbedderInterface:
        if self.search_type == 'Híbrida':
            return get_fastembed_hybrid_embedder()
        if self.search_type == 'Semântica':
            return get_fastembed_dense_embedder()

        else:
            raise FastembedEmbedderNotImplementedException(
                f"Não há implementação de Embedder para o tipo de busca '{self.search_type}'.")


@lru_cache(maxsize=1)
def get_fastembed_hybrid_embedder() -> FastembedHybridEmbedder:
    return FastembedHybridEmbedder()


@lru_cache(maxsize=1)
def get_fastembed_dense_embedder() -> FastembedDenseEmbedder:
    return FastembedDenseEmbedder()
