from typing import List, Dict, Union, Any

from PIL.Image import Image
from openai.types.chat import ChatCompletionMessageParam

from bpm_ai_core.util.image import base64_encode_image
from bpm_ai_core.llm.common.message import ChatMessage, ToolCallsMessage, ToolResultMessage


def get_openai_tool_call_dict(message: ToolCallsMessage):
    return {
        "tool_calls": [
            {
                "type": "function",
                "id": t.id,
                "function": {
                    "name": t.name,
                    "arguments": t.payload
                }
            }
            for t in message.tool_calls
        ]
    }


def message_to_openai_dict(message: ChatMessage) -> ChatCompletionMessageParam:
    if isinstance(message, ToolCallsMessage):
        extra_dict = {
            **get_openai_tool_call_dict(message)
        }
    elif isinstance(message, ToolResultMessage):
        extra_dict = {
            "tool_call_id": message.id
        }
    else:
        extra_dict = {}

    if isinstance(message.content, str):
        content = message.content
    elif isinstance(message.content, list):
        content = []
        for e in message.content:
            if isinstance(e, str):
                content.append(str_to_openai_text_dict(e))
            elif isinstance(e, Image):
                content.append(image_to_openai_image_dict(e))
            else:
                raise ValueError(
                    "Elements in ChatMessage.content must be of type str or PIL.Image."
                )
    else:
        raise ValueError(
            "ChatMessage.content must be of type str or List[Union[str, PIL.Image]] if used for chat completions."
        )
    return {
        "role": message.role,
        "content": content,
        **extra_dict,
        **({"name": message.name} if message.name else {})
    }


def image_to_openai_image_dict(image: Image) -> dict:
    return {
        "type": "image_url",
        "image_url": {
            "url": f"data:image/{image.format.lower()};base64,{base64_encode_image(image)}"
        }
    }

def str_to_openai_text_dict(text: str) -> dict:
    return {
        "type": "text",
        "text": text
    }


def messages_to_openai_dicts(messages: List[ChatMessage]):
    return [message_to_openai_dict(m) for m in messages]


def json_schema_from_shorthand(schema: dict) -> dict:
    def type_or_default(x):
        # If x is a string, return the string type
        if isinstance(x, str):
            return {"type": "string", "description": x}

        # If x is a list, treat it as an array
        elif isinstance(x, list):
            # If the list has items, process the first item
            if x:
                return {"type": "array", "items": type_or_default(x[0])}
            else:
                return {"type": "array", "items": {}}

        # If x is a dictionary
        elif isinstance(x, dict):
            # Check for explicitly provided "type" and "properties"
            if 'type' in x and x['type'] == 'object' and 'properties' in x:
                properties = {k: type_or_default(v) for k, v in x['properties'].items()}
                return {"type": "object", "properties": properties, "required": list(properties.keys())}

            # If 'type' is not present or if 'type' is 'object', treat x as an object
            elif 'type' not in x or x['type'] == 'object':
                properties = {k: type_or_default(v) for k, v in x.items()}
                return {"type": "object", "properties": properties, "required": list(properties.keys())}
            else:
                return x
        else:
            return x

    return {k: type_or_default(v) for k, v in schema.items()}


def schema_from_properties(properties: Dict[str, Union[str, dict]]):
    return {
        "type": "object",
        "properties": json_schema_from_shorthand(properties),
        "required": list(properties.keys()),
    }


def json_schema_to_openai_function(name: str, desc: str, schema: Dict[str, Any]) -> dict:
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": desc,
            "parameters": schema_from_properties(schema),
        }
    }
