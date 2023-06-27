from typing import List

from langchain.base_language import BaseLanguageModel
from langchain.chains.base import Chain

from gpt.chains.translate_chain.openai_functions.chain import create_openai_functions_translate_chain
from gpt.chains.translate_chain.standard.chain import create_standard_translate_chain
from gpt.config import supports_openai_functions


def create_translate_chain(
    llm: BaseLanguageModel,
    input_keys: List[str],
    target_language: str,
) -> Chain:
    if supports_openai_functions(llm):
        return create_openai_functions_translate_chain(llm, input_keys, target_language)
    else:
        return create_standard_translate_chain(llm, input_keys, target_language)
