from pydantic import BaseModel, Field
from typing import Literal, get_args

ScopeLiteral = Literal["catholic_doctrine", "general_christian", "off_topic"]


def set_action(scope: str) -> Literal["proceed_rag", "reject"]:
    if scope == "off_topic":
        return "reject"

    return "proceed_rag"


class QueryValidation(BaseModel):
    scope: ScopeLiteral
    confidence: float = Field(ge=0.0, le=1.0)
    action: Literal["proceed_rag", "reject"] = Field(
        default_factory=lambda data: set_action(data["scope"])
    )


def get_query_scope_labels() -> list[str]:
    return list(get_args(ScopeLiteral))
