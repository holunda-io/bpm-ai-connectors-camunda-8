import os
from typing import Dict, Any, Optional, Callable, List, Type, Sequence

from langchain.callbacks.manager import CallbackManagerForChainRun, AsyncCallbackManagerForToolRun, \
    CallbackManagerForToolRun
from langchain.chat_models import ChatOpenAI
from langchain.chat_models.base import BaseChatModel
from langchain.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.prompts.chat import BaseMessagePromptTemplate
from langchain.vectorstores import VectorStore
from langchain.pydantic_v1 import Field, BaseModel

from gpt.agents.common.agent.base import AgentParameterResolver, Agent
from gpt.agents.common.agent.code_execution.natural_lang_answer_chain import create_natural_lang_answer_chain
from gpt.agents.common.agent.code_execution.prompt import SYSTEM_MESSAGE_FUNCTIONS, DEFAULT_FEW_SHOT_PROMPT_MESSAGES, \
    HUMAN_MESSAGE, \
    SYSTEM_MESSAGE_FUNCTIONS_WITH_STUB, HUMAN_MESSAGE_WITH_STUB, DEFAULT_FEW_SHOT_PROMPT_MESSAGES_WITH_STUB
from gpt.agents.common.agent.code_execution.python_tool import PythonREPLTool
from gpt.agents.common.agent.code_execution.skill_creation.create_skill import CreateSkillTool
from gpt.agents.common.agent.code_execution.skill_creation.eval_chain import create_code_eval_chain
from gpt.agents.common.agent.code_execution.util import create_func_obj, get_python_functions_descriptions, \
    is_simple_call, generate_function_stub, named_parameters_snake_case, get_function_name
from gpt.agents.common.agent.memory import AgentMemory
from gpt.agents.common.agent.openai_functions.openai_functions_agent import OpenAIFunctionsAgent
from gpt.agents.common.agent.openai_functions.output_parser import OpenAIFunctionsOutputParser
from gpt.agents.common.agent.step import AgentStep
from gpt.agents.common.agent.toolbox import Toolbox, AutoFinishTool


class CodeExecutionParameterResolver(AgentParameterResolver):

    skill_store: Optional[VectorStore] = Field(None, exclude=True)
    n_skills = 2
    skill_relevance_threshold = 0

    output_schema: Optional[Dict[str, Any]] = None
    llm_call: bool = True

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
            **({"result_function_stub": generate_function_stub(inputs['context'], self.output_schema)} if (self.output_schema or not self.llm_call) else {}),
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
    additional_defs: Optional[Sequence[str]] = None

    output_schema: Optional[Dict[str, Any]] = None
    llm_call: bool = True

    skill_store: Optional[VectorStore] = None
    enable_skill_creation: bool = False

    @classmethod
    def from_functions(
        cls,
        llm: BaseChatModel,
        python_functions: Optional[List[Callable]] = None,
        additional_python_definitions: Optional[Sequence[str]] = None,
        llm_call: bool = True,
        output_schema: Optional[Dict[str, Any]] = None,
        enable_skill_creation: bool = False,
        skill_store: Optional[VectorStore] = None,
        system_prompt_template: Optional[SystemMessagePromptTemplate] = None,
        user_prompt_templates: Optional[List[BaseMessagePromptTemplate]] = None,
        few_shot_prompt_messages: Optional[List[BaseMessagePromptTemplate]] = None,
        agent_memory: Optional[AgentMemory] = None,
        **kwargs
    ) -> "PythonCodeExecutionAgent":
        if enable_skill_creation and not skill_store:
            raise Exception("When enabling skill creation a vector store for the skills must be provided.")

        system_prompt_template = system_prompt_template or (
            # if we want to directly call the result function without LLM help or get a defined output schema, we need to predefine a function stub
            SystemMessagePromptTemplate.from_template(
                (SYSTEM_MESSAGE_FUNCTIONS_WITH_STUB if (output_schema or not llm_call) else SYSTEM_MESSAGE_FUNCTIONS)
                .format(additional_defs=("\n" + "\n\n".join(additional_python_definitions) + "\n" if additional_python_definitions else ""))
            )
        )
        user_prompt_templates = user_prompt_templates or (
            [HumanMessagePromptTemplate.from_template(HUMAN_MESSAGE_WITH_STUB if (output_schema or not llm_call) else HUMAN_MESSAGE)]
        )
        few_shot_prompt_messages = few_shot_prompt_messages or (
            DEFAULT_FEW_SHOT_PROMPT_MESSAGES_WITH_STUB if (output_schema or not llm_call) else DEFAULT_FEW_SHOT_PROMPT_MESSAGES
        )

        agent = cls(
            llm=llm,
            system_prompt_template=system_prompt_template,
            user_prompt_templates=user_prompt_templates,
            few_shot_prompt_messages=few_shot_prompt_messages,
            prompt_parameters_resolver=CodeExecutionParameterResolver(
                skill_store=skill_store,
                output_schema=output_schema,
                llm_call=llm_call
            ),
            output_parser=OpenAIFunctionsOutputParser(no_function_call_means_final_answer=False),
            toolbox=Toolbox(),
            base_functions=python_functions,
            additional_defs=additional_python_definitions,
            enable_skill_creation=enable_skill_creation,
            skill_store=skill_store,
            output_schema=output_schema,
            llm_call=llm_call,
            stop_words=None,
            agent_memory=agent_memory,
            **kwargs
        )

        python_tool = PythonREPLTool.from_functions(python_functions, additional_defs=additional_python_definitions)
        final_tool = StoreFinalResultWithCallTool(agent=agent) if llm_call else StoreFinalResultDefTool(agent=agent)
        agent.add_tools([python_tool, final_tool])

        return agent

    def _call(
        self,
        inputs: Dict[str, Any],
        run_manager: Optional[CallbackManagerForChainRun] = None,
    ) -> Dict[str, Any]:

        if not self.llm_call:
            task = inputs['input']
            context = inputs['context']
            filename = str(task).lower().replace(' ', '_') + "_".join(context.keys())
            if os.path.exists(filename):
                with open(filename, "r") as f:
                    function_def = f.read()

                    # todo duplication
                    python_tool = self.toolbox.get_tool('python')
                    function = function_def
                    function_name = get_function_name(function_def)
                    function_params = context
                    function_call = f'{function_name}({named_parameters_snake_case(function_params)})'
                    function_and_call = f'{function}\n\n{function_call}'

                    output = python_tool.run(function_and_call, truncate=False)

                    # todo duplication
                    if self.output_schema and len(self.output_schema.items()) == 1 and not isinstance(output, dict):
                        output = {list(self.output_schema.keys())[0]: output}

                    return {self.output_key: output}

        return super()._call(inputs, run_manager)

    def _return(
        self,
        inputs: Dict[str, Any],
        template_params: Dict[str, Any],
        last_step: AgentStep,
        run_manager: Optional[CallbackManagerForChainRun] = None
    ) -> Dict[str, Any]:
        if self.enable_skill_creation and self.skill_store:
            self.run_skill_creation(inputs, template_params, last_step, run_manager)

        return_vals = last_step.return_values

        # if output schema has just one field, the result function returns a simple value, and we need to wrap it
        if self.output_schema and len(self.output_schema.items()) == 1 and not isinstance(return_vals['output'], dict):
            return_vals['output'] = {list(self.output_schema.keys())[0]: return_vals['output']}

        if not self.output_schema:
            answer = create_natural_lang_answer_chain(self.llm).run(
                query=inputs["input"],
                context=inputs["context"],
                function=return_vals['function_def'] + '\n\n' + return_vals['function_call'],
                result=return_vals['output']
            )
            return_vals['output'] = answer

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

                if not self.llm_call:
                    filename = str(task).lower().replace(' ', '_') + "_".join(dict(context).keys())
                    with open(filename, mode="wt") as f:
                        f.write(function_def)

            else:
                print("Code evaluation failed, don't create new skill")
        else:
            print("Trivial composition, don't create new skill")


