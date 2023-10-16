from typing import Optional, List

from langchain import LLMChain
from langchain.base_language import BaseLanguageModel
from langchain.chains import SequentialChain
from langchain.chains.base import Chain
from langchain.chains.openai_functions.utils import get_llm_kwargs
from langchain.output_parsers.openai_functions import JsonOutputFunctionsParser
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate, \
    AIMessagePromptTemplate

from gpt.chains.decide_chain.common import get_decision_output_schema
from gpt.chains.decide_chain.openai_functions.prompt import SYSTEM_MESSAGE_TEMPLATE, USER_MESSAGE_TEMPLATE, \
    ONE_SHOT_USER_MESSAGE, COT_SUFFIX, DEFAULT_SUFFIX, ONE_SHOT_FUNCTION_CALL_ARG
from gpt.config import llm_to_model_tag
from gpt.util.functions import get_openai_function
from gpt.util.prompt import FunctionMessagePromptTemplate
from gpt.util.transform import transform_to_md_chain

def get_cot_decision_output_schema(
    output_type: str,
    possible_values: Optional[List] = None
):
    return {
        "relevantFacts": {
            "type": "array",
            "items": {
                "type": "string",
                "description": "A discrete fact"
            }
        },
        "deducedInformation": {
            "type": "array",
            "items": {
                "type": "string",
                "description": "Additional information that can be deduced from the relevantFacts"
            }
        },
        "reasoningSteps": {
            "type": "array",
            "items": {
                "type": "string",
                "description": "A discrete reasoning step. Do not perform multiple steps in one. Be very fine-grained and use discrete steps/items."
            }
        },
        "finalReasoning": "concise description of the final reasoning behind the decision",
        "decision": {
            "description": "the final decision value, may be null if no decision was possible",
            "type": output_type,
            **({"enum": possible_values} if possible_values is not None else {})
        }
    }


def create_openai_functions_decide_chain(
    llm: BaseLanguageModel,
    instructions: str,
    output_type: str,
    possible_values: Optional[List] = None,
    strategy: Optional[str] = None,
) -> Chain:
    if strategy == 'cot':
        output_schema = get_cot_decision_output_schema(output_type, possible_values)
    else:
        output_schema = get_decision_output_schema(output_type, possible_values)

    function = get_openai_function(
        "store_decision",
        "Stores a final decision value and corresponding reasoning.",
        output_schema
    )
    output_parser = JsonOutputFunctionsParser()

    prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(
            SYSTEM_MESSAGE_TEMPLATE.format(
                suffix=(COT_SUFFIX if strategy == 'cot' else DEFAULT_SUFFIX)
            )
        )]
        + ([HumanMessagePromptTemplate.from_template(
            ONE_SHOT_USER_MESSAGE
        ),
        AIMessagePromptTemplate.from_template(
            template="",
            additional_kwargs={"function_call": {"name": "store_decision", "arguments": ONE_SHOT_FUNCTION_CALL_ARG}}
        ),
        FunctionMessagePromptTemplate.from_template(
            name="store_decision",
            template="Decision stored, continue with next task.",
        )] if strategy == 'cot' else [])
        + [HumanMessagePromptTemplate.from_template(
            USER_MESSAGE_TEMPLATE.format(task=instructions)
        )]
    )

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
