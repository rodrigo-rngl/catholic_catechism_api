from src.application.DTOs.QueryEmbedding import QueryHybridEmbedding
from src.application.DTOs.IngestionEmbeddings import IngestionHybridEmbeddings

from src.application.use_cases.CatholicCatechismParagraphsSearcher import CatholicCatechismParagraphsSearcher

from src.infrastructure.information_retriever_base.vector_db_qdrant.qdrant_vector_db_repository import QdrantVectorDBRepository
from src.infrastructure.information_retriever_base.fastembed_embedder.fastembed_embedder_factory import FastembedEmbedderFactory
from src.interface_adapters.controllers.catholic_catechism_paragraphs_searcher_controller import CatholicCatechismSeacherController
from src.infrastructure.information_retriever_base.vector_db_qdrant.points_searchers.qdrant_points_searcher_factory import QdrantPointsSearcherFactory

from src.interface_adapters.interfaces.fastembed_embedder_interface import FastembedEmbedderInterface
from src.interface_adapters.interfaces.qdrant_points_searcher_interface import QdrantPointsSearcherInterface


async def catholic_catechism_hybrid_searcher_composer() -> CatholicCatechismSeacherController:
    search_type = "Híbrida"
    collection_name = "Parágrafos do Catecismo (Hybrid Search)"

    embedder: FastembedEmbedderInterface[IngestionHybridEmbeddings, QueryHybridEmbedding] = FastembedEmbedderFactory(
        search_type=search_type).produce()

    points_searcher: QdrantPointsSearcherInterface[QueryHybridEmbedding] = QdrantPointsSearcherFactory(
        search_type=search_type).produce()

    qdrant_vector_db_repository = QdrantVectorDBRepository(collection_name=collection_name,
                                                           points_searcher=points_searcher)

    use_case = CatholicCatechismParagraphsSearcher(
        embedder=embedder, repository=qdrant_vector_db_repository)

    return CatholicCatechismSeacherController(use_case=use_case)
