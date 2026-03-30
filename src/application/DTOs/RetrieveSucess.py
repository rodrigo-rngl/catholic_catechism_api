from typing import List
from pydantic import BaseModel
from src.application.DTOs.RetrieveOutput import RetrieveOutput


class RetrieveSuccess(BaseModel):
    retrieve_output: List[RetrieveOutput]
