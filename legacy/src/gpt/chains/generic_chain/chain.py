from typing import Union, Dict

from langchain.base_language import BaseLanguageModel
from langchain.chains.base import Chain

from gpt.chains.generic_chain.openai_functions.chain import create_openai_functions_generic_chain
from gpt.chains.generic_chain.standard.chain import create_standard_generic_chain
from gpt.config import supports_openai_functions


def create_generic_chain(
    llm: BaseLanguageModel,
    instructions: str,
    output_format: Dict[str, Union[str, dict]],
) -> Chain:
    if supports_openai_functions(llm):
        return create_openai_functions_generic_chain(llm, instructions, output_format)
    else:
        return create_standard_generic_chain(llm, instructions, output_format)
