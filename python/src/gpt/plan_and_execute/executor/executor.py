from functools import partial
from typing import Dict, Callable, Any, Tuple

from langchain import PromptTemplate, LLMChain
from langchain.base_language import BaseLanguageModel
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, SystemMessagePromptTemplate
from langchain.schema import BaseMessage
from langchain.tools import format_tool_to_openai_function, StructuredTool
from pydantic import Field, BaseModel

from gpt.config import supports_openai_functions
from gpt.openapi_agent.api_planner.prompt import API_PLANNER_SYSTEM_MESSAGE, API_PLANNER_USER_MESSAGE
from gpt.openapi_agent.openapi import OpenAPISpec
from gpt.plan_and_execute.executor.prompt import EXECUTOR_SYSTEM_MESSAGE, EXECUTOR_USER_MESSAGE, EXECUTOR_USER_MESSAGE_FUNCTIONS, \
    EXECUTOR_SYSTEM_MESSAGE_FUNCTIONS, EXECUTOR_FUNCTION_INPUT_DESCRIPTION, EXECUTOR_NOOP_FUNCTION_DESCRIPTION


class InputSchema(BaseModel):
    input: str = Field(..., description=EXECUTOR_FUNCTION_INPUT_DESCRIPTION)


def noop(_):
    pass


def tool_dict_to_function(t: Tuple[str, str]):
    tool = StructuredTool(
        name=t[0],
        description=t[1],
        func=noop,
        args_schema=InputSchema
    )
    return format_tool_to_openai_function(tool)


def create_executor(
        tools: Dict[str, str],
        llm: BaseLanguageModel
) -> Callable:
    if supports_openai_functions(llm):
        messages = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(EXECUTOR_SYSTEM_MESSAGE_FUNCTIONS),
            HumanMessagePromptTemplate.from_template(EXECUTOR_USER_MESSAGE_FUNCTIONS)
        ])
        noop_function = tool_dict_to_function(("noop", EXECUTOR_NOOP_FUNCTION_DESCRIPTION))
        functions = [tool_dict_to_function(t) for t in tools.items()] + [noop_function]
        return partial(predict, llm, messages, functions=functions)
    else:
        return LLMChain(
            llm=llm,
            prompt=_create_prompt(tools),
            verbose=True,
            output_key="step"
        ).run


def predict(llm: ChatOpenAI, prompt: ChatPromptTemplate, functions, **kwargs: Any):
    messages = prompt.format_prompt(**kwargs).to_messages()
    return llm.predict_messages(messages=messages, functions=functions)


def _create_prompt(tools: Dict[str, str]):
    tool_strings = "\n".join(
        [f"{name}: {description}" for name, description in tools.items()]
    )
    tool_names = ", ".join([name for name, _ in tools.items()])
    system_message = EXECUTOR_SYSTEM_MESSAGE.format(
        tool_names=tool_names, tools=tool_strings
    )
    return ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(system_message),
        HumanMessagePromptTemplate.from_template(EXECUTOR_USER_MESSAGE)
    ])
