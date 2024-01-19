from bpm_ai.extract.extract import run_extract
from bpm_ai_connectors_c8.decorators import ai_task
from bpm_ai_core.llm.common.llm import LLM
from bpm_ai_core.speech.stt.stt import STTModel
from pyzeebe import ZeebeTaskRouter

extract_router = ZeebeTaskRouter()


@ai_task(extract_router, "extract", 2)
async def extract(
    llm: LLM,
    stt: STTModel | None,
    inputJson: dict,
    extractionJson: dict,
    mode: str,
    entitiesDescription="",
):
    return run_extract(
        llm=llm,
        stt=stt,
        input_data=inputJson,
        output_schema=extractionJson,
        repeated=(mode == 'REPEATED'),
        repeated_description=entitiesDescription
    )
