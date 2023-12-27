from bpm_ai_core.util.json import expand_simplified_json_schema


def test_json_schema_1():
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

    expected_schema = {
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
                }},

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

    assert expand_simplified_json_schema(test1) == expected_schema


def test_json_schema_2():
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

    expected_schema = {
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
    assert expand_simplified_json_schema(test2) == expected_schema


def test_json_schema_3():
    test3 = {
        "id": 1,
        "member": True,
        "member_values": {
            "type": "array",
            "items": 2.5
        }
    }

    expected_schema = {
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
    assert expand_simplified_json_schema(test3) == expected_schema
