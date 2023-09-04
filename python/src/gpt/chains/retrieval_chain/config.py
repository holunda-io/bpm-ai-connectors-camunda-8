from langchain.embeddings import OpenAIEmbeddings
from langchain.embeddings.base import Embeddings
from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain.storage import RedisStore
from langchain.vectorstores import Weaviate, AzureSearch
from langchain.vectorstores.weaviate import _create_weaviate_client
from typing import List, Optional, Dict, Union

from gpt.util.storage.azure_cosmos import AzureCosmosDbNoSqlStore


def get_vector_store(database: str, database_url: str, embeddings: Embeddings, meta_attributes: Optional[List[str]] = None, password: Optional[str] = None):
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
        case _:
            raise Exception(f'Unsupported vector database {database}.')


def get_document_store(document_store: str, document_store_url: str, document_store_namespace: str, password: Optional[str] = None):
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

        case _:
            raise Exception(f'Unsupported document store {document_store}.')


def get_embeddings(embedding_provider: str, embedding_model: str) -> Embeddings:
    match embedding_provider:
        case 'openai':
            return OpenAIEmbeddings(model=embedding_model)
        case _:
            raise Exception(f'Unsupported embedding provider: {embedding_provider}')