import inspect
import os
import re
from typing import List, Dict, Any

from jinja2 import Template

from bpm_ai_core.llm.common.message import ChatMessage, FunctionCallMessage, FunctionResultMessage


class Prompt:
    path: str
    template_vars: Dict[str, Any]

    def __init__(self, path: str, kwargs: Dict[str, Any]):
        self.path = path
        self.template_vars = kwargs

    @classmethod
    def from_file(cls, path: str, **kwargs):
        # Get the frame of the caller of the function that called this function
        caller_frame = inspect.stack()[1]
        caller_filename = caller_frame.filename

        # Get the directory of the caller's file
        current_dir = os.path.dirname(os.path.abspath(caller_filename))
        file_path = os.path.join(current_dir, path)

        return cls(file_path, kwargs)

    def format(self, llm_name: str = "") -> List[ChatMessage]:
        template = self.load_template(self.path, llm_name)
        full_prompt = template.render(self.template_vars)

        regex = r'\[#\s*(user|assistant|system|function_result:.*|function_call:.*)\s*#\]'

        # Check if the raw template contains message prompt sections
        if re.search(regex, full_prompt):
            sections = re.split(regex, full_prompt)[1:]
            # Create a list of messages from the sections
            messages = [
                self.section_to_message(sections, i)
                for i in range(0, len(sections) - 1, 2)
            ]
        else:
            # If the raw template doesn't contain any sections, treat whole file as 'user' message
            messages = [{'user': full_prompt}]

        return [m for m in messages if m]

    @staticmethod
    def section_to_message(sections, i) -> ChatMessage:
        role = sections[i].strip()
        next_role = sections[i+2].strip() if len(sections) > (i+2) else None
        content = sections[i+1].strip()
        next_content = sections[i+3].strip() if len(sections) > (i+3) else None
        if role == "assistant" and next_role and next_role.startswith("function_call"):
            return FunctionCallMessage(
                name=next_role.split(":")[-1].strip(),
                content=content,
                payload=next_content
            )
        elif role.startswith("function_result"):
            return FunctionResultMessage(name=role.split(":")[-1].strip(), content=content)
        elif role.startswith("function_call"):
            prev_role = sections[i-2].strip() if i > 1 else None
            if prev_role and prev_role == "assistant":
                return None
            else:
                return FunctionCallMessage(
                    name=next_role.split(":")[-1].strip(),
                    content=None,
                    payload=content
                )
        else:
            return ChatMessage(role=role, content=content)


    @staticmethod
    def load_template(path: str, llm_name: str) -> Template:
        default_path = f"{path}.prompt"
        llm_specific_path = f"{path}.{llm_name}.prompt"
        filename = llm_specific_path if os.path.exists(llm_specific_path) else default_path
        if not os.path.exists(filename):
            raise FileNotFoundError(f"No prompt file found at {filename}")
        with open(filename, 'r') as f:
            return Template(f.read())
