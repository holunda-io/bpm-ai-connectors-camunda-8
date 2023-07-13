import uuid

from pytest_httpserver import HTTPServer

from gpt.agents.openapi_agent.api_controller.tools import RequestsPostToolWithParsing, RequestsGetToolWithParsing, \
    RequestsPatchToolWithParsing, \
    RequestsDeleteToolWithParsing
from openapi_agent.openapi_spec import get_test_api_spec
from util.fake_llm import FakeLLM


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
