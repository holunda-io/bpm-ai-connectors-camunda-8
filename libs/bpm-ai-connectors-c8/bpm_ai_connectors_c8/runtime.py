import os

import requests


def _runtime_url() -> str:
    return os.environ.get("CONNECTOR_RUNTIME_URL", "http://localhost:9999")


def create_output_variables(context, result_expression):
    url = f"{_runtime_url()}/createOutputVariables"
    payload = {
        "context": context,
        "resultExpression": result_expression
    }
    response = requests.post(url, json=payload)
    return response.json()


def examine_error_expression(context, error_expression):
    url = f"{_runtime_url()}/examineErrorExpression"
    payload = {
        "context": context,
        "errorExpression": error_expression
    }
    response = requests.post(url, json=payload)
    return response.json()
