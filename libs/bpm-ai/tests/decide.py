from bpm_ai_core.llm.openai_chat import ChatOpenAI
from bpm_ai_core.testing.test_llm import TestLLM, tool_response

from bpm_ai.decide.decide import run_decide


def test_decide(use_real_llm=False):
    llm = TestLLM(
        name="openai",
        real_llm_delegate=ChatOpenAI() if use_real_llm else None,
        responses=[
            tool_response(
                name="store_decision",
                payload='{"decision": "yup", "reasoning": null}'
            )
        ]
    )
    result = run_decide(
        llm=llm,
        input_data={"email": "Hey ich bins, der Meier John. Mein 30. Geburtstag war gut!"},
        instructions="Is the user older than 18 years?",
        strategy="cot",
        possible_values=["yup", "nope"],
        output_type="string"
    )

    llm.assert_last_request_contains("Meier John")
    llm.assert_last_request_defined_tool("store_decision", is_fixed_tool_choice=True)

    assert result["decision"] == "yup"
