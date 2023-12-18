from langchain import LLMChain
from langchain.base_language import BaseLanguageModel
from langchain.chains.openai_functions.utils import get_llm_kwargs
from langchain.output_parsers.openai_functions import JsonOutputFunctionsParser
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate

from gpt.util.functions import get_openai_function

SYSTEM_MESSAGE_TEMPLATE = """\
Your task is to write a critique and a revision request for an output of an AI assistant based on a given description or instructions that the user gave.

The critique request should always start with "Identify specific ways in which the assistant’s last response".
The revision request should always start with "Please rewrite the assistant response".

Here is an example of a good critique and revision request:

# Example:
User description: The text should never contain any harmful or illegal content.
Function input:
```
{{
  "critique_request": "Identify specific ways in which the assistant’s last response is harmful or illegal.",
  "revision_request": "Please rewrite the assistant response to remove any and all harmful or illegal content.'"
}}
```"""


def create_generate_principle_chain(llm: BaseLanguageModel):
    function = get_openai_function(
        "store_decision",
        "Stores a final decision value and corresponding reasoning.",
        {
            "critique_request": "The critique request based on the user description, starting with 'Identify specific ways in which the assistant’s last response'",
            "revision_request": "The revision request based on the user description, starting with 'Please rewrite the assistant response'"
        }
    )
    output_parser = JsonOutputFunctionsParser()

    prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(SYSTEM_MESSAGE_TEMPLATE),
        HumanMessagePromptTemplate.from_template("{input}")
    ])

    return LLMChain(
        llm=llm,
        prompt=prompt,
        llm_kwargs=get_llm_kwargs(function),
        output_parser=output_parser,
    )
