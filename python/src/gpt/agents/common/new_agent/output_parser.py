from abc import abstractmethod
from dataclasses import dataclass
from typing import Union, Any

from langchain.load.serializable import Serializable
from langchain.schema import BaseMessage, AgentAction, AgentFinish


class AgentOutputParser(Serializable):
    @abstractmethod
    def parse(self, llm_response: BaseMessage) -> Union[AgentAction, AgentFinish]:
        """
        Parse LLM response into agent action/finish.
        """


