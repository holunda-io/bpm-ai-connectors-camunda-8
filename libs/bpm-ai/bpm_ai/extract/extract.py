from bpm_ai_core.llm.common.llm import LLM
from bpm_ai_core.llm.common.message import ToolCallsMessage
from bpm_ai_core.llm.common.tool import Tool
from bpm_ai_core.prompt.prompt import Prompt
from langsmith import traceable

from bpm_ai.common.json_utils import json_to_md
from bpm_ai.common.multimodal import prepare_audio


@traceable(name="Extract")
def run_extract(
    llm: LLM,
    input_data: dict[str, str | dict],
    output_schema: dict[str, str | dict],
    repeated: bool = False,
    repeated_description: str = ""
) -> dict:
    def transform_result(**extracted):
        def empty_to_none(v):
            return None if v in ["", "null"] else v

        if repeated and "entities" in extracted.keys():
            extracted = extracted["entities"]

        if isinstance(extracted, list):
            return [transform_result(**d) for d in extracted]
        else:
            return {k: empty_to_none(v) for k, v in extracted.items()}

    tool = Tool.from_callable(
        "information_extraction",
        f"Extracts the relevant {'entities' if repeated else 'information'} from the passage.",
        args_schema={
            "entities": {"type": "array", "description": repeated_description, "items": output_schema}
        } if repeated else output_schema,
        callable=transform_result
    )

    #input_data = prepare_images(input_data)  todo enable once GPT-4V is stable
    input_data = prepare_audio(input_data)

    input_md = json_to_md(input_data)

    prompt = Prompt.from_file("extract", input=input_md)

    result = llm.predict(prompt, tools=[tool])

    if isinstance(result, ToolCallsMessage):
        return result.tool_calls[0].invoke()
    else:
        return {}



