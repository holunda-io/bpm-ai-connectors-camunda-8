import inspect
import os
from jinja2 import Template


def read_relative_file(filename):
    # Get the frame of the caller of the function that called this function
    caller_frame = inspect.stack()[2]
    caller_filename = caller_frame.filename

    # Get the directory of the caller's file
    current_dir = os.path.dirname(os.path.abspath(caller_filename))

    file_path = os.path.join(current_dir, filename)
    with open(file_path, 'r') as f:
        return f.read()


def format_prompt(path: str, **kwargs):
    raw_template = read_relative_file(f"{path}.prompt")
    template = Template(raw_template)
    formatted_prompt = template.render(**kwargs)
    return formatted_prompt
