import pytest
from langchain.schema import AIMessage
from gpt.chains.generic_chain.openai_functions.chain import create_openai_functions_generic_chain
from util.fake_chat_llm import FakeChatOpenAI


def llm_response(arguments: str):
    return [
        AIMessage(
            content="",
            additional_kwargs={"function_call": {"name": "store_task_result", "arguments": arguments}}
        )
    ]


def test_generic():
    instructions = "Perform a task."
    output_format = {"result": "string"}

    llm = FakeChatOpenAI(responses=llm_response('{ "result": "success" }'))

    chain = create_openai_functions_generic_chain(
        llm=llm,
        instructions=instructions,
        output_format=output_format
    )

    result = chain.run(input={"input": "Task data."})

    assert result == {"result": "success"}

    llm.assert_last_request_contains("Task data.")
    llm.assert_last_request_defined_function("store_task_result", function_call=True)
