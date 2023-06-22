import json

from gpt.util.json import json_to_md
from gpt.config import supports_openai_functions
from langchain.chains import TransformChain

def transform_to_md_chain(input_key: str, output_key: str) -> TransformChain:
    def transform_to_md(inputs):
        return {output_key: json_to_md(json.loads(inputs[input_key]))}

    return TransformChain(
        input_variables=[input_key],
        output_variables=[output_key],
        transform=transform_to_md
    )


def transform_empty_chain(input_key: str, output_key: str) -> TransformChain:
    def empty_to_null(d) -> dict:
        return {k: (None if v == "" or v == "null" else v) for k, v in d.items()}

    def transform_empty_values(inputs):
        x = inputs[input_key]
        if isinstance(x, list):
            res = [empty_to_null(d) for d in x]
        else:
            res = empty_to_null(x)
        return {output_key: res}

    return TransformChain(
        input_variables=[input_key],
        output_variables=[output_key],
        transform=transform_empty_values
    )
