from typing import Any, Dict, Optional, Type
from typing import Sequence, Callable

from langchain.callbacks.manager import CallbackManagerForToolRun, AsyncCallbackManagerForToolRun
from langchain.tools.base import BaseTool
from pydantic import Field, BaseModel

from gpt.agents.common.agent.code_execution.util import python_exec, globals_from_function_defs


class PythonREPLSchema(BaseModel):
    code: str = Field(description="valid python code")


class PythonREPLTool(BaseTool):
    """A tool for running python code in a REPL."""

    name = "python"
    description = (
        "A Python REPL. Use this to execute python code. "
        "Input should be valid python code. "
        "Output is the evaluated last expression of the code."
    )
    args_schema: Type[PythonREPLSchema] = PythonREPLSchema
    globals: Optional[Dict] = Field(default_factory=dict)
    sanitize_input: bool = True

    @classmethod
    def from_functions(
        cls,
        functions: Optional[Sequence[Callable]] = None,
        functions_str: Optional[Sequence[str]] = None,
    ) -> "PythonREPLTool":
        return cls(globals=globals_from_function_defs(functions, functions_str))

    def _run(
        self,
        code: str,
        truncate: bool = True,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> Any:
        """Use the tool."""
        return python_exec(
            code,
            _globals=self.globals,
            sanitize=self.sanitize_input,
            truncate=truncate
        )

    async def _arun(
        self,
        query: str,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> Any:
        """Use the tool asynchronously."""
        raise NotImplementedError("PythonReplTool does not support async")
