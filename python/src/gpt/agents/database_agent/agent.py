"""
Agent that interacts with databases via a multistep planning approach.
"""

from typing import Any, Dict, List, Optional

from langchain import SQLDatabase
from langchain.agents.agent import AgentExecutor, BaseSingleActionAgent
from langchain.agents.agent_toolkits.sql.prompt import (
    SQL_FUNCTIONS_SUFFIX,
    SQL_PREFIX,
)
from langchain.agents.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain.agents.agent_types import AgentType
from langchain.agents.mrkl.base import ZeroShotAgent
from langchain.agents.mrkl.prompt import FORMAT_INSTRUCTIONS
from langchain.base_language import BaseLanguageModel
from langchain.callbacks.base import BaseCallbackManager
from langchain.chains import SequentialChain, TransformChain
from langchain.chains.base import Chain
from langchain.chains.llm import LLMChain
from langchain.prompts.chat import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
)
from langchain.schema import AIMessage, SystemMessage

from gpt.agents.common.functions_agent.base import FunctionsAgent
from gpt.config import supports_openai_functions
from gpt.util.data_extract import create_data_extract_chain


def create_sql_agent(
    llm: BaseLanguageModel,
    toolkit: SQLDatabaseToolkit,
    agent_type: AgentType = AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    callback_manager: Optional[BaseCallbackManager] = None,
    prefix: str = SQL_PREFIX,
    human_message: Optional[str] = None,
    format_instructions: str = FORMAT_INSTRUCTIONS,
    input_variables: Optional[List[str]] = None,
    top_k: int = 10,
    max_iterations: Optional[int] = 15,
    max_execution_time: Optional[float] = None,
    early_stopping_method: str = "force",
    verbose: bool = False,
    agent_executor_kwargs: Optional[Dict[str, Any]] = None,
    **kwargs: Dict[str, Any],
) -> AgentExecutor:
    """Construct a sql agent from an LLM and tools."""
    tools = toolkit.get_tools()
    prefix = prefix.format(dialect=toolkit.dialect, top_k=top_k)
    agent: BaseSingleActionAgent

    if agent_type == AgentType.ZERO_SHOT_REACT_DESCRIPTION:
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
            callback_manager=callback_manager,
        )
        tool_names = [tool.name for tool in tools]
        agent = ZeroShotAgent(llm_chain=llm_chain, allowed_tools=tool_names, **kwargs)

    elif agent_type == AgentType.OPENAI_FUNCTIONS:
        messages = [
            SystemMessage(content=prefix),
            HumanMessagePromptTemplate.from_template(human_message),
            AIMessage(content=SQL_FUNCTIONS_SUFFIX),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
        _prompt = ChatPromptTemplate.from_messages(messages=messages)

        agent = FunctionsAgent(
            llm=llm,
            prompt=_prompt,
            tools=tools,
            callback_manager=callback_manager,
            **kwargs,
        )
    else:
        raise ValueError(f"Agent type {agent_type} not supported at the moment.")

    return AgentExecutor.from_agent_and_tools(
        agent=agent,
        tools=tools,
        callback_manager=callback_manager,
        verbose=verbose,
        max_iterations=max_iterations,
        max_execution_time=max_execution_time,
        early_stopping_method=early_stopping_method,
        **(agent_executor_kwargs or {}),
    )


HUMAN_MESSAGE = """Begin!

Context: {context}
Question: {input}
Thought: I should look at the tables in the database to see what I can query. Then I should query the schema of the most relevant tables.
{agent_scratchpad}"""

HUMAN_MESSAGE_FUNCTIONS = """Context: {context}
Question: {input}"""


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
                agent_type=AgentType.OPENAI_FUNCTIONS,
                toolkit=toolkit,
                human_message=HUMAN_MESSAGE_FUNCTIONS,
                #input_variables=["input", "context", "agent_scratchpad"],
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
