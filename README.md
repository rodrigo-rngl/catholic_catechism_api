<h1><p align="center"><b>API do Catecismo da Igreja Católica</b></p></h1> 

<p align="center"><img src="src/img/api-cic.svg" alt=""></a></p> 

> **Status**: *Em desenvolvimento ⚙️*


<div style="margin: 40px;"></div>

# Objetivos do Projeto
A **API do Catecismo da Igreja Católica** nasceu de uma vontade simples: usar o meu conhecimento em **Engenharia de IA** para <u>ajudar a espalhar a evangelização católica a todos</u>. A ideia central do projeto é começar a criar um curadoria de conteúdos textuais da Igreja Católica que possam servir aplicações digitais, em principal, chatbots que utilizam a arquitetura **RAG** (Retrieval-Augmented Generation), permitindo o enriquecimento do contexto de modelos de linguagem com base nas informações obtidas através desta API, melhorando a respostas aos usuários.

Até o momento, a API expõe endpoints dedicados: 
- `POST /hybrid_search`, capaz de receber perguntas catequéticas, validar sua adequação e devolver os parágrafos mais relevantes do Catecismo com localização completa, através de busca híbrida (busca que combina os métodos: busca por palavras-chave e a busca semântica - aproveitando o melhor dos dois mundos para fornecer resultados mais relevantes); e 
- `GET /catechism_paragraph/{paragraph_number}` / `POST /catechism_paragraphs`, que permitem recuperar diretamente parágrafos específicos a partir de suas numerações, mantendo a transparência doutrinal.

A partir desse propósito, o projeto também virou um laboratório onde treino e aplico conceitos de desenvolvimento importantes como: <u>mineração de dados, embeddigns de dados, armazenamento e consumo em banco de dados vetoriais, boas práticas de arquitetura de software e codificação, modelagem de sistemas e deploy de aplicações</u>. 

### Tags

- Web Scraping
- Sistema de Recuperação de Informação
- Banco de Dados Vetorial
- Embedding
- Consumo de SLM
- Conteinerização (Docker)
- Arquitetura Limpa

### Ferramentas

<p align="center">
  <img src="https://cdn.simpleicons.org/python/white" alt="Python" height="28" style="margin-right: 6px;" />
  <img src="https://qdrant.tech/img/brand-resources-logos/qdrant-brandmark-white.png" alt="Qdrant" height="28" style="margin-right: 6px;" />
  <img src="https://cdn.simpleicons.org/huggingface/white" alt="Hugging Face" height="28" style="margin-right: 6px;" />
  <img src="https://cdn.simpleicons.org/pydantic/white" alt="Pydantic" height="28" style="margin-right: 6px;" />
  <img src="https://cdn.simpleicons.org/uv/white" alt="uv" height="28" style="margin-right: 6px;" />
  <img src="https://cdn.simpleicons.org/docker/white" alt="Docker" height="28" />
</p>

<div style="margin: 20px;"></div>

# Arquitetura e Fluxo da API
1. **Ingestão e curadoria do Catecismo**

   A inicialização da aplicação ativa um pipeline de ingestão dos parágrafos do catecismo em um banco de dados **Qdrant** conteinerizado. 
   
   O pipeline rastreia o site do Vaticano, organiza os parágrafos em  `partes > seções > capítulos > artigos > grupo de parágrafos > seção interna > subseção temática`, gera payloads estruturados, cria embeddings, monta `PointStructs`, e persiste tudo no **Qdrant**.

2. **Validação pastoral das requisições**

    Chamadas ao `POST /hybrid_search` passam pelo `QueryContextValidator`, que validam a query da requisição do usuário através de um modelo de linguagem de pequeno porte (SLM) de classificação "zero-shot" fornecido pela Hugging Face.
    
    Consultas fora do contexto catequético ou inadequadas retornam ` 406 - Not Acceptable (Domain Error)`.

3. **Busca híbrida (Fastembed + Qdrant) e recuperação direta de parágrafos por numeração**

    Para `POST /hybrid_search`, o `FastembedHybridEmbedder` gera vetores densos, representações BM25 e matrizes de late interaction, através dos modelos inicializados no lifespan do FastAPI. 
    
    Para `GET /catechism_paragraph/{paragraph_number}` e `POST /catechism_paragraphs`, o controlador busca diretamente os parágrafos solicitados pela numeração. 
    
    Em ambos os casos, o `QdrantVectorDBRepository` e suas factories cuidam da coleção e retornam trechos com metadados completos.

4. **Orquestração e resposta HTTP**

    Tanto `CatholicCatechismSearcherController` qunato `CatholicCatechismParagraphsRetrieverController` calculam `took_ms`, e entregam respostas `200` (sucesso). Em falhas de validação da reuisiçõ, domínio ou infraestrutura, o `handle_errors` garante mensagens consistentes para quem consome a API.

