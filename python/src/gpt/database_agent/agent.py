"""
Agent that interacts with databases via a multistep planning approach.
"""

from langchain import SQLDatabase
from langchain.agents import create_sql_agent
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from langchain.base_language import BaseLanguageModel
from langchain.chains import SequentialChain, TransformChain
from langchain.chains.base import Chain

from gpt.config import get_default_llm
from gpt.util.data_extract import create_data_extract_chain


SQL_SUFFIX = """Begin!

Context: {context}
Question: {input}
Thought: I should look at the tables in the database to see what I can query.
{agent_scratchpad}"""


def create_database_agent(
        database_url: str,
        llm: BaseLanguageModel = get_default_llm(),
) -> Chain:
    db = SQLDatabase.from_uri(database_url)
    toolkit = SQLDatabaseToolkit(db=db, llm=llm)

    def noop(data: dict) -> dict:
        return {"data": data["output"]}

    return SequentialChain(
        chains=[
            create_sql_agent(
                llm=llm,
                toolkit=toolkit,
                suffix=SQL_SUFFIX,
                input_variables=["input", "context", "agent_scratchpad"],
                verbose=True
            ),
            TransformChain(
                input_variables=["output"],
                output_variables=["data"],
                transform=noop
            ),
            # format result into output schema
            create_data_extract_chain(llm)
        ],
        input_variables=["input", "context", "output_schema"],
        output_variables=["result"],
        verbose=True
    )
