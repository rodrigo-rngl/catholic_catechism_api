import os
from typing import cast
from huggingface_hub import AsyncInferenceClient

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
