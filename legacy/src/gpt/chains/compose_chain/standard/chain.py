from typing import Optional

from langchain import LLMChain
from langchain.base_language import BaseLanguageModel
from langchain.chains import SequentialChain, TransformChain
from langchain.chains.base import Chain
from langchain.chat_models.base import BaseChatModel
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate

from gpt.chains.compose_chain.common import type_to_prompt_type_str
from gpt.chains.compose_chain.standard.prompt import SYSTEM_MESSAGE_TEMPLATE, USER_MESSAGE_TEMPLATE, LETTER_INSTRUCTIONS
from gpt.chains.support.constitutional_chain.chain import ConstitutionalChain
from gpt.config import llm_to_model_tag
from gpt.util.prompt import chat_to_standard_prompt
from gpt.util.transform import transform_to_md_chain


def create_standard_compose_chain(
    llm: BaseLanguageModel,
    instructions: str,
    type: str,
    style: str,
    tone: str,
    length: str,
    language: str,
    sender: str,
    constitutional_principle: Optional[str] = None
) -> Chain:
    type_str = type_to_prompt_type_str(type)

    prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(
            SYSTEM_MESSAGE_TEMPLATE.format(
                style=style,
                tone=tone,
                length=length,
                lang=language,
                type=type_str,
                special_instructions=LETTER_INSTRUCTIONS if type == 'letter' else ''
            )
        ),
        HumanMessagePromptTemplate.from_template(
            USER_MESSAGE_TEMPLATE.format(
                instructions=instructions,
                lang=language
            )
        )
    ])
    if not isinstance(llm, BaseChatModel):
        prompt = chat_to_standard_prompt(prompt)

    llm_chain = LLMChain(
        llm=llm,
        prompt=prompt,
        output_key="output"
    )

    def transform_sender(input_key: str, output_key: str) -> TransformChain:
        def transform(inputs):
            if sender:
                return {output_key: inputs[input_key].replace('[SENDER]', sender)}
            else:
                return {output_key: inputs[input_key]}

        return TransformChain(
            input_variables=[input_key],
            output_variables=[output_key],
            transform=transform
        )

    output_variables = ["text"]

    constitutional_chain = None
    if constitutional_principle is not None:
        constitutional_chain = ConstitutionalChain.from_llm(
            chain=llm_chain,
            principle=constitutional_principle,
            llm=llm,
            verbose=True,
        )
        output_variables += ["initial_text"]

    return SequentialChain(
        tags=[
            "compose-chain",
            llm_to_model_tag(llm)
        ],
        input_variables=["input"],
        output_variables=output_variables,
        chains=[
            transform_to_md_chain(input_key="input", output_key="context_md"),
            constitutional_chain or llm_chain,
            transform_sender(input_key="output", output_key="text")
        ])
