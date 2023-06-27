from typing import Optional, List

from langchain import LLMChain
from langchain.base_language import BaseLanguageModel
from langchain.chains import SequentialChain
from langchain.chains.base import Chain
from langchain.chains.openai_functions.utils import get_llm_kwargs
from langchain.output_parsers.openai_functions import JsonOutputFunctionsParser
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate

from gpt.chains.decide_chain.common import get_decision_output_schema
from gpt.chains.decide_chain.openai_functions.prompt import SYSTEM_MESSAGE_TEMPLATE, USER_MESSAGE_TEMPLATE
from gpt.config import llm_to_model_tag
from gpt.util.functions import get_openai_function
from gpt.util.transform import transform_to_md_chain


def create_openai_functions_decide_chain(
    llm: BaseLanguageModel,
    instructions: str,
    output_type: str,
    possible_values: Optional[List] = None,
) -> Chain:

    function = get_openai_function(
        "store_decision",
        "Stores a final decision value and corresponding reasoning.",
        get_decision_output_schema(output_type, possible_values)
    )
    output_parser = JsonOutputFunctionsParser()

    prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(
            SYSTEM_MESSAGE_TEMPLATE
        ),
        HumanMessagePromptTemplate.from_template(
            USER_MESSAGE_TEMPLATE.format(task=instructions)
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
            "decide-chain",
            "openai-functions-decide-chain",
            llm_to_model_tag(llm)
        ],
        input_variables=["input"],
        output_variables=["text"],
        chains=[
            transform_to_md_chain(input_key="input", output_key="context_md"),
            llm_chain
        ])
