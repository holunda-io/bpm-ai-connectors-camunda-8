import pytest
from langchain.schema import AIMessage
from gpt.chains.compose_chain.template_openai_functions.chain import TemplateComposeChain
from util.fake_chat_llm import FakeChatOpenAI


def llm_response(arguments: str):
    return [
        AIMessage(
            content="",
            additional_kwargs={"function_call": {"name": "store_text", "arguments": arguments}}
        )
    ]


def test_template_compose():
    template = "Dear {recipient}, \n\n I hope this letter finds you in good health. \n\n Best, \n\n { sender } \n\n {closing remarks}"
    type = "letter"
    style = "formal"
    tone = "polite"
    length = "short"
    language = "english"
    constitutional_principle = None

    llm = FakeChatOpenAI(responses=llm_response('{ "closing_remarks": "Stay safe." }'))

    chain = TemplateComposeChain(
        llm=llm,
        template=template,
        type=type,
        style=style,
        tone=tone,
        length=length,
        language=language,
        constitutional_principle=constitutional_principle
    )

    result = chain(inputs={"input": {"sender": "Alice", "recipient": "John"}})

    assert result["text"] == "Dear John, \n\n I hope this letter finds you in good health. \n\n Best, \n\n Alice \n\n Stay safe."

    llm.assert_last_request_contains(type)
    llm.assert_last_request_contains(style)
    llm.assert_last_request_contains(tone)
    llm.assert_last_request_contains(length)
    llm.assert_last_request_contains(language)

    llm.assert_last_request_defined_function("store_text", function_call=True)
    llm.assert_last_request_contains("Dear recipient, \n\n I hope this letter finds you in good health. \n\n Best, \n\n sender \n\n {closing remarks}")
    llm.assert_last_request_not_contains("Alice")
    llm.assert_last_request_not_contains("John")