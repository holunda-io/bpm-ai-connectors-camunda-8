from typing import List, Optional, Sequence, Tuple

from langchain.agents import ConversationalChatAgent
from langchain.prompts.base import BasePromptTemplate
from langchain.prompts.chat import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
)
from langchain.schema import (
    BaseOutputParser, AgentAction, BaseMessage, AIMessage, HumanMessage, SystemMessage,
)
from langchain.tools.base import BaseTool

from gpt.convo_agent.prompt import CONVO_AGENT_SYSTEM_MESSAGE, CONVO_AGENT_HUMAN_MESSAGE, CONVO_AGENT_TOOL_RESPONSE, \
    CONVO_AGENT_REMINDER
from gpt.output_parsers.json_agent_output_parser import JsonAgentOutputParser


class ConvoChatAgent(ConversationalChatAgent):
    output_parser = JsonAgentOutputParser()
    template_tool_response: str = CONVO_AGENT_TOOL_RESPONSE
    output_key: str = "output"

    @property
    def return_values(self) -> List[str]:
        return [self.output_key]

    @classmethod
    def _validate_tools(cls, tools: Sequence[BaseTool]) -> None:
        """Validate that appropriate tools are passed in."""
        pass

    def _construct_scratchpad(
        self, intermediate_steps: List[Tuple[AgentAction, str]]
    ) -> List[BaseMessage]:
        """Construct the scratchpad that lets the agent continue its thought process."""
        thoughts: List[BaseMessage] = []
        for action, observation in intermediate_steps:
            thoughts.append(AIMessage(
                content=action.log
            ))
            thoughts.append(HumanMessage(
                content=self.template_tool_response.format(observation=observation)
            ))
            thoughts.append(SystemMessage(
                content=CONVO_AGENT_REMINDER)
            )
        return thoughts

    @classmethod
    def create_prompt(
            cls,
            tools: Sequence[BaseTool],
            system_message: str = CONVO_AGENT_SYSTEM_MESSAGE,
            human_message: str = CONVO_AGENT_HUMAN_MESSAGE,
            input_variables: Optional[List[str]] = None,
            output_parser: Optional[BaseOutputParser] = None,
    ) -> BasePromptTemplate:
        tool_strings = "\n".join(
            [f"# {tool.name}:\n{tool.description}" for tool in tools]
        )
        tool_names = ", ".join([tool.name for tool in tools])
        system_prompt = system_message.format(
            tool_names=tool_names, tools=tool_strings
        )
        if input_variables is None:
            input_variables = ["input", "agent_scratchpad"]
        messages = [
            SystemMessagePromptTemplate.from_template(system_prompt),
            HumanMessagePromptTemplate.from_template(human_message),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
        return ChatPromptTemplate(input_variables=input_variables, messages=messages)
