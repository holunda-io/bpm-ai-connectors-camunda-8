import json

import langchain
import streamlit as st
from dotenv import load_dotenv
from langchain.callbacks import StreamlitCallbackHandler
from langchain.chat_models import ChatOpenAI

from gpt.agents.openapi_agent.agent import create_openapi_agent
from gpt.agents.openapi_agent.code_execution.base import create_openapi_code_execution_agent
from gpt.config import get_openai_chat_llm

load_dotenv(dotenv_path='../../../connector-secrets.txt')
from langchain.cache import SQLiteCache

langchain.llm_cache = SQLiteCache(database_path="../manual_integration/.langchain-test.db")

###############################################################################################



context = st.text_input("Context")
output_schema = st.text_input("Output Schema")

if prompt := st.chat_input():
    st.chat_message("user").write(prompt)
    with st.chat_message("assistant"):
        st_callback = StreamlitCallbackHandler(st.container())

        agent = create_openapi_code_execution_agent(
            llm=ChatOpenAI(model="gpt-4", streaming=True),
            api_spec_url='http://localhost:8090/v3/api-docs',
            # skill_store=skill_store,
            enable_skill_creation=False,
            output_schema=json.loads(output_schema) if output_schema else None,
            llm_call=True,
            #agent_memory=memory()
        )

        response = agent(
            inputs={
                "input": prompt,
                "context": json.loads(context) if context else "",
            },
            callbacks=[st_callback],
            return_only_outputs=True
        )
        st.write(response)
