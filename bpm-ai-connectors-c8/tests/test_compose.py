import logging

from pytest_zeebe.client.zeebe_test_client import ZeebeTestClient

logger = logging.getLogger(__name__)


def test_compose(runtime_selector, zeebe_test_client: ZeebeTestClient):
    # given
    variables = {
        "customer_name": "John",
        "company_name": "Toyz Corp.",
        "text_template": """\
Hello {customerName},

{ thank the customer for ordering a teddy }

Yours,
{companyName}"""
    }

    zeebe_test_client.deploy_process("bpmn/test_compose.bpmn")

    # when
    _, result = zeebe_test_client.create_process_instance_with_result(
        "test_compose",
        variables=variables
    )

    # then
    text = result['result']['text']
    assert "John" in text
    assert "Toyz Corp." in text
    assert "teddy" in text
