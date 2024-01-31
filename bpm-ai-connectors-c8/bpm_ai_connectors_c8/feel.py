import os

import requests


def _feel_wrapper_url() -> str:
    return os.environ.get("FEEL_ENGINE_WRAPPER_URL", "http://localhost:8080")


def create_output_variables(context, result_expression) -> dict:
    url = f"{_feel_wrapper_url()}/createOutputVariables"
    request = {
        "context": context,
        "resultExpression": result_expression
    }
    response = requests.post(url, json=request)
    if not response.ok:
        raise Exception(f"Error creating output variables: {response}")
    return response.json()


def examine_error_expression(context, error_expression) -> dict | None:
    url = f"{_feel_wrapper_url()}/examineErrorExpression"
    request = {
        "context": context,
        "errorExpression": error_expression
    }
    response = requests.post(url, json=request)
    if not response.ok:
        raise Exception(f"Error examining error expression: {response}")
    return response.json() if response.content else None
