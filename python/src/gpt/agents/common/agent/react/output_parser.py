import re
from typing import Union

from langchain.schema import BaseMessage, AgentAction, AgentFinish

from gpt.agents.common.agent.output_parser import AgentOutputParser
from gpt.agents.common.agent.react.prompt import FINAL_ANSWER_PREFIX


class ReActOutputParser(AgentOutputParser):

    tool_pattern = r"Action\s*\d*\s*:[\s]*(.*?)[\s]*Action\s*\d*\s*Input\s*\d*\s*:[\s]*(.*)"
    action_pattern = r"Action\s*\d*\s*:[\s]*(.*?)"
    action_input_pattern = r"[\s]*Action\s*\d*\s*Input\s*\d*\s*:[\s]*(.*)"

    def parse(self, llm_response: BaseMessage) -> Union[AgentAction, AgentFinish]:
        response_text = llm_response.content

        includes_answer = FINAL_ANSWER_PREFIX in response_text
        action_match = re.search(self.tool_pattern, response_text, re.DOTALL)

        if action_match:
            if includes_answer:
                raise Exception(f"Parsing LLM output produced both a final answer and a parse-able action: {response_text}")
            action = action_match.group(1).strip()
            action_input = action_match.group(2)
            tool_input = action_input.strip(" ")
            return AgentAction(action, tool_input, log=response_text)

        elif includes_answer:
            return AgentFinish({self.output_key: response_text.split(FINAL_ANSWER_PREFIX)[-1].strip()}, log=response_text)

        if not re.search(self.action_pattern, response_text, re.DOTALL):
            raise Exception(f"Could not parse LLM output: `{response_text}`. Invalid Format: Missing 'Action:' after 'Thought:'")

        elif not re.search(self.action_input_pattern, response_text, re.DOTALL):
            raise Exception(f"Could not parse LLM output: `{response_text}`. Missing 'Action Input:' after 'Action:'")

        else:
            raise Exception(f"Could not parse LLM output: `{response_text}`")


