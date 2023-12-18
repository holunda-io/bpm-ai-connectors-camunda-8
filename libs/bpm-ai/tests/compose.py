from bpm_ai_core.llm.openai_chat import ChatOpenAI
from bpm_ai_core.testing.test_llm import TestLLM, tool_response

from bpm_ai.compose.compose import run_compose


def test_compose(use_real_llm=False):
    llm = TestLLM(
        name="openai",
        real_llm_delegate=ChatOpenAI() if use_real_llm else None,
        responses=[
            tool_response(
                name="store_text",
                payload='{'
                        '"greet_customer": "Hey Max", '
                        '"thank_customer_mail": "Thanks for your mail", '
                        '"answer_question_based_provided_answer": "Your order was shipped today!"'
                        '}'
            )
        ]
    )
    result = run_compose(
        llm=llm,
        input_data={
            "email": "Hey, where is my order? Max",
            "answer": "Shipped today",
            "agent_name": "Lisa"
        },
        template="{greet customer}, {thank customer for mail}.\n{answer question based on provided answer}.\nBest,\n{agent_name}",
        properties={
            "language": "English",
            "type": "letter",
            "tone": "friendly",
            "length": "short",
            "style": "formal",
            "temperature": "0"
        }
    )

    llm.assert_last_request_contains("Shipped today")
    llm.assert_last_request_defined_tool("store_text", is_fixed_tool_choice=True)

    assert "Max" in result["text"]
    assert "Lisa" in result["text"]
    assert "shipped" in result["text"]
