from __future__ import annotations

import logging
from typing import Optional, Dict, Any, Callable, Union, List

from langchain.load.serializable import Serializable
from langchain.schema import AIMessage, BaseMessage, HumanMessage

from gpt.agents.common.new_agent.output_parser import AgentOutputParser, AgentAction, AgentFinish

logger = logging.getLogger(__name__)


class AgentStep(Serializable):
    """
    The AgentStep class represents a single step in the execution of an agent.
    """

    output_parser: AgentOutputParser
    max_steps: int = 10
    current_step: int = 1
    llm_response: Optional[BaseMessage] = None
    parsed_action: Optional[Union[AgentAction, AgentFinish]] = None
    transcript: List[BaseMessage] = []

    @classmethod
    def empty(cls, output_parser: AgentOutputParser, max_steps: int = 10):
        return cls(output_parser=output_parser, max_steps=max_steps)

    def create_next_step(self, llm_response: BaseMessage, current_step: Optional[int] = None) -> AgentStep:
        """
        Creates the next agent step based on the current step and the PromptNode response.
        :param llm_response: The PromptNode response received.
        :param current_step: The current step in the execution of the agent.
        """
        cls = type(self)
        return cls(
            output_parser=self.output_parser,
            current_step=current_step if current_step else self.current_step + 1,
            llm_response=llm_response,
            transcript=self.transcript,
            parsed_action=self._try_parse(llm_response),
        )

    def _try_parse(self, llm_response: BaseMessage) -> Union[AgentAction, AgentFinish]:
        try:
            return self.output_parser.parse(llm_response)
        except Exception as error:
            e = str(error)
            return AgentAction("_Exception", e, e)

    def is_last(self) -> bool:
        """
        Check if this is the last step of the Agent.
        :return: True if this is the last step of the Agent, False otherwise.
        """
        return isinstance(self.parsed_action, AgentFinish) or self.current_step > self.max_steps

    @property
    def return_values(self) -> dict:
        if not self.is_last():
            raise Exception("Trying to access return values while current step is not the last.")
        return self.parsed_action.return_values

    def complete(self, observation_message: Optional[BaseMessage]) -> None:
        """
        Update the transcript with the observation
        :param observation_message: received observation from the Agent environment.
        """
        self.transcript += [self.llm_response]
        if observation_message:
            self.transcript += [observation_message]

    def __repr__(self) -> str:
        """
        Return a string representation of the AgentStep object.

        :return: A string that represents the AgentStep object.
        """
        return (
            f"AgentStep(current_step={self.current_step}, "
            f"llm_response={self.llm_response}, "
            f"parsed_action={self.parsed_action}, "
            f"transcript={self.transcript})"
        )
