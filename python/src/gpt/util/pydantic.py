import json
from typing import Type

from langchain.pydantic_v1 import BaseModel


def get_example_value(field: dict) -> any:
    """
    Get an example value for a given Pydantic field based on the field's type.
    """
    if field['type'] == 'integer':
        return 0
    elif field['type'] == 'number':
        return 0.0
    elif field['type'] == 'boolean':
        return False
    elif field['type'] == 'object':
        return {}
    elif field['type'] == 'array':
        return []
    else:
        return "string"


def model_to_example_json(model: Type[BaseModel]) -> str:
    """
    Convert a Pydantic model into an example JSON and description based on the field type and description.
    """
    schema = model.schema()['properties']
    example_json = json.dumps(
        {name: get_example_value(field) for name, field in schema.items()},
        indent=2
    )
    desc = [f"- {name}: {field['description']}" for name, field in schema.items() if 'description' in field]
    return example_json + "\n\n" + "\n".join(desc)
