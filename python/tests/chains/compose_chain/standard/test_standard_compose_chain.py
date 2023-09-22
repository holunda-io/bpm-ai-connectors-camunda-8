import pytest
from gpt.chains.compose_chain.standard.chain import create_standard_compose_chain
from util.fake_llm import FakeLLM


def test_compose():
    instructions = "Write a letter to John."
    type = "letter"
    style = "formal"
    tone = "polite"
    length = "short"
    language = "english"
    sender = "Alice"
    constitutional_principle = None

    llm = FakeLLM(responses=["Dear John,\n\nI hope this letter finds you in good health.\n\n Best,\n\n[SENDER]"])

    chain = create_standard_compose_chain(
        llm=llm,
        instructions=instructions,
        type=type,
        style=style,
        tone=tone,
        length=length,
        language=language,
        sender=sender,
        constitutional_principle=constitutional_principle
    )

    result = chain(inputs={"input": {"my_var": "It's sunny outside."}})

    assert result["text"] == "Dear John,\n\nI hope this letter finds you in good health.\n\n Best,\n\nAlice"

    llm.assert_last_request_contains(instructions)
    llm.assert_last_request_contains(type)
    llm.assert_last_request_contains(style)
    llm.assert_last_request_contains(tone)
    llm.assert_last_request_contains(length)
    llm.assert_last_request_contains(language)

    llm.assert_last_request_contains("It's sunny outside.")
