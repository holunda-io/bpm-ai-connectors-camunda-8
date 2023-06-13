import re
from typing import List

from langchain.output_parsers import ListOutputParser
from langchain.schema import OutputParserException


class ThoughtResultListOutputParser(ListOutputParser):
    """Parse out comma separated lists with preceding thoughts"""

    result_prefix: str = "Result:"

    def parse(self, text: str) -> List[str]:
        regex = (
            r"(.*?)[\s]*" + re.escape(self.result_prefix) + "[\s]*(.*)"
        )
        match = re.search(regex, text, re.DOTALL)
        if not match:
            if not re.search(re.escape(self.result_prefix), text, re.DOTALL):
                raise OutputParserException(f"Could not parse LLM output, no 'Result:': `{text}`")
            else:
                raise OutputParserException(f"Could not parse LLM output: `{text}`")

        thought = match.group(1).strip()
        result = match.group(2)

        return [s.strip() for s in result.strip().split(',')]