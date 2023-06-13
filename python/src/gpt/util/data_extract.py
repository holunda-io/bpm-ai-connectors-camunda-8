from typing import List, Dict, Any, Optional, Union

from langchain import LLMChain, PromptTemplate
from langchain.base_language import BaseLanguageModel
from langchain.callbacks.manager import CallbackManagerForChainRun
from langchain.chains.base import Chain
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate


def create_data_extract_chain(
        llm: BaseLanguageModel,
        output_key: str = "result"
) -> LLMChain:
    return LLMChain(
        llm=llm,
        prompt=_create_prompt(),
        verbose=True,
        output_key=output_key
    )


def _create_prompt():
    return ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate(
            prompt=PromptTemplate(
                template=SYSTEM_MESSAGE,
                input_variables=[]
            )
        ),
        HumanMessagePromptTemplate(
            prompt=PromptTemplate(
                template="Data: {data}\n\nOutput Schema: {output_schema}\n\nResult:",
                input_variables=["data", "output_schema"],
            )
        )
    ])

SYSTEM_MESSAGE = """You are a genius data extraction AI. 
Your task is to extract some information from a given text or piece of data and return it as a json blob according to a given schema.
Only output a valid json blob with all information according to the schema. Do not output anything else.
Only add information that actually can be found in the given data. Do not make anything up!
If you can not find some of the requested information, set it to null."""