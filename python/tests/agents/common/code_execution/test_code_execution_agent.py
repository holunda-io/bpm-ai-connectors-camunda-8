from typing import Optional

import pytest
from langchain.schema import AIMessage

from agents.util import fake_tool, FakeStoreFinalResultTool
from gpt.agents.common.agent.code_execution.code_execution_agent import PythonCodeExecutionAgent
from gpt.agents.common.agent.openai_functions.openai_functions_agent import OpenAIFunctionsAgent
from gpt.agents.common.agent.toolbox import Toolbox
from util.fake_chat_llm import FakeChatOpenAI
from util.prompt import messages_to_str


def get_tool_calls():
    return [
        AIMessage(
            content="Let's run some random python.",
            additional_kwargs={"function_call": {"name": "python", "arguments": '{ "code": "1 + 1" }'}}
        ),
        AIMessage(
            content="Let's run some random python (2).",
            additional_kwargs={"function_call": {"name": "python", "arguments": '{ "code": "fake_function(\\"foo\\")" }'}}
        )
    ]


def get_fake_llm(final_answer: AIMessage):
    return FakeChatOpenAI(responses=get_tool_calls() + [final_answer])


########################################################################################################################################

def fake_function(x: str):
    return x + " bar"


def test_code_execution_no_llm_call_no_output_schema_no_context():
    context = {}

    agent = PythonCodeExecutionAgent.from_functions(
        llm=FakeChatOpenAI(responses=get_tool_calls() + [AIMessage(
                content="I now know the final answer.",
                additional_kwargs={"function_call": {"name": "store_final_result",
                                                     "arguments": '{ "function_def": "def my_function():\n    return fake_function(\\"foo\\")" }'}}
            )] + [AIMessage(content="The result is foo bar")]
        ),
        llm_call=False,
        output_schema=None,
        python_functions=[
            fake_function
        ]
    )

    result = agent.run(input="calculate bar", context=context)

    assert result['output'] == "The result is foo bar"
    assert result['function_name'] == "my_function"
    assert result['function_call'] == "my_function()"


answer = AIMessage(
    content="I now know the final answer.",
    additional_kwargs={"function_call": {"name": "store_final_result",
                                         "arguments": '{ "function_def": "def my_function(my_input: str, my_other_input: int):\n    return fake_function(my_input)" }'}}
)


def test_code_execution_no_llm_call_no_output_schema_with_context():
    context = {"my_input": "foo", "my_other_input": 10}

    agent = PythonCodeExecutionAgent.from_functions(
        llm=FakeChatOpenAI(responses=get_tool_calls() + [answer] + [AIMessage(content="The result is foo bar")]),
        llm_call=False,
        output_schema=None,
        python_functions=[
            fake_function
        ]
    )

    result = agent.run(input="calculate bar", context=context)

    assert result['output'] == "The result is foo bar"
    assert result['function_name'] == "my_function"
    assert result['function_call'] == "my_function(my_input='foo', my_other_input=10)"


def test_code_execution_no_llm_call_with_simple_output_schema_with_context():
    output_schema = {
        "result": "the result value"
    }

    llm = get_fake_llm(final_answer=answer)

    agent = PythonCodeExecutionAgent.from_functions(
        llm=llm,
        llm_call=False,
        output_schema=output_schema,
        python_functions=[
            fake_function
        ]
    )

    result = agent.run(input="calculate bar", context={"my_input": "foo", "my_other_input": 10})

    llm.assert_last_request_contains("the result value")

    assert result['output'] == {"result": "foo bar"}
    assert result['function_name'] == "my_function"
    assert result['function_call'] == "my_function(my_input='foo', my_other_input=10)"


def test_code_execution_no_llm_call_with_output_schema_with_context():
    output_schema = {
        "result": {"type": "string", "description": "the result value"},
        "other_value": {"type": "integer", "description": "the integer value"}
    }

    llm = get_fake_llm(final_answer=AIMessage(
            content="I now know the final answer.",
            additional_kwargs={"function_call": {"name": "store_final_result",
                                                 "arguments": '{ "function_def": "def my_function(my_input: str, my_other_input: int):\n    return {\\"result\\": fake_function(my_input), \\"other_value\\": my_other_input}" }'}}
        ))

    agent = PythonCodeExecutionAgent.from_functions(
        llm=llm,
        llm_call=False,
        output_schema=output_schema,
        python_functions=[
            fake_function
        ]
    )

    result = agent.run(input="calculate bar", context={"my_input": "foo", "my_other_input": 10})

    llm.assert_last_request_contains("the result value")
    llm.assert_last_request_contains("the integer value")

    assert result['output'] == {"result": "foo bar", "other_value": 10}
    assert result['function_name'] == "my_function"
    assert result['function_call'] == "my_function(my_input='foo', my_other_input=10)"


def test_code_execution_llm_call_no_output_schema_with_context():
    agent = PythonCodeExecutionAgent.from_functions(
        llm=FakeChatOpenAI(responses=get_tool_calls() + [AIMessage(
            content="I now know the final answer.",
            additional_kwargs={"function_call": {"name": "store_final_result",
                                                 "arguments": '{ "function_def": "def my_function(my_input: str, my_other_input: int):\n    return {\\"result\\": fake_function(my_input), \\"other_value\\": my_other_input}",'
                                                              '  "function_call": "my_function(\'foo\', 10)" }',
                            }}
        )] + [AIMessage(content="The result is foo bar and 10")]),
        llm_call=True,
        output_schema=None,
        python_functions=[
            fake_function
        ]
    )

    result = agent.run(input="calculate bar", context={"my_input": "foo", "my_other_input": 10})

    assert result['output'] == "The result is foo bar and 10"
    assert result['function_name'] == "my_function"
    assert result['function_call'] == "my_function('foo', 10)"


def test_code_execution_llm_call_with_output_schema_with_context():
    output_schema = {
        "result": {"type": "string", "description": "the result value"},
        "other_value": {"type": "integer", "description": "the integer value"}
    }

    llm = get_fake_llm(final_answer=AIMessage(
            content="I now know the final answer.",
            additional_kwargs={"function_call": {"name": "store_final_result",
                                                 "arguments": '{ "function_def": "def my_function(my_input: str, my_other_input: int):\n    return {\\"result\\": fake_function(my_input), \\"other_value\\": my_other_input}",'
                                                              '  "function_call": "my_function(\'foo\', 10)" }',
                            }}
        ))

    agent = PythonCodeExecutionAgent.from_functions(
        llm=llm,
        llm_call=True,
        output_schema=output_schema,
        python_functions=[
            fake_function
        ]
    )

    result = agent.run(input="calculate bar", context={"my_input": "foo", "my_other_input": 10})

    llm.assert_last_request_contains("the result value")
    llm.assert_last_request_contains("the integer value")

    assert result['output'] == {"result": "foo bar", "other_value": 10}
    assert result['function_name'] == "my_function"
    assert result['function_call'] == "my_function('foo', 10)"
