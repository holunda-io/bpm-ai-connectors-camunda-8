import re

from jinja2 import Template
from langsmith import traceable
from pydantic import BaseModel, Field

from bpm_ai_core.llm.common.function import Function
from bpm_ai_core.llm.common.message import FunctionCallMessage
from bpm_ai_core.llm.openai_chat import ChatOpenAI
from bpm_ai_core.prompt.prompt import Prompt
from bpm_ai_core.util.openai import json_schema_from_shorthand


@traceable(run_type="chain", name="Test_OpenAI")
def test_openai(name: str = "Bennet"):
    llm = ChatOpenAI()
    prompt = Prompt.from_file("test", name=name, x=False)
    print("Prompt: ")
    print(prompt.format())
    print("Answer: ")
    message = llm.predict(prompt)
    print(message)
    return message.content


def test_prompt():
    prompt = Prompt.from_file("test_history", task="go go gadget")
    print("Prompt: ")
    print(prompt.format())


@traceable(run_type="chain", name="Test_OutputSchema_OpenAI")
def test_openai_json():
    llm = ChatOpenAI()
    prompt = Prompt.from_file("test", name="Bennet", x=False)
    print("Prompt: ")
    print(prompt.format())
    print("Answer: ")
    message = llm.predict(
        prompt,
        output_schema={
            "is_question": {
                "type": "boolean"
            }
        }
    )
    print(message.content)
    return message.content


class WeatherArgs(BaseModel):
    location: str
    n_days: int = Field(description="number of days to forecast")


def test_fun(locations, days):
    print(f"called fun with {locations} and {days}")


@traceable(run_type="chain", name="Test_Functions_OpenAI")
def test_openai(name: str = "Bennet"):
    llm = ChatOpenAI()
    prompt = Prompt.from_file("test", name=name, x=False)
    print("Prompt: ")
    print(prompt.format())
    print("Answer: ")
    message = llm.predict(
        prompt,
        functions=[
            Function.from_callable("get_weather", "get the weather", WeatherArgs, test_fun),
            Function.from_callable("get_news", "get the news",
                                   {"locations": ["location for the news"], "days": [{"type": "integer", "description": "n days to check news"}]}, test_fun),
        ]
    )
    print(message)

    if isinstance(message, FunctionCallMessage):
        print(message.invoke())

    return message.content