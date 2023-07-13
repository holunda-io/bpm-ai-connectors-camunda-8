import streamlit as st
from dotenv import load_dotenv
from langchain.callbacks import StreamlitCallbackHandler

from gpt.agents.common.agent.code_execution.code_execution_agent import PythonCodeExecutionAgent
from gpt.config import get_openai_chat_llm

load_dotenv(dotenv_path='../../connector-secrets.txt')

import langchain
from langchain.cache import SQLiteCache

langchain.llm_cache = SQLiteCache(database_path="../tests/manual_integration/.langchain-test.db")

llm = get_openai_chat_llm(model_name='gpt-4')

#############################################################################

# toolbox = Toolbox([ListDirectoryTool(), ReadFileTool()])
#
# agent = OpenAIFunctionsAgent(llm=llm, toolbox=toolbox)
#
# if prompt := st.chat_input():
#     st.chat_message("user").write(prompt)
#     with st.chat_message("assistant"):
#         st_callback = StreamlitCallbackHandler(st.container())
#         response = agent.run(prompt, callbacks=[st_callback])
#         st.write(response)

def get_accounts():
    """Returns all accounts as a tuple (id, full name, balance)"""
    return [
        (1, "Max Power", 213.1),
        (2, "Jeff Jefferson", 2343.3),
        (3, "Heinz Wolff", 100.0),
        (4, "Job Jeb", 98.11),
        (5, "Max Mustermann", 990.5),
    ]

def get_first_account():
    return get_accounts()[0]

agent = PythonCodeExecutionAgent(llm=llm, python_functions=[get_accounts, get_first_account])

if prompt := st.chat_input():
    st.chat_message("user").write(prompt)
    with st.chat_message("assistant"):
        st_callback = StreamlitCallbackHandler(st.container())
        response = agent.run(prompt, callbacks=[st_callback])
        st.write(response)
