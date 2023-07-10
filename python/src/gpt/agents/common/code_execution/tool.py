import ast
from contextlib import redirect_stdout
from io import StringIO
from typing import Any, Dict, Optional, List
from typing import Sequence, Callable

from langchain.callbacks.manager import CallbackManagerForToolRun, AsyncCallbackManagerForToolRun
from langchain.tools.base import BaseTool
from langchain.tools.python.tool import sanitize_input, _get_default_python_repl
from langchain.utilities import PythonREPL
from pydantic import Field


def abbreviate(val) -> str:
    if isinstance(val, list):
        return str(val[:3])[:-1] + ', ...]'
    else:
        return val


class PythonREPLTool(BaseTool):
    """A tool for running python code in a REPL."""

    name = "python"
    description = (
        "A Python REPL. Use this to execute python code. "
        "Input should be valid python code. "
        "Output is the evaluated last expression of the code."
    )
    globals: Optional[Dict] = Field(default_factory=dict)
    sanitize_input: bool = True

    @classmethod
    def from_functions(cls, functions: Sequence[Callable] = [], functions_str: Sequence[str] = []):
        _globals = globals()
        _globals.update({f.__name__: f for f in functions})
        for f in functions_str:
            exec(f, _globals)
        return cls(globals=_globals)

    def _run(
        self,
        query: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool."""
        try:
            if self.sanitize_input:
                query = sanitize_input(query)
            tree = ast.parse(query)
            module = ast.Module(tree.body[:-1], type_ignores=[])
            exec(ast.unparse(module), self.globals)  # type: ignore
            module_end = ast.Module(tree.body[-1:], type_ignores=[])
            module_end_str = ast.unparse(module_end)  # type: ignore
            io_buffer = StringIO()
            try:
                with redirect_stdout(io_buffer):
                    ret = eval(module_end_str, self.globals)
                    if ret is None:
                        return io_buffer.getvalue()
                    else:
                        return abbreviate(ret)
            except Exception:
                with redirect_stdout(io_buffer):
                    exec(module_end_str, self.globals)
                return io_buffer.getvalue()
        except Exception as e:
            return "{}: {}".format(type(e).__name__, str(e))

    async def _arun(
        self,
        query: str,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> Any:
        """Use the tool asynchronously."""
        raise NotImplementedError("PythonReplTool does not support async")
