import json
import re
from typing import Any, Optional

from langchain.schema import OutputParserException, BaseOutputParser


class JsonOutputParser(BaseOutputParser):
    """Class to parse the output of an LLM call to a json."""

    key_name: Optional[str] = None

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
            if self.key_name:
                return json_dict[self.key_name]
            else:
                return json_dict

        except json.JSONDecodeError as e:

            msg = f"Invalid JSON\n {text}\nGot: {e}"
            raise OutputParserException(msg)

    def get_format_instructions(self) -> str:
        """Instructions on how the LLM output should be formatted."""
        return "Return result as a valid JSON"
