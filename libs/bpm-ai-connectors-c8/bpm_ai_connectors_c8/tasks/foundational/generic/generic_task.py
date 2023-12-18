from bpm_ai.generic.generic import run_generic
from bpm_ai_core.llm.common.llm import LLM
from pyzeebe import ZeebeTaskRouter

from bpm_ai_connectors_c8.config import DEFAULT_TASK_TIMEOUT

generic_router = ZeebeTaskRouter()


@generic_router.task(
    task_type="io.holunda:connector-generic:2",
    timeout_ms=DEFAULT_TASK_TIMEOUT
)
async def generic(
    model: LLM,
    inputJson: dict,
    taskDescription: str,
    outputFormat: dict
):
    return run_generic(
        llm=model,
        input_data=inputJson,
        instructions=taskDescription,
        output_schema=outputFormat
    )
