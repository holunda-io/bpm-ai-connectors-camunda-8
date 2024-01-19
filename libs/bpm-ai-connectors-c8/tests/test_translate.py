import logging

import pytest
from pytest_zeebe.assertion import assert_that
from pytest_zeebe.client.zeebe_test_client import ZeebeTestClient

logger = logging.getLogger(__name__)


def test_translate(zeebe_test_client: ZeebeTestClient):
    # given
    variables = {
        "text1": "Hello World",
        "text2": "Process",
        "target_lang": "German"
    }

    zeebe_test_client.deploy_process("bpmn/test_translate.bpmn")

    # when
    _, result = zeebe_test_client.create_process_instance_with_result("test_translate", variables=variables)

    # then
    assert result['translated1'] == 'Hallo Welt'
    assert result['translated2'] == 'Prozess'
