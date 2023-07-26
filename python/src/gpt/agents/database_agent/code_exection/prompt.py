from typing import Optional

from langchain.prompts import AIMessagePromptTemplate, HumanMessagePromptTemplate

from gpt.util.prompt import FunctionMessagePromptTemplate


def create_few_shot_messages(tables: str, function_stub: Optional[str] = None, call_direct: bool = False):
    return [
        HumanMessagePromptTemplate.from_template(
            template="""\
# Context:
String: "Hello World"

# User task:
Reverse the name of the first table and prepend it with \"reversed: \""""
            if not function_stub else (
                ("# Context:\nprefix: \"reversed: \"\n\n" if not call_direct else "") +
"""\
# User task:
Reverse the name of the first table and prepend it with the given string.

# Function Stub:
def rename_me(prefix: str):
    # TODO: implement
    return # TODO
""")
        ),
        AIMessagePromptTemplate.from_template(
            template="To reverse a string, we can use a slice:",
            additional_kwargs={"function_call": {"name": "python", "arguments": '{ "code": "\"Hello World\"[::-1]" }'}}
        ),
        FunctionMessagePromptTemplate.from_template(
            name="python",
            template="dlroW olleH",
        ),
        AIMessagePromptTemplate.from_template(
            template='We can get a list of table names using `sql_list_tables()`:',
            additional_kwargs={"function_call": {"name": "python", "arguments": '{ "code": "sql_list_tables()" }'}}
        ),
        FunctionMessagePromptTemplate.from_template(
            name="python",
            template=tables,
        ),
        AIMessagePromptTemplate.from_template(
            template=f"Let's implement {'the function stub as' if function_stub else 'a generic function'} `reverse_first_table_name(prefix: str)` that takes the first table name, reverses it, and prepends the prefix:",
            additional_kwargs={"function_call": {"name": "store_final_result",
                                                 "arguments": '{ '
                                                              '"function_def": "def reverse_first_table_name(prefix: str):\n    first_table_name = sql_list_tables()[0]\n    return prefix + first_table_name[::-1]"'
                                                              + (', "function_call": "reverse_first_table_name(\"reversed: \")" }' if not call_direct else '')
                                                 }
                               }
        ),
        FunctionMessagePromptTemplate.from_template(
            name="store_final_result",
            template="Result stored. Continue with next task.",
        )
    ]


def create_user_prompt_messages(tables: str, call_direct: bool, stub_function: bool):
    return [
        HumanMessagePromptTemplate.from_template(
            template= ("# Context:\n{context}\n\n" if not call_direct else "") + """\
# User task:
{input}""" + ("""

# Function Stub:
{result_function_stub}""" if stub_function else "")
        ),
        AIMessagePromptTemplate.from_template(
            template="Let's first use the `sql_list_tables` function to find the relevant tables for the user task.",
            additional_kwargs={"function_call": {"name": "python", "arguments": '{ "code": "sql_list_tables()" }'}}
        ),
        FunctionMessagePromptTemplate.from_template(
            name="python",
            template=tables,
        ),
    ]
