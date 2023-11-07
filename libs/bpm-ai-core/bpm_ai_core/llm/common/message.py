import inspect
import json
from typing import TypedDict, Optional, Literal, Any, Union

from pydantic import BaseModel, Field

from bpm_ai_core.llm.common.function import Function


class ChatMessage(BaseModel):
    content: Optional[Union[str, dict]] = None
    """
    The contents of the message. 
    Either a string for normal completions or a dict for prediction with output schema.
    """

    role: Literal["system", "user", "assistant", "function"]
    """
    The role of the messages author.
    One of `system`, `user`, `assistant`, or `function`.
    """

    name: Optional[str] = None
    """
    The name of the author of this message.
    """


class FunctionCallMessage(ChatMessage):

    role: str = Field("assistant")

    name: str
    """
    The name of the function that was used.
    """

    payload: Any

    function: Optional[Function] = None

    def payload_dict(self) -> dict:
        if isinstance(self.payload, dict):
            return self.payload
        elif isinstance(self.payload, str):
            try:
                return json.loads(self.payload)
            except ValueError as e:
                raise Exception(f"Payload could not be converted to a dict: {e}")
        else:
            raise Exception("Payload has unexpected type.")

    def invoke(self):
        return self.function.callable(**self.payload_dict())

    async def ainvoke(self):
        _callable = self.function.callable
        inputs = self.payload_dict()
        from bpm_ai_core.tracing.tracing import LangsmithTracer
        tracer = LangsmithTracer()  # todo
        tracer.start_function_trace(self.function, inputs)
        if inspect.iscoroutinefunction(_callable):
            result = await _callable(**inputs)
        else:
            result = _callable(**inputs)
        tracer.end_function_trace(result)
        return result


class FunctionResultMessage(ChatMessage):

    role: str = Field("function")

    name: str
    """
    The name of the function.
    """

