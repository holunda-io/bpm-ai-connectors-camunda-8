import logging

import pytest
from pytest_zeebe.client.zeebe_test_client import ZeebeTestClient

from tests.conftest import local_inference

logger = logging.getLogger(__name__)


@pytest.fixture
def vars():
    return {
        "text1": "Hello World",
        "text2": "My dog is called Bob.",
        "target_lang": "German"
    }


def test_translate(vars, runtime_selector, zeebe_test_client: ZeebeTestClient):
    # given
    zeebe_test_client.deploy_process("bpmn/test_translate.bpmn")

    # when
    _, result = zeebe_test_client.create_process_instance_with_result(
        "test_translate",
        variables=vars
    )

    # then
    assert result['result']['text1'] == 'Hallo Welt'
    assert result['result']['text2'] == 'Mein Hund heißt Bob.'


@local_inference()
def test_translate_nmt(vars, runtime_selector, zeebe_test_client: ZeebeTestClient):
    # given
    zeebe_test_client.deploy_process("bpmn/test_translate_nmt.bpmn")

    # when
    _, result = zeebe_test_client.create_process_instance_with_result(
        "test_translate",
        variables=vars
    )

    # then
    assert result['result']['text1'] == 'Hallo Welt'
    assert result['result']['text2'] == 'Mein Hund heißt Bob.'