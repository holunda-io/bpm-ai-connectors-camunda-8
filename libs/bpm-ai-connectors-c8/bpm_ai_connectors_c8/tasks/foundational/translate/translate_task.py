from bpm_ai.translate.translate import run_translate
from bpm_ai_core.llm.common.llm import LLM
from pyzeebe import ZeebeTaskRouter

from bpm_ai_connectors_c8.config import DEFAULT_TASK_TIMEOUT

translate_router = ZeebeTaskRouter()


@translate_router.task(
    task_type="io.holunda:connector-translate:2",
    timeout_ms=DEFAULT_TASK_TIMEOUT
)
async def translate(
    model: LLM,
    inputJson: dict,
    language: str
):
    return run_translate(
        llm=model,
        input_data=inputJson,
        language=language
    )
