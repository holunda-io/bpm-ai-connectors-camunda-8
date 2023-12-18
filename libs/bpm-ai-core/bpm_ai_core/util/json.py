from typing import Any, Dict, List, Union


# def get_type(type_: Any) -> str:
#     support_type = ['string', 'number', 'array', 'object', 'boolean', 'integer']
#     if not type_:
#         type_ = 'string'
#     if type_ in support_type:
#         return type_
#     return str(type(type_))
#
#
# def is_schema(object_: Any) -> bool:
#     support_type = ['string', 'number', 'array', 'object', 'boolean', 'integer']
#     return object_['type'] in support_type if 'type' in object_ else False
#
#
# def handle_schema(json: Dict[str, Any], schema: Dict[str, Any]) -> None:
#     schema.update(json)
#     if schema['type'] == 'object':
#         schema.pop('properties', None)
#         parse(json['properties'], schema)
#     if schema['type'] == 'array':
#         schema.pop('items', None)
#         schema['items'] = {}
#         parse(json['items'], schema['items'])
#
#
# def handle_array(arr: List[Any], schema: Dict[str, Any]) -> None:
#     schema['type'] = 'array'
#     props = schema['items'] = {}
#     parse(arr[0], props)
#
#
# def handle_object(json: Dict[str, Any], schema: Dict[str, Any]) -> None:
#     if is_schema(json):
#         handle_schema(json, schema)
#         return
#     schema['type'] = 'object'
#     schema['required'] = []
#     props = schema['properties'] = {}
#     for key, item in json.items():
#         cur_schema = props[key] = {}
#         schema['required'].append(key)
#         parse(item, cur_schema)
#
# def parse(json: Union[Dict[str, Any], List[Any]], schema: Dict[str, Any]) -> None:
#     if isinstance(json, list):
#         handle_array(json, schema)
#     elif isinstance(json, dict):
#         handle_object(json, schema)
#     elif isinstance(json, str):
#         schema['type'] = 'string'
#         schema['description'] = json
#     else:
#         schema['type'] = get_type(json)
#
#
# def ejs(data: Dict[str, Any]) -> Dict[str, Any]:
#     json_schema = {}
#     parse(data, json_schema)
#     return json_schema

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


import unittest


class TestJSON(unittest.TestCase):
    def test_json1(self):
        test1 = {
            "id": 'string',
            "name": {
                'type': 'string',
                'enum': ['tom', 'jay'],
                'minLength': 1,
                'maxLength': 10
            },
            "images": [{
                "id": 'the id',
                'names': {
                    'type': 'array',
                    'title': 'Images Collections.',
                    'items': {
                        "id": 'string',
                        "name": 'string'
                    }
                }
            }],
            'abc': {
                'a': {
                    'x': 'string',
                    'y': {
                        'type': 'number',
                        'minimum': 400000,
                        'maximum': 900000
                    }
                }
            }
        }

        result1 = {
            "type": "object",
            "required": [
                "id",
                "name",
                "images",
                "abc"
            ],
            "properties": {
                "id": {
                    "type": "string",
                    "description": "string"
                },
                "name": {
                    "type": "string",
                    "enum": [
                        "tom",
                        "jay"
                    ],
                    "minLength": 1,
                    "maxLength": 10
                },
                "images": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "required": [
                            "id",
                            "names"
                        ],
                        "properties": {
                            "id": {
                                "type": "string",
                                "description": "the id"
                            },
                            "names": {
                                "type": "array",
                                "title": "Images Collections.",
                                "items": {
                                    "type": "object",
                                    "required": [
                                        "id",
                                        "name"
                                    ],
                                    "properties": {
                                        "id": {
                                            "type": "string",
                                            "description": "string",
                                        },
                                        "name": {
                                            "type": "string",
                                            "description": "string",
                                        }
                                    }
                                }
                            }
                        }
                    }
                },
                "abc": {
                    "type": "object",
                    "required": ["a"],
                    "properties": {
                        "a": {
                            "type": "object",
                            "required": ["x", "y"],
                            "properties": {
                                "x": {
                                    "type": "string",
                                    "description": "string",
                                },
                                "y": {
                                    "type": "number",
                                    "minimum": 400000,
                                    "maximum": 900000
                                }
                            }
                        }
                    }
                }
            }
        }

        self.assertEqual(expand_simplified_json_schema(test1), result1)

    def test_2(self):
        test2 = {
            "id": "the id",
            "role": {
                "type": "string",
                "enum": ["owner", "dev", "guest"]
            },
            "member_uids": {
                "type": "array",
                "items": "the uids",
                "minItems": 1
            }
        }
        result2 = {
            "type": "object",
            "required": [
                "id",
                "role",
                "member_uids"
            ],
            "properties": {
                "id": {
                    "type": "string",
                    "description": "the id",
                },
                "role": {
                    "type": "string",
                    "enum": [
                        "owner",
                        "dev",
                        "guest"
                    ]
                },
                "member_uids": {
                    "type": "array",
                    "minItems": 1,
                    "items": {
                        "type": "string",
                        "description": "the uids"
                    }
                }
            }
        }
        self.assertEqual(expand_simplified_json_schema(test2), result2)

    def test_3(self):
        test3 = {
            "id": 1,
            "member": True,
            "member_values": {
                "type": "array",
                "items": 2.5
            }
        }
        result3 = {
            "type": "object",
            "required": [
                "id",
                "member",
                "member_values"
            ],
            "properties": {
                "id": {
                    "type": "integer",
                    "example": 1
                },
                "member": {
                    "type": "boolean",
                    "example": True

                },
                "member_values": {
                    "type": "array",
                    "items": {
                        "type": "number",
                        "example": 2.5
                    }
                }
            }
        }
        self.assertEqual(expand_simplified_json_schema(test3), result3)
