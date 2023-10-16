from typing import List, Optional

from langchain.base_language import BaseLanguageModel
from langchain.chains.base import Chain

from gpt.chains.decide_chain.openai_functions.chain import create_openai_functions_decide_chain
from gpt.chains.decide_chain.standard.chain import create_standard_decide_chain
from gpt.config import supports_openai_functions


def create_decide_chain(
    llm: BaseLanguageModel,
    instructions: str,
    output_type: str,
    possible_values: Optional[List] = None,
    strategy: Optional[str] = None,
) -> Chain:
    if supports_openai_functions(llm):
        return create_openai_functions_decide_chain(llm, instructions, output_type, possible_values, strategy)
    else:
        return create_standard_decide_chain(llm, instructions, output_type, possible_values)
