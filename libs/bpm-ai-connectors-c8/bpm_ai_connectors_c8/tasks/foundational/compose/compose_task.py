from typing import TypedDict

from bpm_ai.compose.compose import run_compose
from bpm_ai_core.llm.common.llm import LLM
from pyzeebe import ZeebeTaskRouter

from bpm_ai_connectors_c8.config import DEFAULT_TASK_TIMEOUT

compose_router = ZeebeTaskRouter()


class TextProperties(TypedDict):
    style: str
    type: str
    tone: str
    length: str
    language: str
    temperature: str


@compose_router.task(
    task_type="io.holunda:connector-compose:2",
    timeout_ms=DEFAULT_TASK_TIMEOUT
)
async def compose(
    model: LLM,
    inputJson: dict,
    properties: TextProperties,
    template: str
):
    return run_compose(
        llm=model,
        input_data=inputJson,
        template=template,
        properties=properties
    )
