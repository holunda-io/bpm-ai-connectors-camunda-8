from typing import List, Tuple

from dotenv import load_dotenv
from langchain.agents import initialize_agent, AgentExecutor
from langchain.retrievers import MultiQueryRetriever
from langchain.tools import PythonAstREPLTool
from langchain.utilities import PythonREPL

from gpt.agents.common.code_execution.chain import PythonCodeExecutionChain
from gpt.agents.common.code_execution.tool import PythonREPLTool
from gpt.agents.common.functions_agent.base import FunctionsAgent
from gpt.chains.retrieval_chain.prompt import MULTI_QUERY_PROMPT
from gpt.config import get_openai_chat_llm

load_dotenv(dotenv_path='../../../connector-secrets.txt')

from langchain.chains import RetrievalQA
from langchain.embeddings import OpenAIEmbeddings

import langchain
from langchain.cache import SQLiteCache

langchain.llm_cache = SQLiteCache(database_path=".langchain-test.db")

llm = get_openai_chat_llm(model_name='gpt-4')


# def find_user_name(id: int) -> str:
#     """Returns the full name of the user with given id"""
#     return "Max Mustermann"
#
# def get_users() -> List[Tuple[int, str]]:
#     """Returns all users as a tuple (id, full name)"""
#     return [
#         (1, "Max Power"),
#         (2, "Jeff Jefferson"),
#         (3, "Heinz Wolff"),
#         (4, "Job Jeb"),
#         (5, "Max Mustermann"),
#     ]
#
# def log_to_file(txt: str):
#     """Logs the given string to a file"""
#     pass
#
# def get_accounts() -> List[Tuple[int, str, float]]:
#     """Returns all accounts as a tuple (id, full name, balance)"""
#     return [
#         (1, "Max Power", 213.1),
#         (2, "Jeff Jefferson", 2343.3),
#         (3, "Heinz Wolff", 100.0),
#         (4, "Job Jeb", 98.11),
#         (5, "Max Mustermann", 990.5),
#     ]

f1 = """
from typing import List, Tuple
def get_accounts() -> List[Tuple[int, str, float]]:
    return [
        (1, "Max Power", 213.1),
        (2, "Jeff Jefferson", 2343.3),
        (3, "Heinz Wolff", 100.0),
        (4, "Job Jeb", 98.11),
        (5, "Max Mustermann", 990.5),
    ]
"""
f2 = """
def get_first_account():
    return get_accounts()[0]
"""

def get_accounts():
    """Returns all accounts as a tuple (id, full name, balance)"""
    return [
        (1, "Max Power", 213.1),
        (2, "Jeff Jefferson", 2343.3),
        (3, "Heinz Wolff", 100.0),
        (4, "Job Jeb", 98.11),
        (5, "Max Mustermann", 990.5),
    ]

def log_to_file(txt: str):
    """Logs the given string to a file"""
    pass

tools=[PythonREPLTool.from_functions(functions=[get_accounts, log_to_file])]

chain = FunctionsAgent.from_llm_and_tools(
    llm=llm,
    tools=tools,
)
e = AgentExecutor.from_agent_and_tools(chain, tools)
print(e.run("Return a list of 10 random numbers"))
