from typing import Optional

from langchain.chains.base import Chain
from langchain.chat_models import ChatOpenAI
from langchain.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate

from gpt.agents.common.agent.openai_functions.openai_functions_agent import OpenAIFunctionsAgent
from gpt.agents.common.agent.toolbox import Toolbox
from gpt.agents.openapi_agent.api_controller.prompt import API_CONTROLLER_HUMAN_MESSAGE, \
    API_CONTROLLER_SYSTEM_MESSAGE_FUNCTIONS
from gpt.agents.openapi_agent.api_controller.tools import RequestsToolkit
from gpt.agents.openapi_agent.openapi import OpenAPISpec
from gpt.config import supports_openai_functions


def create_api_controller_agent(
        api_spec: OpenAPISpec,
        headers: Optional[dict],
        llm: ChatOpenAI,
        output_key: str = "output",
) -> Chain:
    if not supports_openai_functions(llm):
        raise Exception("OpenAPI agent is currently only supported for OpenAI models with function calling")
    toolkit = RequestsToolkit(
        headers=headers,
        api_spec=api_spec,
        llm=llm,
        verbose=True,
    )
    return OpenAIFunctionsAgent(
        llm=llm,
        system_prompt_template=SystemMessagePromptTemplate.from_template(API_CONTROLLER_SYSTEM_MESSAGE_FUNCTIONS),
        user_prompt_template=HumanMessagePromptTemplate.from_template(API_CONTROLLER_HUMAN_MESSAGE),
        toolbox=Toolbox.from_toolkit(toolkit),
        no_function_call_means_final_answer=True,
        output_key=output_key
    )
