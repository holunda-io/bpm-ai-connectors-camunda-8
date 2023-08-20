import json

import langchain
import streamlit as st
from dotenv import load_dotenv
from langchain.callbacks import StreamlitCallbackHandler
from langchain.chat_models import ChatOpenAI

from gpt.agents.openapi_agent.agent import create_openapi_agent
from gpt.agents.openapi_agent.code_execution.base import create_openapi_code_execution_agent
from gpt.agents.retrieval_agent.retrieval_agent import create_retrieval_agent
from gpt.chains.retrieval_chain.chain import create_legacy_retrieval_chain
from gpt.config import get_openai_chat_llm

load_dotenv(dotenv_path='../../../connector-secrets.txt')
from langchain.cache import SQLiteCache

langchain.llm_cache = SQLiteCache(database_path="../manual_integration/.langchain-test.db")

###############################################################################################



output_schema = st.text_input("Output Schema")

if prompt := st.chat_input():
    st.chat_message("user").write(prompt)
    with st.chat_message("assistant"):
        st_callback = StreamlitCallbackHandler(st.container())

        agent = create_retrieval_agent(
            llm=ChatOpenAI(model="gpt-4", streaming=True),
            database='weaviate',
            database_url='http://localhost:8080/Test_index',
            embedding_provider="openai",
            embedding_model="text-embedding-ada-002",
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
