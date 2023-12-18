from typing import Any

from bpm_ai_core.llm.common.llm import LLM
from bpm_ai_core.llm.common.message import ToolCallsMessage
from bpm_ai_core.llm.common.tool import Tool
from bpm_ai_core.prompt.prompt import Prompt
from langsmith import traceable

from bpm_ai.common.json_utils import json_to_md
from bpm_ai.common.multimodal import prepare_audio
from bpm_ai.decide.schema import get_cot_decision_output_schema, get_decision_output_schema


@traceable(name="Decide")
def run_decide(
    llm: LLM,
    input_data: dict[str, str | dict],
    instructions: str,
    output_type: str,
    possible_values: list[Any] | None = None,
    strategy: str | None = None
) -> dict:
    if strategy == 'cot':
        output_schema = get_cot_decision_output_schema(output_type, possible_values)
    else:
        output_schema = get_decision_output_schema(output_type, possible_values)

    tool = Tool.from_callable(
        "store_decision",
        "Stores the final decision value and corresponding reasoning.",
        args_schema=output_schema,
        callable=lambda **x: x
    )

    #input_data = prepare_images(input_data)  todo enable once GPT-4V is stable
    input_data = prepare_audio(input_data)

    input_md = json_to_md(input_data)

    prompt = Prompt.from_file(
        "decide",
        context=input_md,
        task=instructions,
        output_type=output_type,
        possible_values=possible_values,
        strategy=strategy
    )

    result = llm.predict(prompt, tools=[tool])

    if isinstance(result, ToolCallsMessage):
        return result.tool_calls[0].invoke()
    else:
        return {}



