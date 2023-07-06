from inspect import signature
from typing import Union, List, Dict, Sequence, Callable

from langchain import LLMChain, BasePromptTemplate
from langchain.base_language import BaseLanguageModel
from langchain.chains.openai_functions.utils import get_llm_kwargs, _convert_schema
from langchain.tools.convert_to_openai import FunctionDescription

from gpt.output_parsers.function_output_parser import FunctionsOutputParser


def functions_chain(
    prompt: BasePromptTemplate,
    functions: Union[FunctionDescription, List[FunctionDescription]],
    llm: BaseLanguageModel
) -> LLMChain:
    output_parser = FunctionsOutputParser()
    if isinstance(functions, list):
        kwargs = {"functions": functions}
    else:
        kwargs = get_llm_kwargs(functions)
    return LLMChain(
        llm=llm,
        prompt=prompt,
        llm_kwargs=kwargs,
        output_parser=output_parser,
    )


def schema_from_properties(properties: Dict[str, Union[str, dict]]):
    def type_or_default(x):
        if isinstance(x, str):
            return {"type": "string", "description": x}
        else:
            return x

    return {
        "properties": {k: type_or_default(v) for k, v in properties.items()},
        "required": list(properties.keys()),
    }


def schema_object_from_properties(properties: Dict[str, Union[str, dict]]):
    return _convert_schema(schema_from_properties(properties))


def get_openai_function(name, desc, schema: dict, array_name=None, array_description="") -> dict:
    schema = schema_object_from_properties(schema)
    if array_name is None:
        parameters = schema
    else:
        parameters = {
            "type": "object",
            "properties": {
                array_name: {"type": "array", "items": schema}
            },
            "required": [array_name],
        }
    return {
        "name": name,
        "description": desc,
        "parameters": parameters,
    }
