from typing import Any

from bpm_ai.decide.decide import run_decide
from bpm_ai_core.llm.common.llm import LLM
from pyzeebe import ZeebeTaskRouter

from bpm_ai_connectors_c8.config import DEFAULT_TASK_TIMEOUT

decide_router = ZeebeTaskRouter()


@decide_router.task(
    task_type="io.holunda:connector-decide:2",
    timeout_ms=DEFAULT_TASK_TIMEOUT
)
async def decide(
    model: LLM,
    inputJson: dict,
    instructions: str,
    outputType: str,
    possibleValues: list[Any] | None = None,
    strategy: str | None = None
):
    return run_decide(
        llm=model,
        input_data=inputJson,
        instructions=instructions,
        output_type=outputType,
        possible_values=possibleValues,
        strategy=strategy
    )
