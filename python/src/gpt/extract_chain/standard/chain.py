import json
from typing import Union, Dict

from langchain import LLMChain, PromptTemplate
from langchain.base_language import BaseLanguageModel
from langchain.chains import SequentialChain
from langchain.chains.base import Chain
from langchain.chains.openai_functions.utils import _convert_schema
from langchain.output_parsers.openai_functions import JsonKeyOutputFunctionsParser

from gpt.extract_chain.common import transform_to_md_chain, transform_empty_chain
from gpt.extract_chain.openai_functions.prompt import TASK_EXTRACT_REPEATED, TASK_EXTRACT_SINGLE
from gpt.extract_chain.standard.prompt import PROMPT_TEMPLATE
from gpt.output_parsers.json_output_parser import JsonOutputParser
from gpt.util.functions import _create_schema, get_openai_function


def create_standard_extract_chain(
    properties: Dict[str, Union[str, dict]],
    llm: BaseLanguageModel,
    repeated: bool = False
) -> Chain:
    if repeated:
        task = TASK_EXTRACT_REPEATED
        schema = get_openai_function('', '', properties, array_name="entities")["parameters"]
        output_parser = JsonOutputParser(key_name="entities")
    else:
        task = TASK_EXTRACT_SINGLE
        schema = properties
        output_parser = JsonOutputParser()

    schema = json.dumps(schema, indent=2).replace('{', '{{').replace('}', '}}')

    prompt = PromptTemplate.from_template(
        PROMPT_TEMPLATE.format(task=task, schema=schema)
    )

    llm_chain = LLMChain(
        llm=llm,
        prompt=prompt,
        output_parser=output_parser
    )

    return SequentialChain(
        input_variables=["input"],
        output_variables=["output"],
        chains=[
            transform_to_md_chain(input_key="input", output_key="input_md"),
            llm_chain,
            transform_empty_chain(input_key="text", output_key="output")
        ])
