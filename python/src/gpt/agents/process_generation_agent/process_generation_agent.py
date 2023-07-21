import json
from typing import Any, Dict, Optional, List

from langchain import SQLDatabase, LLMChain
from langchain.callbacks.manager import CallbackManagerForChainRun
from langchain.chains.base import Chain
from langchain.chat_models import ChatOpenAI
from langchain.experimental.plan_and_execute.planners.base import LLMPlanner
from langchain.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.vectorstores import VectorStore

from gpt.agents.common.agent.code_execution.code_execution_agent import PythonCodeExecutionAgent
from gpt.agents.common.agent.code_execution.util import generate_function_stub
from gpt.agents.database_agent.code_exection.functions import get_database_functions
from gpt.agents.database_agent.code_exection.prompt import create_user_prompt_messages, create_few_shot_messages
from gpt.agents.plan_and_execute.planner.planner import create_planner

SYSTEM_MESSAGE = """\
Assistant is a genius Python programmer and business process modeler that implements business processes in Python code to solve a task.
You will receive a task and a high-level plan to solve the task. Your task is to implement an executable business process as a Python function to solve the task end to end according to the plan.
You will be given a stub of the result function that you need to implement.

# Available Python Functions
Here are the functions that you can use in your code:
{functions}
Do not add placeholders for these functions but assume that they are in scope.

All functions follow this schema: `task_type(task_instructions: str, output_schema: dict, **input_variables) -> dict`
Every function will use the input variable values to perform the given high-level instruction and return a result dict according to the output_schema json schema.
Make sure every function receives the input variables it needs to fulfill its task!
If expressions may only use boolean fields from previous results, make sure to request the boolean type if you plan on using a value in an if expression!
The function must return string literals (no format string!) that describe the types of end events.

# Example
Here is an example for the task `create a new subscription for the customer`:

def process(customer_email: str) -> str:
    id_result = customer_database(
        'Find the id of the customer by his email',
        output_schema={{"id": "the id of the customer"}}
        customer_email=customer_email
    )
    subscription_result = subscription_service(
        'Create a new subscription for the customer',
        output_schema={{"success": {{"type": "boolean", "description": "whether the subscription was created successfully"}}}}
        customer_id=id_result['id'],
    )
    if subscription_result['success']:
        return "Subscription created"
    else:
        return "Subscription not created"

The Python environment uses "tinypy" Python implementation that only supports a very minimal set of Python features:
- if/else and if/elif/else with simple boolean expression
- function calls with keyword and positional arguments
- dicts

Do NOT use any other functions than the ones listed above! Do NOT use any standard lib functions.

Call `store_final_result` with the full implementation of the function stub containing the full code to solve the task and returning the final result.

Begin!

Remember:
- only use the provided functions and nothing else!
- implement a task-solving process in the function stub according to the plan
- keep it simple and don't overcomplicate things
- return values must be string literals
- Do NOT use any standard lib functions.
- return your final solution as an implementation of the given function stub using `store_final_result`"""

HUMAN_MESSAGE = """\
# Task:
{input}

# Plan:
{plan}

# Function stub:
{result_function_stub}"""

def human_task(task: str, output_schema: dict, **kwargs) -> dict:
    """A human task. You should only use this if a subtask is not suitable for the automated functions. The human will receive all keyword arguments and return a result as a dict according to output_schema."""
    print(f"{task}: {kwargs}")
    return output_schema

def extract_data(task: str, output_schema: dict, **kwargs) -> dict:
    """A service that can transform unstructured data into a given output format. Returns a result as a dict according to output_schema."""
    print(f"{task}: {kwargs}")
    return output_schema

def customer_database(task: str, output_schema: dict, **kwargs) -> dict:
    """A service that can retrieve information about a customer and its data. Needs appropriate input to find the customer. Returns a result as a dict according to output_schema."""
    print(f"{task}: {kwargs}")
    return output_schema

def subscription_service(task: str, output_schema: dict, **kwargs) -> dict:
    """A service that can manage customer subscriptions. Returns a result as a dict according to output_schema."""
    print(f"{task}: {kwargs}")
    return output_schema

def create_process_generation_agent(
    llm: ChatOpenAI,
    output_schema: Optional[Dict[str, Any]] = None
) -> Chain:
    return PythonCodeExecutionAgent.from_functions(
        llm=llm,
        python_functions=[human_task, extract_data, customer_database, subscription_service],
        system_prompt_template=SystemMessagePromptTemplate.from_template(SYSTEM_MESSAGE),
        user_prompt_templates=[HumanMessagePromptTemplate.from_template(HUMAN_MESSAGE)],
        few_shot_prompt_messages=[],
        enable_skill_creation=False,
        skill_store=None,
        call_direct=True,
        output_schema=output_schema
    )


def to_markdown_ordered_list(lst):
    return '\n'.join(f'{i+1}. {item}' for i, item in enumerate(lst))


class ProcessGenerationChain(Chain):

    output_key: str = "output"  #: :meta private:

    llm: ChatOpenAI
    agent: Chain
    planner: LLMPlanner

    verbose = True

    @property
    def input_keys(self) -> List[str]:
        return ["input", "context"]

    @property
    def output_keys(self) -> List[str]:
        return [self.output_key]

    @classmethod
    def from_llm(
        cls,
        llm: ChatOpenAI,
        tools: Dict[str, str],
        output_schema: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> "ProcessGenerationChain":
        """Initialize from LLM."""
        return cls(
            llm=llm,
            planner=create_planner(llm=llm, tools=tools),
            agent=create_process_generation_agent(llm, output_schema),
            **kwargs
        )

    def _call(
        self,
        inputs: Dict[str, Any],
        run_manager: Optional[CallbackManagerForChainRun] = None,
    ) -> Dict[str, Any]:
        """Query and get response."""
        input = inputs['input']
        context = inputs['context']

        plan = self.planner.plan({
            "context": json.dumps(context, indent=2),
            "task": input
        })
        steps = [s.value for s in plan.steps]
        plan_str = to_markdown_ordered_list(steps)

        agent = create_process_generation_agent(
            llm=self.llm,
            # output_schema=json.loads(output_schema) if output_schema else None,
        )

        function_def = agent(
            inputs={
                "input": input,
                "plan": plan_str,
                #"context": plan_str + "\n\n# Function Stub:\n" + generate_function_stub(context),
                "context": context
            },
            return_only_outputs=True
        )["function_def"]

        return {self.output_key: function_def}
