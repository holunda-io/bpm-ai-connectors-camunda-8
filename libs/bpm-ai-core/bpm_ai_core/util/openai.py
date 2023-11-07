from typing import List, Dict, Union, Any

from openai.types.chat import ChatCompletionMessageParam

from bpm_ai_core.llm.common.message import ChatMessage, FunctionCallMessage, FunctionResultMessage


def get_openai_function_call_dict(message: FunctionCallMessage):
    return {"function_call": {"name": message.name, "arguments": message.payload}}


def message_to_openai_dict(message: ChatMessage) -> ChatCompletionMessageParam:
    if isinstance(message, FunctionCallMessage):
        return {
            "role": message.role,
            "content": message.content,
            **get_openai_function_call_dict(message)
        }
    elif isinstance(message, FunctionResultMessage):
        return {
            "role": message.role,
            "content": message.content,
            "name": message.name
        }
    elif isinstance(message, ChatMessage):
        return {
            "role": message.role,
            "content": message.content,
            **({"name": message.name} if message.name else {})
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
            elif not 'type' in x or x['type'] == 'object':
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
        "name": name,
        "description": desc,
        "parameters": schema_from_properties(schema),
    }