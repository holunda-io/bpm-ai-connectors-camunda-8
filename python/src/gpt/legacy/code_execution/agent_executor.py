from typing import Dict, Optional, Any, List, Tuple, Union

from langchain.agents import AgentExecutor
from langchain.agents.agent import ExceptionTool
from langchain.agents.tools import InvalidTool
from langchain.base_language import BaseLanguageModel
from langchain.callbacks.base import BaseCallbackManager
from langchain.callbacks.manager import AsyncCallbackManagerForChainRun, CallbackManagerForChainRun
from langchain.schema import AgentFinish, AgentAction, OutputParserException
from langchain.tools import BaseTool
from langchain.vectorstores import VectorStore

from gpt.legacy.code_execution.agent import PythonReplAgent
from gpt.agents.common.agent.code_execution.skill_creation.comment_chain import create_code_comment_chain
from gpt.agents.common.agent.code_execution.skill_creation.eval_chain import create_code_eval_chain
from gpt.agents.common.agent.code_execution.python_tool import PythonREPLTool
from gpt.agents.common.agent.code_execution.util import extract_functions, extract_function_calls, extract_imports, \
    get_python_functions_descriptions, \
    create_func_obj, is_simple_call


class PythonReplAgentExecutor(AgentExecutor):

    agent: PythonReplAgent

    skill_store: Optional[VectorStore] = None
    k_skills = 5
    skill_relevance_score = 0.3

    inputs: Dict[str, str] = {}

    @classmethod
    def from_agent(
        cls,
        agent: PythonReplAgent,
        skill_store: Optional[VectorStore] = None,
        callback_manager: Optional[BaseCallbackManager] = None,
        **kwargs: Any,
    ) -> "PythonReplAgentExecutor":
        """Create from agent and tools."""
        return cls(
            agent=agent,
            skill_store=skill_store,
            tools=[PythonREPLTool.from_functions(agent.functions)],
            callback_manager=callback_manager,
            **kwargs
        )

    def run_skill_creation(self, return_values: dict):
        if not isinstance(self.agent, PythonReplAgent):
            raise Exception("Underlying agent must be CodeExecutionAgent")

        code = return_values['code']
        execution_result = return_values['output']
        functions = self.agent.get_all_functions()
        task = self.inputs['input']
        context = self.inputs['context']
        llm = self.agent.llm_chain.llm

        if is_simple_call(extract_functions(code)[0], [f.__name__ for f in functions]):
            print("Trivial composition, don't create new skill")
            return  # generated function simply calls another basic or skill function, no need to create new skill

        eval_chain = create_code_eval_chain(llm=llm)
        success = eval_chain.run(
            task=task,
            context=context,
            function=code,
            functions=get_python_functions_descriptions(functions),
            result=execution_result
        )
        if success:
            print("Create new skill")
            self.store_skill(llm, task, code, execution_result)

    def store_skill(self, llm: BaseLanguageModel, task: str, code: str, result: Any):
        comment = self.generate_comment(llm, task, code, result)
        function = extract_functions(code)[0]
        imports = '\n'.join(extract_imports(code))
        function_with_imports = imports + '\n' + function
        call = extract_function_calls(code)[0]
        self.skill_store.add_texts(
            texts=[f'# {task}\n\n{comment}\n{function_with_imports}'],
            metadatas=[{
                'task': task,
                'comment': comment,
                'function': function_with_imports,
                'example_call': call,
            }]
        )

    @staticmethod
    def generate_comment(llm: BaseLanguageModel, task: str, function: str, result: Any) -> str:
        comment_chain = create_code_comment_chain(llm=llm)
        return comment_chain.run(
            task=task,
            function=function,
            result=str(result)
        )

    def _return(
        self,
        output: AgentFinish,
        intermediate_steps: list,
        run_manager: Optional[CallbackManagerForChainRun] = None,
    ) -> Dict[str, Any]:
        if run_manager:
            run_manager.on_agent_finish(output, color="green", verbose=self.verbose)
        final_output = output.return_values

        if self.skill_store:
            self.run_skill_creation(final_output)

        if self.return_intermediate_steps:
            final_output["intermediate_steps"] = intermediate_steps
        return final_output

    def _take_next_step(
        self,
        name_to_tool_map: Dict[str, BaseTool],
        color_mapping: Dict[str, str],
        inputs: Dict[str, str],
        intermediate_steps: List[Tuple[AgentAction, str]],
        run_manager: Optional[CallbackManagerForChainRun] = None,
    ) -> Union[AgentFinish, List[Tuple[AgentAction, str]]]:
        """Take a single step in the thought-action-observation loop."""

        relevant_skills_str = ""
        if self.skill_store:
            relevant_skill_documents = self.skill_store.similarity_search_with_relevance_scores(
                query=inputs['input'],
                k=self.k_skills
            )
            relevant_skill_documents = [s[0] for s in relevant_skill_documents if s[1] > self.skill_relevance_score]
            skill_functions_strs = [s.metadata['function'] for s in relevant_skill_documents]
            skill_functions = [create_func_obj(s.metadata['function'], s.metadata['comment']) for s in relevant_skill_documents]

            name_to_tool_map['python'] = PythonREPLTool.from_functions(self.agent.functions, skill_functions_strs)

            self.agent.skill_functions = skill_functions

        try:
            # Call the LLM to see what to do.
            output = self.agent.plan(
                intermediate_steps,
                callbacks=run_manager.get_child() if run_manager else None,
                **inputs,
            )
        except OutputParserException as e:
            if isinstance(self.handle_parsing_errors, bool):
                raise_error = not self.handle_parsing_errors
            else:
                raise_error = False
            if raise_error:
                raise e
            text = str(e)
            if isinstance(self.handle_parsing_errors, bool):
                if e.send_to_llm:
                    observation = str(e.observation)
                    text = str(e.llm_output)
                else:
                    observation = "Invalid or incomplete response"
            elif isinstance(self.handle_parsing_errors, str):
                observation = self.handle_parsing_errors
            elif callable(self.handle_parsing_errors):
                observation = self.handle_parsing_errors(e)
            else:
                raise ValueError("Got unexpected type of `handle_parsing_errors`")
            output = AgentAction("_Exception", observation, text)
            if run_manager:
                run_manager.on_agent_action(output, color="green")
            tool_run_kwargs = self.agent.tool_run_logging_kwargs()
            observation = ExceptionTool().run(
                output.tool_input,
                verbose=self.verbose,
                color=None,
                callbacks=run_manager.get_child() if run_manager else None,
                **tool_run_kwargs,
            )
            return [(output, observation)]
        # If the tool chosen is the finishing tool, then we end and return.
        if isinstance(output, AgentFinish):
            return output
        actions: List[AgentAction]
        if isinstance(output, AgentAction):
            actions = [output]
        else:
            actions = output
        result = []
        for agent_action in actions:
            if run_manager:
                run_manager.on_agent_action(agent_action, color="green")
            # Otherwise we lookup the tool
            if agent_action.tool in name_to_tool_map:
                tool = name_to_tool_map[agent_action.tool]
                return_direct = tool.return_direct
                color = color_mapping[agent_action.tool]
                tool_run_kwargs = self.agent.tool_run_logging_kwargs()
                if return_direct:
                    tool_run_kwargs["llm_prefix"] = ""
                # We then call the tool on the tool input to get an observation
                observation = tool.run(
                    agent_action.tool_input,
                    verbose=self.verbose,
                    color=color,
                    callbacks=run_manager.get_child() if run_manager else None,
                    **tool_run_kwargs,
                )
            else:
                tool_run_kwargs = self.agent.tool_run_logging_kwargs()
                observation = InvalidTool().run(
                    agent_action.tool,
                    verbose=self.verbose,
                    color=None,
                    callbacks=run_manager.get_child() if run_manager else None,
                    **tool_run_kwargs,
                )
            result.append((agent_action, observation))
        return result

    def _call(
        self,
        inputs: Dict[str, str],
        run_manager: Optional[CallbackManagerForChainRun] = None,
    ) -> Dict[str, Any]:
        self.inputs = inputs
        return super()._call(inputs, run_manager)

    async def _acall(
        self,
        inputs: Dict[str, str],
        run_manager: Optional[AsyncCallbackManagerForChainRun] = None,
    ) -> Dict[str, str]:
        raise NotImplementedError("async not supported for CodeAgentExecutor")



