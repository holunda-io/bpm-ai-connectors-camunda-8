import re
from typing import Optional

from langchain.chains.base import Chain
from langchain.schema import BaseLanguageModel

from gpt.chains.compose_chain.standard.chain import create_standard_compose_chain
from gpt.chains.compose_chain.template_openai_functions.chain import TemplateComposeChain, TEMPLATE_VAR_PATTERN
from gpt.config import supports_openai_functions


def is_template(instructions_or_template: str) -> bool:
    return bool(re.search(TEMPLATE_VAR_PATTERN, instructions_or_template))


def create_compose_chain(
    llm: BaseLanguageModel,
    instructions_or_template: str,
    type: str,
    style: str,
    tone: str,
    length: str,
    language: str,
    sender: Optional[str] = None,
    constitutional_principle: Optional[str] = None
) -> Chain:
    template = is_template(instructions_or_template)
    if template and supports_openai_functions(llm):
        return TemplateComposeChain(
            llm=llm,
            template=instructions_or_template,
            type=type,
            language=language,
            style=style,
            tone=tone,
            length=length
        )
    elif not template:
        return create_standard_compose_chain(
            llm=llm,
            instructions=instructions_or_template,
            type=type,
            style=style,
            tone=tone,
            length=length,
            language=language,
            sender=sender,
            constitutional_principle=constitutional_principle
        )
    else:
        raise Exception("Templating not supported for this model")

