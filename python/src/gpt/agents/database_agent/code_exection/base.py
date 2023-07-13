from langchain import SQLDatabase
from langchain.base_language import BaseLanguageModel
from langchain.chains.base import Chain

from gpt.agents.database_agent.code_exection.functions import get_database_functions


# todo use new agent
def create_database_code_execution_agent(llm: BaseLanguageModel, db: SQLDatabase) -> Chain:
    # return .from_llm_and_functions(
    #     llm=llm,
    #     functions=get_database_functions(llm, db),
    #     output_schema={}
    # )
    pass
