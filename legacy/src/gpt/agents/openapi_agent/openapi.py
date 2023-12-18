import typing
from dataclasses import dataclass
from typing import List

import requests
import yaml
from langchain.agents.agent_toolkits.openapi.spec import dereference_refs


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

    # 2. Replace any refs so that complete docs are retrieved.
    # Note: probably want to do this post-retrieval, it blows up the size of the spec.
    if dereference:
        endpoints = [
            (method, route, operationId, description, dereference_refs(docs, spec))
            for method, route, operationId, description, docs in endpoints
        ]

    # 3. Strip docs down to required request args + happy path response.
    def reduce_endpoint_docs(docs: dict) -> dict:
        out = {}
        if docs.get("description"):
            out["description"] = docs.get("description")
        if docs.get("parameters"):
            out["parameters"] = [
                parameter
                for parameter in docs.get("parameters", [])
                if parameter.get("required")
            ]
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
