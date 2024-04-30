import logging

import pytest
from pytest_zeebe.client.zeebe_test_client import ZeebeTestClient

from tests.conftest import local_inference

logger = logging.getLogger(__name__)


@pytest.fixture
def vars_extract_single():
    return {
        "text1": "I am John Watts",
        "text2": "I am 20 years old",
        "schema": {
          "name": "full name",
          "age": {"type": "integer", "description": "age in years"}
        }
    }


@pytest.fixture
def vars_extract_multiple():
    return {
        "friends1": "My friends are John and Kelly",
        "friends2": "Also Jim and Joanna",
        "schema": {"name": "What is the friend's name?"}
    }


def test_extract_single(vars_extract_single, runtime_selector, zeebe_test_client: ZeebeTestClient):
    # given
    zeebe_test_client.deploy_process("bpmn/test_extract_single.bpmn")

    # when
    _, result = zeebe_test_client.create_process_instance_with_result(
        "test_extract_single",
        variables=vars_extract_single
    )

    # then
    assert result['result'] == {'name': 'John Watts', 'age': 20}


def test_extract_multiple(vars_extract_multiple, runtime_selector, zeebe_test_client: ZeebeTestClient):
    # given
    zeebe_test_client.deploy_process("bpmn/test_extract_multiple.bpmn")

    # when
    _, result = zeebe_test_client.create_process_instance_with_result(
        "test_extract_multiple",
        variables=vars_extract_multiple
    )

    # then
    assert result['result'] == [
        {'name': 'John'}, {'name': 'Kelly'}, {'name': 'Jim'}, {'name': 'Joanna'}
    ]


@local_inference()
def test_extract_single_local(vars_extract_single, runtime_selector, zeebe_test_client: ZeebeTestClient):
    # given
    zeebe_test_client.deploy_process("bpmn/test_extract_single_local.bpmn")

    # when
    _, result = zeebe_test_client.create_process_instance_with_result(
        "test_extract_single",
        variables=vars_extract_single
    )

    # then
    assert result['result'] == {'name': 'John Watts', 'age': 20}


@local_inference()
def test_extract_qa_single(vars_extract_single, runtime_selector, zeebe_test_client: ZeebeTestClient):
    # given
    zeebe_test_client.deploy_process("bpmn/test_extract_qa_single.bpmn")

    # when
    _, result = zeebe_test_client.create_process_instance_with_result(
        "test_extract_single",
        variables=vars_extract_single
    )

    # then
    assert result['result'] == {'name': 'John Watts', 'age': 20}


@local_inference()
def test_extract_qa_multiple(vars_extract_multiple, runtime_selector, zeebe_test_client: ZeebeTestClient):
    # given
    variables = {
        "text": "We received the following orders: Pizza (10.99€) and Steak (28.89€).",
        "schema": {"order": {"type": "string", "description": "What is the meal name?"}}
    }
    zeebe_test_client.deploy_process("bpmn/test_extract_qa_multiple.bpmn")

    # when
    _, result = zeebe_test_client.create_process_instance_with_result(
        "test_extract_multiple",
        variables=variables
    )

    # then
    assert sorted(result['result'], key=repr) == sorted([{'order': "Pizza"}, {'order': "Steak"}], key=repr)