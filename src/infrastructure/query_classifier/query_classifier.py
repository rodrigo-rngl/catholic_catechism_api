import os
from typing import cast
from huggingface_hub import AsyncInferenceClient

from src.application.DTOs.QueryValidation import QueryValidation, ScopeLiteral, get_query_scope_labels

from src.infrastructure.query_classifier.exceptions.query_classifier_exception import QueryClassifierException
from src.infrastructure.query_classifier.exceptions.huggingface_inference_connection_handler_exception import HuggingFaceInferenceConnectionHandlerException


from src.config.logger_config import setup_logger
logger = setup_logger(name="HuggingFaceInferenceConnectionHandler")


class HuggingFaceInferenceConnectionHandler:
    def __init__(self) -> None:
        self.__token = os.getenv("HF_TOKEN")
        self.client = self.__create_inference_client()

    def __create_inference_client(self) -> AsyncInferenceClient:
        if not self.__token:
            raise HuggingFaceInferenceConnectionHandlerException(
                "Variável de ambiente 'HF_TOKEN' não informada."
            )

        logger.info(
            "HuggingFaceInferenceConnectionHandler: Criando cliente de inferência da Hugging Face..."
        )

        return AsyncInferenceClient(token=self.__token)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.close()


class QueryClassifier:
    def __init__(self) -> None:
        self.__model = "facebook/bart-large-mnli"
        self.__candidate_labels = get_query_scope_labels()

    async def classify(self, query: str) -> QueryValidation:
        try:
            async with HuggingFaceInferenceConnectionHandler() as handler:
                logger.info(
                    "QueryClassifier: Enviando requisição para classificação da query..."
                )

                formatted_candidate_labels = [label.replace(
                    "_", " ") for label in self.__candidate_labels]

                result = await handler.client.zero_shot_classification(
                    model=self.__model,
                    text=query,
                    candidate_labels=formatted_candidate_labels,
                )

                return QueryValidation(
                    scope=cast(
                        ScopeLiteral, result[0].label.replace(" ", "_")),
                    confidence=result[0].score
                )

        except Exception as exception:
            message = "Exceção ao classificar a query."
            logger.exception(
                f"QueryClassifier: {message}",
                exc_info=exception,
            )
            raise QueryClassifierException(message) from exception
