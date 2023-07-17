from typing import Type, Optional, Callable, Sequence, Dict

from langchain.callbacks.manager import CallbackManagerForToolRun, AsyncCallbackManagerForToolRun
from langchain.tools import BaseTool
from pydantic import BaseModel, Field

from gpt.agents.common.agent.code_execution.python_tool import PythonREPLTool
from gpt.agents.common.agent.code_execution.util import globals_from_function_defs, python_exec, get_function_name


class StoreFinalResultWithCallSchema(BaseModel):
    function_def: str = Field(description="generic python function definition")
    function_call: str = Field(description="concrete call")


class StoreFinalResultWithCallTool(BaseTool):

    name = "store_final_result"
    description = "Stores the final python function definition and call."
    args_schema: Type[StoreFinalResultWithCallSchema] = StoreFinalResultWithCallSchema
    return_direct = True

    def _run(
        self,
        function_def: str,
        function_call: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> dict:
        """Use the tool."""
        return {
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


class StoreFinalResultDefTool(BaseTool):

    name = "store_final_result"
    description = "Stores the final implementation of the python function stub."
    args_schema: Type[StoreFinalResultDefSchema] = StoreFinalResultDefSchema
    return_direct = True

    def _run(
        self,
        function_def: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> dict:
        """Use the tool."""
        return {
            "function_def": function_def,
            "function_name": get_function_name(function_def)
        }

    async def _arun(
        self,
        function_def: str,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool asynchronously."""
        raise Exception("async not supported")
