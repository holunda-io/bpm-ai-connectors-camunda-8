"""
Agent that interacts with OpenAPI APIs via a multistep planning approach.
"""
from typing import Optional

from langchain.base_language import BaseLanguageModel
from langchain.chains import SequentialChain, TransformChain
from langchain.chains.base import Chain

from gpt.agents.openapi_agent.api_controller.controller import create_api_controller_agent
from gpt.agents.openapi_agent.api_planner.planner import create_api_planner_chain
from gpt.agents.openapi_agent.api_planner.selector import create_api_selector_chain
from gpt.agents.openapi_agent.openapi import load_api_spec, escape_format_placeholders, create_docs
from gpt.util.data_extract import create_data_extract_chain


def create_openapi_agent(
        api_spec_url: str,
        llm: BaseLanguageModel,
        headers: Optional[dict] = None,
) -> Chain:
    api_spec = load_api_spec(api_spec_url)

    def operations_to_docs(inputs: dict) -> dict:
        operations = inputs["operations"]
        if "NOT_APPLICABLE" in operations:
            raise Exception("No operations found for query.")
        return {"endpoints": escape_format_placeholders(create_docs(api_spec, operations))}

    def check_plan(inputs: dict) -> dict:
        plan = inputs["plan"]
        if "NOT_APPLICABLE" in plan:
            raise Exception("No plan possible for query.")
        return {}

    def check_result(inputs: dict) -> dict:
        plan = inputs["output"]
        if "PLAN_FAILED" in plan:
            raise Exception("Plan execution failed.")
        return {}

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
            create_api_planner_chain(llm),
            TransformChain(
                input_variables=["plan"],
                output_variables=[],
                transform=check_plan
            ),
            # execute plan
            create_api_controller_agent(api_spec, headers, llm, output_key="data"),
            TransformChain(
                input_variables=["output"],
                output_variables=[],
                transform=check_result
            ),
            # format result into output schema
            create_data_extract_chain(llm)
        ],
        input_variables=["query", "context", "output_schema"],
        output_variables=["result"],
        verbose=True
    )
