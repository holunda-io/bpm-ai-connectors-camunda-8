from typing import Union, Dict

from langchain import LLMChain
from langchain.base_language import BaseLanguageModel
from langchain.chains import SequentialChain
from langchain.chains.base import Chain
from langchain.chains.openai_functions.utils import get_llm_kwargs
from langchain.output_parsers.openai_functions import JsonOutputFunctionsParser, JsonKeyOutputFunctionsParser
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate

from gpt.chains.extract_chain.common import transform_empty_chain
from gpt.chains.extract_chain.openai_functions.prompt import SYSTEM_MESSAGE_TEMPLATE, TASK_EXTRACT_REPEATED, \
    TASK_EXTRACT_SINGLE
from gpt.util.functions import get_openai_function
from gpt.util.transform import transform_to_md_chain


def create_openai_functions_extract_chain(
    properties: Dict[str, Union[str, dict]],
    llm: BaseLanguageModel,
    repeated: bool = False,
    repeated_description: str = ""
) -> Chain:
    if repeated:
        task = TASK_EXTRACT_REPEATED
        function = get_openai_function(
            "information_extraction",
            "Extracts the relevant entities from the passage.",
            properties,
            array_name="entities",
            array_description=repeated_description
        )
        output_parser = JsonKeyOutputFunctionsParser(key_name="entities")
    else:
        task = TASK_EXTRACT_SINGLE
        function = get_openai_function(
            "information_extraction",
            "Extracts the relevant information from the passage.",
            properties
        )
        output_parser = JsonOutputFunctionsParser()

    prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(
            SYSTEM_MESSAGE_TEMPLATE.format(task=task)
        ),
        HumanMessagePromptTemplate.from_template(
            "{input_md}"
        )
    ])

    llm_chain = LLMChain(
        llm=llm,
        prompt=prompt,
        llm_kwargs=get_llm_kwargs(function),
        output_parser=output_parser,
    )

    return SequentialChain(
        input_variables=["input"],
        output_variables=["output"],
        chains=[
            transform_to_md_chain(input_key="input", output_key="input_md"),
            llm_chain,
            transform_empty_chain(input_key="text", output_key="output")
        ])
