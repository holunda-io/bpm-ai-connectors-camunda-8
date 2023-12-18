import pytest
from gpt.chains.decide_chain.standard.chain import create_standard_decide_chain
from util.fake_llm import FakeLLM


@pytest.mark.parametrize("llm_response, expected_result", [
    ('```\n{ "decision": "yes" }\n```', {"decision": "yes"}),
    ('```json\n{ "decision": "yes" }\n```', {"decision": "yes"}),
    ('```json\n\n{"decision":"no"}\n\n```', {"decision": "no"}),
    ('{"decision":"yes"}', {"decision": "yes"}),
])
def test_decide(llm_response: str, expected_result: dict):
    instructions = "Should I go to the park today?"
    output_type = "boolean"
    possible_values = ["yes", "no"]

    llm = FakeLLM(responses=[llm_response])

    chain = create_standard_decide_chain(
        llm=llm,
        instructions=instructions,
        output_type=output_type,
        possible_values=possible_values
    )

    result = chain.run(input={"input": "It's sunny outside."})

    assert result == expected_result

    llm.assert_last_request_contains("It's sunny outside.")