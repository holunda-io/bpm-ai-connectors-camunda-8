"""
Agent that interacts with databases.
"""

from typing import Any, Dict, List, Optional

from langchain import SQLDatabase
from langchain.agents.agent import AgentExecutor
from langchain.agents.mrkl.base import ZeroShotAgent
from langchain.agents.mrkl.prompt import FORMAT_INSTRUCTIONS
from langchain.base_language import BaseLanguageModel
from langchain.chains import SequentialChain, TransformChain
from langchain.chains.base import Chain
from langchain.chains.llm import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.prompts.chat import (
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)

from gpt.agents.common.agent.openai_functions.openai_functions_agent import OpenAIFunctionsAgent
from gpt.agents.common.agent.openai_functions.output_parser import OpenAIFunctionsOutputParser
from gpt.agents.common.agent.toolbox import Toolbox
from gpt.agents.database_agent.prompt import HUMAN_MESSAGE_FUNCTIONS, HUMAN_MESSAGE, SYSTEM_MESSAGE
from gpt.agents.database_agent.toolkit import SQLDatabaseToolkit
from gpt.config import supports_openai_functions
from gpt.util.data_extract import create_data_extract_chain


def create_sql_agent(
    llm: BaseLanguageModel,
    toolkit: SQLDatabaseToolkit,
    prefix: str = SYSTEM_MESSAGE,
    human_message: Optional[str] = None,
    format_instructions: str = FORMAT_INSTRUCTIONS,
    input_variables: Optional[List[str]] = None,
    top_k: int = 10,
    max_iterations: Optional[int] = 15,
    verbose: bool = False,
    **kwargs: Dict[str, Any],
) -> Chain:
    """Construct a sql agent from an LLM and tools."""
    tools = toolkit.get_tools()
    prefix = prefix.format(dialect=toolkit.dialect, top_k=top_k)
    agent: Chain

    if not supports_openai_functions(llm):
        prompt = ZeroShotAgent.create_prompt(
            tools,
            prefix=prefix,
            suffix=human_message or HUMAN_MESSAGE,
            format_instructions=format_instructions,
            input_variables=input_variables,
        )
        llm_chain = LLMChain(
            llm=llm,
            prompt=prompt,
        )
        tool_names = [tool.name for tool in tools]
        _agent = ZeroShotAgent(llm_chain=llm_chain, allowed_tools=tool_names, **kwargs)
        agent = AgentExecutor.from_agent_and_tools(
            agent=_agent,
            tools=tools,
            verbose=verbose,
            max_iterations=max_iterations,
        )

    elif isinstance(llm, ChatOpenAI):
        agent = OpenAIFunctionsAgent(
            llm=llm,
            system_prompt_template=SystemMessagePromptTemplate.from_template(prefix),
            user_prompt_templates=[HumanMessagePromptTemplate.from_template(human_message or HUMAN_MESSAGE_FUNCTIONS)],
            toolbox=Toolbox(tools),
            no_function_call_means_final_answer=True,
            **kwargs,
        )
    else:
        raise Exception(f"Unsupported LLM: {llm}")

    return agent


def create_database_agent(
        database_url: str,
        llm: BaseLanguageModel,
) -> Chain:
    if not supports_openai_functions(llm):
        raise Exception("Database agent is currently only supported for OpenAI models with function calling")

    db = SQLDatabase.from_uri(database_url)
    toolkit = SQLDatabaseToolkit(db=db, llm=llm)

    def noop(data: dict) -> dict:
        return {"data": data["output"]}

    return SequentialChain(
        chains=[
            create_sql_agent(
                llm=llm,
                toolkit=toolkit,
                human_message=HUMAN_MESSAGE_FUNCTIONS,
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
