class ServerError(Exception):
    def __init__(self, message: str) -> None:
        self.message = message
        self.name = 'Server Error'
        self.status_code = 500
