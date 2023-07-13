import json
from typing import Dict, List, Any, Optional

from dotenv import load_dotenv

from gpt.agents.database_agent.agent import create_database_agent
from gpt.agents.plan_and_execute.executor.executor import create_executor
from gpt.agents.plan_and_execute.planner.planner import create_planner
from gpt.chains.compose_chain.chain import create_compose_chain
from gpt.chains.decide_chain.chain import create_decide_chain
from gpt.chains.extract_chain.chain import create_extract_chain
from gpt.chains.generic_chain.chain import create_generic_chain
from gpt.chains.retrieval_chain.chain import create_retrieval_chain
from gpt.chains.translate_chain.chain import create_translate_chain
from gpt.config import model_id_to_llm

load_dotenv(dotenv_path='../../../../connector-secrets.txt')
from gpt.agents.openapi_agent.agent import create_openapi_agent

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class OpenApiTask(BaseModel):
    model: str
    task: str
    context: dict
    outputSchema: dict
    specUrl: str


@app.post("/openapi")
async def post(task: OpenApiTask):
    agent = create_openapi_agent(
        task.specUrl,
        llm=model_id_to_llm(task.model)
    )
    res = agent.run(
        query=task.task,
        context=json.dumps(task.context, indent=2),
        output_schema=json.dumps(task.outputSchema, indent=2)
    )
    return json.loads(res)


class DatabaseTask(BaseModel):
    model: str
    task: str
    context: dict
    outputSchema: dict
    databaseUrl: str


@app.post("/database")
async def post(task: DatabaseTask):
    agent = create_database_agent(
        task.databaseUrl,
        llm=model_id_to_llm(task.model)
    )
    res = agent.run(
        input=task.task,
        context=json.dumps(task.context, indent=2),
        output_schema=json.dumps(task.outputSchema, indent=2)
    )
    return json.loads(res)


class PlannerTask(BaseModel):
    model: str
    task: str
    tools: Dict[str, str]
    context: dict


@app.post("/planner")
async def post(task: PlannerTask):
    planner = create_planner(
        tools=task.tools,
        llm=model_id_to_llm(task.model)
    )
    res = planner.plan({
        "context": json.dumps(task.context, indent=2),
        "task": task.task
    })
    steps = [s.value for s in res.steps]
    return steps


class ExecutorTask(BaseModel):
    model: str
    task: str
    tools: Dict[str, str]
    context: dict
    previous_steps: Any
    current_step: str


@app.post("/executor")
async def post(task: ExecutorTask):
    executor = create_executor(
        tools=task.tools,
        llm=model_id_to_llm(task.model)
    )
    return executor.run(
        context=json.dumps(task.context, indent=2),
        task=task.task,
        previous_steps=task.previous_steps,
        current_step=task.current_step
    )


class ExtractTask(BaseModel):
    model: str
    extraction_schema: dict
    context: dict
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
    return chain.run(input=task.context)


class DecideTask(BaseModel):
    model: str
    context: dict
    instructions: str
    output_type: str
    possible_values: Optional[List[Any]] = None


@app.post("/decide")
async def post(task: DecideTask):
    chain = create_decide_chain(
        instructions=task.instructions,
        output_type=task.output_type,
        possible_values=task.possible_values,
        llm=model_id_to_llm(task.model)
    )
    return chain.run(input=task.context)


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
    context: dict
    instructions: str
    output_schema: dict


@app.post("/generic")
async def post(task: GenericTask):
    chain = create_generic_chain(
        instructions=task.instructions,
        output_format=task.output_schema,
        llm=model_id_to_llm(task.model)
    )
    return chain.run(input=task.context)


class ComposeTask(BaseModel):
    model: str
    context: dict
    instructions: str
    style: str
    tone: str
    length: str
    language: str
    sender: str
    constitutional_principle: Optional[str] = None


@app.post("/compose")
async def post(task: ComposeTask):
    chain = create_compose_chain(
        instructions=task.instructions,
        style=task.style,
        tone=task.tone,
        length=task.length,
        language=task.language,
        sender=task.sender,
        constitutional_principle=task.constitutional_principle,
        llm=model_id_to_llm(task.model)
    )
    return chain(
        inputs={"input": task.context},
        return_only_outputs=True
    )


class RetrievalTask(BaseModel):
    model: str
    database_url: str
    embedding_provider: str
    embedding_model: str
    mode: str
    query: str


@app.post("/retrieval")
async def post(task: RetrievalTask):
    chain = create_retrieval_chain(
        llm=model_id_to_llm(task.model),
        database_url=task.database_url,
        embedding_provider=task.embedding_provider,
        embedding_model=task.embedding_model,
        mode=task.mode
    )
    return chain.run(query=task.query)
