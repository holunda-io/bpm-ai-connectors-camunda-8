import streamlit as st
from dotenv import load_dotenv

load_dotenv(dotenv_path='../../connector-secrets.txt')
import langchain
from langchain.cache import SQLiteCache

langchain.llm_cache = SQLiteCache(database_path=".langchain-test.db")
from langchain.embeddings import OpenAIEmbeddings
from gpt.chains.retrieval_chain.chain import get_vector_store

st.title('📚 Skill Library')

vector_store = get_vector_store(
    'weaviate://http://localhost:8080/SkillLibrary',
    OpenAIEmbeddings(),
    meta_attributes=['task', 'comment', 'function', 'example_call']
)

def get_skills():
    with st.spinner('Loading skills...'):
        return vector_store.similarity_search("function definition", k=1000)


skills = get_skills()

st.info(f'Currently there are **{len(skills)}** skills in the library.', icon="ℹ️")

for skill in skills:
    meta = skill.metadata
    task: str = meta['task']
    function: str = meta['function']
    comment: str = meta['comment']
    example_call: str = meta['example_call']

    with st.expander(f"🛠 **{task}**"):
        st.write(f"##### Task: {task}")
        st.write(comment.replace('"""', ''))
        st.code(function)
        st.write("###### Example call:")
        st.code(example_call)
