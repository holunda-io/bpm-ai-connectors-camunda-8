import logging

from pytest_zeebe.client.zeebe_test_client import ZeebeTestClient

from tests.conftest import local_inference

logger = logging.getLogger(__name__)


def test_extract_whisper(runtime_selector, zeebe_test_client: ZeebeTestClient):
    # given
    zeebe_test_client.deploy_process("bpmn/test_extract_whisper.bpmn")

    # when
    _, result = zeebe_test_client.create_process_instance_with_result(
        "test_extract_single",
        variables={
            "schema": {"leap_size": "How big is the leap according to the quote?"}
        }
    )

    # then
    assert result['result']['leap_size'].lower() == "giant"


@local_inference()
def test_extract_faster_whisper(runtime_selector, zeebe_test_client: ZeebeTestClient):
    # given
    zeebe_test_client.deploy_process("bpmn/test_extract_faster_whisper.bpmn")

    # when
    _, result = zeebe_test_client.create_process_instance_with_result(
        "test_extract_single",
        variables={
            "schema": {"leap_size": "How big is the leap according to the quote?"}
        }
    )

    # then
    assert result['result']['leap_size'].lower() == "giant"
