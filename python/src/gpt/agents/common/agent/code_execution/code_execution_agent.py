import json
from typing import Dict, Any, Optional, Callable, List

from langchain.callbacks.manager import CallbackManagerForChainRun
from langchain.vectorstores import VectorStore
from pydantic import Field

from gpt.agents.common.agent.base import AgentParameterResolver, Agent
from gpt.agents.common.agent.code_execution.skill_creation.create_skill import CreateSkillTool
from gpt.agents.common.agent.code_execution.store_final_result import StoreFinalResultWithCallTool, StoreFinalResultDefTool
from gpt.agents.common.agent.openai_functions.openai_functions_agent import OpenAIFunctionsAgent
from gpt.agents.common.agent.step import AgentStep
from gpt.agents.common.agent.toolbox import Toolbox
from gpt.agents.common.agent.code_execution.skill_creation.eval_chain import create_code_eval_chain
from gpt.agents.common.agent.code_execution.prompt import SYSTEM_MESSAGE_FUNCTIONS, DEFAULT_FEW_SHOT_PROMPT_MESSAGES, HUMAN_MESSAGE, \
    SYSTEM_MESSAGE_FUNCTIONS_WITH_STUB
from gpt.agents.common.agent.code_execution.python_tool import PythonREPLTool
from gpt.agents.common.agent.code_execution.util import create_func_obj, get_python_functions_descriptions, is_simple_call, generate_function_stub, python_exec, \
    named_parameters_snake_case
from langchain.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.prompts.chat import BaseMessagePromptTemplate
from langchain.chat_models import ChatOpenAI


class CodeExecutionParameterResolver(AgentParameterResolver):

    skill_store: Optional[VectorStore] = Field(None, exclude=True)
    n_skills = 5
    skill_relevance_threshold = 0.5

    output_schema: Optional[Dict[str, Any]] = None
    call_direct: bool = True

    class Config:
        arbitrary_types_allowed = True

    def resolve_parameters(self, inputs: Dict[str, Any], agent: Agent, agent_step: AgentStep, **kwargs) -> Dict[str, Any]:
        if not isinstance(agent, PythonCodeExecutionAgent):
            raise Exception("Agent must be PythonCodeExecutionAgent")

        base_functions = agent.base_functions

        if self.skill_store:
            # retrieve up to n relevant skill functions (with a minimum relevance threshold)
            skill_functions_strs, skill_functions = self.retrieve_skill_functions(inputs)
            # update tools with new set of available functions
            self.update_tools(agent, base_functions, skill_functions_strs)
            # new set of available functions
            all_functions = base_functions + skill_functions
        else:
            # without skill store only base functions are available
            all_functions = base_functions

        return {
            "functions": get_python_functions_descriptions(all_functions),
            "function_names": [f.__name__ for f in all_functions],
            **({"result_function_stub": generate_function_stub(json.loads(inputs['context']), self.output_schema)} if (self.output_schema or self.call_direct) else {}),
            "transcript": agent_step.transcript,
            **inputs
        }

    def retrieve_skill_functions(self, inputs):
        relevant_skill_documents = self.skill_store.similarity_search_with_relevance_scores(
            query=inputs['input'],
            k=self.n_skills
        )
        relevant_skill_documents = [s[0] for s in relevant_skill_documents if s[1] > self.skill_relevance_threshold]
        skill_functions_strs = [s.metadata['function'] for s in relevant_skill_documents]

        # create function objects
        skill_functions = [create_func_obj(s.metadata['function'], s.metadata['comment']) for s in relevant_skill_documents]
        return skill_functions_strs, skill_functions

    @staticmethod
    def update_tools(agent, base_functions, skill_functions_strs):
        updated_python_tool = PythonREPLTool.from_functions(base_functions, skill_functions_strs)
        agent.toolbox.add_tool(updated_python_tool, replace=True)


