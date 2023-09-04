from langchain.base_language import BaseLanguageModel
from langchain.chains import RetrievalQA
from langchain.chains.base import Chain
from gpt.chains.retrieval_chain.config import get_vector_store, get_embeddings
from gpt.chains.retrieval_chain.multiquery_retriever.retriever import create_multi_query_retriever
from gpt.chains.support.flare_instruct.base import FLAREInstructChain
from gpt.chains.support.sub_query_retriever.chain import SubQueryRetriever


def create_legacy_retrieval_chain(
    llm: BaseLanguageModel,
    database: str,
    database_url: str,
    embedding_provider: str,
    embedding_model: str,
    mode: str = 'standard'
) -> Chain:

    embeddings = get_embeddings(embedding_provider, embedding_model)
    vector_store = get_vector_store(database, database_url, embeddings)

    # rephrase query multiple times and get union of docs
    multi_retriever = create_multi_query_retriever(
        retriever=vector_store.as_retriever(),
        llm=llm,
    )

    # split query into sub queries if necessary, run multiquery on each, get union of all docs
    sub_query_retriever = SubQueryRetriever.from_llm(
        retriever=multi_retriever,
        llm=llm
    )

    # answer synthesizer
    retrieval_qa = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=multi_retriever,
    )

    if mode == 'standard':
        return retrieval_qa
    elif mode == 'flare_instruct':
        return FLAREInstructChain.from_llm(
            llm=llm,
            retrieval_qa=retrieval_qa,
            retriever=multi_retriever
        )
    else:
        raise Exception(f"Unknown retrieval mode {mode}")
