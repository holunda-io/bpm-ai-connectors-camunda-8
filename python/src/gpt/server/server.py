import json

from dotenv import load_dotenv
from langchain.embeddings import OpenAIEmbeddings

from gpt.agents.database_agent.code_exection.base import create_database_code_execution_agent
from gpt.agents.plan_and_execute.executor.executor import create_executor
from gpt.agents.plan_and_execute.planner.planner import create_planner
from gpt.agents.process_generation_agent.process_generation_agent import create_process_generation_agent
from gpt.chains.compose_chain.chain import create_compose_chain
from gpt.chains.decide_chain.chain import create_decide_chain
from gpt.chains.extract_chain.chain import create_extract_chain
from gpt.chains.generic_chain.chain import create_generic_chain
from gpt.chains.retrieval_chain.chain import create_retrieval_chain, get_vector_store
from gpt.chains.translate_chain.chain import create_translate_chain
from gpt.config import model_id_to_llm
from gpt.server.types import RetrievalTask, ComposeTask, GenericTask, TranslateTask, DecideTask, ExtractTask, \
    ProcessTask, ExecutorTask, PlannerTask, \
    DatabaseTask, OpenApiTask

load_dotenv(dotenv_path='../../../../connector-secrets.txt')
from gpt.agents.openapi_agent.agent import create_openapi_agent

from fastapi import FastAPI

app = FastAPI()


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


@app.post("/decide")
async def post(task: DecideTask):
    chain = create_decide_chain(
        instructions=task.instructions,
        output_type=task.output_type,
        possible_values=task.possible_values,
        llm=model_id_to_llm(task.model)
    )
    return chain.run(input=task.context)


@app.post("/translate")
async def post(task: TranslateTask):
    chain = create_translate_chain(
        input_keys=list(task.input.keys()),
        target_language=task.target_language,
        llm=model_id_to_llm(task.model)
    )
    return chain.run(input=task.input)


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


@app.post("/generic")
async def post(task: GenericTask):
    chain = create_generic_chain(
        instructions=task.instructions,
        output_format=task.output_schema,
        llm=model_id_to_llm(task.model)
    )
    return chain.run(input=task.context)


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


@app.post("/database")
async def post(task: DatabaseTask):
    if task.skill_store_url:
        skill_store = get_vector_store(
            task.skill_store_url,
            OpenAIEmbeddings(),
            meta_attributes=['task', 'comment', 'function', 'example_call']
        )
    else:
        skill_store = None

    agent = create_database_code_execution_agent(
        llm=model_id_to_llm(task.model),
        database_url=task.database_url,
        skill_store=skill_store,
        enable_skill_creation=(skill_store is not None),
        output_schema=task.output_schema,
        call_direct=True
    )
    res = agent(
        inputs={
            "input": task.task,
            "context": task.context,
        },
        return_only_outputs=True
    )["output"]
    return res


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


@app.post("/process")
async def post(task: ProcessTask):
    agent = create_process_generation_agent(
        llm=model_id_to_llm(task.model),
        tools=task.activities,
        context=task.context
    )
    return agent(
        inputs={
            "input": task.task,
            "context": ""  # todo not necessary
        },
        return_only_outputs=True
    )["process"]


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