## Excução da Aplicação

### 1) Pré-requisitos

- Python `>=3.11`
- `uv` instalado
- Docker e Docker Compose (para execução containerizada)
- Hugging Face Token válido para classificação de contexto (`HF_TOKEN`)

### 2) Variáveis de ambiente

Defina no ambiente (ou em um arquivo `.env`, conforme seu fluxo):

- `QDRANT_URL` (ex.: `http://qdrant:6333` no Docker Compose, `http://localhost:6333` local)
- `HF_TOKEN` (token para chamada do classificador zero-shot no Hugging Face Inference)
- `HF_ZERO_SHOT_API_URL` (opcional; default: `https://router.huggingface.co/hf-inference/models/facebook/bart-large-mnli`)

### 3) Exemplo de `.env`

```env
QDRANT_URL=http://qdrant:6333
HF_TOKEN=seu_token_hf_aqui
HF_ZERO_SHOT_API_URL=https://router.huggingface.co/hf-inference/models/facebook/bart-large-mnli
```

### Como executar e utilizar a aplicação?

```bash
uv sync

docker compose --env-file .env up --build
```
- Faça requisições para `POST /hybrid_search` para busca híbrida de parágrafos.
- Use `GET /catechism_paragraph/{paragraph_number}` para recuperar um parágrafo específico.
- Use `POST /catechism_paragraphs` para recuperar múltiplos parágrafos por numeração.
- Consulte a documentação interativa em `http://localhost:8000/docs`.

![Inicialização da aplicação](src/img/readme-tutorial.gif)

<div style="margin: 20px;"></div>

# Estrutura de Pastas do Projeto
```
catholic_catechism_rag_api/
├── run.py                                            # Inicialização do servidor FastAPI
├── pyproject.toml                                   # Configuração do projeto e dependências
├── uv.lock                                          # Lockfile de dependências (uv)
├── docker-compose.yml                               # Orquestração dos serviços (API + Qdrant)
├── Dockerfile.fastapi                               # Imagem da aplicação FastAPI
├── Dockerfile.qdrant                                # Imagem/ajustes do serviço Qdrant
├── pipelines/
│   └── catechism_paragraphs_ingestion/
│       └── ingest_catechism_paragraphs.py           # Pipeline de ingestão dos parágrafos do CIC
├── src/
│   ├── application/
│   │   ├── DTOs/                                     # DTOs de entrada/saída dos fluxos
│   │   ├── services/                                 # Serviços de domínio (scraper, validator etc.)
│   │   └── use_cases/                                # Casos de uso de busca e recuperação
│   ├── config/logger_config.py                       # Configuração central de logs
│   ├── data/                                         # Dados auxiliares (ex.: escopo de queries)
│   ├── errors/                                       # Tipos de erro da aplicação
│   ├── infrastructure/
│   │   ├── information_retriever_base/               # Embedders FastEmbed e integração com Qdrant
│   │   └── query_classifier/                         # Classificador de contexto da consulta
│   ├── interface_adapters/
│   │   ├── composers/                                # Composição das dependências por endpoint
│   │   ├── controllers/                              # Controladores de entrada HTTP
│   │   └── interfaces/                               # Contratos/abstrações da aplicação
│   ├── main/
│   │   ├── routes/                                   # Definição das rotas da API
│   │   ├── server/                                   # Instância FastAPI e inicializadores
│   │   └── errors/                                   # Tratamento de erros na camada principal
│   └── img/                                          # Assets de imagem usados no projeto/README
├── catechism_payloads.json                           # Payloads gerados para ingestão
└── LICENSE                                           # Licença MIT
```

<div style="margin: 20px;"></div>

# Próximos Passos
- Desenvolver busca de parágrafos do CIC mais similares a conjunto de palavras chaves definidas pelo usuário (busca esparça), e busca de parágrafos do CIC exclusivamente por similaridade semântica a requisição do usuário (busca semântica);
- Criar testes unitátios e de integração para promover ainda mais confiabilidade da aplicação;
- Realizar mineração de dados e embedding do Código do Direito Canônico.

<div style="margin: 20px;"></div>

# Referências
CATECISMO DA IGREJA CATÓLICA. Edição típica vaticana. Disponível em: https://www.vatican.va/archive/cathechism_po/index_new/prima-pagina-cic_po.html

QDRANT. Documentation. Disponível em: https://qdrant.tech/documentation/.

FASTAPI. Documentation. Disponível em: https://fastapi.tiangolo.com/.

<hr></hr>
<div style="margin: 20px;"></div> 

<p align="center">Para acompanhar evoluções do projeto, siga as atualizações neste repositório.</p> <p align="center">Que Deus te abençoe! 🙏</p>
