import json
from typing import Any, Dict, Optional, List, Union, Type

from langchain.callbacks.manager import CallbackManagerForToolRun, AsyncCallbackManagerForToolRun
from langchain.chains.base import Chain
from langchain.chat_models import ChatOpenAI
from langchain.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.tools import tool
from pydantic import BaseModel, Field

from gpt.agents.common.agent.openai_functions.openai_functions_agent import OpenAIFunctionsAgent
from gpt.agents.common.agent.toolbox import AutoFinishTool
from gpt.agents.process_generation_agent.engine import Engine
from gpt.agents.process_generation_agent.prompt import SYSTEM_MESSAGE, HUMAN_MESSAGE


class SubmitSolutionToolSchema(BaseModel):
    done: bool = Field(True)


class SubmitSolutionTool(AutoFinishTool):

    name = "submit_solution"
    description = "Submits the modelled process."
    args_schema: Type[SubmitSolutionToolSchema] = SubmitSolutionToolSchema

    context: dict
    engine: Engine

    def is_finish(self, observation: Any) -> bool:
        """
        If the result of the tool run did not raise any errors, we can finish.
        """
        return "<engine_error>" not in str(observation)

    def _run(
        self,
        done: bool = True,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> Union[dict, str]:
        """Use the tool."""
        try:
            for i in range(100):
                self.engine.run(self.context)
        except Exception as e:
            return "<engine_error>" + str(e)

        #write_json_to_file(self.engine.raw_elements, 'elements.json')
        #write_json_to_file(self.engine.raw_flows, 'flows.json')

        return {"output": self.engine.log, "process": {"elements": self.engine.raw_elements, "flows": self.engine.raw_flows}}

    async def _arun(
        self,
        done: bool = True,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> dict:
        """Use the tool asynchronously."""
        raise Exception("async not supported")


def create_process_generation_agent(
    llm: ChatOpenAI,
    context: dict,
    tools: Dict[str, Union[str, dict]]
) -> OpenAIFunctionsAgent:

    engine = Engine()

    @tool
    def add_task(type: str, name: str, instruction: str, input_variables: List[str], output_variable: Optional[str] = None,
                 output_schema: Optional[dict] = None) -> str:
        """Adds a new task."""
        try:
            engine.add_element({
                "type": type,
                "name": name,
                "instruction": instruction,
                "input_variables": input_variables,
                "output_variable": output_variable,
                "output_schema": output_schema
            })
        except Exception as e:
            return str(e)
        return f"Task '{name}' added."

    @tool
    def add_gateway(name: str) -> str:
        """Adds a new gateway."""
        try:
            engine.add_element({
                "type": "gateway",
                "name": name
            })
        except Exception as e:
            return str(e)
        return f"Gateway '{name}' added."

    @tool
    def add_start_event(name: str) -> str:
        """Adds the start event."""
        engine.add_element({
            "type": "start",
            "name": name
        })
        return f"Start event '{name}' added."

    @tool
    def add_end_event(name: str) -> str:
        """Adds a new end event."""
        engine.add_element({
            "type": "end",
            "name": name
        })
        return f"End event '{name}' added."

    @tool
    def add_flow(from_: str, to_: str, condition: Optional[str] = None) -> str:
        """Adds a new flow from an element to another."""
        try:
            engine.add_flow({
                "from": from_,
                "to": to_,
                "condition": condition
            })
        except Exception as e:
            return str(e)
        return f"Flow from '{from_}' to '{to_}'{' on condition ' + condition if condition else ''} added."

    agent = OpenAIFunctionsAgent.create(
        llm=llm,
        system_prompt_template=SystemMessagePromptTemplate.from_template(
            SYSTEM_MESSAGE.format(tasks="\n".join([f"- {n}: {d}" for n, d in tools.items()]))
        ),
        user_prompt_templates=[
            HumanMessagePromptTemplate.from_template(
                HUMAN_MESSAGE.format(context=", ".join(context.keys()))
            )
        ],
        few_shot_prompt_messages=[],
        max_steps=20
    )

    agent.add_tools([
        add_start_event, add_task, add_flow, add_gateway, add_end_event, SubmitSolutionTool(context=context, engine=engine)
    ])

    return agent
