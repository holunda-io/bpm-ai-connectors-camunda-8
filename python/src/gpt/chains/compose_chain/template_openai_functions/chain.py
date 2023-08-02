import re
from typing import List, Dict, Optional, Any

from jinja2 import Template
from langchain import LLMChain
from langchain.callbacks.manager import AsyncCallbackManagerForChainRun, CallbackManagerForChainRun
from langchain.chains.base import Chain
from langchain.chains.openai_functions.utils import get_llm_kwargs
from langchain.chat_models.base import BaseChatModel
from langchain.output_parsers.openai_functions import JsonOutputFunctionsParser
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate

from gpt.agents.openapi_agent.openapi import escape_format_placeholders
from gpt.chains.compose_chain.common import type_to_prompt_type_str
from gpt.chains.compose_chain.template_openai_functions.prompt import SYSTEM_MESSAGE_TEMPLATE, USER_MESSAGE_TEMPLATE
from gpt.util.functions import get_openai_function
from gpt.util.json import json_to_md

TEMPLATE_VAR_PATTERN = r'{\s*(\w+)(?:\s*:\s*([^\n}]+))?\s*}'


class TemplateComposeChain(Chain):

    llm: BaseChatModel

    template: str
    type: str
    style: str
    tone: str
    length: str
    language: str
    constitutional_principle: Optional[str] = None

    @property
    def input_keys(self) -> List[str]:
        return ["input"]

    @property
    def output_keys(self) -> List[str]:
        return ["text"]

    def _call(
        self,
        inputs: Dict[str, Any],
        run_manager: Optional[CallbackManagerForChainRun] = None,
    ) -> Dict[str, Any]:

        template = self.template.format(**inputs['input'])

        template_vars = {var: desc for var, desc in re.findall(TEMPLATE_VAR_PATTERN, template)}

        function = get_openai_function(
            "store_text",
            "Stores composed text parts for template variables.",
            template_vars
        )
        output_parser = JsonOutputFunctionsParser()

        context_md = json_to_md(inputs["input"])
        type_str = type_to_prompt_type_str(self.type)

        prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(
                SYSTEM_MESSAGE_TEMPLATE.format(
                    type=type_str,
                    style=self.style,
                    tone=self.tone,
                    length=self.length,
                    lang=self.language,
                )
            ),
            HumanMessagePromptTemplate.from_template(
                USER_MESSAGE_TEMPLATE.format(
                    template=escape_format_placeholders(template),
                    lang=self.language,
                    context_md=context_md
                )
            )
        ])

        llm_chain = LLMChain(
            llm=self.llm,
            prompt=prompt,
            llm_kwargs=get_llm_kwargs(function),
            output_parser=output_parser,
        )

        vars = llm_chain.run({})

        result = re.sub(TEMPLATE_VAR_PATTERN, lambda m: vars[m.group(1)], template)

        return {"text": result}

    async def _acall(
        self,
        inputs: Dict[str, Any],
        run_manager: Optional[AsyncCallbackManagerForChainRun] = None,
    ) -> Dict[str, Any]:
        """Asynchronously execute the chain."""
        raise NotImplementedError()
