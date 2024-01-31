import logging

from pytest_zeebe.client.zeebe_test_client import ZeebeTestClient

logger = logging.getLogger(__name__)


def test_decide_string(runtime_selector, zeebe_test_client: ZeebeTestClient):
    # given
    variables = {
        "text": "I would like to cancel my order",
        "instruction": "Decide what the intention of the customer is.",
        "options": [
            "CANCEL_ORDER",
            "CHANGE_ADDRESS",
            "COMPLAINT",
            "OTHER"
        ]
    }

    zeebe_test_client.deploy_process("bpmn/test_decide_string.bpmn")

    # when
    _, result = zeebe_test_client.create_process_instance_with_result(
        "test_decide_string",
        variables=variables
    )

    # then
    assert result['result']['decision'] == 'CANCEL_ORDER'


def test_decide_boolean(runtime_selector, zeebe_test_client: ZeebeTestClient):
    # given
    variables = {
        "text": "I would like to cancel my order",
        "instruction": "Does the customer want to cancel his or her order?"
    }

    zeebe_test_client.deploy_process("bpmn/test_decide_bool.bpmn")

    # when
    _, result = zeebe_test_client.create_process_instance_with_result(
        "test_decide_bool",
        variables=variables
    )

    # then
    assert result['result']['decision'] is True

