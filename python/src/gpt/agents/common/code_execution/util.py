import ast

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


