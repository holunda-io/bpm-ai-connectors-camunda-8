from typing import Dict, Union

from bpm_ai_core.llm.common.llm import LLM
from bpm_ai_core.llm.common.message import ToolCallsMessage
from bpm_ai_core.llm.common.tool import Tool
from bpm_ai_core.prompt.prompt import Prompt
from bpm_ai_core.util.audio import is_supported_audio_file
from bpm_ai_core.util.image import is_supported_img_file
from bpm_ai_core.voice.common.voice import Voice
from bpm_ai_core.voice.openai_voice import OpenAIVoice
from langsmith import traceable

from bpm_ai.common.json_utils import json_to_md


def prepare_images(input_data: dict):
    return {k: f"[# image {v} #]" if is_supported_img_file(v) else v for k, v in input_data.items()}


def prepare_audio(input_data: dict, voice: Voice):
    return {k: voice.transcribe(v) if is_supported_audio_file(v) else v for k, v in input_data.items()}


@traceable(name="Extract")
def run_extract(
    llm: LLM,
    input_data: Dict[str, Union[str, dict]],
    output_schema: Dict[str, Union[str, dict]],
    repeated: bool = False,
    repeated_description: str = ""
) -> dict:
    def transform_result(**extracted):
        def empty_to_none(d) -> dict:
            return {k: (None if v in ["", "null"] else v) for k, v in d.items()}

        if repeated:
            extracted = extracted["entities"]
        print(extracted)
        if isinstance(extracted, list):
            return [empty_to_none(d) for d in extracted]
        else:
            return empty_to_none(extracted)

    tool = Tool.from_callable(
        "information_extraction",
        f"Extracts the relevant {'entities' if repeated else 'information'} from the passage.",
        args_schema={
            "entities": {"type": "array", "description": repeated_description, "items": output_schema}
        } if repeated else output_schema,
        callable=transform_result
    )

    #input_data = prepare_images(input_data)
    input_data = prepare_audio(input_data, OpenAIVoice())

    input_md = json_to_md(input_data)

    prompt = Prompt.from_file("extract", input=input_md)

    result = llm.predict(prompt, tools=[tool])

    if isinstance(result, ToolCallsMessage):
        return result.tool_calls[0].invoke()
    else:
        return {}



