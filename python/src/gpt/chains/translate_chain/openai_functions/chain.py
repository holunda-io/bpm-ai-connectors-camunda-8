from typing import List

from langchain import LLMChain
from langchain.base_language import BaseLanguageModel
from langchain.chains import SequentialChain
from langchain.chains.base import Chain
from langchain.chains.openai_functions.utils import get_llm_kwargs
from langchain.output_parsers.openai_functions import JsonOutputFunctionsParser
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate

from gpt.chains.translate_chain.common import get_output_schema, transform_to_pretty_json_chain
from gpt.chains.translate_chain.openai_functions.prompt import SYSTEM_MESSAGE_TEMPLATE, USER_MESSAGE_TEMPLATE
from gpt.config import llm_to_model_tag
from gpt.util.functions import get_openai_function


def create_openai_functions_translate_chain(
    llm: BaseLanguageModel,
    input_keys: List[str],
    target_language: str,
) -> Chain:

    function = get_openai_function(
        "store_translation",
        "Stores a finished translation into " + target_language,
        get_output_schema(input_keys, target_language)
    )
    output_parser = JsonOutputFunctionsParser()

    prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(
            SYSTEM_MESSAGE_TEMPLATE.format(lang=target_language)
        ),
        HumanMessagePromptTemplate.from_template(
            USER_MESSAGE_TEMPLATE
        )
    ])

    llm_chain = LLMChain(
        llm=llm,
        prompt=prompt,
        llm_kwargs=get_llm_kwargs(function),
        output_parser=output_parser,
    )

    return SequentialChain(
        tags=[
            "translate-chain",
            "openai-functions-translate-chain",
            llm_to_model_tag(llm)
        ],
        input_variables=["input"],
        output_variables=["text"],
        chains=[
            transform_to_pretty_json_chain(input_key="input", output_key="input_json"),
            llm_chain
        ])
