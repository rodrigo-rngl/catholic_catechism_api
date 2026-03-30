from pydantic import BaseModel, Field
from typing import Literal


def set_action(scope: str) -> Literal["proceed_rag", "reject"]:
    if scope == "off_topic":
        return "reject"

    return "proceed_rag"


class QueryValidation(BaseModel):
    scope: Literal["catholic_doctrine", "general_christian", "off_topic"]
    confidence: float = Field(ge=0.0, le=1.0)
    action: Literal["proceed_rag", "reject"] = Field(
        default_factory=lambda data: set_action(data["scope"])
    )
