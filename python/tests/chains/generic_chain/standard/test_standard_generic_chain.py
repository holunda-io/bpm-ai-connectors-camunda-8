import pytest
from gpt.chains.generic_chain.standard.chain import create_standard_generic_chain
from util.fake_llm import FakeLLM


@pytest.mark.parametrize("llm_response, expected_result", [
    ('```\n{ "result": "success" }\n```', {"result": "success"}),
    ('```\n{ "result": "failure" }\n```', {"result": "failure"}),
    ('```json\n{ "result": "success" }\n```', {"result": "success"}),
    ('```json\n\n{"result":"failure"}\n\n```', {"result": "failure"}),
    ('{"result":"success"}', {"result": "success"}),
])
def test_generic(llm_response: str, expected_result: dict):
    instructions = "Perform a task."
    output_format = {"result": "string"}

    llm = FakeLLM(responses=[llm_response])

    chain = create_standard_generic_chain(
        llm=llm,
        instructions=instructions,
        output_format=output_format
    )

    result = chain.run(input={"input": "Task data."})

    assert result == expected_result

    llm.assert_last_request_contains("Task data.")
