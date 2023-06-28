import os

from dotenv import load_dotenv
from langchain.chains import FlareChain
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import WebBaseLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from llama_index import ServiceContext, LLMPredictor, VectorStoreIndex, Document, OpenAIEmbedding
from llama_index.query_engine import FLAREInstructQueryEngine

from gpt.config import get_openai_chat_llm

load_dotenv(dotenv_path='../../../connector-secrets.txt')

import langchain
from langchain.cache import SQLiteCache
langchain.llm_cache = SQLiteCache(database_path=".langchain.db")

import uvicorn
from gpt.server.server import app

SERVER_PORT = os.environ.get('SERVER_PORT', '9999')

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=int(SERVER_PORT))

# loader = WebBaseLoader([
#     "https://help.netflix.com/en/node/24926?ui_action=kb-article-popular-categories",
#     "https://help.netflix.com/en/node/41049?ui_action=kb-article-popular-categories",
#     "https://help.netflix.com/en/node/407"
# ])
# documents = loader.load()
#
# #text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=20)
# #texts = text_splitter.split_documents(documents)
# #embeddings = OpenAIEmbeddings()
# #chroma_retriever = Chroma.from_documents(texts, embeddings).as_retriever()
#
# service_context = ServiceContext.from_defaults(
#     # llm_predictor=LLMPredictor(llm=ChatOpenAI(model_name='gpt-3.5-turbo', temperature=0)),
#     llm_predictor=LLMPredictor(llm=ChatOpenAI(model_name='gpt-3.5-turbo', temperature=0)),
#     chunk_size=512
# )
#
# llama_index_docs = [Document.from_langchain_format(d) for d in documents]
#
# index = VectorStoreIndex.from_documents(llama_index_docs, service_context=service_context)
# index_query_engine = index.as_query_engine(similarity_top_k=2)
#
# flare_query_engine = FLAREInstructQueryEngine(
#     query_engine=index_query_engine,
#     service_context=service_context,
#     max_iterations=7,
#     verbose=True
# )
#
# print("\n\n")
# print(flare_query_engine.query("what is the cheapest netflix plan and what are the limitations compared to the bigger plans?"))
