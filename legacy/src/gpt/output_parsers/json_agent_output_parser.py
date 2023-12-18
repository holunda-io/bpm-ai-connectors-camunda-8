import json
from typing import Union

from langchain.agents import AgentOutputParser
from langchain.schema import AgentAction, AgentFinish, OutputParserException


def find_json_blob(input_string):
    # Finding the first and last occurrence of { and } respectively
    start = input_string.find('{')
    end = input_string.rfind('}') + 1  # Adding 1 because slicing is end-exclusive

    if start == -1 or end == 0:  # No JSON object found
        return None

    # Extracting the potential JSON blob
    json_blob_string = input_string[start:end]

    try:
        json_blob = json.loads(json_blob_string)
        return json_blob
    except json.JSONDecodeError:
        return None


class JsonAgentOutputParser(AgentOutputParser):
    output_key: str = "output"

    finish_action: str = "Final Answer"

    action_key: str = "action"
    action_input_key: str = "input"

    def get_format_instructions(self) -> str:
        return ""

    def parse(self, text: str) -> Union[AgentAction, AgentFinish]:
        try:
            response = find_json_blob(text)
            if response is not None:
                if response[self.action_key] == self.finish_action:
                    return AgentFinish({self.output_key: response[self.action_input_key]}, text)
                else:
                    return AgentAction(response[self.action_key], response.get(self.action_input_key, {}), text)
            else:
                return AgentFinish({self.output_key: text}, text)
        except Exception as e:
            raise OutputParserException(f"Could not parse LLM output: {text}") from e

    @property
    def _type(self) -> str:
        return "structured_chat"
