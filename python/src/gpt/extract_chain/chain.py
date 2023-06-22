import json
from typing import Union, Dict

from langchain.base_language import BaseLanguageModel
from langchain.chains.base import Chain

from gpt.config import supports_openai_functions
from gpt.extract_chain.openai_functions.chain import create_openai_functions_extract_chain
from gpt.extract_chain.standard.chain import create_standard_extract_chain


def create_extract_chain(
    properties: Dict[str, Union[str, dict]],
    llm: BaseLanguageModel,
    repeated: bool = False
) -> Chain:
    if supports_openai_functions(llm):
        return create_openai_functions_extract_chain(properties, llm, repeated)
    else:
        return create_standard_extract_chain(properties, llm, repeated)
