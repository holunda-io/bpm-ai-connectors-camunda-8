import pytest
from langchain.schema import AIMessage
from gpt.chains.decide_chain.openai_functions.chain import create_openai_functions_decide_chain
from util.fake_chat_llm import FakeChatOpenAI

def llm_response(arguments: str):
    return [
        AIMessage(
            content="",
            additional_kwargs={"function_call": {"name": "store_decision", "arguments": arguments}}
        )
    ]

def test_decide():
    instructions = "Should I go to the park today?"
    output_type = "boolean"
    possible_values = ["yes", "no"]

    llm = FakeChatOpenAI(responses=llm_response('{ "decision": "yes" }'))

    chain = create_openai_functions_decide_chain(
        llm=llm,
        instructions=instructions,
        output_type=output_type,
        possible_values=possible_values
    )

    result = chain.run(input={"input": "It's sunny outside."})

    assert result == {"decision": "yes"}

    llm.assert_last_request_contains("It's sunny outside.")
    llm.assert_last_request_defined_function("store_decision", function_call=True)