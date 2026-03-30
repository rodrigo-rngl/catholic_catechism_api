from src.infrastructure.information_retriever_base.fastembed_embedder.exceptions.fastembed_embedder_exception import (
    FastembedEmbedderException,
)


class FastembedEmbedderNotImplementedException(FastembedEmbedderException):
    def __init__(self, message: str) -> None:
        super().__init__(message)
