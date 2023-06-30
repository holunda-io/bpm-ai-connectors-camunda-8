import json

from dotenv import load_dotenv
from langchain.retrievers import MultiQueryRetriever

from gpt.chains.retrieval_chain.prompt import MULTI_QUERY_PROMPT

load_dotenv(dotenv_path='../../../connector-secrets.txt')

import pytest
from langchain import Cohere
from langchain.chains import RetrievalQA, FlareChain
from langchain.embeddings import OpenAIEmbeddings
from langchain.llms import AlephAlpha

import langchain
from langchain.cache import SQLiteCache
from langchain.vectorstores import Chroma, Weaviate

from gpt.agents.database_agent.agent import create_database_agent
from gpt.chains.compose_chain.chain import create_compose_chain
from gpt.chains.decide_chain.chain import create_decide_chain
from gpt.chains.generic_chain.chain import create_generic_chain
from gpt.chains.retrieval_chain.chain import create_retrieval_chain, get_vector_store
from gpt.chains.retrieval_chain.flare_instruct.base import FLAREInstructChain
from gpt.chains.retrieval_chain.sub_query_retriever.chain import create_sub_query_chain

langchain.llm_cache = SQLiteCache(database_path=".langchain-test.db")

from gpt.config import get_openai_chat_llm, LUMINOUS_SUPREME_CONTROL
from gpt.chains.extract_chain.chain import create_extract_chain
from gpt.agents.openapi_agent.agent import create_openapi_agent
from gpt.agents.plan_and_execute.executor.executor import create_executor
from gpt.chains.translate_chain.chain import create_translate_chain
from langchain.chains.openai_functions.openapi import get_openapi_chain


llm = get_openai_chat_llm(model_name='gpt-4')

retriever = get_vector_store(
    'weaviate://http://localhost:8080/Test_index',
    OpenAIEmbeddings()
).as_retriever()

multi_retriever = MultiQueryRetriever.from_llm(
    retriever=retriever,
    llm=llm,
    prompt=MULTI_QUERY_PROMPT
)

retrieval_qa = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=retriever,
)

chain = FLAREInstructChain.from_llm(llm=llm, retrieval_qa=retrieval_qa, retriever=multi_retriever)
print(chain.run('compare hp of tesla model y and vw golf'))
