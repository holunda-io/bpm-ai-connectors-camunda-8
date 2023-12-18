from typing import Optional

import pytest
from langchain.schema import AIMessage

from agents.util import fake_tool, FakeStoreFinalResultTool
from gpt.agents.common.agent.openai_functions.openai_functions_agent import OpenAIFunctionsAgent
from gpt.agents.common.agent.toolbox import Toolbox
from util.fake_chat_llm import FakeChatOpenAI


def get_tool_calls():
    return [
        AIMessage(
            content="Let's call a useless tool.",
            additional_kwargs={"function_call": {"name": "fake_tool", "arguments": '{ "input": "foo" }'}}
        )
    ] * 3


def get_responses(answer: AIMessage):
    return get_tool_calls() + [answer]


def get_fake_llm(final_answer: Optional[AIMessage] = None):
    return FakeChatOpenAI(responses=get_responses(
        final_answer or AIMessage(content="I now know the final answer: bar")
    ))


def test_openai_functions_agent_with_plain_answer():
    agent = OpenAIFunctionsAgent.create(
        llm=get_fake_llm(),
        toolbox=Toolbox([fake_tool]),
        no_function_call_means_final_answer=True
    )

    result = agent.run(input="test", context={})["output"]

    assert "bar" in result


def test_openai_functions_agent_with_final_answer_function():
    agent = OpenAIFunctionsAgent.create(
        llm=get_fake_llm(
            final_answer=AIMessage(
                content="I now know the final answer.",
                additional_kwargs={"function_call": {"name": "store_final_result", "arguments": '{ "input": "bar" }'}}
            )
        ),
        toolbox=Toolbox([
            fake_tool,
            FakeStoreFinalResultTool()
        ]),
    )

    result = agent.run(input="test", context={})["output"]

    assert "bar" in result


def test_max_steps_abort():
    max_steps = len(get_fake_llm().responses) - 1

    agent = OpenAIFunctionsAgent.create(
        llm=get_fake_llm(),
        toolbox=Toolbox([fake_tool]),
        no_function_call_means_final_answer=True,
        max_steps=max_steps
    )

    with pytest.raises(Exception) as exc_info:
        agent.run(input="test", context={})

    assert "max_steps" in exc_info.value.args[0]


def test_max_steps_success():
    max_steps = len(get_fake_llm().responses)

    agent = OpenAIFunctionsAgent.create(
        llm=get_fake_llm(),
        toolbox=Toolbox([fake_tool]),
        no_function_call_means_final_answer=True,
        max_steps=max_steps
    )

    result = agent.run(input="test", context={})["output"]

    assert "bar" in result
