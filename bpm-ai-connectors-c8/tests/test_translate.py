import logging

from pytest_zeebe.client.zeebe_test_client import ZeebeTestClient

logger = logging.getLogger(__name__)


def test_translate(runtime_selector, zeebe_test_client: ZeebeTestClient):
    # given
    variables = {
        "text1": "Hello World",
        "text2": "Process",
        "target_lang": "German"
    }

    zeebe_test_client.deploy_process("bpmn/test_translate.bpmn")

    # when
    _, result = zeebe_test_client.create_process_instance_with_result(
        "test_translate",
        variables=variables
    )

    # then
    assert result['result']['text1'] == 'Hallo Welt'
    assert result['result']['text2'] == 'Prozess'
