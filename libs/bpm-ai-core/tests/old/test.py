from langsmith import traceable
from pydantic import BaseModel, Field

from bpm_ai_core.llm.anthropic import AnthropicChat
from bpm_ai_core.llm.common.message import ToolCallsMessage
from bpm_ai_core.llm.common.tool import Tool
from bpm_ai_core.llm.openai_chat import ChatOpenAI
from bpm_ai_core.prompt.prompt import Prompt


@traceable(run_type="chain", name="Test_OpenAI")
def test_openai(name: str = "Bennet"):
    llm = ChatOpenAI(model="gpt-4-1106-preview")
    prompt = Prompt.from_file("test", name=name, x=False)
    print("Prompt: ")
    print(prompt.format())
    print("Answer: ")
    message = llm.predict(prompt)
    print(message)
    return message.content


def test_prompt():
    prompt = Prompt.from_file("test_history2", task="go go gadget", image_url="https://www.planet-wissen.de/technik/verkehr/mobilitaet_von_morgen/mobilitaet-google-auto-100~_v-gseapremiumxl.jpg")
    print("Prompt: ")
    messages = prompt.format()
    print(messages)
    #for m in messages:
    #    print(m)


@traceable(run_type="chain", name="Test_OutputSchema_OpenAI")
def test_openai_output_schema():
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


@traceable(run_type="chain", name="Test_Images_OpenAI")
def test_openai_images():
    llm = ChatOpenAI(model="gpt-4-vision-preview")
    prompt = Prompt.from_file("test_image", image_url="/Users/bennet/Desktop/Screenshot 2023-10-16 at 00.13.54.png")
    print("Prompt: ")
    print(prompt.format())
    print("Answer: ")
    message = llm.predict(prompt)
    print(message.content)
    return message.content


class WeatherArgs(BaseModel):
    location: str
    n_days: int = Field(description="number of days to forecast")

def weather_fun(location, n_days):
    print(f"called weather fun with {location} and {n_days}")
    return "Sunny"

def news_fun(locations, days):
    print(f"called news fun with {locations} and {days}")
    return "Coool news"


def test1():
    print(WeatherArgs.model_json_schema())

@traceable(run_type="chain", name="Test_Tools_OpenAI")
def test_openai_tools():
    llm = ChatOpenAI()
    prompt = Prompt.from_file("test_tools")
    print(prompt.format())
    print("Answer: ")
    message = llm.predict(
        prompt,
        tools=[
            Tool.from_callable("get_weather", "get the weather", WeatherArgs, weather_fun),
            Tool.from_callable("get_news", "get the news",
                               {"locations": ["location for the news"], "days": [{"type": "integer", "description": "n days to check news"}]}, news_fun),
        ]
    )
    print(message)

    if isinstance(message, ToolCallsMessage):
        print(message.invoke_all())

    return message.content


@traceable(run_type="chain", name="Test_Anthropic")
def test_anthropic(name: str = "Bennet"):
    llm = AnthropicChat()
    prompt = Prompt.from_file("test", name=name, trait="helpful, German-only speaking")
    print("Prompt: ")
    print(prompt.format())
    print("Answer: ")
    message = llm.predict(prompt)
    print(message)
    return message.content
