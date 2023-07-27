import json

import streamlit as st
from dotenv import load_dotenv

import langchain
from langchain.callbacks import StreamlitCallbackHandler
from langchain.cache import SQLiteCache
from langchain.chains import RetrievalQA
from langchain.embeddings import OpenAIEmbeddings

load_dotenv(dotenv_path='../../../connector-secrets.txt')

from langchain.llms import LlamaCpp
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

from gpt.chains.retrieval_chain.chain import get_vector_store

langchain.llm_cache = SQLiteCache(database_path="../manual_integration/.langchain-test.db")

##############################################################################################################

n_gpu_layers = 1  # Metal set to 1 is enough.
n_batch = 512  # Should be between 1 and n_ctx, consider the amount of RAM of your Apple Silicon Chip.
callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])

@st.cache_data
def llama():
    # Make sure the model path is correct for your system!
    return LlamaCpp(
        model_path="/Users/bennet/Downloads/llama-2-13b-chat.ggmlv3.q4_0.bin",
        #model_path="/Users/bennet/Downloads/nous-hermes-llama2-13b.ggmlv3.q4_K_M.bin",
        n_gpu_layers=n_gpu_layers,
        n_batch=n_batch,
        n_ctx=2048,
        f16_kv=True,  # MUST set to True, otherwise you will run into problem after a couple of calls
        #callback_manager=callback_manager,
        verbose=True,
    )

TEMPLATE = """\
[INST] <<SYS>> You are a helpful assistant. <</SYS>> {user_message} [/INST]"""

TEMPLATE_2 = """\
### Instruction:
You are a helpful assistant.

### Input:
{user_message}

### Response:
"""

RETRIEVAL_PROMPT = """\
Use the following pieces of context to answer the question at the end. If you don't know the answer, just say that you don't know, don't try to make up an answer.

{context}

Question: {question}
Answer in Italian:"""

if prompt := st.chat_input():
    st.chat_message("user").write(prompt)
    with st.chat_message("assistant"):
        st_callback = StreamlitCallbackHandler(st.container())

        llm = llama()

        vs = get_vector_store(
            'weaviate://http://localhost:8080/Test_index',
            OpenAIEmbeddings(),
        )

        chain_type_kwargs = {"prompt": RETRIEVAL_PROMPT}
        qa = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=vs.as_retriever(),
            chain_type_kwargs=chain_type_kwargs
        )

        #response = llm(TEMPLATE.format(user_message=prompt), callbacks=[st_callback])
        response = qa.run(prompt)

        st.write(response)
