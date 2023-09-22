import pytest
from gpt.chains.translate_chain.standard.chain import create_standard_translate_chain
from util.fake_llm import FakeLLM


def test_translate():
    input_keys = ["text"]
    target_language = "French"

    llm = FakeLLM(responses=['```\n{ "text": "Bonjour le monde" }\n```'])

    chain = create_standard_translate_chain(
        llm=llm,
        input_keys=input_keys,
        target_language=target_language
    )

    result = chain.run(input={"text": "Hello world"})

    assert result["text"] == "Bonjour le monde"

    llm.assert_last_request_contains("Hello world")
    llm.assert_last_request_contains("French")
