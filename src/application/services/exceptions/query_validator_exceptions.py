from src.main.errors.types.domain_error import DomainError


class QueryOutOfScopeException(DomainError):
    def __init__(self, message: str, body: dict) -> None:
        super().__init__(message=message, body=body)
