from typing import Dict, Optional, Any

from langchain.agents import AgentExecutor
from langchain.base_language import BaseLanguageModel
from langchain.callbacks.base import BaseCallbackManager
from langchain.callbacks.manager import AsyncCallbackManagerForChainRun, CallbackManagerForChainRun
from langchain.schema import AgentFinish
from langchain.vectorstores import VectorStore

from gpt.agents.common.code_execution.agent import PythonReplAgent
from gpt.agents.common.code_execution.comment_chain import create_code_comment_chain
from gpt.agents.common.code_execution.eval_chain import create_code_eval_chain
from gpt.agents.common.code_execution.tool import PythonREPLTool
from gpt.agents.common.code_execution.util import extract_functions, extract_function_calls
from gpt.util.functions import get_python_functions_descriptions


class PythonReplAgentExecutor(AgentExecutor):

    skill_store: Optional[VectorStore] = None

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
        functions = self.agent.functions
        task = self.inputs['input']
        context = self.inputs['context']
        llm = self.agent.llm_chain.llm

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
        call = extract_function_calls(code)[0]
        self.skill_store.add_texts(
            texts=[f'# {task}\n\n{comment}\n{function}'],
            metadatas=[{
                'task': task,
                'comment': comment,
                'function': function,
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

