from bpm_ai_core.llm.common.llm import LLM
from bpm_ai_core.llm.common.message import ToolCallsMessage
from bpm_ai_core.llm.common.tool import Tool
from bpm_ai_core.prompt.prompt import Prompt
from langsmith import traceable

from bpm_ai.common.json_utils import json_to_md
from bpm_ai.common.multimodal import prepare_audio


@traceable(name="Generic")
def run_generic(
    llm: LLM,
    input_data: dict[str, str | dict],
    instructions: str,
    output_schema: dict[str, str | dict]
) -> dict:
    tool = Tool.from_callable(
        "store_task_result",
        "Stores the result of the task.",
        args_schema=output_schema,
        callable=lambda **x: x
    )

    #input_data = prepare_images(input_data)  todo enable once GPT-4V is stable
    input_data = prepare_audio(input_data)

    input_md = json_to_md(input_data)

    prompt = Prompt.from_file(
        "generic",
        context=input_md,
        task=instructions,
    )

    result = llm.predict(prompt, tools=[tool])

    if isinstance(result, ToolCallsMessage):
        return result.tool_calls[0].invoke()
    else:
        return {}



