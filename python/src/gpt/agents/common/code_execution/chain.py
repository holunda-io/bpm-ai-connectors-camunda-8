from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence, Callable

from langchain import LLMChain
from langchain.agents import AgentExecutor
from langchain.base_language import BaseLanguageModel
from langchain.callbacks.base import BaseCallbackManager
from langchain.callbacks.manager import (
    AsyncCallbackManagerForChainRun,
    CallbackManagerForChainRun,
)
from langchain.chains.base import Chain
from langchain.embeddings import OpenAIEmbeddings

from gpt.agents.common.code_execution.agent import PythonReplAgent
from gpt.agents.common.code_execution.agent_executor import PythonReplAgentExecutor
from gpt.chains.retrieval_chain.chain import get_vector_store
from gpt.util.data_extract import create_data_extract_chain
from gpt.util.functions import schema_from_properties


def create_python_code_execution_agent(
    llm: BaseLanguageModel,
    functions: Sequence[Callable],
    callback_manager: Optional[BaseCallbackManager] = None,
    verbose: bool = True,
    agent_executor_kwargs: Optional[Dict[str, Any]] = None,
    **kwargs: Dict[str, Any],
) -> PythonReplAgentExecutor:
    """Construct a python agent from an LLM"""
    agent = PythonReplAgent.from_llm_and_functions(
        llm=llm,
        functions=functions,
        **(kwargs or {}),
    )
    return PythonReplAgentExecutor.from_agent(
        agent=agent,
        skill_store=get_vector_store(
            'weaviate://http://localhost:8080/SkillLibrary',
            OpenAIEmbeddings(),
            meta_attributes=['task', 'comment', 'function', 'example_call']
        ),
        callback_manager=callback_manager,
        verbose=verbose,
        **(agent_executor_kwargs or {}),
    )


DATA_TEMPLATE = """\
Code:
{code}

Result:
{result}"""

class PythonCodeExecutionChain(Chain):

    llm: BaseLanguageModel
    output_key: str = "result"  #: :meta private:

    code_execution_agent: AgentExecutor
    extract_chain: LLMChain
    output_schema: dict

    @property
    def input_keys(self) -> List[str]:
        return self.code_execution_agent.input_keys

    @property
    def output_keys(self) -> List[str]:
        return [self.output_key]

    @classmethod
    def from_llm_and_functions(
        cls,
        llm: BaseLanguageModel,
        functions: Sequence[Callable],
        output_schema: dict,
        output_key: str = "result"
    ) -> "PythonCodeExecutionChain":
        code_execution_agent = create_python_code_execution_agent(llm=llm, functions=functions)
        extract_chain = create_data_extract_chain(llm=llm)
        schema = schema_from_properties(output_schema)['properties']
        return cls(
            llm=llm,
            code_execution_agent=code_execution_agent,
            extract_chain=extract_chain,
            output_schema=schema,
            output_key=output_key
        )

    def _call(
        self,
        inputs: Dict[str, Any],
        run_manager: Optional[CallbackManagerForChainRun] = None,
    ) -> Dict[str, str]:
        result = self.code_execution_agent(inputs)
        execution_result = result['output']
        code = result['code']

        if run_manager:
            run_manager.on_text(f"Code execution yielded: {execution_result}")

        # extracted_result = self.extract_chain.run(
        #     output_schema=json.dumps(self.output_schema, indent=2),
        #     data=DATA_TEMPLATE.format(code=code, result=execution_result)
        # )
        # extracted_result = JsonOutputParser().parse(extracted_result)
        extracted_result = execution_result

        if run_manager:
            run_manager.on_text(f"Extracted result: {extracted_result}")

        return {self.output_key: extracted_result}

    async def _acall(
        self,
        inputs: Dict[str, Any],
        run_manager: Optional[AsyncCallbackManagerForChainRun] = None,
    ) -> Dict[str, str]:
        raise NotImplementedError("async not supported")


    @property
    def _chain_type(self) -> str:
        return "python_code_execution_chain"
