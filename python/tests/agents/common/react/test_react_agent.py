import pytest
from langchain.chat_models import FakeListChatModel

from agents.util import fake_tool
from gpt.agents.common.agent.react.react_agent import ReActAgent
from gpt.agents.common.agent.toolbox import Toolbox


@pytest.fixture
def responses():
    return [
        "I need to call a useless tool.\nAction: fake_tool\nAction Input: foo"
    ] * 3 + [
        "I now know the final answer.\nFinal Answer: bar"
    ]


def test_react_agent(responses):
    agent = ReActAgent.create(
        llm=FakeListChatModel(responses=responses),
        toolbox=Toolbox([fake_tool])
    )

    result = agent.run(input="test", context={})["output"]

    assert result == "bar"


def test_max_steps_abort(responses):
    max_steps = len(responses) - 1

    agent = ReActAgent.create(
        llm=FakeListChatModel(responses=responses),
        toolbox=Toolbox([fake_tool]),
        max_steps=max_steps
    )

    with pytest.raises(Exception) as exc_info:
        agent.run(input="test", context={})

    assert "max_steps" in exc_info.value.args[0]


def test_max_steps_success(responses):
    max_steps = len(responses)

    agent = ReActAgent.create(
        llm=FakeListChatModel(responses=responses),
        toolbox=Toolbox([fake_tool]),
        max_steps=max_steps
    )

    result = agent.run(input="test", context={})["output"]

    assert result == "bar"
