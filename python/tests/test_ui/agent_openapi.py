import streamlit as st
from dotenv import load_dotenv
from langchain.callbacks import StreamlitCallbackHandler

from gpt.agents.openapi_agent.agent import create_openapi_agent
from gpt.config import get_openai_chat_llm

load_dotenv(dotenv_path='../../../connector-secrets.txt')
import langchain
from langchain.cache import SQLiteCache

langchain.llm_cache = SQLiteCache(database_path="../manual_integration/.langchain-test.db")

###############################################################################################

agent = create_openapi_agent(
    llm=get_openai_chat_llm(model_name="gpt-4"),
    api_spec_url="http://localhost:8090/v3/api-docs"
)

context = st.text_input("Context")
output_schema = st.text_input("Output Schema")

if prompt := st.chat_input():
    st.chat_message("user").write(prompt)
    with st.chat_message("assistant"):
        st_callback = StreamlitCallbackHandler(st.container())
        response = agent.run(
            query=prompt,
            context=context,
            output_schema=output_schema,
            callbacks=[st_callback]
        )
        st.write(response)
