from gpt.agents.common.code_execution.util import extract_function_calls, extract_functions

TEST_SOURCE_CODE = """
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
