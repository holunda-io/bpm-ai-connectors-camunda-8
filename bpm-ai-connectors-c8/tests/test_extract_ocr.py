import logging

import pytest
from pytest_zeebe.client.zeebe_test_client import ZeebeTestClient

from tests.conftest import requires_inference

logger = logging.getLogger(__name__)


@requires_inference()
def test_extract_ocr(runtime_selector, zeebe_test_client: ZeebeTestClient):
    # given
    variables = {
        "invoice": "https://github.com/holunda-io/camunda-8-connector-gpt/raw/bpm-ai/bpm-ai-connectors-c8/tests/data/sample-invoice.webp",
        "schema": {
            "invoice_number": "What is the invoice number?",
            "total": {
                "type": "number",
                "description": "What is the total?"
            },
        }
    }
    zeebe_test_client.deploy_process("bpmn/test_extract_ocr.bpmn")

    # when
    _, result = zeebe_test_client.create_process_instance_with_result(
        "test_extract_single",
        variables=variables
    )

    # then
    assert result['result']['invoice_number'] == "102"
    assert result['result']['total'] == 300.0
