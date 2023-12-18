from abc import abstractmethod
from typing import Union

from langchain.load.serializable import Serializable
from langchain.schema import BaseMessage, AgentAction, AgentFinish


class AgentOutputParser(Serializable):

    output_key: str = "output"

    @abstractmethod
    def parse(self, llm_response: BaseMessage) -> Union[AgentAction, AgentFinish]:
        """
        Parse LLM response into agent action/finish.
        """


