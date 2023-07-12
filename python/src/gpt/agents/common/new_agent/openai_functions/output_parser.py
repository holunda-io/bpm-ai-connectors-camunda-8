import json
from json import JSONDecodeError
from typing import Tuple, Optional, Union

from langchain.load.serializable import Serializable
from langchain.schema import AIMessage, BaseMessage
from langchain.tools import Tool, BaseTool

from gpt.agents.common.new_agent.output_parser import AgentOutputParser, AgentAction, AgentFinish
from gpt.agents.common.new_agent.toolbox import Toolbox


def function_call_log(function_name: str, tool_input: str, response_text: str):
    response_text = response_text + '\n' if response_text else ""
    return f"\n{response_text}Invoking: `{function_name}` with `{tool_input}`\n"


class OpenAIFunctionsOutputParser(AgentOutputParser):

    final_tool: Optional[BaseTool] = None

    def parse(self, llm_response: BaseMessage) -> Union[AgentAction, AgentFinish]:

        response_text = llm_response.content
        function_call = llm_response.additional_kwargs.get("function_call", {})

        if function_call:
            function_name = function_call["name"]
            try:
                tool_input = json.loads(function_call["arguments"], strict=False)
            except JSONDecodeError:
                raise Exception(
                    f"Could not parse tool input: {function_call} because `arguments` is not valid JSON."
                )

            if self.final_tool is not None and self.final_tool.name == function_name:
                # final tool was called with final answer
                return AgentFinish({"output": tool_input}, log=response_text)
            else:
                # normal tool call
                return AgentAction(function_name, tool_input, log=function_call_log(function_name, tool_input, response_text))

        elif self.final_tool is not None:
            # Agent responded with text and no function call, but we need the final tool to be called to finish.
            # So we continue and potentially let a special `no_function_call` tool handle this.
            return AgentAction("no_function_call", response_text, log=response_text)

        else:
            # Agent responded with text and no function call, treat as final answer
            return AgentFinish({"output": response_text}, log=response_text)
