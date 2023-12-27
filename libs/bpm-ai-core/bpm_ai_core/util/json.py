from typing import Any, Dict, List, Union


TYPE_MAP = {
    int: 'integer',
    float: 'number',
    bool: 'boolean',
    None: None
}


def is_schema(object_: Any) -> bool:
    return 'type' in object_


def handle_schema(json: Dict[str, Any], schema: Dict[str, Any]) -> None:
    schema.update(json)
    if schema['type'] == 'object':
        schema.pop('properties', None)
        parse(json.get('properties', {}), schema)
    if schema['type'] == 'array':
        schema.pop('items', None)
        schema['items'] = {}
        parse(json.get('items', {}), schema['items'])


def handle_array(arr: List[Any], schema: Dict[str, Any]) -> None:
    schema['type'] = 'array'
    props = schema['items'] = {}
    parse(arr[0], props)


def handle_object(json: Dict[str, Any], schema: Dict[str, Any]) -> None:
    if is_schema(json):
        handle_schema(json, schema)
        return
    schema['type'] = 'object'
    schema['required'] = list(json.keys())
    schema['properties'] = {k: {} for k in json.keys()}
    for key, item in json.items():
        parse(item, schema['properties'][key])


def parse(json: Union[Dict[str, Any], List[Any]], schema: Dict[str, Any]) -> None:
    if isinstance(json, list):
        handle_array(json, schema)
    elif isinstance(json, dict):
        handle_object(json, schema)
    elif isinstance(json, str):
        schema['type'] = 'string'
        schema['description'] = json
    else:
        schema['type'] = TYPE_MAP.get(type(json), 'string')
        schema['example'] = json


def expand_simplified_json_schema(data: Dict[str, Any]) -> Dict[str, Any]:
    json_schema = {}
    parse(data, json_schema)
    return json_schema

