import asyncio

from bpm_ai.extract.extract import run_extract
from bpm_ai_core.llm.common.llm import LLM
from bpm_ai_core.llm.openai_chat import ChatOpenAI
from bpm_ai_experimental.browser_agent.agent import run_browser_agent
from pyzeebe import ZeebeTaskRouter

from bpm_ai_connectors_c8.tasks.routers import experimental_task_router


rpa_router = ZeebeTaskRouter()

@rpa_router.task(
    task_type="io.holunda:connector-rpa:1",
    timeout_ms=(5*60*1000)
)
async def rpa(model: LLM, inputJson: dict, startUrl: str, task: dict):
    result = await run_browser_agent(
        llm=model,
        input_data=inputJson,
        output_schema=task["outputSchema"] if "outputSchema" in task.keys() else None,
        start_url=startUrl,
        task=task["task"]
    )
    print(f"RESULT: {result}")
    return {"result": result}
