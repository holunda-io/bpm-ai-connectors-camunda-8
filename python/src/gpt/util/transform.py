from langchain.chains import TransformChain

from gpt.util.json import json_to_md


def transform_to_md_chain(input_key: str, output_key: str) -> TransformChain:
    def transform_to_md(inputs):
        return {output_key: json_to_md(inputs[input_key])}

    return TransformChain(
        input_variables=[input_key],
        output_variables=[output_key],
        transform=transform_to_md
    )
