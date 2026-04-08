from uuid import uuid4
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from contextlib import asynccontextmanager
from fastapi.responses import JSONResponse
from datetime import datetime, timezone, timedelta

from fastapi.exceptions import RequestValidationError

from src.main.errors.handle_errors import handle_errors
from src.main.errors.types.validation_error import ValidationError

from src.application.DTOs.http.HttpRequest import HttpRequestValidationError

from src.infrastructure.information_retriever_base.fastembed_embedder.fastembed_embedder_factory import get_fastembed_hybrid_embedder

from src.main.routes.search_routes import search_routes
from src.main.routes.retrieve_routes import retrieve_routes

from src.main.server.catechism_hybrid_information_base_initializer import initialize_hybrid_catechism_information_base

load_dotenv(override=True)


@asynccontextmanager
async def inicialization_lifespan(app: FastAPI):
    get_fastembed_hybrid_embedder()
    await initialize_hybrid_catechism_information_base()
    yield

app = FastAPI(
    root_path="/catholic_catechism_api/",
    title="API do Catecismo da Igreja Católica",
    description="A **API do Catecismo da Igreja Católica** nasceu de uma vontade simples: usar conhecimento em **Engenharia de IA** para ajudar a espalhar a evangelização católica. Ela cria uma curadoria de conteúdos textuais da Igreja voltada para aplicações digitais — especialmente chatbots — que utilizam a técnica **RAG** (Retrieval-Augmented Generation) para enriquecer o contexto de modelos de linguagem com base no Catecismo.\n\n"
    "Este projeto existe para que comunidades, catequistas, agentes pastorais e curiosos da fé encontrem apoio em momentos de dúvida. Ao disponibilizar um acesso rápido e confiável ao Catecismo, a API pretende apoiar um movimento de evangelização que respeita a tradição e, ao mesmo tempo, dialoga com o mundo digital.\n\n"
    "“Ser cristão, para mim, significa observar o mundo e levar minha alegria e a minha força aos demais.” — **São Carlo Acutis**\n\n"
    "**O que essa API faz exatamente?**\n\n"
    "Até o momento, a API expõe endpoints dedicados:\n"
    "- `POST /hybrid_search`, capaz de receber perguntas catequéticas, validar sua adequação e devolver os parágrafos mais relevantes do Catecismo com localização completa;\n"
    "- `GET /catechism_paragraph/{paragraph_number}` / `POST /catechism_paragraphs`, que permitem recuperar diretamente parágrafos específicos a partir de suas numerações, mantendo a transparência doutrinal.\n\n"
    "**Como a API funciona por trás dos panos?**\n"
    "- O endpoint de busca, ao receber uma requisição, a API verifica se o conteúdo da requisição é compatível com a missão da Igreja e se está expresso com clareza. Caso a pergunta seja inadequada ou fora de escopo, a resposta será um erro de status `406` (reject). Se a pergunta for válida, a API vasculha a coleção do Catecismo, organizada com localizações completas (Parte, Seção, Capítulo, Artigo etc.), e entrega os parágrafos mais próximos do questionamento — sempre com contexto e transparência.\n"
    "- Já nos endpoints de recuperação, quando você envia um número de parágrafo, a API localiza e retorna diretamente esse trecho.\n\n"
    "**Recomendações de uso**\n"
    "- Traga todo o contexto possível na sua pergunta; quanto mais detalhes, maior a chance de encontrar os parágrafos que realmente iluminem a questão.\n"
    "- Valores de `top_k` entre 3 e 5 costumam equilibrar profundidade e clareza. Se precisar de múltiplos pontos de vista, experimente 7 ou 8, respeitando o limite de 10.\n"
    "- Em caso de erro `406` (reject), entenda que o assunto ultrapassa o escopo da fé católica ou contém algo impróprio. Peço que cuide para proteger o espaço espiritual que estamos construindo juntos!\n\n"
    "Que esta API ajude você a criar experiências que não apenas respondem perguntas, mas também anunciam a esperança cristã com fidelidade, ternura e responsabilidade. Que Deus te abençoe!\n\n"
    "- **Repositório do Projeto**: [github.com/rodrigo-rngl/catholic_catechism_api](https://github.com/rodrigo-rngl/catholic_catechism_api)\n",
    version="1.0.0",
    lifespan=inicialization_lifespan
)
app.include_router(search_routes)
app.include_router(retrieve_routes)


@app.middleware("http")
async def request_context_middleware(request: Request, call_next):
    UTC_MINUS_3 = timezone(timedelta(hours=-3))

    request.state.request_id = uuid4()
    request.state.created_in = datetime.now(tz=UTC_MINUS_3)

    return await call_next(request)


@app.exception_handler(RequestValidationError)
async def request_validation_error_handler(request: Request,
                                           exc: RequestValidationError) -> JSONResponse:

    http_request = HttpRequestValidationError(
        id=request.state.request_id,
        created_in=request.state.created_in
    )

    validation_error = ValidationError(message="Erro de validação no corpo da requisição.",
                                       body=exc.errors())

    http_response = handle_errors(
        http_request=http_request,
        error=validation_error
    )

    return JSONResponse(status_code=http_response.status_code,
                        content=http_response.model_dump(mode="json"))
