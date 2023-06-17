from typing import Dict

from langchain import PromptTemplate, LLMChain
from langchain.base_language import BaseLanguageModel
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, SystemMessagePromptTemplate

from gpt.openapi_agent.api_planner.prompt import API_PLANNER_SYSTEM_MESSAGE, API_PLANNER_USER_MESSAGE
from gpt.openapi_agent.openapi import OpenAPISpec
from gpt.plan_and_execute.executor.prompt import EXECUTOR_SYSTEM_MESSAGE, EXECUTOR_USER_MESSAGE


def create_executor_chain(
        tools: Dict[str, str],
        llm: BaseLanguageModel
) -> LLMChain:
    return LLMChain(
        llm=llm,
        prompt=_create_prompt(tools),
        verbose=True,
        output_key="step"
    )


def _create_prompt(tools: Dict[str, str]):
    tool_strings = "\n".join(
        [f"{name}: {description}" for name, description in tools.items()]
    )
    tool_names = ", ".join([name for name, _ in tools.items()])
    system_message = EXECUTOR_SYSTEM_MESSAGE.format(
        tool_names=tool_names, tools=tool_strings
    )
    return ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(system_message),
        HumanMessagePromptTemplate.from_template(EXECUTOR_USER_MESSAGE)
    ])
