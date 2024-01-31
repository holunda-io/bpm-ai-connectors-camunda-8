from bpm_ai.generic.generic import run_generic
from bpm_ai_core.llm.common.llm import LLM
from bpm_ai_core.speech.stt.stt import STTModel
from pyzeebe import ZeebeTaskRouter

from bpm_ai_connectors_c8.decorators import ai_task

generic_router = ZeebeTaskRouter()


@ai_task(generic_router, "generic", 2)
async def generic(
    llm: LLM,
    stt: STTModel | None,
    inputJson: dict,
    taskDescription: str,
    outputFormat: dict
):
    return run_generic(
        llm=llm,
        stt=stt,
        input_data=inputJson,
        instructions=taskDescription,
        output_schema=outputFormat
    )
