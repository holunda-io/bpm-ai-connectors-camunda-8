from bpm_ai.translate.translate import run_translate
from bpm_ai_connectors_c8.decorators import ai_task
from bpm_ai_core.llm.common.llm import LLM
from bpm_ai_core.speech.stt.stt import STTModel
from pyzeebe import ZeebeTaskRouter

translate_router = ZeebeTaskRouter()


@ai_task(translate_router, "translate", 2)
async def translate(
    llm: LLM,
    stt: STTModel | None,
    inputJson: dict,
    language: str
):
    return run_translate(
        llm=llm,
        stt=stt,
        input_data=inputJson,
        target_language=language
    )
