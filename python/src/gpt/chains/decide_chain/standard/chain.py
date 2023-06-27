import json
from typing import Optional, List

from langchain import LLMChain, PromptTemplate
from langchain.base_language import BaseLanguageModel
from langchain.chains import SequentialChain
from langchain.chains.base import Chain

from gpt.chains.decide_chain.common import get_output_schema
from gpt.chains.decide_chain.standard.prompt import PROMPT_TEMPLATE
from gpt.config import llm_to_model_tag
from gpt.output_parsers.json_output_parser import JsonOutputParser
from gpt.util.functions import schema_from_properties
from gpt.util.transform import transform_to_md_chain


def create_standard_decide_chain(
    llm: BaseLanguageModel,
    instructions: str,
    output_type: str,
    possible_values: Optional[List] = None,
) -> Chain:
    schema = schema_from_properties(get_output_schema(output_type, possible_values))["properties"]
    schema = json.dumps(schema, indent=2).replace('{', '{{').replace('}', '}}')

    output_parser = JsonOutputParser()

    prompt = PromptTemplate.from_template(
        PROMPT_TEMPLATE.format(task=instructions, schema=schema)
    )

    llm_chain = LLMChain(
        llm=llm,
        prompt=prompt,
        output_parser=output_parser
    )

    return SequentialChain(
        tags=[
            "decide-chain",
            "standard-decide-chain",
            llm_to_model_tag(llm)
        ],
        input_variables=["input"],
        output_variables=["text"],
        chains=[
            transform_to_md_chain(input_key="input", output_key="context_md"),
            llm_chain
        ])
