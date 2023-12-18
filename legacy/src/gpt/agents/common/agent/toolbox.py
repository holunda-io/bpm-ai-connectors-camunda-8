from __future__ import annotations

import logging
from abc import abstractmethod
from typing import List, Optional, Dict, Any

from langchain.agents.agent import ExceptionTool
from langchain.agents.agent_toolkits.base import BaseToolkit
from langchain.agents.tools import InvalidTool
from langchain.callbacks.manager import CallbackManagerForToolRun
from langchain.schema import AgentAction
from langchain.tools import BaseTool

logger = logging.getLogger(__name__)


class Toolbox:
    """
    The ToolBox contains and manages the tools for an Agent.
    """

    def __init__(
        self,
        tools: Optional[List[BaseTool]] = None,
        verbose: bool = True
    ):
        """
        :param tools: A list of tools to add to the ToolBox. Each tool must have a unique name.
        """
        self._tools: Dict[str, BaseTool] = {tool.name: tool for tool in tools} if tools else {}
        self._virtual_tools: Dict[str, BaseTool] = self._default_virtual_tools()
        self.verbose = verbose

    @classmethod
    def from_toolkit(cls, toolkit: BaseToolkit) -> Toolbox:
        return cls(tools=toolkit.get_tools())

    @staticmethod
    def _default_virtual_tools():
        return {"_Exception": ExceptionTool(), "invalid_tool": InvalidTool()}

    def add_tool(self, tool: BaseTool, replace=False):
        if tool.name in self._tools and not replace:
            raise Exception(f"Tool with name {tool.name} already exists.")
        self._tools[tool.name] = tool

    def has_tool(self, tool_name: str):
        return tool_name in self._tools

    def get_tool(self, tool_name: str) -> Optional[BaseTool]:
        if tool_name in self._tools:
            return self.tools[tool_name]
        elif tool_name in self._virtual_tools:
            return self._virtual_tools[tool_name]
        else:
            return None

    @property
    def tools(self):
        return self._tools

    def get_tool_names(self) -> str:
        """
        Returns a string with the names of all registered tools.
        """
        return ", ".join(self.tools.keys())

    def get_tools(self) -> List[BaseTool]:
        """
        Returns a list of all registered tool instances.
        """
        return list(self.tools.values())

    def get_tool_names_with_descriptions(self) -> str:
        """
        Returns a string with the names and descriptions of all registered tools.
        """
        return "\n".join([f"{tool.name}: {tool.description}" for tool in self.tools.values()])

    def run_tool(self, agent_action: AgentAction, run_manager: Optional[CallbackManagerForToolRun] = None) -> Any:
        tool: BaseTool = self.get_tool(agent_action.tool)
        if not tool:
            raise Exception(f"Tool {agent_action.tool} not found in ToolBox.")
        return tool.run(agent_action.tool_input, verbose=self.verbose, callbacks=run_manager)


class AutoFinishTool(BaseTool):
    @abstractmethod
    def is_finish(self, observation: Any) -> bool:
        """Whether the tool run should make the agent finish."""
