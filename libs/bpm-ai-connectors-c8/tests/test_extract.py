import logging

import pytest
from pytest_zeebe.client.zeebe_test_client import ZeebeTestClient


logger = logging.getLogger(__name__)


def test_extract_single(zeebe_test_client: ZeebeTestClient):
    # given
    variables = {
        "text1": "I am John",
        "text2": "I am 20 years old",
        "schema": {
          "name": "full name",
          "age": {"type": "integer", "description": "age in years"}
        }
    }
    zeebe_test_client.deploy_process("bpmn/test_extract_single.bpmn")

    # when
    _, result = zeebe_test_client.create_process_instance_with_result("test_extract_single", variables=variables)

    # then
    assert result['full_result'] == {'name': 'John', 'age': 20}
    assert result['mapped_name'] == 'John'
    assert result['mapped_age'] == 20


def test_extract_multiple(zeebe_test_client: ZeebeTestClient):
    # given
    variables = {
        "friends1": "My friends are John and Kelly",
        "friends2": "Also Jim, Mike and Joanna",
        "schema": {"name": "friend's name"}
    }
    zeebe_test_client.deploy_process("bpmn/test_extract_multiple.bpmn")

    # when
    _, result = zeebe_test_client.create_process_instance_with_result("test_extract_multiple", variables=variables)

    # then
    assert result['friends'] == [
        {'name': 'John'}, {'name': 'Kelly'}, {'name': 'Jim'}, {'name': 'Mike'}, {'name': 'Joanna'}
    ]
