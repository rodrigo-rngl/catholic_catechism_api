from src.application.services.exceptions.catechism_paragraphs_scrapper_exception import (
    CatechismParagraphsScrapperException,
)


class ContentTextTagsNotFoundException(CatechismParagraphsScrapperException):
    def __init__(self, message: str) -> None:
        super().__init__(message)
