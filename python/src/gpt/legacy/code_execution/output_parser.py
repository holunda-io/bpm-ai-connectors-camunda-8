import re
from typing import Any, Callable, Sequence
from typing import Union

from langchain.agents import AgentOutputParser
from langchain.schema import AgentAction, AgentFinish
from langchain.schema import OutputParserException, BaseOutputParser

from gpt.legacy.code_execution.tool import PythonREPLTool


def parse_python_markdown(s: str) -> str:
    # Try to find code within triple backticks
    match = re.search(r"```(python)?(.*?)```", s, re.DOTALL)

    # If no match found, assume the entire string is a code string
    if match is None:
        code_str = s
    else:
        # If match found, use the content within the backticks
        code_str = match.group(2)

    # Strip whitespace and newlines from the start and end
    code_str = code_str.strip()

    return code_str


class PythonCodeOutputParser(BaseOutputParser):

    @property
    def _type(self) -> str:
        return "python_code"

    def parse(self, text: str) -> Any:
        return parse_python_markdown(text)

    def get_format_instructions(self) -> str:
        """Instructions on how the LLM output should be formatted."""
        return "Return result as valid python code in a markdown code block."


class PythonCodeAgentOutputParser(AgentOutputParser):
    functions: Sequence[Callable]

    def get_format_instructions(self) -> str:
        return ""

    def parse(self, text: str) -> Union[AgentAction, AgentFinish]:
        try:
            response = parse_python_markdown(text)
            if "def " in response:
                output = PythonREPLTool.from_functions(self.functions).run(response)
                return AgentFinish({"output": output, "code": response}, text)
            else:
                return AgentAction("python", response, text)
        except Exception as e:
            raise OutputParserException(f"Could not parse LLM output: {text}") from e

    @property
    def _type(self) -> str:
        return "code"
