import json
from typing import Any, Dict, Optional, List, Union, Type

from langchain import SQLDatabase, LLMChain
from langchain.callbacks.manager import CallbackManagerForChainRun, CallbackManagerForToolRun, AsyncCallbackManagerForToolRun
from langchain.chains.base import Chain
from langchain.chat_models import ChatOpenAI
from langchain.experimental.plan_and_execute.planners.base import LLMPlanner
from langchain.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate, AIMessagePromptTemplate
from langchain.tools import tool
from langchain.vectorstores import VectorStore
from pydantic import BaseModel, Field

from gpt.agents.common.agent.code_execution.code_execution_agent import PythonCodeExecutionAgent
from gpt.agents.common.agent.code_execution.util import generate_function_stub
from gpt.agents.common.agent.openai_functions.openai_functions_agent import OpenAIFunctionsAgent
from gpt.agents.common.agent.toolbox import AutoFinishTool
from gpt.agents.database_agent.code_exection.functions import get_database_functions
from gpt.agents.database_agent.code_exection.prompt import create_user_prompt_messages, create_few_shot_messages
from gpt.agents.plan_and_execute.planner.planner import create_planner
from gpt.agents.process_generation_agent.engine import Engine
from gpt.util.prompt import FunctionMessagePromptTemplate

SYSTEM_MESSAGE = """\
Assistant is a genius business process modeler that models correct and efficient business processes to solve a given task.
You will receive a task and a set of process input variables.
Your task is to model an executable business process to solve the task end to end.
You will call functions to model the process step by step and get feedback from the process engine.

# Supported Elements
## Tasks
Here are the task types that you can use in your process:
{tasks}

All tasks need a natural language instruction on what to do, a set of input variable expressions, an output variable (or None) and an output_schema (if there is an output variable).

## Other Elements
- "start": The single start event
- "end": An end event
- "gateway": An exclusive gateway

## Flows
Flows go "from_" an element name "to_" another element name.
Flows that exit a gateway have a condition expression that references an input variable or previous result variable.
Nested fields are accessed by dot notation. Negation uses "!".
Flows that don't belong to a gateway have no condition.

Make sure that you input all variables to a task that are required to fulfill its instructions.
Make sure to correctly access existing variables and fields.
Gateway conditions must be exclusive and only use boolean variable value types.

# Instructions
- Always describe your thoughts first and describe step-by-step what needs to be done
- Model the process step-by-step by adding elements and their flows and pay attention to the feedback from the process engine
- If you encounter an error, fix it and try again
- make sure the process follows the structure of a valid BPMN process (one start event, process may only split on gateways, every path ends with an end event)
- when you think you are done, submit your solution

Begin!

Remember:
- describe your thoughts, think and model step-by-step
- keep it simple and don't overcomplicate things
- process must be correct and valid
- variable access must be correct"""

HUMAN_MESSAGE = """\
# Task:
{{input}}

# Input Variables:
{context}"""

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
    ) -> str:
        """Use the tool."""
        try:
            for i in range(25):
                print(f"Running process #{i}")
                self.engine.run(self.context)
        except Exception as e:
            return "<engine_error>" + str(e)

        write_json_to_file(self.engine.raw_elements, 'elements.json')
        write_json_to_file(self.engine.raw_flows, 'flows.json')

        return self.engine.log

    async def _arun(
        self,
        done: bool = True,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool asynchronously."""
        raise Exception("async not supported")

def write_json_to_file(dict_obj, filename):
    try:
        with open(filename, 'w') as file:
            file.write(json.dumps(dict_obj, indent=4))
        print(f"Dictionary successfully written to {filename}")
    except Exception as e:
        print(f"An error occurred: {e}")

def create_process_generation_agent(
    llm: ChatOpenAI,
    context: dict,
    tools: Dict[str, Union[str, dict]]
) -> Chain:

    engine = Engine([], [])

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
            SYSTEM_MESSAGE.format(tasks=", ".join(tools.keys()))
        ),
        user_prompt_templates=[
            HumanMessagePromptTemplate.from_template(HUMAN_MESSAGE.format(context=", ".join(context.keys())))
        ],
        few_shot_prompt_messages=[],
        max_steps=20
    )

    agent.add_tools([
        add_start_event, add_task, add_flow, add_gateway, add_end_event, SubmitSolutionTool(context=context, engine=engine)
    ])

    return agent
