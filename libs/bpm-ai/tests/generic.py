from bpm_ai_core.llm.openai_chat import ChatOpenAI
from bpm_ai_core.testing.test_llm import TestLLM, tool_response

from bpm_ai.generic.generic import run_generic


def test_generic(use_real_llm=False):
    llm = TestLLM(
        name="openai",
        real_llm_delegate=ChatOpenAI() if use_real_llm else None,
        responses=[
            tool_response(
                name="store_task_result",
                payload='{"firstname": "John", "lastname": "Meier"}'
            )
        ]
    )
    result = run_generic(
        llm=llm,
        input_data={"email": "Hey ich bins, der John Meier."},
        instructions="Extract the information",
        output_schema={
            "firstname": "the firstname",
            "lastname": "the lastname"
        }
    )

    llm.assert_last_request_contains("John Meier")
    llm.assert_last_request_defined_tool("store_task_result", is_fixed_tool_choice=True)

    assert result["firstname"] == "John"
    assert result["lastname"] == "Meier"
