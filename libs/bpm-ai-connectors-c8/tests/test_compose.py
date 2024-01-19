import logging

import pytest
from pytest_zeebe.assertion import assert_that
from pytest_zeebe.client.zeebe_test_client import ZeebeTestClient

logger = logging.getLogger(__name__)


def test_compose(zeebe_test_client: ZeebeTestClient):
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
    _, result = zeebe_test_client.create_process_instance_with_result("test_compose", variables=variables)

    # then
    assert "John" in result['text']
    assert "Toyz Corp." in result['text']
    assert "teddy" in result['text']
