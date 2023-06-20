import json
from typing import Dict, List, Any

from dotenv import load_dotenv

from gpt.config import model_id_to_llm
from gpt.output_parsers.json_output_parser import JsonOutputParser
from gpt.plan_and_execute.executor.executor import create_executor

load_dotenv(dotenv_path='../../../../connector-secrets.txt')
from gpt.plan_and_execute.planner.planner import create_planner

from gpt.database_agent.agent import create_database_agent
from gpt.openapi_agent.agent import create_openapi_agent

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class OpenApiTask(BaseModel):
    model: str
    task: str
    context: str
    outputSchema: str
    specUrl: str


@app.post("/openapi")
async def post(task: OpenApiTask):
    agent = create_openapi_agent(
        task.specUrl,
        llm=model_id_to_llm(task.model)
    )
    res = agent.run(
        query=task.task,
        context=task.context,
        output_schema=task.outputSchema
    )
    return json.loads(res)


class DatabaseTask(BaseModel):
    model: str
    task: str
    context: str
    outputSchema: str
    databaseUrl: str


@app.post("/database")
async def post(task: DatabaseTask):
    agent = create_database_agent(
        task.databaseUrl,
        llm=model_id_to_llm(task.model)
    )
    res = agent.run(
        input=task.task,
        context=task.context,
        output_schema=task.outputSchema
    )
    return json.loads(res)


class PlannerTask(BaseModel):
    model: str
    task: str
    tools: Dict[str, str]
    context: str


@app.post("/planner")
async def post(task: PlannerTask):
    planner = create_planner(
        tools=task.tools,
        llm=model_id_to_llm(task.model)
    )
    res = planner.plan({
        "context": task.context,
        "task": task.task
    })
    steps = [s.value for s in res.steps]
    return steps


class ExecutorTask(BaseModel):
    model: str
    task: str
    tools: Dict[str, str]
    context: str
    previous_steps: Any
    current_step: str


@app.post("/executor")
async def post(task: ExecutorTask):
    executor = create_executor(
        tools=task.tools,
        llm=model_id_to_llm(task.model)
    )
    res = executor(
        context=task.context,
        task=task.task,
        previous_steps=task.previous_steps,
        current_step=task.current_step
    )
    return JsonOutputParser().parse(res)
