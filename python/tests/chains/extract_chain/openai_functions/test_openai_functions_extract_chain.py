from typing import Optional

import pytest
from langchain.schema import AIMessage

from gpt.chains.extract_chain.openai_functions.chain import create_openai_functions_extract_chain
from util.fake_chat_llm import FakeChatOpenAI


def llm_response(arguments: str):
    return [
        AIMessage(
            content="",
            additional_kwargs={"function_call": {"name": "information_extraction", "arguments": arguments}}
        )
    ]


def test_extract():
    output_schema = {}
    repeated = False

    llm = FakeChatOpenAI(responses=llm_response('{ "name": "foo" }'))

    chain = create_openai_functions_extract_chain(
        llm=llm,
        output_schema=output_schema,
        repeated=repeated
    )

    result = chain.run(input={"variable": "i am foo"})

    assert result == {"name": "foo"}

    llm.assert_last_request_contains("i am foo")
    llm.assert_last_request_defined_function("information_extraction", function_call=True)


def test_extract_repeated():
    output_schema = {}
    repeated = True

    llm = FakeChatOpenAI(responses=llm_response('{"entities": [{ "name": "foo" }, { "name": "bar" }]}'))

    chain = create_openai_functions_extract_chain(
        llm=llm,
        output_schema=output_schema,
        repeated=repeated
    )

    result = chain.run(input={"variable": "i am foo and bar"})

    assert result == [{"name": "foo"}, {"name": "bar"}]

    llm.assert_last_request_contains("i am foo and bar")
    llm.assert_last_request_defined_function("information_extraction", function_call=True)
