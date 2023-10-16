import json
from unittest.mock import patch

from dotenv import load_dotenv
from langchain.chains import OpenAIModerationChain
from langchain.embeddings import OpenAIEmbeddings
from openai.error import RateLimitError

from gpt.agents.database_agent.code_exection.base import create_database_code_execution_agent
from gpt.agents.openapi_agent.code_execution.base import create_openapi_code_execution_agent
from gpt.agents.plan_and_execute.executor.executor import create_executor
from gpt.agents.plan_and_execute.planner.planner import create_planner
from gpt.agents.process_generation_agent.process_generation_agent import create_process_generation_agent
from gpt.agents.retrieval_agent.retrieval_agent import create_retrieval_agent
from gpt.chains.compose_chain.chain import create_compose_chain
from gpt.chains.decide_chain.chain import create_decide_chain
from gpt.chains.extract_chain.chain import create_extract_chain
from gpt.chains.generic_chain.chain import create_generic_chain
from gpt.chains.translate_chain.chain import create_translate_chain
from gpt.config import model_id_to_llm, get_vector_store, get_embeddings, get_document_store
from gpt.server.types import RetrievalTask, ComposeTask, GenericTask, TranslateTask, DecideTask, ExtractTask, \
    ProcessTask, ExecutorTask, PlannerTask, \
    DatabaseTask, OpenApiTask

load_dotenv(dotenv_path='../../../../connector-secrets.txt')

from fastapi import FastAPI

app = FastAPI()


@app.post("/extract")
async def post(task: ExtractTask):
    schema = task.extraction_schema
    chain = create_extract_chain(
        llm=model_id_to_llm(task.model),
        output_schema=schema,
        repeated=task.repeated,
        repeated_description=task.repeated_description
    )
    return chain.run(input=task.context)


@app.post("/decide")
async def post(task: DecideTask):
    chain = create_decide_chain(
        llm=model_id_to_llm(task.model),
        strategy=task.strategy,
        instructions=task.instructions,
        output_type=task.output_type,
        possible_values=task.possible_values,
    )
    return chain.run(input=task.context)


@app.post("/translate")
async def post(task: TranslateTask):
    chain = create_translate_chain(
        llm=model_id_to_llm(task.model),
        input_keys=list(task.input.keys()),
        target_language=task.target_language
    )
    return chain.run(input=task.input)


@app.post("/compose")
async def post(task: ComposeTask):
    chain = create_compose_chain(
        llm=model_id_to_llm(task.model, task.temperature, cache=(task.temperature == 0.0)),
        instructions_or_template=task.instructions,
        type=task.type,
        style=task.style,
        tone=task.tone,
        length=task.length,
        language=task.language,
        sender=task.sender,
        constitutional_principle=task.constitutional_principle
    )
    return chain(
        inputs={"input": task.context}
    )["text"]


@app.post("/generic")
async def post(task: GenericTask):
    chain = create_generic_chain(
        llm=model_id_to_llm(task.model),
        instructions=task.instructions,
        output_format=task.output_schema
    )
    return chain.run(input=task.context)


@app.post("/openapi")
async def post(task: OpenApiTask):
    if task.skill_mode and task.skill_mode != "none":
        skill_store = get_vector_store(
            task.skill_store,
            task.skill_store_url,
            OpenAIEmbeddings(),
            password=task.skill_store_password,
            meta_attributes=['task', 'comment', 'function', 'example_call']
        )
    else:
        skill_store = None

    agent = create_openapi_code_execution_agent(
        llm=model_id_to_llm(task.model),
        api_spec_url=task.spec_url,
        skill_store=skill_store,
        enable_skill_creation=task.skill_mode == "use_create",
        output_schema=task.output_schema,
        llm_call=True
    )
    return agent.run(input=task.task, context=task.context)["output"]


@app.post("/database")
async def post(task: DatabaseTask):
    if task.skill_mode and task.skill_mode != "none":
        skill_store = get_vector_store(
            task.skill_store,
            task.skill_store_url,
            OpenAIEmbeddings(),
            password=task.skill_store_password,
            meta_attributes=['task', 'comment', 'function', 'example_call']
        )
    else:
        skill_store = None

    agent = create_database_code_execution_agent(
        llm=model_id_to_llm(task.model),
        database_url=task.database_url,
        skill_store=skill_store,
        enable_skill_creation=task.skill_mode == "use_create",
        output_schema=task.output_schema,
        llm_call=True
    )
    return agent.run(input=task.task, context=task.context)["output"]


@app.post("/retrieval")
async def post(task: RetrievalTask):
    embeddings = get_embeddings(task.embedding_provider, task.embedding_model)
    vector_store = get_vector_store(task.database, task.database_url, embeddings, password=task.password)
    if task.parent_document_store:
        parent_document_store = get_document_store(
            task.parent_document_store,
            task.parent_document_store_url,
            task.parent_document_store_namespace,
            password=task.parent_document_store_password
        )
    else:
        parent_document_store = None

    if task.summary_index:
        base_url, _ = task.database_url.rsplit('/', 1)
        summary_store = get_vector_store(task.database, base_url + "/" + task.summary_index, embeddings, password=task.password)
    else:
        summary_store = None
    agent = create_retrieval_agent(
        llm=model_id_to_llm(task.model),
        filter_llm=model_id_to_llm(task.model),
        vector_store=vector_store,
        output_schema=task.output_schema,
        reranker=task.reranker,
        filter_metadata_field=task.filter_metadata_field,
        document_content_description=task.document_content_description,
        metadata_field_info=task.metadata_field_info,
        summary_store=summary_store,
        parent_document_store=parent_document_store,
        parent_document_id_key=task.parent_document_id_key
    )
    result = agent.run(input=task.query, context="")
    return result["output"]


@app.post("/process")
async def post(task: ProcessTask):
    agent = create_process_generation_agent(
        llm=model_id_to_llm(task.model),
        tools=task.activities,
        context=task.context
    )
    return agent.run(input=task.task, context="")["process"]


@app.post("/planner")
async def post(task: PlannerTask):
    planner = create_planner(
        llm=model_id_to_llm(task.model),
        tools=task.tools
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
        llm=model_id_to_llm(task.model),
        tools=task.tools,
    )
    return executor.run(
        context=json.dumps(task.context, indent=2),
        task=task.task,
        previous_steps=task.previous_steps,
        current_step=task.current_step
    )
