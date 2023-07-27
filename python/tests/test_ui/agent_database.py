import json

import streamlit as st
from dotenv import load_dotenv

from gpt.agents.common.agent.memory import AgentMemory
from gpt.agents.database_agent.agent import create_database_agent
from gpt.agents.database_agent.code_exection.base import create_database_code_execution_agent
from gpt.chains.retrieval_chain.chain import get_vector_store
from gpt.config import get_openai_chat_llm

load_dotenv(dotenv_path='../../../connector-secrets.txt')

import langchain
from langchain.callbacks import StreamlitCallbackHandler
from langchain.embeddings import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.cache import SQLiteCache

langchain.llm_cache = SQLiteCache(database_path="../manual_integration/.langchain-test.db")

##############################################################################################################

@st.cache_data
def memory():
    return AgentMemory()

skill_store = get_vector_store(
    'weaviate://http://localhost:8080/SkillLibrary',
    OpenAIEmbeddings(),
    meta_attributes=['task', 'comment', 'function', 'example_call']
)

context = st.text_input("Context")
output_schema = st.text_input("Output Schema")

if prompt := st.chat_input():
    st.chat_message("user").write(prompt)
    with st.chat_message("assistant"):
        st_callback = StreamlitCallbackHandler(st.container())

        agent = create_database_code_execution_agent(
            llm=ChatOpenAI(model="gpt-4", streaming=True),
            database_url='postgresql://postgres:postgres@localhost:5438/postgres',
            #skill_store=skill_store,
            enable_skill_creation=False,
            output_schema=json.loads(output_schema) if output_schema else None,
            llm_call=True,
            agent_memory=memory()
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
