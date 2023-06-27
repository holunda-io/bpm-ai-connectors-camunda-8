import json
from typing import List

from langchain import LLMChain, PromptTemplate
from langchain.base_language import BaseLanguageModel
from langchain.chains import SequentialChain
from langchain.chains.base import Chain

from gpt.chains.translate_chain.common import get_output_schema, transform_to_pretty_json_chain
from gpt.chains.translate_chain.standard.prompt import PROMPT_TEMPLATE
from gpt.config import llm_to_model_tag
from gpt.output_parsers.json_output_parser import JsonOutputParser


def create_standard_translate_chain(
    llm: BaseLanguageModel,
    input_keys: List[str],
    target_language: str,
) -> Chain:
    schema = get_output_schema(input_keys, target_language)
    schema = json.dumps(schema, indent=2).replace('{', '{{').replace('}', '}}')

    output_parser = JsonOutputParser()

    prompt = PromptTemplate.from_template(
        PROMPT_TEMPLATE.format(lang=target_language, schema=schema)
    )

    llm_chain = LLMChain(
        llm=llm,
        prompt=prompt,
        output_parser=output_parser
    )

    return SequentialChain(
        tags=[
            "translate-chain",
            "standard-translate-chain",
            llm_to_model_tag(llm)
        ],
        input_variables=["input"],
        output_variables=["text"],
        chains=[
            transform_to_pretty_json_chain(input_key="input", output_key="input_json"),
            llm_chain
        ])
