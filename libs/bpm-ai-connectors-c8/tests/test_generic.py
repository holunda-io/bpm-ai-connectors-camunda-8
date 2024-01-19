import logging

import pytest
from pytest_zeebe.assertion import assert_that
from pytest_zeebe.client.zeebe_test_client import ZeebeTestClient

logger = logging.getLogger(__name__)


def test_decide_string(zeebe_test_client: ZeebeTestClient):
    # given
    variables = {
        "x": 42,
        "task": "Increase the given number by one and store the result in the result field.",
    }

    zeebe_test_client.deploy_process("bpmn/test_generic.bpmn")

    # when
    _, result = zeebe_test_client.create_process_instance_with_result("test_generic", variables=variables)

    # then
    assert result['task_result'] == 43
