from dataclasses import dataclass
from typing import List

import typing

import requests
import yaml
from langchain.agents.agent_toolkits.openapi.spec import dereference_refs
from langchain.chains.openai_functions import _resolve_schema_references
from langchain.tools.convert_to_openai import FunctionDescription


@dataclass(frozen=True)
class Endpoint:
    method: str
    route: str
    operationId: str
    description: str
    docs: dict


@dataclass(frozen=True)
class OpenAPISpec:
    base_url: str
    description: str
    endpoints: List[Endpoint]
    endpoints_by_operation_id: typing.Dict[str, Endpoint]
    spec: dict


def dereference_schema(schema: typing.Any, definitions: typing.Dict[str, typing.Any]) -> typing.Any:
    """
    Resolves the $ref keys in a JSON schema object using the provided definitions.
    """
    if isinstance(schema, list):
        return [_resolve_schema_references(item, definitions) for item in schema]
    elif isinstance(schema, dict):
        if "$ref" in schema:
            ref_key = schema.pop("$ref").split("/")[-1]
            schema = definitions.get(ref_key, {})
        return {k: _resolve_schema_references(v, definitions) for k, v in schema.items()}
    else:
        return schema


def endpoint_to_function(endpoint: Endpoint) -> FunctionDescription:
    """Format OpenAPI operation into an OpenAI function description."""

    operation = endpoint.docs

    properties = {}
    required = []

    # Extract properties and required parameters from 'parameters'
    for param in operation.get("parameters", []):
        if "name" in param:
            param_info = {}
            # Fallback to direct type if not in schema
            if "schema" in param:
                param_info["type"] = param["schema"].get("type", param.get("type"))
            else:
                param_info["type"] = param.get("type")

            # Only add description or enum if present
            if param.get("description"):
                param_info["description"] = param.get("description")
            if param.get("enum"):
                param_info["enum"] = param.get("enum")
            if param.get("items"):
                param_info["items"] = param.get("items")

            properties[param["name"]] = param_info

            if param.get("required", False):
                required.append(param["name"])

    # Extract properties from 'requestBody', if present (OpenAPI 3)
    requestBody = operation.get("requestBody", {}).get("content", {}).get("application/json", {}).get("schema", {})
    if requestBody:
        for prop_name, prop_value in requestBody.get("properties", {}).items():
            prop_info = {"type": prop_value.get("type", None)}

            # Only add description or enum if present
            if prop_value.get("description"):
                prop_info["description"] = prop_value.get("description")
            if prop_value.get("enum"):
                prop_info["enum"] = prop_value.get("enum")
            if prop_value.get("items"):
                prop_info["items"] = prop_value.get("items")

            properties[prop_name] = prop_info

            # If requestBody is required, all its properties are required
            if operation.get("requestBody", {}).get("required", False):
                required.append(prop_name)

    return {
        "name": endpoint.operationId,
        "description": endpoint.description,
        "parameters": {
            "type": "object",
            "properties": properties,
            "required": required,
        },
    }


def reduce_openapi_spec(spec: dict, dereference: bool = True) -> OpenAPISpec:
    """Simplify/distill/minify a spec somehow.

    I want a smaller target for retrieval and (more importantly)
    I want smaller results from retrieval.
    I was hoping https://openapi.tools/ would have some useful bits
    to this end, but doesn't seem so.
    """
    # 1. Consider only get, post, patch, delete endpoints.
    endpoints = [
        (method.upper(), route, docs.get("operationId"), docs.get("description") or docs.get("summary"), docs)
        for route, operation in spec["paths"].items()
        for method, docs in operation.items()
        if method in ["get", "post", "patch", "delete"]
    ]

    schemas = dereference_schema(spec['components']['schemas'], spec['components']['schemas'])

    # 2. Replace any refs so that complete docs are retrieved.
    # Note: probably want to do this post-retrieval, it blows up the size of the spec.
    if dereference:
        endpoints = [
            #(method, route, operationId, description, dereference_refs(docs, spec))
            (method, route, operationId, description, dereference_schema(docs, schemas))
            for method, route, operationId, description, docs in endpoints
        ]

    # 3. Strip docs down to required request args + happy path response.
    def reduce_endpoint_docs(docs: dict) -> dict:
        out = {}
        if docs.get("description") or docs.get("summary"):
            out["description"] = docs.get("description") or docs.get("summary")
        if docs.get("parameters"):
            out["parameters"] = [
                parameter
                for parameter in docs.get("parameters", [])
                if parameter.get("required")
            ]
        if docs.get("requestBody"):
            out["requestBody"] = docs.get("requestBody")
        if "200" in docs["responses"]:
            out["responses"] = docs["responses"]["200"]
        return out

    endpoints = [
        Endpoint(method, route, operationId, description, reduce_endpoint_docs(docs))
        for method, route, operationId, description, docs in endpoints
    ]

    def extract_base_url(s):
        if s.get('openapi', '2').startswith('3'):
            base_url = s['servers'][0]['url']
        else:
            # Retrieve components of the base URL
            schema = s.get('schemes', ['http'])[0]  # Default to 'http' if not provided
            host = s.get('host', '')
            base_path = s.get('basePath', '')

            # Construct the base URL
            base_url = f"{schema}://{host}{base_path}"

        return base_url

    return OpenAPISpec(
        base_url=extract_base_url(spec),
        description=spec["info"].get("description", ""),
        endpoints=endpoints,
        endpoints_by_operation_id={e.operationId: e for e in endpoints},
        spec=spec
    )


def load_api_spec(url: str) -> OpenAPISpec:
    raw_api_spec = requests.get(url).json()
    return reduce_openapi_spec(raw_api_spec)


def create_docs(api_spec: OpenAPISpec, selected_operations: List[str]):
    docs_str = ""
    for e in api_spec.endpoints:
        if e.operationId in selected_operations:
            docs_str += f"== Docs for {e.operationId} ({e.method}) == \n{yaml.dump(e.docs)}\n"
    return docs_str


def escape_format_placeholders(s):
    return s.replace('{', '{{').replace('}', '}}')
