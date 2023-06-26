from langchain import PromptTemplate, LLMChain
from langchain.base_language import BaseLanguageModel
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, SystemMessagePromptTemplate

from gpt.agents.openapi_agent.api_planner.prompt import API_PLANNER_SELECTOR_SYSTEM_MESSAGE, API_PLANNER_SELECTOR_USER_MESSAGE
from gpt.agents.openapi_agent.openapi import OpenAPISpec


def create_api_selector_chain(
        api_spec: OpenAPISpec,
        llm: BaseLanguageModel
) -> LLMChain:
    prompt = _create_prompt(api_spec)
    return LLMChain(
        llm=llm,
        prompt=prompt,
        verbose=True,
        output_key="operations"
    )


def _create_prompt(api_spec: OpenAPISpec):
    return ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate(
            prompt=PromptTemplate(
                template=API_PLANNER_SELECTOR_SYSTEM_MESSAGE,
                input_variables=[],
                partial_variables={"endpoints": "- " + "- ".join(
                    generate_endpoint_descriptions(api_spec)
                )},
            )
        ),
        HumanMessagePromptTemplate(
            prompt=PromptTemplate(
                template=API_PLANNER_SELECTOR_USER_MESSAGE,
                input_variables=["query", "context"],
            )
        )
    ])


def generate_endpoint_descriptions(api_spec: OpenAPISpec):
    return [f"{e.operationId} ({e.method}): {e.description}\n" for e in api_spec.endpoints]
