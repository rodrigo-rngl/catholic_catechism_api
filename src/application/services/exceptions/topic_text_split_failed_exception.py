from src.application.services.exceptions.catechism_page_content_splitter_exception import (
    CatechismPageContentSplitterException,
)


class TopicTextSplitFailedException(CatechismPageContentSplitterException):
    def __init__(self, message: str) -> None:
        super().__init__(message)
