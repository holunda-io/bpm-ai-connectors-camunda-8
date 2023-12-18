from typing import Any, Optional

from langchain.callbacks.manager import CallbackManagerForToolRun, AsyncCallbackManagerForToolRun
from langchain.tools import tool

from gpt.agents.common.agent.toolbox import AutoFinishTool


@tool
def fake_tool(input: str) -> str:
    """"""
    return "Output"

class FakeStoreFinalResultTool(AutoFinishTool):

    name = "store_final_result"
    description = ""

    def is_finish(self, observation: Any) -> bool:
        return True

    def _run(
        self,
        input: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        return input

    async def _arun(
        self,
        input: str,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        raise Exception("async not supported")
