import json
import random

from dotenv import load_dotenv
from langchain.chains.openai_functions.utils import get_llm_kwargs
from langchain.chat_models import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage, FunctionMessage, AIMessage

from gpt.util.functions import get_openai_function

load_dotenv(dotenv_path='../../../connector-secrets.txt')


def functions():
    model = ChatOpenAI(model="gpt-3.5-turbo-0613")
    function = get_openai_function(
        name='get_weather',
        desc='Gets the weather forecast for a city and timeframe.',
        schema={
            "city": {
                "description": "the city",
                "type": "string",
                "enum": ["Hamburg", "Kiel", "Munich"]
            },
            "n_days": {
                "description": "number of days to forecast",
                "type": "integer"
            }
        }
    )

    messages = [
        SystemMessage(content="You are a helpful assistant that calls functions to answer user requests."),
        HumanMessage(content="How will the weather be at the baltic sea the next 3 days?")
    ]

    result_message = model.predict_messages(messages, **get_llm_kwargs(function))

    f = result_message.additional_kwargs.get("function_call", None)
    if f is not None:
        f_name = f['name']
        f_args = json.loads(f['arguments'])

        print(f"\n\nCalled function '{f_name}' with arguments: {f_args}")


###############################################################################################


def interactive_functions():
    model = ChatOpenAI(model="gpt-3.5-turbo-0613")

    functions = [get_openai_function(
        name='my_function',
        desc='A mysterious function',
        schema={
            "input": {
                "description": "the input to the function",
                "type": "string",
            }
        }
    )
    ]

    print("What do you want to know?")

    messages = [
        SystemMessage(content="You are a helpful assistant."),
        HumanMessage(content="My aunt has 3 ducks, 5 dogs and a cat."),
        AIMessage(content="", additional_kwargs={"function_call": { "name": "my_function", "arguments": '{ "input": "3" }' }}),
        HumanMessage(content="There once was a little farm with 10 chickens, a horse, two dogs, five cats and a sheep. It was a nice farm with 1000 acres."),
        AIMessage(content="", additional_kwargs={"function_call": { "name": "my_function", "arguments": '{ "input": "5" }' }}),
        HumanMessage(content=input())
    ]

    while True:
        result_message = model.predict_messages(messages, functions=functions)
        messages.append(result_message)

        print(f"result: <{result_message}>")

        f = result_message.additional_kwargs.get("function_call", None)

        if f is not None:
            f_name = f['name']
            f_args = json.loads(f['arguments'])

            print(f"\nCalled function '{f_name}' with arguments: {f_args}")

        break

interactive_functions()

#############################################################################################################


def extract_function():
    model = ChatOpenAI(model="gpt-3.5-turbo-0613")
    function = get_openai_function(
        name='store_decision',
        desc='Stores a business decision with corresponding reasoning.',
        schema={
            "reasoning": {
                "description": "brief description of the reasoning behind the decision",
                "type": "string",
            },
            "intent": {
                "description": "the final value of the decision itself",
                "type": "string",
                "enum": ["ORDER_PROBLEM", "ORDER_QUESTION", "ORDER_CANCEL", "GENERAL_QUESTION", "GENERAL_COMPLAINT", "POSITIVE_FEEDBACK"]
            }
        }
    )

    messages = [
        SystemMessage(content="You are a helpful business assistant makes business decisions and stores them together with their reasoning."),
        HumanMessage(content="""\
        What is the intent of the customer?

        Customer: Hallo, die Lieferung ging echt schnell. Max Mustermann
        """)
    ]

    result_message = model.predict_messages(messages, **get_llm_kwargs(function))

    f = result_message.additional_kwargs.get("function_call", None)
    if f is not None:
        f_name = f['name']
        f_args = json.loads(f['arguments'])

        print(f"\n\nCalled function '{f_name}' with arguments: {f_args}")

