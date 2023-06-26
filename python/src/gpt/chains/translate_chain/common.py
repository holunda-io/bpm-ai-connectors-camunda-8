import json
from typing import Optional, List, Dict

from langchain.chains import TransformChain


def get_output_schema(input_keys: List[str], target_language: str):
    return {k: f'{k} translated into {target_language}' for k in input_keys}


def transform_to_pretty_json_chain(input_key: str, output_key: str) -> TransformChain:
    def transform_pretty(inputs):
        _input = inputs[input_key]
        _input = json.loads(_input) if isinstance(_input, str) else _input
        return {output_key: json.dumps(_input, indent=2)}

    return TransformChain(
        input_variables=[input_key],
        output_variables=[output_key],
        transform=transform_pretty
    )
