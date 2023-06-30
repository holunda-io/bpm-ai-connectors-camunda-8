from uuid import uuid4

from langchain.base_language import BaseLanguageModel
from langchain.chains import RetrievalQA
from langchain.chains.base import Chain
from langchain.embeddings import OpenAIEmbeddings
from langchain.embeddings.base import Embeddings
from langchain.vectorstores import Weaviate, VectorStore
from langchain.vectorstores.weaviate import _create_weaviate_client
from langchain.retrievers.multi_query import MultiQueryRetriever

from gpt.chains.retrieval_chain.prompt import MULTI_QUERY_PROMPT
from gpt.chains.retrieval_chain.sub_query_retriever.chain import SubQueryRetriever


def get_vector_store(database_url: str, embeddings: Embeddings):
    db, url = database_url.split('://', 1)
    match db:
        case 'weaviate':
            base_url, index = url.rsplit('/', 1)
            return Weaviate(
                client=_create_weaviate_client(weaviate_url=base_url),
                index_name=index,
                text_key="text",
                embedding=embeddings,
                by_text=False
            )
        case _:
            raise Exception(f'Unsupported vector database {db} in url {database_url}')


def get_embeddings(embedding_provider: str, embedding_model: str) -> Embeddings:
    match embedding_provider:
        case 'openai':
            return OpenAIEmbeddings(model=embedding_model)
        case _:
            raise Exception(f'Unsupported embedding provider: {embedding_provider}')


def create_retrieval_chain(
    llm: BaseLanguageModel,
    database_url: str,
    embedding_provider: str,
    embedding_model: str
) -> Chain:

    embeddings = get_embeddings(embedding_provider, embedding_model)
    vector_store = get_vector_store(database_url, embeddings)

    # rephrase query multiple times and get union of docs
    multi_retriever = MultiQueryRetriever.from_llm(
        retriever=vector_store.as_retriever(),
        llm=llm,
        prompt=MULTI_QUERY_PROMPT
    )

    # split query into sub queries if necessary, run multiquery on each, get union of all docs
    sub_query_retriever = SubQueryRetriever.from_llm(
        retriever=multi_retriever,
        llm=llm
    )

    return RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=sub_query_retriever,
    )
