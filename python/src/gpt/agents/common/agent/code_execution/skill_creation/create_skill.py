from typing import Type, Optional, Any

from langchain.callbacks.manager import CallbackManagerForToolRun, AsyncCallbackManagerForToolRun, \
    CallbackManagerForChainRun
from langchain.schema import BaseLanguageModel
from langchain.tools import BaseTool
from langchain.vectorstores import VectorStore
from pydantic import BaseModel, Field

from gpt.agents.common.agent.code_execution.skill_creation.comment_chain import create_code_comment_chain
from gpt.agents.common.agent.code_execution.util import extract_functions, extract_imports


class CreateSkillToolSchema(BaseModel):
    task: str = Field()
    function_def: str = Field()
    function_call: str = Field()
    output: Any = Field()


class CreateSkillTool(BaseTool):
    """Tool for creating a re-usable skill and storing it in a vector database."""

    name = "create_skill"
    description = "Store a re-usable skill for later use."
    args_schema: Type[CreateSkillToolSchema] = CreateSkillToolSchema

    llm: BaseLanguageModel
    skill_store: VectorStore

    def _run(
        self,
        task: str,
        function_def: str,
        function_call: str,
        output: Any,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        self.store_skill(task, function_def, function_call, output, run_manager)
        return "Skill created."

    async def _arun(
        self,
        task: str,
        function_def: str,
        function_call: str,
        output: Any,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        raise NotImplementedError("CreateSkillTool does not support async")

    def store_skill(
        self,
        task: str,
        function_def: str,
        function_call: str,
        result: Any,
        run_manager: Optional[CallbackManagerForChainRun] = None
    ):
        function_and_call = function_def + "\n\n" + function_call
        comment = self.generate_comment(task, function_and_call, result, run_manager)
        function = extract_functions(function_def)[0]
        imports = '\n'.join(extract_imports(function_def))
        function_with_imports = imports + '\n' + function

        self.skill_store.add_texts(
            texts=[f'# {task}\n\n{comment}\n{function_with_imports}'],
            metadatas=[{
                'task': task,
                'comment': comment,
                'function': function_with_imports,
                'example_call': function_call,
            }]
        )

    def generate_comment(self, task: str, function: str, result: Any, run_manager: Optional[CallbackManagerForChainRun] = None) -> str:
        comment_chain = create_code_comment_chain(llm=self.llm)
        return comment_chain.run(
            task=task,
            function=function,
            result=str(result),
            callbacks=run_manager.get_child() if run_manager else None
        )
