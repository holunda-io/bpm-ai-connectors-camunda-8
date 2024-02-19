from typing import TypedDict

from bpm_ai.compose.compose import compose_llm
from bpm_ai_core.llm.common.llm import LLM
from bpm_ai_core.ocr.ocr import OCR
from bpm_ai_core.speech_recognition.asr import ASRModel
from pyzeebe import ZeebeTaskRouter

from bpm_ai_connectors_c8.decorators import ai_task

compose_router = ZeebeTaskRouter()


class TextProperties(TypedDict):
    style: str
    type: str
    tone: str
    length: str
    language: str
    temperature: str


@ai_task(compose_router, "compose", 2)
async def compose(
    llm: LLM,
    asr: ASRModel | None,
    ocr: OCR | None,
    input_json: dict,
    properties: TextProperties,
    template: str,
):
    return await compose_llm(
        llm=llm,
        asr=asr,
        ocr=ocr,
        input_data=input_json,
        template=template,
        properties=properties,
    )
