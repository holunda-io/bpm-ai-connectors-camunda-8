from dotenv import load_dotenv
from langchain.retrievers import MultiQueryRetriever

from gpt.chains.retrieval_chain.prompt import MULTI_QUERY_PROMPT

load_dotenv(dotenv_path='../../../connector-secrets.txt')

from langchain.chains import RetrievalQA
from langchain.embeddings import OpenAIEmbeddings

import langchain
from langchain.cache import SQLiteCache

from gpt.chains.retrieval_chain.chain import get_vector_store
from gpt.chains.support.flare_instruct import FLAREInstructChain

langchain.llm_cache = SQLiteCache(database_path=".langchain-test.db")

from gpt.config import get_openai_chat_llm

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
