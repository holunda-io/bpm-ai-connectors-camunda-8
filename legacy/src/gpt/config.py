from typing import Union, Optional, List

from langchain import Cohere
from langchain.base_language import BaseLanguageModel
from langchain.chat_models import ChatOpenAI, ChatCohere
from langchain.embeddings import OpenAIEmbeddings, DeterministicFakeEmbedding, AlephAlphaAsymmetricSemanticEmbedding, \
    CohereEmbeddings, HuggingFaceEmbeddings
from langchain.embeddings.base import Embeddings
from langchain.llms import AlephAlpha
from langchain.schema import BaseStore
from langchain.schema.runnable import RunnableWithFallbacks
from langchain.storage import RedisStore
from langchain.vectorstores import Weaviate, AzureSearch
from langchain.vectorstores.weaviate import _create_weaviate_client

from gpt.util.storage.azure_cosmos import AzureCosmosDbNoSqlStore

OPENAI_3_5 = "gpt-3.5-turbo"
OPENAI_4 = "gpt-4"
DEFAULT_OPENAI_MODEL = OPENAI_3_5

LUMINOUS_SUPREME_CONTROL = "luminous-supreme-control"
COHERE_CHAT_COMMAND = "command"


def get_openai_chat_llm(model_name: str = DEFAULT_OPENAI_MODEL) -> ChatOpenAI:
    return ChatOpenAI(
        model_name=model_name,
        temperature=0,
    )


def supports_openai_functions(llm: BaseLanguageModel):
    return isinstance(llm, ChatOpenAI)


def model_id_to_llm(
    model_id: str,
    temperature: float = 0.0,
    cache: bool = True
) -> Union[BaseLanguageModel, ChatOpenAI, ChatCohere, RunnableWithFallbacks]:
    match model_id:
        case "gpt-3.5-turbo":
            return ChatOpenAI(model_name=OPENAI_3_5, temperature=temperature, cache=cache)
        case "gpt-4":
            return ChatOpenAI(model_name=OPENAI_4, temperature=temperature, cache=cache)
            # .with_fallbacks(
            #     [ChatOpenAI(model_name=OPENAI_3_5, temperature=temperature, cache=cache)]
            # ))
        case "luminous-supreme":
            return AlephAlpha(model=LUMINOUS_SUPREME_CONTROL, temperature=temperature, cache=cache)
        case "cohere-chat-command":
            return ChatCohere(model=COHERE_CHAT_COMMAND, temperature=temperature, cache=cache, max_tokens=1024)


def llm_to_model_tag(llm: BaseLanguageModel) -> str:
    match llm:
        case ChatOpenAI():
            return "openai-chat"
        case AlephAlpha():
            return "aleph-alpha"
        case ChatCohere():
            return "cohere"
        case _:
            return "unknown"


def get_embeddings(embedding_provider: str, embedding_model: str) -> Embeddings:
    match embedding_provider:
        case 'openai':
            return OpenAIEmbeddings(model=embedding_model)
        case 'aleph-alpha':
            return AlephAlphaAsymmetricSemanticEmbedding(normalize=True, compress_to_size=128)
        case 'cohere':
            return CohereEmbeddings(model=embedding_model)  # 'embed-multilingual-v2.0'
        case 'huggingface':
            return HuggingFaceEmbeddings(model_name=embedding_model)


def get_vector_store(
    database: str,
    database_url: str,
    embeddings: Embeddings,
    meta_attributes: Optional[List[str]] = None,
    password: Optional[str] = None
):
    match database:
        case 'weaviate':
            base_url, index = database_url.rsplit('/', 1)
            return Weaviate(
                client=_create_weaviate_client(weaviate_url=base_url),
                index_name=index,
                text_key="text",
                embedding=embeddings,
                attributes=meta_attributes,
                by_text=False
            )
        case 'azure_cognitive_search':
            base_url, index = database_url.rsplit('/', 1)
            return AzureSearch(
                azure_search_endpoint=base_url,
                azure_search_key=password,
                index_name=index,
                search_type="hybrid",
                embedding_function=embeddings.embed_query,
            )


def get_document_store(
    document_store: str,
    document_store_url: str,
    document_store_namespace: str,
    password: Optional[str] = None
) -> BaseStore:
    match document_store:
        case 'redis':
            return RedisStore(
                redis_url=document_store_url,
                namespace=document_store_namespace
            )
        case 'azure_cosmos_nosql':
            return AzureCosmosDbNoSqlStore(
                endpoint=document_store_url,
                key=password,
                database_name=document_store_namespace,
                container_name=document_store_namespace
            )
