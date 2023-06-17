from typing import Dict
from langchain.base_language import BaseLanguageModel
from langchain.chains import LLMChain
from langchain.experimental.plan_and_execute.planners.base import LLMPlanner
from langchain.experimental.plan_and_execute.planners.chat_planner import PlanningOutputParser
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain.schema import SystemMessage
from gpt.plan_and_execute.planner.prompt import PLANNER_SYSTEM_MESSAGE, PLANNER_USER_MESSAGE


def create_planner(
    tools: Dict[str, str],
    llm: BaseLanguageModel
) -> LLMPlanner:
    tools = "\n".join([name + ": " + desc for name, desc in tools.items()])
    prompt_template = ChatPromptTemplate.from_messages(
        [
            SystemMessage(content=PLANNER_SYSTEM_MESSAGE.format(tools=tools)),
            HumanMessagePromptTemplate.from_template(PLANNER_USER_MESSAGE),
        ]
    )
    llm_chain = LLMChain(llm=llm, prompt=prompt_template)
    return LLMPlanner(
        llm_chain=llm_chain,
        output_parser=PlanningOutputParser(),
        stop=["<END_OF_PLAN>"],
    )
