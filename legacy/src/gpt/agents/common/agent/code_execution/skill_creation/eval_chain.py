from langchain import LLMChain
from langchain.base_language import BaseLanguageModel
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate

from gpt.output_parsers.BooleanContainsOutputParser import BooleanContainsOutputParser

SYSTEM_MESSAGE = """\
You are a genius Python code evaluation AI.
You will receive:
 - a user task
 - some context information
 - a python function and a call to it
 - the result of the call
Your task is to decide if the given function and call satisfy the user task.

You should look at:
 - the function implementation: does it seem to correctly capture the task and return the correct result?
 - the call values: Are the parameters correctly set and only contain information present in the context or task?
 - the result: Does the result value indicate a successful run and seem plausible?
Decide if everything in combination was successful at solving the user task.

First describe your reasoning in 1-2 sentences and then, if you think it was a success, output "TASK_SUCCESS", if it was no success, output "TASK_FAILURE".
Do not output anything else."""

HUMAN_MESSAGE = """\
# User task:
{task}

# Context:
{context}

# Available functions:
{functions}

# Function and call:
{function}

# Result:
{result}

TASK_SUCCESS or TASK_FAILURE:"""


def create_code_eval_chain(
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
    output_parser = BooleanContainsOutputParser(true_tag="TASK_SUCCESS", false_tag="TASK_FAILURE")
    return LLMChain(
        tags=["code-eval"],
        llm=llm,
        prompt=prompt,
        output_parser=output_parser,
        verbose=verbose
    )
