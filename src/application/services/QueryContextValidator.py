from src.application.DTOs.QueryValidation import QueryValidation

from src.infrastructure.query_classifier.query_classifier import QueryClassifier

from src.application.services.exceptions.query_validator_exceptions import QueryOutOfScopeException

from src.config.logger_config import setup_logger
logger = setup_logger(name="QueryContextValidator")


class QueryContextValidator:
    def __init__(self) -> None:
        self.query_classifier = QueryClassifier()

    async def validate(self, query: str) -> QueryValidation:
        logger.info(
            "QueryContextValidator: Verificando se a query recebida possui relação de contexto válida para esta aplicação..."
        )

        query_validation = await self.query_classifier.classify(query=query)

        if query_validation.action == "reject":
            raise QueryOutOfScopeException(
                message='A query enviada não possui relação de contexto para esta aplicação.',
                body=query_validation.model_dump(),
            )

        logger.info(
            "QueryContextValidator: A query possui relação de contexto válida para esta aplicação. Query validada com sucesso!"
        )

        return query_validation
