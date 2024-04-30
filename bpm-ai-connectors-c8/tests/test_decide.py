import logging

import pytest
from pytest_zeebe.client.zeebe_test_client import ZeebeTestClient

from bpm_ai_connectors_c8.tasks.decide.decide_task import decide
from tests.conftest import local_inference

logger = logging.getLogger(__name__)


@pytest.fixture
def vars_decide_string():
    return {
        "text": "I would like to cancel my order",
        "instruction": "What is the intention of the customer?",
        "options": [
            "CANCEL ORDER",
            "CHANGE ADDRESS",
            "COMPLAINT",
            "OTHER"
        ]
    }


@pytest.fixture
def vars_decide_boolean():
    return {
        "text": "I would like to cancel my order",
        "instruction": "Does the customer want to cancel his or her order?"
    }


def test_decide_string(vars_decide_string, runtime_selector, zeebe_test_client: ZeebeTestClient):
    # given
    zeebe_test_client.deploy_process("bpmn/test_decide_string.bpmn")

    # when
    _, result = zeebe_test_client.create_process_instance_with_result(
        "test_decide_string",
        variables=vars_decide_string
    )

    # then
    assert result['result']['decision'] == 'CANCEL ORDER'


def test_decide_string_multiple(vars_decide_string, runtime_selector, zeebe_test_client: ZeebeTestClient):
    # given
    variables = vars_decide_string
    variables['instruction'] = "I would like to cancel my order and change my address."
    zeebe_test_client.deploy_process("bpmn/test_decide_string_multi.bpmn")

    # when
    _, result = zeebe_test_client.create_process_instance_with_result(
        "test_decide_string",
        variables=vars_decide_string
    )

    # then
    assert set(result['result']['decision']) == {'CANCEL ORDER', 'CHANGE ADDRESS'}


def test_decide_boolean(vars_decide_boolean, runtime_selector, zeebe_test_client: ZeebeTestClient):
    # given
    zeebe_test_client.deploy_process("bpmn/test_decide_bool.bpmn")

    # when
    _, result = zeebe_test_client.create_process_instance_with_result(
        "test_decide_bool",
        variables=vars_decide_boolean
    )

    # then
    assert result['result']['decision'] is True


@local_inference()
def test_decide_string_local(vars_decide_string, runtime_selector, zeebe_test_client: ZeebeTestClient):
    # given
    zeebe_test_client.deploy_process("bpmn/test_decide_string_local.bpmn")

    # when
    _, result = zeebe_test_client.create_process_instance_with_result(
        "test_decide_string",
        variables=vars_decide_string
    )

    # then
    assert result['result']['decision'] == 'CANCEL ORDER'


@local_inference()
def test_decide_classifier_string(vars_decide_string, runtime_selector, zeebe_test_client: ZeebeTestClient):
    # given
    zeebe_test_client.deploy_process("bpmn/test_decide_classifier_string.bpmn")

    # when
    _, result = zeebe_test_client.create_process_instance_with_result(
        "test_decide_string",
        variables=vars_decide_string
    )

    # then
    assert result['result']['decision'] == 'CANCEL ORDER'


@local_inference()
def test_decide_classifier_boolean(vars_decide_boolean, runtime_selector, zeebe_test_client: ZeebeTestClient):
    # given
    zeebe_test_client.deploy_process("bpmn/test_decide_classifier_bool.bpmn")

    # when
    _, result = zeebe_test_client.create_process_instance_with_result(
        "test_decide_bool",
        variables=vars_decide_boolean
    )

    # then
    assert result['result']['decision'] is True
