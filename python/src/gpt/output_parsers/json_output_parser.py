import json
from typing import List, Any
import re

from langchain.schema import OutputParserException, BaseOutputParser


class JsonOutputParser(BaseOutputParser):
    """Class to parse the output of an LLM call to a json."""

    @property
    def _type(self) -> str:
        return "json"

    def parse(self, text: str) -> Any:
        try:
            # Greedy search for 1st json candidate.
            match = re.search(r"\{.*\}", text.strip(), re.MULTILINE | re.IGNORECASE | re.DOTALL)
            json_str = ""
            if match:
                json_str = match.group()
            json_dict = json.loads(json_str, strict=False)
            return json_dict

        except json.JSONDecodeError as e:

            msg = f"Invalid JSON\n {text}\nGot: {e}"
            raise OutputParserException(msg)

    def get_format_instructions(self) -> str:
        """Instructions on how the LLM output should be formatted."""
        return "Return result as a valid JSON"
