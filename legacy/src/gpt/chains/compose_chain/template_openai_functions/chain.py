import re
from typing import List, Dict, Optional, Any, Callable

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
from gpt.util.text import remove_stop_words

TEMPLATE_VAR_PATTERN = r'\{\s*([^{}\s]+(?:\s*[^{}\s]+)*)\s*\}'


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
        def desc_to_var_name(desc: str):
            v = remove_stop_words(desc, separator='_')
            return re.sub(r'[^A-Za-z0-9_\'äöüÄÖÜß]+', '', v).lower()

        def format_vars(template: str, f: Callable[[str], str]):
            return re.sub(TEMPLATE_VAR_PATTERN, lambda m: f(m.group(1)), template)

        # input variable map
        input_dict = inputs['input']
        # all variables found in the template
        template_vars = re.findall(TEMPLATE_VAR_PATTERN, self.template)
        # map of template variables that are not already in the input and need to be generated
        template_vars_to_generate_dict = {desc_to_var_name(desc): desc for desc in template_vars if desc not in input_dict.keys()}
        # input variables that are not present in the template
        non_template_input_var_dict = {k: v for k, v in input_dict.items() if k not in template_vars}

        function = get_openai_function(
            "store_text",
            "Stores composed text parts for template variables.",
            template_vars_to_generate_dict
        )
        output_parser = JsonOutputFunctionsParser()

        prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(
                SYSTEM_MESSAGE_TEMPLATE.format(
                    type=type_to_prompt_type_str(self.type),
                    style=self.style,
                    tone=self.tone,
                    length=self.length,
                    lang=self.language,
                )
            ),
            HumanMessagePromptTemplate.from_template(
                USER_MESSAGE_TEMPLATE.format(
                    template=escape_format_placeholders(
                        # remove template braces from variables that are already present in the input to not confuse the model what to generate
                        # we do not resolve these variables here to avoid sending that data to the API
                        format_vars(self.template, lambda v: v if v in input_dict.keys() else '{' + v + '}')
                    ),
                    lang=self.language,
                    context_md=json_to_md(non_template_input_var_dict)
                )
            )
        ])

        llm_chain = LLMChain(
            llm=self.llm,
            prompt=prompt,
            llm_kwargs=get_llm_kwargs(function),
            output_parser=output_parser,
        )

        if len(template_vars_to_generate_dict) > 0:
            generated_vars = llm_chain.run({})
        else:
            generated_vars = {}
        input_vars = {desc_to_var_name(k): v for k, v in inputs['input'].items()}
        all_vars = generated_vars | input_vars

        # resolve all template variables using either input or generated values
        result = format_vars(self.template, lambda v: all_vars[desc_to_var_name(v)])

        return {"text": result}

    async def _acall(
        self,
        inputs: Dict[str, Any],
        run_manager: Optional[AsyncCallbackManagerForChainRun] = None,
    ) -> Dict[str, Any]:
        """Asynchronously execute the chain."""
        raise NotImplementedError()