class StoreFinalResultWithCallSchema(BaseModel):
    function_def: str = Field(description="generic python function definition")
    function_call: str = Field(description="concrete call")

class StoreFinalResultWithCallTool(AutoFinishTool):

    name = "store_final_result"
    description = "Stores the final python function definition and call."
    args_schema: Type[StoreFinalResultWithCallSchema] = StoreFinalResultWithCallSchema

    agent: PythonCodeExecutionAgent

    def is_finish(self, observation: Any) -> bool:
        """
        If the result of the tool run did not raise any errors, we can finish.
        """
        return "<python_error>" not in str(observation['output'])

    def _run(
        self,
        function_def: str,
        function_call: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> dict:
        """Use the tool."""
        python_tool = self.agent.toolbox.get_tool('python')

        function_and_call = function_def + "\n\n" + function_call

        output = python_tool.run(function_and_call, truncate=False)

        return {
            "output": output,
            "function_def": function_def,
            "function_name": get_function_name(function_def),
            "function_call": function_call
        }

    async def _arun(
        self,
        function_def: str,
        function_call: str,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool asynchronously."""
        raise Exception("async not supported")

######################################################################################################


class StoreFinalResultDefSchema(BaseModel):
    function_def: str = Field(description="full implementation of function stub")


class StoreFinalResultDefTool(AutoFinishTool):

    name = "store_final_result"
    description = "Stores the final implementation of the python function stub."
    args_schema: Type[StoreFinalResultDefSchema] = StoreFinalResultDefSchema

    agent: PythonCodeExecutionAgent

    def is_finish(self, observation: Any) -> bool:
        """
        If the result of the tool run did not raise any errors, we can finish.
        """
        return "<python_error>" not in str(observation['output'])

    def _run(
        self,
        function_def: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> dict:
        """Use the tool."""
        python_tool = self.agent.toolbox.get_tool('python')

        function = function_def
        function_name = get_function_name(function_def)
        function_params = self.agent.template_params['context']
        function_call = f'{function_name}({named_parameters_snake_case(function_params)})'
        function_and_call = f'{function}\n\n{function_call}'

        output = python_tool.run(function_and_call, truncate=False)

        return {
            "output": output,
            "function_def": function_def,
            "function_name": function_name,
            "function_call": function_call
        }

    async def _arun(
        self,
        function_def: str,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool asynchronously."""
        raise Exception("async not supported")
