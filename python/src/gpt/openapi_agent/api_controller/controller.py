from typing import List, Optional

from langchain.agents.agent import AgentExecutor
from langchain.base_language import BaseLanguageModel

from gpt.convo_agent.base import ConvoChatAgent
from gpt.openapi_agent.api_controller.prompt import API_CONTROLLER_SYSTEM_MESSAGE, API_CONTROLLER_HUMAN_MESSAGE
from gpt.openapi_agent.api_controller.tools import RequestsToolkit
from gpt.openapi_agent.openapi import OpenAPISpec
from gpt.output_parsers.json_agent_output_parser import JsonAgentOutputParser


def create_api_controller_agent(
        api_spec: OpenAPISpec,
        headers: Optional[dict],
        llm: BaseLanguageModel,
        output_key: str = "output",
) -> AgentExecutor:
    toolkit = RequestsToolkit(
        headers=headers,
        api_spec=api_spec,
        llm=llm,
        verbose=True,
    )
    agent = ConvoChatAgent.from_llm_and_tools(
        llm=llm,
        tools=toolkit.get_tools(),
        system_message=API_CONTROLLER_SYSTEM_MESSAGE,
        human_message=API_CONTROLLER_HUMAN_MESSAGE,
        input_variables=["plan", "context", "endpoints", "agent_scratchpad"],
        output_parser=JsonAgentOutputParser(output_key="data"),
        verbose=True
    )
    agent.output_key = output_key
    return AgentExecutor.from_agent_and_tools(
        agent=agent,
        tools=toolkit.get_tools(),
        verbose=True
    )
