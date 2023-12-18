import json
from typing import Any, List

from langchain.schema import BaseLLMOutputParser, Generation, ChatGeneration


class FunctionsOutputParser(BaseLLMOutputParser[Any]):
    def parse_result(self, result: List[Generation]) -> Any:
        generation = result[0]
        if not isinstance(generation, ChatGeneration):
            raise ValueError(
                "This output parser can only be used with a chat generation."
            )
        message = generation.message
        try:
            func_call = message.additional_kwargs["function_call"]
        except ValueError as exc:
            raise ValueError(f"Could not parse function call: {exc}")

        return {"name": func_call["name"], "arguments": json.loads(func_call["arguments"])}
