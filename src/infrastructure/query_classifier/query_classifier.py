import os
import asyncio
import aiohttp
from typing import Dict, Literal

from src.application.DTOs.QueryValidation import QueryValidation

from src.infrastructure.query_classifier.exceptions.query_classifier_exception import QueryClassifierException
from src.infrastructure.query_classifier.exceptions.query_classifier_parse_output_missing_exception import QueryClassifierParseOutputMissingException

from src.config.logger_config import setup_logger
logger = setup_logger(name="QueryClassifier")


class QueryClassifier:
    def __init__(self) -> None:
        self.__token = os.getenv("HF_TOKEN")
        self.__api_url = os.getenv(
            "HF_ZERO_SHOT_API_URL",
            "https://router.huggingface.co/hf-inference/models/facebook/bart-large-mnli",
        )
        self.__candidate_labels = [
            "catholic_doctrine",
            "general_christian",
            "off_topic",
        ]

    def __parse_response(self, payload: Dict[str, Literal['catholic_doctrine', 'general_christian', 'off_topic'] | float]) -> QueryValidation:
        if isinstance(payload, dict):
            label = payload["label"]
            score = payload["score"]

            if not label or not score:
                raise QueryClassifierParseOutputMissingException(
                    "Resposta da classificação sem campos 'label' e 'score'."
                )

            query_validation = QueryValidation(
                scope=label, confidence=score)  # type: ignore

            return query_validation

    async def classify(self, query: str) -> QueryValidation:
        try:
            if not self.__token:
                raise QueryClassifierException(
                    "Variável de ambiente 'HF_TOKEN' não informada."
                )

            logger.info(
                "QueryClassifier: Enviando requisição para classificação da query..."
            )

            headers = {
                "Authorization": f"Bearer {self.__token}",
                "Content-Type": "application/json",
            }
            body = {
                "inputs": query,
                "parameters": {
                    "candidate_labels": self.__candidate_labels,
                },
            }

            timeout = aiohttp.ClientTimeout(
                total=60,
                connect=10,
                sock_connect=10,
                sock_read=45,
            )
            async with aiohttp.ClientSession(timeout=timeout, trust_env=True) as session:
                async with session.post(
                    self.__api_url,
                    headers=headers,
                    json=body,
                ) as response:
                    response.raise_for_status()
                    result = await response.json()

            return self.__parse_response(result[0])

        except asyncio.TimeoutError as exception:
            message = (
                "Timeout ao classificar a query."
                " Verifique conectividade/proxy e disponibilidade da API."
            )
            logger.exception(
                f"QueryClassifier: {message}",
                exc_info=exception,
            )
            raise QueryClassifierException(message) from exception

        except aiohttp.ClientResponseError as exception:
            message = (
                "Falha HTTP ao classificar a query."
                f" status={exception.status}"
            )
            logger.exception(
                f"QueryClassifier: {message}",
                exc_info=exception,
            )
            raise QueryClassifierException(message) from exception

        except aiohttp.ClientError as exception:
            message = "Falha de conexão ao classificar a query."
            logger.exception(
                f"QueryClassifier: {message}",
                exc_info=exception,
            )
            raise QueryClassifierException(message) from exception

        except Exception as exception:
            message = "Exceção ao classificar a query."
            logger.exception(
                f"QueryClassifier: {message}",
                exc_info=exception,
            )
            raise QueryClassifierException(message) from exception
