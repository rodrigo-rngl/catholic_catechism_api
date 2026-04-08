from fastapi import APIRouter
from fastapi.responses import JSONResponse

from src.main.errors.handle_errors import handle_errors

from src.application.DTOs.http.HttpResponse import HttpResponseSearch
from src.application.DTOs.http.HttpRequest import HttpRequestInSearch, HttpRequestSearch

from src.interface_adapters.composers.catholic_catechism_hybrid_searcher_composer import catholic_catechism_hybrid_searcher_composer

from src.config.logger_config import setup_logger
logger = setup_logger(name="SearchRoutes")

search_routes = APIRouter(tags=["Search Routes"])


@search_routes.post("/hybrid_search",
                    summary="Busca Híbrida de Parágrafos do Catecismo",
                    description="A busca híbrida é uma técnica avançada de recuperação de informações que combina dois métodos distintos para encontrar dados: a busca por palavras-chave (lexical/tradicional) e a busca semântica. O objetivo é aproveitar o melhor dos dois mundos para fornecer resultados mais relevantes, precisos e contextualizados.",
                    response_model=HttpResponseSearch,
                    responses={
                        200: {"description": "OK (Successful Response)",
                              "model": HttpResponseSearch,
                              "content": {"application/json":
                                          {"example":
                                           {
                                               "id": "2ab4f3e8-6532-4020-b19f-2a4650295f30",
                                               "status_code": 200,
                                               "created_in": "2025-12-25T00:00:00.000000",
                                               "took_ms": 12000,
                                               "query": "Jesus Cristo é verdadeiro Deus e verdadeiro homem?",
                                               "top_k": 1,
                                               "body": {
                                                   "query_validation": {
                                                        "scope": "general_christian",
                                                        "confidence": 0.9,
                                                        "action": "proceed_rag"
                                                   },
                                                   "points": [
                                                       {
                                                           "text": "480 . Jesus Cristo é verdadeiro Deus e verdadeiro homem, na unidade da sua Pessoa divina; por essa razão, Ele é o único mediador entre Deus e os homens.",
                                                           "localization": {
                                                               "PART": "PRIMEIRA PARTE - A PROFISSÃO DA FÉ",
                                                               "SECTION": "SEGUNDA SECÇÃO - A PROFISSÃO DA FÉ CRISTÃ",
                                                               "CHAPTER": "CAPÍTULO SEGUNDO - CREIO EM JESUS CRISTO, FILHO ÚNICO DE DEUS",
                                                               "ARTICLE": "ARTIGO 3 - «JESUS CRISTO FOI CONCEBIDO PELO PODER DO ESPÍRITO SANTO E NASCEU DA VIRGEM MARIA»",
                                                               "PARAGRAPHS_GROUP": "PARÁGRAFO 1 - O FILHO DE DEUS FEZ-SE HOMEM",
                                                               "INTERNAL_SECTION": "Resumindo:",
                                                               "THEMATIC_SUBSECTION": ""
                                                           },
                                                           "similarity_score": 18.371273040771484
                                                       }
                                                   ]
                                               }
                                           }}}},
                        422: {"description": "Error: Unprocessable Entity (Validation Error)",
                              "model": HttpResponseSearch,
                              "content": {"application/json":
                                          {"example":
                                           {
                                               "id": "550f4c05-9fc5-4f83-9724-f0e4d525d301",
                                               "status_code": 422,
                                               "created_in": "2025-12-25T00:00:00.000000",
                                               "took_ms": 1,
                                               "query": "Jesus é verdadeiramente Deus e verdadeiramente homem?",
                                               "top_k": 0,
                                               "body": {
                                                   "error": {
                                                       "title": "Validation Error",
                                                       "detail": "Erro de validação no corpo da requisição.",
                                                       "validation_errors": [
                                                           {
                                                               "type": "greater_than_equal",
                                                               "loc": [
                                                                "top_k"
                                                               ],
                                                               "msg": "Input should be greater than or equal to 1",
                                                               "input": 0,
                                                               "ctx": {
                                                                   "ge": 1
                                                               }
                                                           }
                                                       ]
                                                   }
                                               }
                                           }}}},
                        406: {"description": "Error: Not Acceptable (Domain Error)",
                              "model": HttpResponseSearch,
                              "content": {"application/json":
                                          {"example":
                                           {
                                               "id": "1cae785b-9b21-423d-8e64-62cf85d4cbc2",
                                                     "status_code": 406,
                                                     "created_in": "2025-12-25T00:00:00.000000",
                                                     "took_ms": 5000,
                                                     "query": "Em que ano o Brasil ganhou a primeira Copa do Mundo?",
                                                     "top_k": 1,
                                                     "body": {
                                                         "error": {
                                                             "title": "Domain Error",
                                                             "detail": "A query enviada não possui relação de contexto para desta aplicação.",
                                                             "query_validation": {
                                                                 "scope": "off_topic",
                                                                 "confidence": 0.92,
                                                                 "action": "reject"
                                                             }
                                                         }
                                                     }
                                           }}}},
                        500: {"description": "Error: Internal Server Error (Server Error)",
                              "model": HttpResponseSearch,
                              "content": {"application/json":
                                          {"example":
                                           {"id": "dcc611fd-060b-484c-9feb-303e7f17cbf0",
                                                  "status_code": 500,
                                                  "created_in": "2025-12-25T00:00:00.000000",
                                                  "took_ms": 10000,
                                                  "query": "Jesus Cristo é verdadeiro Deus e verdadeiro homem?",
                                                  "top_k": 1,
                                                  "body": {
                                                      "error": [
                                                          {
                                                              "title": "Server Error",
                                                              "detail": "Interval Server Error"
                                                          }
                                                      ]
                                                  }
                                            }}}}})
async def hybrid_search(http_request: HttpRequestInSearch) -> JSONResponse:
    try:
        http_request = HttpRequestSearch(**http_request.model_dump())

        logger.info(
            f"HybridSearch: Requisição recebida! ID: {http_request.id}")

        controller = await catholic_catechism_hybrid_searcher_composer()
        http_response = await controller.handle(http_request=http_request)

        return JSONResponse(status_code=http_response.status_code,
                            content=http_response.model_dump(mode="json"))

    except Exception as exception:
        http_request = HttpRequestSearch(**http_request.model_dump())
        http_response = handle_errors(
            http_request=http_request, error=exception)

        return JSONResponse(status_code=http_response.status_code,
                            content=http_response.model_dump(mode="json"))
