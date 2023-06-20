import json
import uuid

from langchain.chains.openai_functions import _resolve_schema_references
from langchain.schema import HumanMessage
from pytest_httpserver import HTTPServer

from gpt.config import get_chat_llm
from gpt.openapi_agent.openapi import endpoint_to_function
from util.fake_llm import FakeLLM
from gpt.openapi_agent.api_controller.tools import RequestsPostToolWithParsing, RequestsGetToolWithParsing, \
    RequestsPatchToolWithParsing, \
    RequestsDeleteToolWithParsing
from openapi_agent.openapi_spec import get_test_api_spec, get_test_api_spec_for_url


def test_get_tool(httpserver: HTTPServer):
    random_response = str(uuid.uuid4())
    httpserver.expect_request(
        "/api/customers",
        method="GET",
        query_string={"page": "0", "pageSize": "1"}
    ).respond_with_json(
        {"x": random_response}
    )

    tool = RequestsGetToolWithParsing(
        api_spec=get_test_api_spec(httpserver),
        llm=FakeLLM()
    )

    tool_output = tool.run({
        "operation_id": "getcustomers",
        "path_params": {},
        "query_params": {"page": 0, "pageSize": 1},
        "output_instructions": ""
    })
    assert random_response in tool_output


def test_get_function(httpserver: HTTPServer):
    random_response = str(uuid.uuid4())
    httpserver.expect_request(
        "/api/customers",
        method="GET",
        query_string={"page": "0", "pageSize": "1"}
    ).respond_with_json(
        {"x": random_response}
    )

    api_spec = get_test_api_spec(httpserver)

    e = api_spec.endpoints_by_operation_id["getcustomers"]

    print(json.dumps(e.docs, indent=4))
    print(json.dumps(endpoint_to_function(e), indent=4))



def test_post_tool(httpserver: HTTPServer):
    random_response = str(uuid.uuid4())
    httpserver.expect_request(
        "/api/customers",
        method="POST",
        data='{"test": 1}'
    ).respond_with_json(
        {"x": random_response}
    )

    tool = RequestsPostToolWithParsing(
        api_spec=get_test_api_spec(httpserver),
        llm=FakeLLM()
    )

    tool_output = tool.run({
        "operation_id": "createcustomer",
        "path_params": {},
        "data": {"test": 1},
        "output_instructions": ""
    })
    assert random_response in tool_output


def test_post_function(httpserver: HTTPServer):
    random_response = str(uuid.uuid4())
    httpserver.expect_request(
        "/api/customers",
        method="POST",
        data='{"test": 1}'
    ).respond_with_json(
        {"x": random_response}
    )

    api_spec = get_test_api_spec(httpserver)

    e = api_spec.endpoints_by_operation_id["createcustomer"]

    print(json.dumps(e.docs, indent=4))
    print(json.dumps(endpoint_to_function(e), indent=4))


def test_dereference():
    api_spec = get_test_api_spec_for_url('')

    e = api_spec.endpoints_by_operation_id["createcustomer"]

    #print(json.dumps(e.docs, indent=4))
    print(json.dumps(endpoint_to_function(e), indent=4))

    # llm = get_chat_llm(model_name="gpt-4-0613")
    # message = llm.predict_messages(
    #     [HumanMessage(content="create a customer with dummy data")], functions=[endpoint_to_function(e)]
    # )
    # print(message)

def test_patch_tool(httpserver: HTTPServer):
    random_response = str(uuid.uuid4())
    httpserver.expect_request(
        "/api/customers/1",
        method="PATCH",
        data='{"test": 1}'
    ).respond_with_json(
        {"x": random_response}
    )

    tool = RequestsPatchToolWithParsing(
        api_spec=get_test_api_spec(httpserver),
        llm=FakeLLM()
    )

    tool_output = tool.run({
        "operation_id": "updatecustomer",
        "path_params": {"customerId": 1},
        "data": {"test": 1},
        "output_instructions": ""
    })
    assert random_response in tool_output


def test_delete_tool(httpserver: HTTPServer):
    random_response = str(uuid.uuid4())
    httpserver.expect_request(
        "/api/customers/1",
        method="DELETE"
    ).respond_with_json(
        {"x": random_response}
    )

    tool = RequestsDeleteToolWithParsing(
        api_spec=get_test_api_spec(httpserver),
        llm=FakeLLM()
    )

    tool_output = tool.run({
        "operation_id": "deletecustomer",
        "path_params": {"customerId": 1},
        "output_instructions": ""
    })
    assert random_response in tool_output
