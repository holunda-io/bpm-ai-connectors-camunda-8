from typing import Union, Dict, Optional

from langchain.base_language import BaseLanguageModel
from langchain.chains.base import Chain

from gpt.chains.extract_chain.openai_functions.chain import create_openai_functions_extract_chain
from gpt.chains.extract_chain.standard.chain import create_standard_extract_chain
from gpt.config import supports_openai_functions


def create_extract_chain(
    output_schema: Dict[str, Union[str, dict]],
    llm: BaseLanguageModel,
    repeated: bool = False,
    repeated_description: Optional[str] = None
) -> Chain:
    if supports_openai_functions(llm):
        return create_openai_functions_extract_chain(llm, output_schema, repeated, repeated_description or "")
    else:
        return create_standard_extract_chain(llm, output_schema, repeated)