class PythonCodeExecutionAgent(OpenAIFunctionsAgent):

    base_functions: List[Callable] = []

    output_schema: Optional[Dict[str, Any]] = None
    call_direct: bool = True

    skill_store: Optional[VectorStore] = None
    enable_skill_creation: bool = False

    def __init__(
        self,
        llm: ChatOpenAI,
        python_functions: Optional[List[Callable]] = None,
        call_direct: bool = True,
        output_schema: Optional[Dict[str, Any]] = None,
        enable_skill_creation: bool = False,
        skill_store: Optional[VectorStore] = None,
        system_prompt_template: Optional[SystemMessagePromptTemplate] = None,
        user_prompt_templates: Optional[List[BaseMessagePromptTemplate]] = None,
        few_shot_prompt_messages: Optional[List[BaseMessagePromptTemplate]] = None,
        max_steps: int = 10
    ):
        python_tool = PythonREPLTool.from_functions(python_functions)
        # without call_direct the LLM generates the concrete call
        final_tool = StoreFinalResultDefTool() if call_direct else StoreFinalResultWithCallTool()
        super().__init__(
            llm=llm,
            system_prompt_template=system_prompt_template or (
                # if we want to directly call the result function without LLM help or get a defined output schema, we need to predefine a function stub
                SystemMessagePromptTemplate.from_template(SYSTEM_MESSAGE_FUNCTIONS_WITH_STUB if (output_schema or call_direct) else SYSTEM_MESSAGE_FUNCTIONS)
            ),
            user_prompt_templates=user_prompt_templates or [HumanMessagePromptTemplate.from_template(HUMAN_MESSAGE)],
            few_shot_prompt_messages=few_shot_prompt_messages or DEFAULT_FEW_SHOT_PROMPT_MESSAGES,
            prompt_parameters_resolver=CodeExecutionParameterResolver(
                skill_store=skill_store,
                output_schema=output_schema,
                call_direct=call_direct
            ),
            toolbox=Toolbox([python_tool, final_tool]),
            stop_words=None,
            max_steps=max_steps
        )
        self.base_functions = python_functions
        self.call_direct = call_direct
        self.output_schema = output_schema
        self.call_direct = call_direct
        if enable_skill_creation and not skill_store:
            raise Exception("When enabling skill creation a vector store for the skills must be provided.")
        self.skill_store = skill_store
        self.enable_skill_creation = enable_skill_creation

    def _return(
        self,
        inputs: Dict[str, Any],
        template_params: Dict[str, Any],
        last_step: AgentStep,
        run_manager: Optional[CallbackManagerForChainRun] = None
    ) -> Dict[str, Any]:
        if self.enable_skill_creation and self.skill_store:
            self.run_skill_creation(inputs, template_params, last_step, run_manager)

        python_tool = self.toolbox.get_tool('python')

        return_vals = last_step.return_values
        if self.call_direct:
            function = return_vals['function_def']
            function_name = return_vals["function_name"]
            function_params = json.loads(inputs['context'])
            function_and_call = f'{function}\n\n{function_name}({named_parameters_snake_case(function_params)})'
            output = python_tool.run(function_and_call, truncate=False)
        else:
            function_and_call = return_vals['function_def'] + "\n\n" + return_vals['function_call']
            output = python_tool.run(function_and_call, truncate=False)

        # if output schema has just one field, the result function returns a simple value, and we need to wrap it
        if self.output_schema and len(self.output_schema.items()) == 1 and not isinstance(output, dict):
            res = {list(self.output_schema.keys())[0]: output}
            print(f'output: {res}')
            output = res

        return_vals = {'output': output, **return_vals}

        return {
            **return_vals,
            **({"last_step": last_step} if self.return_last_step else {})
        }

    def run_skill_creation(self, inputs, template_params, last_step, run_manager):
        task = inputs['input']
        context = inputs['context']
        function_def = last_step.return_values['function_def']
        function_call = last_step.return_values['function_call']
        function_and_call = function_def + "\n\n" + function_call
        execution_result = last_step.return_values['output']
        all_function_descriptions = template_params["functions"]
        all_function_names = template_params["function_names"]

        # if generated function simply delegates to another basic or skill function, no need to create new skill
        if not is_simple_call(function_def, all_function_names):
            # evaluate if function is a valid solution to the task
            eval_chain = create_code_eval_chain(llm=self.llm)
            success = eval_chain.run(
                task=task,
                context=context,
                function=function_and_call,
                functions=all_function_descriptions,
                result=execution_result,
                callbacks=run_manager.get_child() if run_manager else None
            )
            # if function is fine, create a re-usable skill from it
            if success:
                CreateSkillTool(llm=self.llm, skill_store=self.skill_store).run(
                    {"task": task, **last_step.return_values},
                    callbacks=run_manager.get_child() if run_manager else None
                )
            else:
                print("Code evaluation failed, don't create new skill")
        else:
            print("Trivial composition, don't create new skill")

