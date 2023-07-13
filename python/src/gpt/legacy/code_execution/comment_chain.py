from langchain import LLMChain
from langchain.base_language import BaseLanguageModel
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate

SYSTEM_MESSAGE = """\
You are a genius Python code commenting AI. Your task is to comment a given Python function.
You will receive the task that the function solves, the function itself, a call to the function and its result.
Your comment should contain:
 - the purpose of the function
 - a brief, high-level description of the code
 - the type and/or structure of the return value
Output just the Python docstring like that:

\"\"\"
Your comment
\"\"\"

Do not output anything else.
Limit your comment to no more than 3 sentences."""

HUMAN_MESSAGE = """\
# Task:
{task}

# Function and call:
{function}

# Result:
{result}

Function docstring:"""


def create_code_comment_chain(
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
        llm=llm,
        prompt=prompt,
        verbose=verbose
    )
