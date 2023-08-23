from unittest import mock
from unittest.mock import Mock

from fastapi.testclient import TestClient

from gpt.server.server import app

client = TestClient(app)


@mock.patch('gpt.server.server.create_extract_chain')
def test_extract(chain_function_mock):
    chain_instance = chain_function_mock.return_value

    chain_instance.run.return_value = 'test_result'

    response = client.post("/extract", json={"model": "test",
                                             "extraction_schema": {"output": "the output"},
                                             "context": {'my_input': 1},
                                             "repeated": False})
    assert response.status_code == 200
    assert response.json() == 'test_result'

    chain_function_mock.assert_called_with(
        output_schema={"output": "the output"},
        repeated=False,
        repeated_description=None,
        llm=None
    )
    chain_instance.run.assert_called_with(input={'my_input': 1})
