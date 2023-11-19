from bpm_ai.extract.extract import run_extract
from bpm_ai_core.llm.common.llm import LLM
from bpm_ai_core.llm.openai_chat import ChatOpenAI
from pyzeebe import ZeebeTaskRouter
from bpm_ai_connectors_c8.tasks.routers import task_router


@task_router.task(
    task_type="io.holunda:connector-extract:dev"
)
async def extract(model: LLM, inputJson: dict, extractionJson: dict, mode: str, entitiesDescription=""):
    return run_extract(
        llm=model,
        input_data=inputJson,
        output_schema=extractionJson,
        repeated=(mode == 'REPEATED'),
        repeated_description=entitiesDescription
    )
