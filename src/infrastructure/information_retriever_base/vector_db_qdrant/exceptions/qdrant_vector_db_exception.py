from src.main.errors.types.server_error import ServerError


class QdrantVectorDBException(ServerError):
    def __init__(self, message: str) -> None:
        super().__init__(message)
