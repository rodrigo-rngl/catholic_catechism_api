from typing import List
from abc import ABC, abstractmethod
from qdrant_client.http.models import PointStruct

from src.application.DTOs.Payload import Payload


class IngestionPointStructuresCreatorsInterface(ABC):
    @abstractmethod
    def create(self, payloads: List[Payload]) -> List[PointStruct]:
        pass
