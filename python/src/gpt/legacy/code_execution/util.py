import ast
from inspect import signature
from typing import Sequence, Callable

import astunparse


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


def is_simple_call(function_def_str, function_names):
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

