from typing import Dict, Any, Tuple

from langchain import LLMChain
from langchain.base_language import BaseLanguageModel
from langchain.chains import TransformChain, SequentialChain
from langchain.chains.base import Chain
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, SystemMessagePromptTemplate
from langchain.tools import format_tool_to_openai_function, StructuredTool
from pydantic import Field, BaseModel

from gpt.agents.plan_and_execute.executor.prompt import EXECUTOR_SYSTEM_MESSAGE, EXECUTOR_USER_MESSAGE, \
    EXECUTOR_USER_MESSAGE_FUNCTIONS, \
    EXECUTOR_SYSTEM_MESSAGE_FUNCTIONS, EXECUTOR_FUNCTION_INPUT_DESCRIPTION, EXECUTOR_NOOP_FUNCTION_DESCRIPTION, \
    EXECUTOR_FINAL_RESULT_FUNCTION_DESCRIPTION
from gpt.config import supports_openai_functions
from gpt.output_parsers.json_output_parser import JsonOutputParser
from gpt.util.functions import functions_chain


class InputSchema(BaseModel):
    input: str = Field(..., description=EXECUTOR_FUNCTION_INPUT_DESCRIPTION)


def noop(_):
    pass


def tool_tuple_to_function(t: Tuple[str, str]):
    tool = StructuredTool(
        name=t[0],
        description=t[1],
        func=noop,
        args_schema=InputSchema
    )
    return format_tool_to_openai_function(tool)


def transform_output(input_key: str, output_key: str) -> TransformChain:
    def transform(inputs):
        f = inputs[input_key]
        return {output_key: {'action': f['name'], **f['arguments']}}

    return TransformChain(
        input_variables=[input_key],
        output_variables=[output_key],
        transform=transform
    )


def create_executor(
        tools: Dict[str, str],
        llm: BaseLanguageModel
) -> Chain:
    if supports_openai_functions(llm):
        prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(EXECUTOR_SYSTEM_MESSAGE_FUNCTIONS),
            HumanMessagePromptTemplate.from_template(EXECUTOR_USER_MESSAGE_FUNCTIONS)
        ])
        noop_function = tool_tuple_to_function(("noop", EXECUTOR_NOOP_FUNCTION_DESCRIPTION))
        final_result_function = tool_tuple_to_function(("final_result", EXECUTOR_FINAL_RESULT_FUNCTION_DESCRIPTION))
        functions = [tool_tuple_to_function(t) for t in tools.items()] + [noop_function, final_result_function]
        return SequentialChain(
            input_variables=["task", "context", "previous_steps", "current_step"],
            output_variables=["output"],
            chains=[
                functions_chain(prompt, functions, llm),
                transform_output(input_key="text", output_key="output")
            ])
    else:
        return LLMChain(
            llm=llm,
            prompt=_create_prompt(tools),
            verbose=True,
            output_key="step",
            output_parser=JsonOutputParser()
        )


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
