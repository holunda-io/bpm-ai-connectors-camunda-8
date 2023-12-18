from bpm_ai_core.llm.common.message import ChatMessage, ToolCallsMessage, SingleToolCallMessage
from bpm_ai_core.llm.openai_chat import ChatOpenAI
from bpm_ai_core.testing.test_llm import TestLLM, tool_response

from bpm_ai.extract.extract import run_extract


def test_extract(use_real_llm=False):
    llm = TestLLM(
        name="openai",
        real_llm_delegate=ChatOpenAI() if use_real_llm else None,
        responses=[
            tool_response(
                name="information_extraction",
                payload='{"firstname": "John", "lastname": "Meier", "age": 30, "language": "de"}'
            )
        ]
    )
    result = run_extract(
        llm=llm,
        input_data={"email": "Hey ich bins, der John Meier. Mein 30. Geburtstag war mega!"},
        output_schema={
            "firstname": "the firstname",
            "lastname": "the lastname",
            "age": {"type": "integer", "description": "age in years"},
            "language": "the language the email is written in, as two-letter ISO code"
        }
    )
    llm.assert_last_request_contains("John Meier")
    llm.assert_last_request_defined_tool("information_extraction", is_fixed_tool_choice=True)

    assert result["firstname"] == "John"
    assert result["lastname"] == "Meier"
    assert result["age"] == 30
    assert result["language"] == "de"


def test_extract_repeated(use_real_llm=False):
    llm = TestLLM(
        name="openai",
        real_llm_delegate=ChatOpenAI() if use_real_llm else None,
        responses=[
            tool_response(
                name="information_extraction",
                payload='{"entities": [{"firstname": "Jörg"}, {"firstname": "Mike"}, {"firstname": "Sepp"}]}'
            )
        ]
    )
    result = run_extract(
        llm=llm,
        input_data={"email": "Hey ich wollte nur sagen, Jörg, Mike und Sepp kommen alle mit!"},
        output_schema={
            "firstname": "the firstname",
        },
        repeated=True,
        repeated_description="Extract people that are coming"
    )
    llm.assert_last_request_contains("Jörg, Mike und Sepp")
    llm.assert_last_request_defined_tool("information_extraction", is_fixed_tool_choice=True)

    assert result[0]["firstname"] == "Jörg"
    assert result[1]["firstname"] == "Mike"
    assert result[2]["firstname"] == "Sepp"
