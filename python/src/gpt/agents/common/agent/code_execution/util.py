import ast
import re
from contextlib import redirect_stdout
from inspect import signature
from io import StringIO
from typing import Sequence, Callable, List, Any, Optional, Dict

import astunparse
from langchain.tools.python.tool import sanitize_input


def get_function_name(function_string):
    ast_tree = ast.parse(function_string)
    # The first node in the body of the module should be a FunctionDef node
    function_node = ast_tree.body[0]
    # Check if the node is a function definition
    if isinstance(function_node, ast.FunctionDef):
        return function_node.name
    else:
        raise TypeError('The provided string does not define a function.')


def extract_ast_nodes(source_code, condition_func):
    # Parse the source code to get an Abstract Syntax Tree (AST)
    ast_tree = ast.parse(source_code)

    # A list to store the source code for each node that satisfies the condition
    nodes = []

    # Iterate over each top level node in the AST
    for node in ast_tree.body:
        # If the node satisfies the condition, unparse it to get the source code
        if condition_func(node):
            node_code = astunparse.unparse(node)
            nodes.append(node_code.strip())

    # Return the list of node source codes
    return nodes


def extract_functions(source_code):
    return extract_ast_nodes(
        source_code,
        lambda node: isinstance(node, ast.FunctionDef)
    )


def extract_function_calls(source_code):
    return extract_ast_nodes(
        source_code,
        lambda node: isinstance(node, ast.Expr) and isinstance(node.value, ast.Call)
    )


def extract_imports(source_code):
    return extract_ast_nodes(
        source_code,
        lambda node: isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom)
    )


def is_simple_call(function_def_str: str, function_names: List[str]) -> bool:
    functions = extract_functions(function_def_str)
    if len(functions) != 1:
        return False
    function_def_str = functions[0]

    # Parse the function definition to get an Abstract Syntax Tree (AST)
    function_ast = ast.parse(function_def_str)

    # Ensure that the parsed AST has a function definition at its root
    if not isinstance(function_ast, ast.Module) or \
        not len(function_ast.body) == 1 or \
        not isinstance(function_ast.body[0], ast.FunctionDef):
        raise ValueError("Input string does not define a single function")

    # Get the body of the function
    function_body = function_ast.body[0].body

    # Check if the body is a single return statement containing a function call
    if len(function_body) == 1 and \
        isinstance(function_body[0], ast.Return) and \
        isinstance(function_body[0].value, ast.Call) and \
        isinstance(function_body[0].value.func, ast.Name):

        # If the function being called is in the list of function names, return True
        if function_body[0].value.func.id in function_names:
            return True

    # If the body does not match the above criteria, return False
    return False


def create_func_obj(func_code: str, doc_str: str = ""):
    _globals = dict()
    _locals = dict()
    exec(func_code, _globals, _locals)
    if _locals:
        f = list(_locals.values())[0]
        f.__doc__ = doc_str.replace('"""', '').strip()
        return f


def get_python_functions_descriptions(functions: Sequence[Callable]) -> str:
    return "\n".join(
        [f"- {f.__name__}{signature(f)}:\n{f.__doc__}" for f in functions]
    )


def truncate_to_n_chars(obj: Any, n: int):
    """Truncates a string/list/dict/tuple so that its string representation does not exceed n chars."""
    if isinstance(obj, str):
        return obj[:n - 3] + '...' if len(obj) > n else obj

    elif isinstance(obj, (list, tuple)):
        truncated = type(obj)()  # Create an empty list or tuple of the same type
        for item in obj:
            item_str = str(truncate_to_n_chars(item, n))
            if len(str(truncated) + item_str) < n:
                truncated += type(obj)((item,))
            else:
                break
        return truncated

    elif isinstance(obj, dict):
        truncated = dict()
        for key, value in obj.items():
            key_str = str(truncate_to_n_chars(key, n))
            value_str = str(truncate_to_n_chars(value, n))
            if len(str(truncated) + key_str + value_str) < n:
                truncated[key] = value
            else:
                break
        return truncated

    else:
        return obj


def globals_from_function_defs(
    functions: Optional[Sequence[Callable]] = None,
    function_strs: Optional[Sequence[str]] = None
) -> dict:
    functions = functions or []
    function_strs = function_strs or []
    _globals = globals()
    _globals.update({f.__name__: f for f in functions})
    for f in function_strs:
        exec(f, _globals)
    return _globals


def generate_function_stub(inputs: Dict[str, Any], output_schema: Optional[Dict[str, Any]] = None) -> str:
    # Function header with parameter type hints
    parameter_type_hints = ', '.join([f'{camel_to_snake(key)}: {type(value).__name__}' for key, value in inputs.items()])
    function_stub = f"def rename_me({parameter_type_hints})"

    # Determine the function's return type
    if output_schema is None:
        function_stub += ":\n"
    elif len(output_schema) > 1:
        function_stub += " -> dict:\n"
    else:
        key, value = list(output_schema.items())[0]
        if isinstance(value, dict):
            return_type = value.get('type', 'str')
        else:
            return_type = 'str'
        function_stub += f" -> {return_type}:\n"

    # Function body
    function_stub += "    # TODO: implement\n"
    if output_schema is not None:
        if len(output_schema) > 1 or isinstance(list(output_schema.values())[0], dict):
            function_stub += "    return {\n"
            for key, value in output_schema.items():
                function_stub += f'        "{key}":  # TODO: {key}\n'
            function_stub += "    }\n"
        else:
            key = list(output_schema.keys())[0]
            function_stub += f"    return # TODO: {key}\n"
    else:
        function_stub += "    return # TODO\n"

    return function_stub


def camel_to_snake(camel_str):
    segments = camel_str.split("_")
    snake_case_segments = []
    for segment in segments:
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', segment)
        snake_case_segments.append(re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower())
    return "_".join(snake_case_segments)


def named_parameters_snake_case(input_dict):
    return ", ".join(f"{camel_to_snake(k)}={repr(v)}" for k, v in input_dict.items())


def python_exec(code: str, _globals: Optional[dict] = None, sanitize: bool = True, truncate: bool = False) -> Any:
    _globals = _globals or {}
    try:
        if sanitize:
            code = sanitize_input(code)
        tree = ast.parse(code)
        module = ast.Module(tree.body[:-1], type_ignores=[])
        exec(ast.unparse(module), _globals)  # type: ignore
        module_end = ast.Module(tree.body[-1:], type_ignores=[])
        module_end_str = ast.unparse(module_end)  # type: ignore
        io_buffer = StringIO()
        try:
            with redirect_stdout(io_buffer):
                ret = eval(module_end_str, _globals)
                if ret is None:
                    return io_buffer.getvalue()
                else:
                    if truncate:
                        return truncate_to_n_chars(ret, 2000)
                    else:
                        return ret
        except Exception:
            with redirect_stdout(io_buffer):
                exec(module_end_str, _globals)
            return io_buffer.getvalue()
    except Exception as e:
        return "<python_error> {}: {}".format(type(e).__name__, str(e))
