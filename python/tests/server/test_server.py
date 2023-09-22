from unittest import mock
from unittest.mock import Mock

from fastapi.testclient import TestClient

from gpt.server.server import app

client = TestClient(app)


@mock.patch('gpt.server.server.create_extract_chain')
def test_extract(chain_function_mock):
    chain_instance = chain_function_mock.return_value

    chain_instance.run.return_value = 'test_result'

    response = client.post("/extract", json={
        "model": "test",
        "extraction_schema": {"output": "the output"},
        "context": {'my_input': 1},
        "repeated": False
    })
    assert response.status_code == 200
    assert response.json() == 'test_result'

    chain_function_mock.assert_called_with(
        output_schema={"output": "the output"},
        repeated=False,
        repeated_description=None,
        llm=None
    )
    chain_instance.run.assert_called_with(input={'my_input': 1})


@mock.patch('gpt.server.server.create_decide_chain')
def test_decide(chain_function_mock):
    chain_instance = chain_function_mock.return_value

    chain_instance.run.return_value = 'test_result'

    response = client.post("/decide", json={
        "model": "test",
        "instructions": "Decide ...",
        "output_type": "string",
        "possible_values": ["A", "B"],
        "context": {'my_input': 1}
    })
    assert response.status_code == 200
    assert response.json() == 'test_result'

    chain_function_mock.assert_called_with(
        llm=None,
        instructions="Decide ...",
        output_type="string",
        possible_values=["A", "B"]
    )
    chain_instance.run.assert_called_with(input={'my_input': 1})


@mock.patch('gpt.server.server.create_translate_chain')
def test_translate(chain_function_mock):
    chain_instance = chain_function_mock.return_value

    chain_instance.run.return_value = 'test_result'

    response = client.post("/translate", json={
        "model": "test",
        "input": {"text": "Hello"},
        "target_language": "fr"
    })
    assert response.status_code == 200
    assert response.json() == 'test_result'

    chain_function_mock.assert_called_with(
        llm=None,
        input_keys=['text'],
        target_language='fr'
    )
    chain_instance.run.assert_called_with(input={'text': 'Hello'})


@mock.patch('gpt.server.server.create_compose_chain')
def test_compose(chain_function_mock):
    chain_instance = Mock()
    chain_instance.return_value = {"text": 'test_result'}
    chain_function_mock.return_value = chain_instance

    response = client.post("/compose", json={
        "model": "test",
        "instructions": "test_instructions",
        "type": "message",
        "style": "formal",
        "tone": "polite",
        "length": "short",
        "language": "en",
        "context": {'my_input': 1},
        "temperature": 0.0,
        "sender": "John",
        "constitutional_principle": None
    })
    assert response.status_code == 200
    assert response.json() == 'test_result'

    chain_function_mock.assert_called_with(
        llm=None,
        instructions_or_template="test_instructions",
        type="message",
        style="formal",
        tone="polite",
        length="short",
        language="en",
        sender="John",
        constitutional_principle=None
    )
    chain_instance.assert_called_with(inputs={'input': {'my_input': 1}})


@mock.patch('gpt.server.server.create_generic_chain')
def test_generic(chain_function_mock):
    chain_instance = chain_function_mock.return_value

    chain_instance.run.return_value = 'test_result'

    response = client.post("/generic", json={
        "model": "test",
        "instructions": "test_instructions",
        "output_schema": {"result": "the result"},
        "context": {'my_input': 1}
    })
    assert response.status_code == 200
    assert response.json() == 'test_result'

    chain_function_mock.assert_called_with(
        llm=None,
        instructions="test_instructions",
        output_format={"result": "the result"}
    )
    chain_instance.run.assert_called_with(input={'my_input': 1})


@mock.patch('gpt.server.server.create_openapi_code_execution_agent')
def test_openapi(agent_function_mock):
    agent_instance = agent_function_mock.return_value
    agent_instance.run.return_value = {"output": 'test_result'}

    response = client.post("/openapi", json={
        "model": "test",
        "task": "test_task",
        "context": {'my_input': 1},
        "output_schema": {"result": "the result"},
        "spec_url": "http://test.com",
        "skill_mode": None,
        "skill_store": None,
        "skill_store_url": None,
        "skill_store_password": None
    })
    assert response.status_code == 200
    assert response.json() == 'test_result'

    agent_function_mock.assert_called_with(
        llm=None,
        api_spec_url="http://test.com",
        skill_store=None,
        enable_skill_creation=False,
        output_schema={"result": "the result"},
        llm_call=True
    )
    agent_instance.run.assert_called_with(input='test_task', context={'my_input': 1})


@mock.patch('gpt.server.server.create_database_code_execution_agent')
def test_database(agent_function_mock):
    agent_instance = agent_function_mock.return_value
    agent_instance.run.return_value = {"output": 'test_result'}

    response = client.post("/database", json={
        "model": "test",
        "task": "test_task",
        "context": {'my_input': 1},
        "output_schema": {"result": "the result"},
        "database_url": "test_database_url",
        "skill_mode": None,
        "skill_store": None,
        "skill_store_url": None,
        "skill_store_password": None
    })
    assert response.status_code == 200
    assert response.json() == 'test_result'

    agent_function_mock.assert_called_with(
        llm=None,
        database_url="test_database_url",
        skill_store=None,
        enable_skill_creation=False,
        output_schema={"result": "the result"},
        llm_call=True
    )
    agent_instance.run.assert_called_with(input='test_task', context={'my_input': 1})


@mock.patch('gpt.server.server.create_retrieval_agent')
def test_retrieval(agent_function_mock):
    agent_instance = agent_function_mock.return_value
    agent_instance.run.return_value = {"output": 'test_result'}

    response = client.post("/retrieval", json={
        "model": "test",
        "query": "test_query",
        "context": "",
        "database": "test_database",
        "database_url": "test_database_url",
        "password": "test_password",
        "embedding_provider": "test_embedding_provider",
        "embedding_model": "test_embedding_model",
        "output_schema": {"result": "the result"},
        "mode": "test_mode",
        "reranker": "test_reranker",
        "filter_metadata_field": "test_filter_metadata_field",
        "summary_index": None,
        "document_content_description": "test_document_content_description",
        "metadata_field_info": [{"name": "test_field", "description": "test_description", "type": "string"}],
        "parent_document_store": None,
        "parent_document_store_url": None,
        "parent_document_store_password": None,
        "parent_document_store_namespace": None,
        "parent_document_id_key": None
    })
    assert response.status_code == 200
    assert response.json() == 'test_result'

    agent_function_mock.assert_called_with(
        llm=None,
        vector_store=None,
        output_schema={'result': 'the result'},
        reranker='test_reranker',
        filter_metadata_field='test_filter_metadata_field',
        document_content_description='test_document_content_description',
        metadata_field_info=[{'name': 'test_field', 'description': 'test_description', 'type': 'string'}],
        summary_store=None,
        parent_document_store=None,
        parent_document_id_key=None
    )
    agent_instance.run.assert_called_with(input='test_query', context="")
