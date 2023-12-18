
def get_translation_output_schema(input_data: dict, target_language: str):
    return {k: f'{k} translated into {target_language}' for k in input_data.keys()}
