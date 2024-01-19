from typing import TypedDict

from bpm_ai.compose.compose import run_compose
from bpm_ai_connectors_c8.decorators import ai_task
from bpm_ai_core.llm.common.llm import LLM
from bpm_ai_core.speech.stt.stt import STTModel
from pyzeebe import ZeebeTaskRouter

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
    stt: STTModel | None,
    inputJson: dict,
    properties: TextProperties,
    template: str,
):
    return run_compose(
        llm=llm,
        stt=stt,
        input_data=inputJson,
        template=template,
        properties=properties,
    )
