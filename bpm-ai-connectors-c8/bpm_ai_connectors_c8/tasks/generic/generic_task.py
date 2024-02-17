from bpm_ai.generic.generic import generic_llm
from bpm_ai_core.llm.common.llm import LLM
from bpm_ai_core.speech_recognition.asr import ASRModel
from pyzeebe import ZeebeTaskRouter

from bpm_ai_connectors_c8.decorators import ai_task

generic_router = ZeebeTaskRouter()


@ai_task(generic_router, "generic", 2)
async def generic(
    llm: LLM,
    asr: ASRModel | None,
    input_json: dict,
    task_description: str,
    output_schema: dict
):
    return await generic_llm(
        llm=llm,
        asr=asr,
        input_data=input_json,
        instructions=task_description,
        output_schema=output_schema
    )
