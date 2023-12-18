from bpm_ai_core.llm.openai_chat import ChatOpenAI
from bpm_ai_core.testing.test_llm import TestLLM, tool_response

from bpm_ai.translate.translate import run_translate


def test_translate(use_real_llm=False):
    llm = TestLLM(
        name="openai",
        real_llm_delegate=ChatOpenAI() if use_real_llm else None,
        responses=[
            tool_response(
                name="store_translation",
                payload='{"email": "Hey it\'s me, Jürgen. I have a car.", "subject": "Hello!"}'
            )
        ]
    )
    result = run_translate(
        llm=llm,
        input_data={
            "email": "Hey ich bins, der Jürgen. Ich habe ein Auto.",
            "subject": "Hallo!"
        },
        target_language="English",
    )

    llm.assert_last_request_contains("Jürgen")
    llm.assert_last_request_defined_tool("store_translation", is_fixed_tool_choice=True)

    assert "car" in result["email"]
    assert result["subject"] == "Hello!"
