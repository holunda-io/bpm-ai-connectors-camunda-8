import json

from dotenv import load_dotenv

from gpt.config import get_chat_llm

load_dotenv(dotenv_path='../../../../connector-secrets.txt')

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
        llm=get_chat_llm(task.model)
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
        llm=get_chat_llm(task.model)
    )
    res = agent.run(
        input=task.task,
        context=task.context,
        output_schema=task.outputSchema
    )
    return json.loads(res)


# agent = create_openapi_agent(
#     api_spec_url="http://localhost:8090/v3/api-docs"
# )
# print(
#     agent.run(
#         query="Return the details of the customer.",
#         context='{"customerId": 1}',
#         output_schema='{"email": "the email", "name": "firstname and lastname"}'
#     )
# )

# agent = create_database_agent(
#     database_url="postgresql://postgres:password@localhost:5432/mydb"
# )
# print(
#     agent.run(
#         input="Return the details of the customer.",
#         context='{"customerId": 1}',
#         output_schema='{"birthday": "the birthday in format yyyy-mm-dd", "name": "lastname, firstname"}'
#     )
# )
