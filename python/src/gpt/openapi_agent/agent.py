"""
Agent that interacts with OpenAPI APIs via a multistep planning approach.
"""
from typing import Optional

from langchain.base_language import BaseLanguageModel
from langchain.chains import SequentialChain, TransformChain
from langchain.chains.base import Chain

from gpt.config import get_default_llm
from gpt.openapi_agent.api_controller.controller import create_api_controller_agent
from gpt.openapi_agent.api_planner.planner import create_api_planner_chain
from gpt.openapi_agent.api_planner.selector import create_api_selector_chain
from gpt.openapi_agent.openapi import load_api_spec, escape_format_placeholders, create_docs
from gpt.util.data_extract import create_data_extract_chain


def create_openapi_agent(
        api_spec_url: str,
        llm: BaseLanguageModel = get_default_llm(),
        headers: Optional[dict] = None,
) -> Chain:
    api_spec = load_api_spec(api_spec_url)

    def operations_to_docs(inputs: dict) -> dict:
        return {"endpoints": escape_format_placeholders(create_docs(api_spec, inputs["operations"]))}

    return SequentialChain(
        chains=[
            # select relevant operations
            create_api_selector_chain(api_spec, llm),
            # get docs for selected operations
            TransformChain(
                input_variables=["operations"],
                output_variables=["endpoints"],
                transform=operations_to_docs
            ),
            # make a plan
            create_api_planner_chain(api_spec, llm),
            # execute plan
            create_api_controller_agent(api_spec, headers, llm, output_key="data"),
            # format result into output schema
            create_data_extract_chain(llm)
        ],
        input_variables=["query", "context", "output_schema"],
        output_variables=["result"],
        verbose=True
    )
