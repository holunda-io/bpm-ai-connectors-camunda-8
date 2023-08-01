from typing import Union, Dict, Any, Tuple


def dereference_all_refs(full_spec: dict) -> dict:
    """Dereference all $refs in the full OpenAPI specification."""

    def _retrieve_ref_path(path: str, full_spec: dict) -> dict:
        components = path.split("/")
        if components[0] != "#":
            raise RuntimeError(
                "All $refs I've seen so far are uri fragments (start with hash)."
            )
        out = full_spec
        for component in components[1:]:
            out = out[component]
        return out

    def _dereference_refs(obj: Union[dict, list], dereferenced: set = None) -> Union[dict, list]:
        if dereferenced is None:
            dereferenced = set()
        if isinstance(obj, dict):
            if '$ref' in obj and obj['$ref'] not in dereferenced:
                dereferenced.add(obj['$ref'])
                dereferenced_obj = _dereference_refs(_retrieve_ref_path(obj['$ref'], full_spec), dereferenced)
                return {
                    'example': obj['$ref'],  # HACK misusing the example property of the schema object type to remember the original $ref
                    **dereferenced_obj
                }
            else:
                return {k: _dereference_refs(v, set(dereferenced)) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [_dereference_refs(el, set(dereferenced)) for el in obj]
        else:
            return obj

    return _dereference_refs(full_spec)


# OpenAPI to Python type mapping
type_mapping = {
    "string": "str",
    "number": "float",
    "integer": "int",
    "boolean": "bool",
    "array": "list",
    "object": "dict"
}


def param_to_python_arg(param_name: str, param_def: Union[dict, str]):
    if isinstance(param_def, dict):
        python_arg_type = type_mapping[param_def['type']]
    else:
        python_arg_type = param_def
    return param_name + ': ' + python_arg_type


def json_schema_to_typed_dicts(name: str, schema: Dict[str, Any]) -> Dict[str, str]:
    code_dict = {}

    def process_schema(name: str, schema: Dict[str, Any]) -> str:
        lines = [f"class {name}(TypedDict):"]
        for prop, attrs in schema.get('properties', {}).items():
            if attrs['type'] == 'object':
                nested_name = prop.capitalize()
                lines.append(process_schema(nested_name, attrs))
                type_name = nested_name
            elif attrs['type'] == 'integer' or (attrs.get('schema_format') == 'int32'):
                type_name = 'int'
            elif attrs['type'] == 'number' or (attrs.get('schema_format') == 'double'):
                type_name = 'float'
            elif attrs['type'] == 'string':
                type_name = 'str'
            elif attrs['type'] == 'array':
                type_name = 'list'
            elif attrs['type'] == 'boolean':
                type_name = 'bool'
            else:
                type_name = attrs['type']
            lines.append(f"    {prop}: {type_name}")
        code_dict[name] = '\n'.join(lines)
        return ''

    process_schema(name, schema)
    return code_dict


def find_response_schema(full_spec: dict, operation_id: str) -> Union[dict, None]:
    """Find the original ref of the response object type (if any) for a given operation_id, using the full spec dict."""

    for path, operations in full_spec.get("paths", {}).items():
        for operation, details in operations.items():
            if details.get("operationId") == operation_id:
                responses = details.get("responses", {})
                for response_code, response_details in responses.items():
                    content = response_details.get("content", {})
                    for mime_type, mime_details in content.items():
                        schema = mime_details.get("schema", {})
                        return schema
    return None


