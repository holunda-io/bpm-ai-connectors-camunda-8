from typing import List

from langchain.schema import BaseMessage


def messages_to_str(messages: List[BaseMessage]) -> str:
    return "\n\n".join([m.content for m in messages])
