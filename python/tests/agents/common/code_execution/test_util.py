from gpt.agents.common.code_execution.util import extract_function_calls, extract_functions, extract_imports, is_simple_call

TEST_SOURCE_CODE = """
import os

from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple, Union

def add_numbers(a, b):
    return a + b

add_numbers(1, 2)

def hello_world():
    print("Hello, world!")

some_function()

x = 5
y = 7
"""


def test_extract_function_defs():
    functions = extract_functions(TEST_SOURCE_CODE)

    assert functions[0].startswith('def add_numbers(a, b):')
    assert functions[1].startswith('def hello_world():')


def test_extract_function_calls():
    function_calls = extract_function_calls(TEST_SOURCE_CODE)

    assert function_calls[0] == 'add_numbers(1, 2)'
    assert function_calls[1] == 'some_function()'


def test_extract_imports():
    imports = extract_imports(TEST_SOURCE_CODE)

    assert imports[0] == 'import os'
    assert imports[1] == 'from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple, Union'


def test_simple_call():
    function_str = """
def get_balance(account_id: int):

    return get_user_balance(account_id)
    """

    function_names = ["get_account_balance", "get_user_balance"]

    assert is_simple_call(function_str, function_names) == True
