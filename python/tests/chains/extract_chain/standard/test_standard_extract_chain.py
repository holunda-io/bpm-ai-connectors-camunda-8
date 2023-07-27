from typing import Optional

import pytest
from langchain.schema import AIMessage

from gpt.chains.extract_chain.standard.chain import create_standard_extract_chain
from util.fake_llm import FakeLLM


def llm_response(json: str):
    return [f"```\n{json}\n```"]


@pytest.mark.parametrize("llm_response, expected_result", [
    ('```\n{ "name": "foo" }\n```', {"name": "foo"}),
    ('```\n{ "name": "foo", "age": 20, "valid": true }\n```', {"name": "foo", "age": 20, "valid": True}),
    ('```json\n{ "name": "foo" }\n```', {"name": "foo"}),
    ('```json\n\n{"name":"foo"}\n\n```', {"name": "foo"}),
    ('{"name":"foo"}', {"name": "foo"}),
])
def test_extract(llm_response: str, expected_result: dict):
    input = {"variable": "i am foo and bar"}
    output_schema = {}
    repeated = False

    llm = FakeLLM(responses=[llm_response])

    chain = create_standard_extract_chain(
        llm=llm,
        output_schema=output_schema,
        repeated=repeated
    )

    result = chain.run(input=input)

    assert result == expected_result

    llm.assert_last_request_contains(input["variable"])


def test_extract_repeated():
    input = {"variable": "i am foo and bar"}
    output_schema = {}
    repeated = True

    llm = FakeLLM(responses=['```json\n{"entities": [{ "name": "foo" }, { "name": "bar" }]}\n```'])

    chain = create_standard_extract_chain(
        llm=llm,
        output_schema=output_schema,
        repeated=repeated
    )

    result = chain.run(input=input)

    assert result == [{"name": "foo"}, {"name": "bar"}]

    llm.assert_last_request_contains("i am foo and bar")
