import re
from typing import List, Callable, Union, Dict, Tuple, Any

import requests
from langchain.agents.agent_toolkits.openapi.spec import dereference_refs
from langchain.base_language import BaseLanguageModel
from langchain.chains.openai_functions.openapi import openapi_spec_to_openai_fn
from langchain.utilities.openapi import OpenAPISpec

from gpt.agents.common.agent.code_execution.util import camel_to_snake
from gpt.agents.openapi_agent.code_execution.util import dereference_all_refs, json_schema_to_typed_dicts, param_to_python_arg, \
    find_response_schema, type_mapping


def get_api_functions(spec_url: str) -> tuple[str, list[Any], dict[str, Any]]:
    """
    Generate a dictionary of Python functions for each operation in an OpenAPI spec.
    """

    spec_dict = requests.get(spec_url).json()
    spec_dict = dereference_all_refs(spec_dict)

    spec = OpenAPISpec.from_spec_dict(spec_dict)

    # Convert the OpenAPI spec to a set of functions and a default API calling function
    openai_fns, call_api_fn = openapi_spec_to_openai_fn(spec)

    # Generate a dictionary mapping operation names to functions
    api_functions = locals()

    typed_dicts = {}
    fun_names = []

    exec("from typing import TypedDict, Optional, List, cast", api_functions)

    for fn in openai_fns:
        all_args = []
        params = []
        path_params = []
        json_body_fields = []

        for arg_type, args in fn['parameters']['properties'].items():
            property_items = args['properties'].items()

            for param, param_def in property_items:

                param_typed_dict = None
                # create typed dicts for object parameters
                if param_def['type'] == 'object':
                    dict_name = param_def['example'].split('/')[-1]  # HACK dereference_all_refs stores the original ref in `example` after de-referencing
                    new_typed_dicts = json_schema_to_typed_dicts(dict_name, param_def)
                    param_typed_dict = dict_name
                    typed_dicts.update(new_typed_dicts)

                param_snake = camel_to_snake(param)

                # add parameter with type hint to function arguments
                arg = param_to_python_arg(param_snake, param_typed_dict or param_def)
                if arg not in all_args:  # avoid duplicate arguments (e.g. if id is both in path param and body)
                    all_args.append(arg)
                # remember the different types of parameters

                if arg_type == 'params':
                    params.append((param, param_snake))
                elif arg_type == 'path_params':
                    path_params.append((param, param_snake))
                elif arg_type == 'json':
                    json_body_fields.append((param, param_snake))

        all_args_str = ", ".join(all_args)

        def get_dict_str(call_arg_name, call_arg_fields):
            fields_dict_str = ", ".join([f"'{p}': {ps}" for p, ps in call_arg_fields])
            return f"'{call_arg_name}': {{ {fields_dict_str} }}"

        params_str = get_dict_str('params', params) if params else None
        path_params_str = get_dict_str('path_params', path_params) if path_params else None
        json_str = get_dict_str('json', json_body_fields) if json_body_fields else None

        call_args = [params_str, path_params_str, json_str]
        call_args = [x for x in call_args if x]

        call_args_str = f'{{{", ".join(call_args)}}}' if call_args else ''

        operation_id = fn['name']

        response_schema = find_response_schema(spec_dict, operation_id)
        if response_schema:
            if response_schema['type'] in 'object':
                name = response_schema['example'].split('/')[-1]
                typed_dicts.update(json_schema_to_typed_dicts(name, response_schema))
                name = f'Optional[{name}]'
            elif response_schema['type'] == 'array':
                response_schema = response_schema['items']
                name = response_schema['example'].split('/')[-1]
                typed_dicts.update(json_schema_to_typed_dicts(name, response_schema))
                name = f'List[{name}]'
            else:
                name = type_mapping[response_schema['type']]
                name = f'Optional[{name}]'

        fun_name = camel_to_snake(fn['name'])

        # Construct a string representing the function definition
        func_def = f"""
def {fun_name}({all_args_str}){f' -> {name}' if response_schema else ''}:
    \"\"\"{fn['description']}\"\"\"
    res = call_api_fn('{operation_id}'{", " if call_args else ""}{call_args_str})
    return res.json() if res else None
"""
        print(func_def)

        exec("\n\n".join(typed_dicts.values()), api_functions)

        # Use exec to create the function and add it to the dictionary
        exec(func_def, api_functions)

        fun_names.append(fun_name)

    typed_dicts_str = "from typing import TypedDict, Optional, List\n\n" + "\n\n".join(typed_dicts.values())
    print(typed_dicts_str)

    return typed_dicts_str, fun_names, api_functions

#
# typed_dicts, api_functions = get_api_functions('http://localhost:3333/v3/api-docs')
#
# exec("print(count_customers_by_last_name(''))", api_functions)
