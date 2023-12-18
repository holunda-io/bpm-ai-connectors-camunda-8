import pytest
from langchain.schema import AIMessage
from gpt.chains.translate_chain.openai_functions.chain import create_openai_functions_translate_chain
from util.fake_chat_llm import FakeChatOpenAI


def llm_response(arguments: str):
    return [
        AIMessage(
            content="",
            additional_kwargs={"function_call": {"name": "store_translation", "arguments": arguments}}
        )
    ]


def test_translate():
    input_keys = ["text"]
    target_language = "French"

    llm = FakeChatOpenAI(responses=llm_response('{ "text": "Bonjour le monde" }'))

    chain = create_openai_functions_translate_chain(
        llm=llm,
        input_keys=input_keys,
        target_language=target_language
    )

    result = chain.run(input={"text": "Hello world"})

    assert result["text"] == "Bonjour le monde"

    llm.assert_last_request_defined_function("store_translation", function_call=True)
    llm.assert_last_request_contains("Hello world")
    llm.assert_last_request_contains("French")
