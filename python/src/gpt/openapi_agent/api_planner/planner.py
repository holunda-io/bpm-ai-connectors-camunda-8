from langchain import PromptTemplate, LLMChain
from langchain.base_language import BaseLanguageModel
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, SystemMessagePromptTemplate

from gpt.openapi_agent.api_planner.prompt import API_PLANNER_SYSTEM_MESSAGE, API_PLANNER_USER_MESSAGE
from gpt.openapi_agent.openapi import OpenAPISpec


def create_api_planner_chain(
        llm: BaseLanguageModel
) -> LLMChain:
    return LLMChain(
        llm=llm,
        prompt=_create_prompt(),
        verbose=True,
        output_key="plan"
    )


def _create_prompt():
    return ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate(
            prompt=PromptTemplate(
                template=API_PLANNER_SYSTEM_MESSAGE,
                input_variables=["endpoints"],
            )
        ),
        HumanMessagePromptTemplate(
            prompt=PromptTemplate(
                template=API_PLANNER_USER_MESSAGE,
                input_variables=["query", "context"],
            )
        )
    ])



