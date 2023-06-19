import pytest

from gpt.config import get_chat_llm
from gpt.database_agent.agent import create_database_agent
from gpt.openapi_agent.agent import create_openapi_agent
from gpt.plan_and_execute.executor.executor import create_executor


@pytest.mark.skip(reason="only on demand, uses real LLM")
def test_openapi_agent():
    agent = create_openapi_agent(
        llm=get_chat_llm(model_name="gpt-4-0613"),
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
        llm=get_chat_llm(model_name="gpt-4-0613"),
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
        llm=get_chat_llm(model_name="gpt-4-0613"),
        tools={"get_details": "Get details about a customer."}
    )
    result = executor(
        task="Return the details of the customer.",
        context='{"customerId": 1}',
        previous_steps='[]',
        current_step='Get the name of the customer'
    )
    print(result)
