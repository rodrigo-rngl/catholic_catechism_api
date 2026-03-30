from typing import List
from pydantic import BaseModel

from src.application.DTOs.SearchOutput import SearchOutput
from src.application.DTOs.QueryValidation import QueryValidation


class SearchSuccess(BaseModel):
    query_validation: QueryValidation
    search_outputs: List[SearchOutput]
