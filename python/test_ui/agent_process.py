import json

import streamlit as st
from dotenv import load_dotenv

from gpt.agents.process_generation_agent.process_generation_agent_2 import create_process_generation_agent

load_dotenv(dotenv_path='../../connector-secrets.txt')

import langchain
from langchain.callbacks import StreamlitCallbackHandler
from langchain.embeddings import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.cache import SQLiteCache

langchain.llm_cache = SQLiteCache(database_path="../tests/manual_integration/.langchain-test.db")

##############################################################################################################

context = st.text_input("Context")
#output_schema = st.text_input("Output Schema")

if prompt := st.chat_input():
    st.chat_message("user").write(prompt)
    with st.chat_message("assistant"):
        st_callback = StreamlitCallbackHandler(st.container())

        agent = create_process_generation_agent(
            llm=ChatOpenAI(model="gpt-4", streaming=True),
            tools={
                "human_task": "A human task. You should only use this if a subtask is not suitable for the automated tools.",
                "extract_data": "A service that can transform unstructured data into a given output format.",
                "customer_database": "A service that can retrieve information about a customer and its data.",
                "subscription_service": "A service that can manage customer subscriptions."
            },
            context=json.loads(context)
            #output_schema=json.loads(output_schema) if output_schema else None,
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
