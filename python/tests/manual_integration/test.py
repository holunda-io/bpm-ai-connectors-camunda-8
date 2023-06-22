import pytest

from gpt.config import get_openai_chat_llm
from gpt.database_agent.agent import create_database_agent
from gpt.extract_chain.chain import create_extract_chain
from gpt.openapi_agent.agent import create_openapi_agent
from gpt.plan_and_execute.executor.executor import create_executor


@pytest.mark.skip(reason="only on demand, uses real LLM")
def test_openapi_agent():
    agent = create_openapi_agent(
        llm=get_openai_chat_llm(model_name="gpt-4-0613"),
        api_spec_url="http://localhost:8090/v3/api-docs"
    )
    result = agent.run(
        query="Return the details of the customer.",
        context='{"customerId": 1}',
        output_schema='{"email": "the email", "name": "firstname and lastname"}'
    )
    print(result)
    assert "max.mustermann@mail.com" in result


@pytest.mark.skip(reason="only on demand, uses real LLM")
def test_database_agent():
    agent = create_database_agent(
        llm=get_openai_chat_llm(model_name="gpt-4-0613"),
        database_url="postgresql://postgres:password@localhost:5432/mydb"
    )
    result = agent.run(
        input="Return the details of the customer.",
        context='{"customerId": 1}',
        output_schema='{"birthday": "the birthday in format yyyy-mm-dd", "name": "lastname, firstname"}'
    )
    print(result)
    assert "Mustermann" in result


@pytest.mark.skip(reason="only on demand, uses real LLM")
def test_executor():
    executor = create_executor(
        llm=get_openai_chat_llm(model_name="gpt-3.5-turbo"),
        tools={"get_details": "Get details about a customer."}
    )
    result = executor.run(
        task="Return the details of the customer.",
        context='{"customerId": 1}',
        previous_steps='[]',
        current_step='Get the name of the customer'
    )
    print(result)


#@pytest.mark.skip(reason="only on demand, uses real LLM")
def test_extract():
    schema = {
        "name": "the first name only",
        "toys": {"type": "integer", "description": "number of wooden toys"},
        "birthday": {"type": "string", "description": "birthday in format: dd_mm_yyyy"}
    }
    chain = create_extract_chain(
        schema,
        get_openai_chat_llm(model_name="gpt-4-0613"),
        repeated=False
    )
    print(schema)
    print(chain.run('{"text": "My name is Johnny Johnson and I go to ABC Kindergarden (2 miles away) and I am 2 years old. My birthday is on the 6th of November, I was born in 2021. I have 5 toys, 3 of which are made from wood. The other two are metal." }'))
