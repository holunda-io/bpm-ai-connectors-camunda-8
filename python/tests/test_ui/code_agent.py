import streamlit as st
from dotenv import load_dotenv
from langchain.callbacks.streamlit.streamlit_callback_handler import ToolRecord
from langchain.embeddings import OpenAIEmbeddings

from gpt.chains.retrieval_chain.chain import get_vector_store

load_dotenv(dotenv_path='../../../connector-secrets.txt')
from langchain.callbacks import StreamlitCallbackHandler, LLMThoughtLabeler

from gpt.agents.common.agent.code_execution.code_execution_agent import PythonCodeExecutionAgent


import langchain
from langchain.chat_models import ChatOpenAI
from langchain.cache import SQLiteCache

langchain.llm_cache = SQLiteCache(database_path="../manual_integration/.langchain-test.db")
from gpt.config import get_openai_chat_llm

llm = ChatOpenAI(
        model_name='gpt-4',
        temperature=0,
        streaming=True,
    )

#############################################################################

def get_accounts():
    """Returns all accounts as a tuple (id, full name, balance)"""
    return [
        (1, "Max Power", 213.1),
        (2, "Jeff Jefferson", 2343.3),
        (3, "Heinz Wolff", 100.0),
        (4, "Job Jeb", 98.11),
        (5, "Max Mustermann", 990.5),
        (1, "Max Power", 213.1),
        (2, "Jeff Jefferson", 2343.3),
        (3, "Heinz Wolff", 100.0),
        (4, "Job Jeb", 98.11),
        (5, "Max Mustermann", 990.5),
        (1, "Max Power", 213.1),
        (2, "Jeff Jefferson", 2343.3),
        (3, "Heinz Wolff", 100.0),
        (4, "Job Jeb", 98.11),
        (5, "Max Mustermann", 990.5),
        (1, "Max Power", 213.1),
        (2, "Jeff Jefferson", 2343.3),
        (3, "Heinz Wolff", 100.0),
        (4, "Job Jeb", 98.11),
        (5, "Max Mustermann", 990.5),
        (1, "Max Power", 213.1),
        (2, "Jeff Jefferson", 2343.3),
        (3, "Heinz Wolff", 100.0),
        (4, "Job Jeb", 98.11),
        (5, "Max Mustermann", 990.5),
    ]

skill_store = get_vector_store(
    'weaviate://http://localhost:8080/SkillLibrary',
    OpenAIEmbeddings(),
    meta_attributes=['task', 'comment', 'function', 'example_call']
)

agent = PythonCodeExecutionAgent(
    llm=llm,
    python_functions=[get_accounts],
    enable_skill_creation=True,
    skill_store=skill_store
)

context = st.text_input("Context")

if prompt := st.chat_input():
    st.chat_message("user").write(prompt)
    with st.chat_message("assistant"):
        st_callback = StreamlitCallbackHandler(st.container())
        response = agent(
            inputs={
                "input": prompt,
                "context": context,
            },
            callbacks=[st_callback],
            return_only_outputs=True
        )
        st.write(response["output"])
