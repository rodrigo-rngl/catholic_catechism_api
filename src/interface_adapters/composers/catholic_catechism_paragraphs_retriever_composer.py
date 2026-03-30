from src.application.use_cases.CatholicCatechismParagraphsRetriever import CatholicCatechismParagraphsRetriever

from src.infrastructure.information_retriever_base.vector_db_qdrant.qdrant_vector_db_repository import QdrantVectorDBRepository
from src.interface_adapters.controllers.catholic_catechism_paragraphs_retriever_controller import CatholicCatechismRetrieverController


def catholic_catechism_paragraphs_retriever_composer() -> CatholicCatechismRetrieverController:
    collection_name = "Parágrafos do Catecismo (Semantic Search & Retrieve)"

    repository = QdrantVectorDBRepository(collection_name=collection_name)

    use_case = CatholicCatechismParagraphsRetriever(repository=repository)

    return CatholicCatechismRetrieverController(use_case=use_case)
