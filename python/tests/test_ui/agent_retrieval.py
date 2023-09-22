import json
import os

import langchain
import streamlit as st
from dotenv import load_dotenv
from langchain.callbacks import StreamlitCallbackHandler
from langchain.chat_models import ChatOpenAI

from gpt.agents.openapi_agent.agent import create_openapi_agent
from gpt.agents.openapi_agent.code_execution.base import create_openapi_code_execution_agent
from gpt.agents.retrieval_agent.retrieval_agent import create_retrieval_agent
from gpt.chains.retrieval_chain.chain import create_legacy_retrieval_chain
from gpt.config import get_openai_chat_llm, get_embeddings, get_vector_store, get_document_store

load_dotenv(dotenv_path='../../../connector-secrets.txt')
from langchain.cache import SQLiteCache

langchain.llm_cache = SQLiteCache(database_path="../manual_integration/.langchain-test.db")

###############################################################################################



output_schema = st.text_input("Output Schema")

if prompt := st.chat_input():
    st.chat_message("user").write(prompt)
    with st.chat_message("assistant"):
        st_callback = StreamlitCallbackHandler(st.container())

        embeddings = get_embeddings("openai", "text-embedding-ada-002")
        vector_store = get_vector_store(
            'azure_cognitive_search',
            os.getenv("AZURE_COGNITIVE_SEARCH_URL") + "/" + "bikestore",
            embeddings,
            password=os.getenv("AZURE_COGNITIVE_SEARCH_KEY")
        )
        parent_document_store = get_document_store(
            "azure_cosmos_nosql",
            os.getenv("AZURE_COSMOS_DB_URL"),
            "bikestore",
            password=os.getenv("AZURE_COSMOS_DB_KEY")
        )
        summary_store = get_vector_store(
            'azure_cognitive_search',
            os.getenv("AZURE_COGNITIVE_SEARCH_URL") + "/" + "summary-index",
            embeddings,
            password=os.getenv("AZURE_COGNITIVE_SEARCH_KEY")
        )

        agent = create_retrieval_agent(
            llm=ChatOpenAI(model="gpt-4", streaming=True),
            vector_store=vector_store,
            parent_document_store=parent_document_store,
            summary_store=summary_store,
            output_schema=json.loads(output_schema) if output_schema else None,
        )

        response = agent(
            inputs={
                "input": prompt,
                "context": ""
            },
            callbacks=[st_callback],
            return_only_outputs=True
        )
        st.write(response)
