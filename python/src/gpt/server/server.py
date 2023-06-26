import json
from typing import Dict, List, Any, Optional

from dotenv import load_dotenv

from gpt.agents.database_agent.agent import create_database_agent
from gpt.agents.plan_and_execute.planner.planner import create_planner
from gpt.chains.decide_chain.chain import create_decide_chain
from gpt.chains.generic_chain.chain import create_generic_chain
from gpt.chains.translate_chain.chain import create_translate_chain
from gpt.config import model_id_to_llm
from gpt.chains.extract_chain.chain import create_extract_chain
from gpt.output_parsers.json_output_parser import JsonOutputParser
from gpt.agents.plan_and_execute.executor.executor import create_executor

load_dotenv(dotenv_path='../../../../connector-secrets.txt')
from gpt.agents.openapi_agent.agent import create_openapi_agent

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
    res = executor.run(
        context=task.context,
        task=task.task,
        previous_steps=task.previous_steps,
        current_step=task.current_step
    )
    return JsonOutputParser().parse(res)


class ExtractTask(BaseModel):
    model: str
    extraction_schema: dict
    context: str
    repeated: bool
    repeated_description: Optional[str]


@app.post("/extract")
async def post(task: ExtractTask):
    schema = task.extraction_schema
    chain = create_extract_chain(
        properties=schema,
        repeated=task.repeated,
        repeated_description=task.repeated_description,
        llm=model_id_to_llm(task.model)
    )
    return chain.run(task.context)


class DecideTask(BaseModel):
    model: str
    context: str
    instructions: str
    output_type: str
    possible_values: List[str]


@app.post("/decide")
async def post(task: DecideTask):
    chain = create_decide_chain(
        instructions=task.instructions,
        output_type=task.output_type,
        possible_values=task.possible_values,
        llm=model_id_to_llm(task.model)
    )
    return chain.run(task.context)


class TranslateTask(BaseModel):
    model: str
    input: dict
    target_language: str


@app.post("/translate")
async def post(task: TranslateTask):
    chain = create_translate_chain(
        input_keys=list(task.input.keys()),
        target_language=task.target_language,
        llm=model_id_to_llm(task.model)
    )
    return chain.run(input=task.input)


class GenericTask(BaseModel):
    model: str
    context: str
    instructions: str
    output_schema: dict


@app.post("/generic")
async def post(task: GenericTask):
    chain = create_generic_chain(
        instructions=task.instructions,
        output_format=task.output_schema,
        llm=model_id_to_llm(task.model)
    )
    return chain.run(task.context)
