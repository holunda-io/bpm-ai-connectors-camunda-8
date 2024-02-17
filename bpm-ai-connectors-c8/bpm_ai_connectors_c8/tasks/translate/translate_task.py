from bpm_ai.translate.translate import translate_llm, translate_nmt
from bpm_ai_core.llm.common.llm import LLM
from bpm_ai_core.speech_recognition.asr import ASRModel
from bpm_ai_core.translation.nmt import NMTModel
from pyzeebe import ZeebeTaskRouter

from bpm_ai_connectors_c8.decorators import ai_task

translate_router = ZeebeTaskRouter()


@ai_task(translate_router, "translate", 2)
async def translate(
    llm: LLM | None,
    asr: ASRModel | None,
    input_json: dict,
    language: str,
    nmt: NMTModel | None = None
):
    if llm:
        return await translate_llm(
            llm=llm,
            asr=asr,
            input_data=input_json,
            target_language=language
        )
    else:
        return await translate_nmt(
            nmt=nmt,
            asr=asr,
            input_data=input_json,
            target_language=language
        )
