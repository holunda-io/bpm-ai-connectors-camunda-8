from langchain import LLMChain
from langchain.base_language import BaseLanguageModel
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate

from gpt.output_parsers.BooleanContainsOutputParser import BooleanContainsOutputParser

SYSTEM_MESSAGE = """\
Assistant is a genius Python code and question answering AI.
You will receive:
 - a user query/question
 - some context information
 - a python function and a call to it
 - the result of the call
Your task is to answer the original user query/question given this information.

Only use the provided information, do not make anything up! 
If you think that you can't answer the question based on the given information, say so.
The answer is for an end user. Do not mention anything about Python, the code or anything else technical. 
Just use the information to answer the question."""

HUMAN_MESSAGE = """\
# User query/question:
{query}

# Context:
{context}

# Function and call:
{function}

# Result:
{result}

# Answer to user query/question:"""


def create_natural_lang_answer_chain(
    llm: BaseLanguageModel,
    verbose: bool = True,
) -> LLMChain:
    prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(
            SYSTEM_MESSAGE
        ),
        HumanMessagePromptTemplate.from_template(
            HUMAN_MESSAGE
        )
    ])
    return LLMChain(
        tags=["code-answer"],
        llm=llm,
        prompt=prompt,
        verbose=verbose
    )
