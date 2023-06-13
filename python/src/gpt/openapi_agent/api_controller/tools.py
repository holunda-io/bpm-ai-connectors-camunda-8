import textwrap
import typing
from typing import Optional, Any, List, Type

import requests
from langchain import LLMChain
from langchain.agents.agent_toolkits.base import BaseToolkit
from langchain.base_language import BaseLanguageModel
from langchain.tools import BaseTool
from pydantic import Field, BaseModel, root_validator

from gpt.openapi_agent.api_controller.prompt import PARSING_PROMPT
from gpt.openapi_agent.openapi import OpenAPISpec
from gpt.util.pydantic import model_to_example_json


def perform_request(
    api_spec: OpenAPISpec,
    operation_id: str,
    data: Optional[dict],
    path_params: Optional[dict],
    query_params: Optional[dict],
    headers: Optional[dict],
    response_length: Optional[int]
) -> str:
    endpoint = api_spec.endpoints_by_operation_id[operation_id]
    url = api_spec.base_url + endpoint.route

    if path_params:
        url = url.format(**path_params)

    response = requests.request(
        endpoint.method,
        url,
        headers=headers or {},
        params=query_params or {},
        json=data
    ).text
    return response[: response_length]


class BaseRequestsToolWithParsing(BaseTool):
    headers: Optional[dict]
    api_spec: OpenAPISpec
    response_length: Optional[int] = 5000
    llm: BaseLanguageModel

    @root_validator
    def generate_description(cls, values) -> typing.Dict:
        values["description"] = textwrap.dedent(values["description"]) \
                                + "\n" \
                                + model_to_example_json(values["args_schema"]).replace("{", "{{").replace("}", "}}") \
                                + "\n"
        return values

    def _run(self, *args: Any, **kwargs: Any) -> Any:
        response = perform_request(
            self.api_spec,
            kwargs["operation_id"],
            kwargs.get("data", {}),
            kwargs.get("path_params", {}),
            kwargs.get("query_params", {}),
            self.headers,
            self.response_length
        )
        llm_chain = LLMChain(prompt=PARSING_PROMPT, llm=self.llm)
        return llm_chain.predict(
            response=response,
            instructions=kwargs["output_instructions"]
        ).strip()

    async def _arun(self, text: str) -> str:
        raise NotImplementedError()


class RequestsToolkit(BaseToolkit):
    """Toolkit for making requests."""

    api_spec: OpenAPISpec
    headers: Optional[dict]
    llm: BaseLanguageModel
    response_length: Optional[int] = 5000
    verbose = True

    def get_tools(self) -> List[BaseTool]:
        """Return a list of tools."""
        return [
            RequestsGetToolWithParsing(
                headers=self.headers,
                api_spec=self.api_spec,
                llm=self.llm,
                verbose=self.verbose,
            ),
            RequestsPostToolWithParsing(
                headers=self.headers,
                api_spec=self.api_spec,
                llm=self.llm,
                verbose=self.verbose,
            ),
            RequestsPutToolWithParsing(
                headers=self.headers,
                api_spec=self.api_spec,
                llm=self.llm,
                verbose=self.verbose,
            ),
            RequestsPatchToolWithParsing(
                headers=self.headers,
                api_spec=self.api_spec,
                llm=self.llm,
                verbose=self.verbose,
            ),
            RequestsDeleteToolWithParsing(
                headers=self.headers,
                api_spec=self.api_spec,
                llm=self.llm,
                verbose=self.verbose,
            )
        ]


#########################################

class BaseRequestToolInput(BaseModel):
    operation_id: str = Field(..., description="operationId of an endpoint")
    path_params: Optional[dict] = Field({}, description="dict of required path parameters")
    query_params: Optional[dict] = Field({}, description="dict of required query parameters")
    output_instructions: str = Field(..., description="instructions on what information to extract from the response")


class GetToolInput(BaseRequestToolInput):
    operation_id: str = Field(..., description="operationId of a GET endpoint")

class RequestsGetToolWithParsing(BaseRequestsToolWithParsing):
    name = "requests_get"
    args_schema: Type[BaseModel] = GetToolInput
    description = """\
    Use this to GET content from an endpoint.
    Input to the tool must be a json blob according to this schema:
    """


class PostToolInput(BaseRequestToolInput):
    operation_id: str = Field(..., description="operationId of a POST endpoint")
    data: dict = Field(..., description="the json body to send, as a dict")


class RequestsPostToolWithParsing(BaseRequestsToolWithParsing):
    name = "requests_post"
    args_schema: Type[BaseModel] = PostToolInput
    description = """\
    Use this to POST to an endpoint.
    Input to the tool must be a json blob according to this schema:
    """

class PutToolInput(BaseRequestToolInput):
    operation_id: str = Field(..., description="operationId of a PUT endpoint")

class RequestsPutToolWithParsing(BaseRequestsToolWithParsing):
    name = "requests_put"
    args_schema: Type[BaseModel] = PutToolInput
    description = """\
    Use this to PUT to an endpoint.
    Input to the tool must be a json blob according to this schema:
    """

class PatchToolInput(BaseRequestToolInput):
    operation_id: str = Field(..., description="operationId of a PATCH endpoint")

class RequestsPatchToolWithParsing(BaseRequestsToolWithParsing):
    name = "requests_patch"
    args_schema: Type[BaseModel] = PatchToolInput
    description = """\
    Use this to PATCH to an endpoint.
    Input to the tool must be a json blob according to this schema:
    """


class DeleteToolInput(BaseRequestToolInput):
    operation_id: str = Field(..., description="operationId of a DELETE endpoint")

class RequestsDeleteToolWithParsing(BaseRequestsToolWithParsing):
    name = "requests_delete"
    args_schema: Type[BaseModel] = DeleteToolInput
    description = """\
    ONLY USE THIS TOOL IF THE USER HAS SPECIFICALLY REQUESTED TO DELETE A RESOURCE.
    Input to the tool must be a json blob according to this schema:
    """
