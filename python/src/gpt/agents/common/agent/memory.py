from typing import List

from langchain.schema import BaseMessage


class AgentMemory:
    """
    A memory class that stores conversation history.
    """

    transcript: List[BaseMessage] = []

    def add_transcript(self, additional_transcript: List[BaseMessage]):
        self.transcript += additional_transcript

    def get_transcript(self) -> List[BaseMessage]:
        return self.transcript
