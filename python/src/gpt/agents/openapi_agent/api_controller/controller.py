from typing import Optional

from langchain.agents.agent import AgentExecutor
from langchain.base_language import BaseLanguageModel

from gpt.common.functions_agent.base import FunctionsAgent
from gpt.config import supports_openai_functions
from gpt.agents.openapi_agent.api_controller.prompt import API_CONTROLLER_HUMAN_MESSAGE, \
    API_CONTROLLER_SYSTEM_MESSAGE_FUNCTIONS
from gpt.agents.openapi_agent.api_controller.tools import RequestsToolkit
from gpt.agents.openapi_agent.openapi import OpenAPISpec


def create_api_controller_agent(
        api_spec: OpenAPISpec,
        headers: Optional[dict],
        llm: BaseLanguageModel,
        output_key: str = "output",
) -> AgentExecutor:
    if not supports_openai_functions(llm):
        raise Exception("OpenAPI agent is currently only supported for OpenAI models with function calling")
    toolkit = RequestsToolkit(
        headers=headers,
        api_spec=api_spec,
        llm=llm,
        verbose=True,
    )
    agent = FunctionsAgent.from_llm_and_tools(
        llm=llm,
        tools=toolkit.get_tools(),
        system_message=API_CONTROLLER_SYSTEM_MESSAGE_FUNCTIONS,
        human_message=API_CONTROLLER_HUMAN_MESSAGE,
        output_key=output_key,
        verbose=True
    )
    return AgentExecutor.from_agent_and_tools(
        agent=agent,
        tools=toolkit.get_tools(),
        verbose=True
    )
