from typing import cast

from src.application.DTOs.QueryValidation import QueryValidation, ScopeLiteral, get_query_scope_labels

from src.infrastructure.query_classifier.exceptions.query_classifier_exception import QueryClassifierException

from src.infrastructure.query_classifier.context_manager.hugging_face_inference_api_connection_handler import HuggingFaceInferenceConnectionHandler

from src.config.logger_config import setup_logger
logger = setup_logger(name="HuggingFaceInferenceConnectionHandler")


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
