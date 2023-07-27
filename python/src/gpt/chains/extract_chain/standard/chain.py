import json
from typing import Union, Dict

from langchain import LLMChain, PromptTemplate
from langchain.base_language import BaseLanguageModel
from langchain.chains import SequentialChain
from langchain.chains.base import Chain

from gpt.chains.extract_chain.common import transform_empty_chain
from gpt.chains.extract_chain.openai_functions.prompt import TASK_EXTRACT_REPEATED, TASK_EXTRACT_SINGLE
from gpt.chains.extract_chain.standard.prompt import PROMPT_TEMPLATE
from gpt.config import llm_to_model_tag
from gpt.output_parsers.json_output_parser import JsonOutputParser
from gpt.util.functions import schema_from_properties
from gpt.util.transform import transform_to_md_chain


def create_standard_extract_chain(
    llm: BaseLanguageModel,
    output_schema: Dict[str, Union[str, dict]],
    repeated: bool = False
) -> Chain:
    # schema = _convert_schema(_create_schema(properties))
    schema = schema_from_properties(output_schema)['properties']  # not full valid json schema but simpler for the dumber models

    if repeated:
        task = TASK_EXTRACT_REPEATED
        schema = '{"entities": [' + json.dumps(schema, indent=2) + ', ...]}'
        output_parser = JsonOutputParser(key_name="entities")
    else:
        task = TASK_EXTRACT_SINGLE
        schema = json.dumps(schema, indent=2)
        output_parser = JsonOutputParser()

    schema = schema.replace('{', '{{').replace('}', '}}')

    prompt = PromptTemplate.from_template(
        PROMPT_TEMPLATE.format(task=task, schema=schema)
    )

    llm_chain = LLMChain(
        llm=llm,
        prompt=prompt,
        output_parser=output_parser
    )

    return SequentialChain(
        tags=[
            "extract-chain",
            "standard-extract-chain",
            llm_to_model_tag(llm)
        ],
        input_variables=["input"],
        output_variables=["output"],
        chains=[
            transform_to_md_chain(input_key="input", output_key="input_md"),
            llm_chain,
            transform_empty_chain(input_key="text", output_key="output")
        ])
