import json

import pytest
from langchain import Cohere
from langchain.llms import AlephAlpha

import langchain
from langchain.cache import SQLiteCache

from gpt.agents.database_agent.agent import create_database_agent
from gpt.chains.compose_chain.chain import create_compose_chain
from gpt.chains.decide_chain.chain import create_decide_chain
from gpt.chains.generic_chain.chain import create_generic_chain

langchain.llm_cache = SQLiteCache(database_path=".langchain-test.db")

from gpt.config import get_openai_chat_llm, LUMINOUS_SUPREME_CONTROL
from gpt.chains.extract_chain.chain import create_extract_chain
from gpt.agents.openapi_agent.agent import create_openapi_agent
from gpt.agents.plan_and_execute.executor.executor import create_executor
from gpt.chains.translate_chain.chain import create_translate_chain


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


@pytest.mark.skip(reason="only on demand, uses real LLM")
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
    print(chain.run(
        '{"text": "My name is Johnny Johnson and I go to ABC Kindergarden (2 miles away) and I am 2 years old. My birthday is on the 6th of November, I was born in 2021. I have 5 toys, 3 of which are made from wood. The other two are metal." }'
    ))


@pytest.mark.skip(reason="only on demand, uses real LLM")
def test_extract_repeated():
    schema = {
        "firstname": "the first name",
        "lastname": {"type": "string", "description": "the last name"},
        "age": {"type": "integer", "description": "age in full years"}
    }
    chain = create_extract_chain(
        schema,
        get_openai_chat_llm(model_name="gpt-3.5-turbo"),
        repeated=True
    )
    print(schema)
    print(chain.run(
        '{"text": "My name is Johnny Johnson and my birthday is on the 6th of November. My friends are James Miller (13), Max Meier which is 11 and a half years old, and finally Bob - 12 years old." }'
    ))


@pytest.mark.skip(reason="only on demand, uses real LLM")
def test_decide():
    context = {
        "firstname": "Max",
        "lastname": "Meier",
        "age": "39",
        "qualifications": "Went to highschool, no further education.",
    }
    chain = create_decide_chain(
        get_openai_chat_llm(model_name="gpt-3.5-turbo-0613"),
        instructions="Decide if the applicant is qualified for the job as CTO.",
        output_type="string",
        possible_values=["QUALIFIED", "NOT_QUALIFIED"]
    )
    print(chain.run(json.dumps(context)))


@pytest.mark.skip(reason="only on demand, uses real LLM")
def test_decide_standard():
    context = {
        "firstname": "Max",
        "lastname": "Meier",
        "age": "39",
        "qualifications": "Went to highschool, no further education.",
    }
    chain = create_decide_chain(
        AlephAlpha(model=LUMINOUS_SUPREME_CONTROL),
        instructions="Decide if the applicant is qualified for the job as CTO.",
        output_type="string",
        possible_values=["QUALIFIED", "NOT_QUALIFIED"]
    )
    print(chain.run(json.dumps(context)))


@pytest.mark.skip(reason="only on demand, uses real LLM")
def test_translate():
    input = {
        "name": "OpenAI",
        "description": "OpenAI is an American artificial intelligence (AI) research laboratory consisting of the non-profit OpenAI Incorporated and its for-profit subsidiary corporation OpenAI Limited Partnership.",
        "motive": 'Some scientists, such as Stephen Hawking and Stuart Russell, have articulated concerns that if advanced AI someday gains the ability to re-design itself at an ever-increasing rate, an unstoppable "intelligence explosion" could lead to human extinction. Co-founder Musk characterizes AI as humanity\'s "biggest existential threat".',
    }
    chain = create_translate_chain(
        get_openai_chat_llm(model_name="gpt-3.5-turbo-0613"),
        input_keys=list(input.keys()),
        target_language="German",
    )
    print(chain.run(input=input))


@pytest.mark.skip(reason="only on demand, uses real LLM")
def test_translate_standard():
    input = {
        "name": "OpenAI",
        "description": "OpenAI is an American artificial intelligence (AI) research laboratory.",
        "motive": 'Some scientists have articulated concerns.',
    }
    chain = create_translate_chain(
        Cohere(
            model="command-xlarge-beta",
            temperature=0.0,
            max_tokens=1024
        ),
        input_keys=list(input.keys()),
        target_language="German",
    )
    print(chain.run(json.dumps(input)))


#@pytest.mark.skip(reason="only on demand, uses real LLM")
def test_generic_standard():
    input = {
        "name": "OpenAI",
        "description": "OpenAI is an American artificial intelligence (AI) research laboratory.",
        "motive": 'Some scientists have articulated concerns about AI.',
    }
    chain = create_generic_chain(
        get_openai_chat_llm(model_name="gpt-3.5-turbo-0613"),
        # Cohere(
        #     model="command-xlarge-beta",
        #     temperature=0.0,
        #     max_tokens=1024
        # ),
        instructions="Compress the description into 3 words.",
        output_format={
            "reasoning": "the reasoning behind the result",
            "result": "the result of the task"
        }
    )
    print(chain.run(json.dumps(input)))


#@pytest.mark.skip(reason="only on demand, uses real LLM")
def test_compose():
    input = {
        "firstname": "Jim",
        "lastname": "Simpson",
        "question": 'Where is my order ????',
        "customer_service_answer": 'shipped yesterday',
    }
    chain = create_compose_chain(
        Cohere(
            model="command-xlarge-beta",
            temperature=0.0,
            max_tokens=1024
        ),
        instructions="Answer the customers question based on the given answer.",
        language="English",
        style="informal",
        tone="friendly",
        sender="My company",
    )
    print(chain.run(json.dumps(input)))
