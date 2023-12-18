import json
from json import JSONDecodeError
from typing import Union

from langchain.schema import BaseMessage

from gpt.agents.common.agent.output_parser import AgentOutputParser, AgentAction, AgentFinish


def function_call_log(function_name: str, tool_input: str, response_text: str):
    response_text = response_text + '\n' if response_text else ""
    return f"\n{response_text}Invoking: `{function_name}` with `{tool_input}`\n"


class OpenAIFunctionsOutputParser(AgentOutputParser):

    no_function_call_means_final_answer = False

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

            return AgentAction(function_name, tool_input, log=function_call_log(function_name, tool_input, response_text))

        elif self.no_function_call_means_final_answer:
            # Agent responded with text and no function call, treat as final answer
            return AgentFinish({self.output_key: response_text}, log=response_text)

        else:
            # Agent responded with text and no function call, but we need the final tool to be called to finish.
            # So we continue and potentially let a special `no_function_call` tool handle this.
            return AgentAction("no_function_call", response_text, log=response_text)

