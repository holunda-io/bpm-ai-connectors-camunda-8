from bpm_ai.extract.extract import run_extract
from bpm_ai_core.llm.common.llm import LLM
from pyzeebe import ZeebeTaskRouter

from bpm_ai_connectors_c8.config import DEFAULT_TASK_TIMEOUT

extract_router = ZeebeTaskRouter()


@extract_router.task(
    task_type="io.holunda:connector-extract:2",
    timeout_ms=DEFAULT_TASK_TIMEOUT
)
async def extract(
    model: LLM,
    inputJson: dict,
    extractionJson: dict,
    mode: str,
    entitiesDescription=""
):
    return run_extract(
        llm=model,
        input_data=inputJson,
        output_schema=extractionJson,
        repeated=(mode == 'REPEATED'),
        repeated_description=entitiesDescription
    )
