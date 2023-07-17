from typing import Type, Optional

from langchain.callbacks.manager import CallbackManagerForToolRun, AsyncCallbackManagerForToolRun
from langchain.tools import BaseTool
from pydantic import BaseModel, Field


class NoFunctionCallToolSchema(BaseModel):
    input: str = Field()


class NoFunctionCallTool(BaseTool):

    name = "no_function_call"
    description = "Dummy tool to respond something to the agent when it did not call a real tool."
    args_schema: Type[NoFunctionCallToolSchema] = NoFunctionCallToolSchema

    response = "No function called. Tip: If you think you have the final result, use `store_final_result`."

    def _run(
        self,
        input: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool."""
        return self.response

    async def _arun(
        self,
        input: str,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool asynchronously."""
        raise self.response
