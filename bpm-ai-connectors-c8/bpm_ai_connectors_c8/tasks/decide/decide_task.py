from typing import Any

from bpm_ai.decide.decide import run_decide
from bpm_ai_core.llm.common.llm import LLM
from bpm_ai_core.speech.stt.stt import STTModel
from pyzeebe import ZeebeTaskRouter

from bpm_ai_connectors_c8.decorators import ai_task

decide_router = ZeebeTaskRouter()


@ai_task(decide_router, "decide", 2)
async def decide(
    llm: LLM,
    stt: STTModel | None,
    inputJson: dict,
    instructions: str,
    outputType: str,
    possibleValues: list[Any] | None = None,
    strategy: str | None = None
):
    return run_decide(
        llm=llm,
        stt=stt,
        input_data=inputJson,
        instructions=instructions,
        output_type=outputType,
        possible_values=possibleValues,
        strategy=strategy
    )
