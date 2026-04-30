from src.infrastructure.query_classifier.exceptions.query_classifier_exception import (
    QueryClassifierException,
)


class HuggingFaceInferenceConnectionHandlerException(QueryClassifierException):
    def __init__(self, message: str) -> None:
        super().__init__(message)
