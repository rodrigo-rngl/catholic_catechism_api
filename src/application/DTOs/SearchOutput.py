from typing import Dict, Optional
from pydantic import BaseModel


class SearchOutput(BaseModel):
    text: str
    localization: Optional[Dict[str, str]] = None
    similarity_score: float
