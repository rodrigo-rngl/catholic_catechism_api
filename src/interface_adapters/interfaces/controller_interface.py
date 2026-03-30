from typing import Generic
from abc import ABC, abstractmethod

from src.application.DTOs.http.HttpResponse import HttpResponseType
from src.application.DTOs.http.HttpRequest import HttpRequestType


class ControllerInterface(ABC, Generic[HttpRequestType, HttpResponseType]):
    @abstractmethod
    async def handle(self, http_request: HttpRequestType) -> HttpResponseType:
        pass
