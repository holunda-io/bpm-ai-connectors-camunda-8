import asyncio
import inspect
import json
from typing import TypedDict, Optional, Literal, Any, Union, List

from PIL import Image
from pydantic import BaseModel, Field

from bpm_ai_core.llm.common.tool import Tool


class ChatMessage(BaseModel):
    content: Optional[Union[str, dict, List[Union[str, Image]]]] = None
    """
    The contents of the message. 
    Either a string for normal completions, 
    or a list of strings and images for multimodal completions, 
    or a dict for prediction with output schema.
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

    class Config:
        arbitrary_types_allowed = True


class SingleToolCallMessage(BaseModel):

    id: str

    type: str = Field("function")

    name: str
    """
    The name of the tool that was used.
    """

    payload: Any

    tool: Optional[Tool] = None

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
        return self.tool.callable(**self.payload_dict())

    async def ainvoke(self) -> Any:
        _callable = self.tool.callable
        inputs = self.payload_dict()
        from bpm_ai_core.tracing.tracing import LangsmithTracer
        tracer = LangsmithTracer()  # todo
        tracer.start_function_trace(self.tool, inputs)
        if inspect.iscoroutinefunction(_callable):
            result = await _callable(**inputs)
        else:
            result = _callable(**inputs)
        tracer.end_function_trace(result)
        return result


class ToolCallsMessage(ChatMessage):
    role: str = Field("assistant")

    tool_calls: List[SingleToolCallMessage]

    def invoke_all(self) -> List[Any]:
        return [t.invoke() for t in self.tool_calls]

    async def ainvoke_all(self) -> List[Any]:
        return [await t.ainvoke() for t in self.tool_calls]

    async def ainvoke_all_parallel(self) -> List[Any]:
        return await asyncio.gather(*[t.ainvoke() for t in self.tool_calls])


class ToolResultMessage(ChatMessage):

    role: str = Field("tool")

    id: str
    """
    The id of the tool.
    """

