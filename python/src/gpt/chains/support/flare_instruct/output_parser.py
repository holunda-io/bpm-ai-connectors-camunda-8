"""FLARE output parsers."""

from typing import Any

from langchain.schema import BaseOutputParser

from gpt.chains.support.flare_instruct.schema import QueryTask


def default_parse_is_done_fn(response: str) -> bool:
    """Default parse is done function."""
    return "done" in response.lower()


def default_format_done_answer(response: str) -> str:
    """Default format done answer."""
    return response.replace("done", "").strip()


class IsDoneOutputParser(BaseOutputParser):
    """Is done output parser."""

    def parse(self, output: str) -> Any:
        """Parse output."""
        is_done = default_parse_is_done_fn(output)
        if is_done:
            return True, default_format_done_answer(output)
        else:
            return False, output

    def format(self, output: str) -> str:
        """Format a query with structured output formatting instructions."""
        raise NotImplementedError


class QueryTaskOutputParser(BaseOutputParser):
    """QueryTask output parser.

    By default, parses output that contains "[Search(query)]" tags.

    """

    def parse(self, output: str) -> Any:
        """Parse output."""
        query_tasks = []
        for idx, char in enumerate(output):
            if char == "[":
                start_idx = idx
            elif char == "]":
                end_idx = idx
                raw_query_str = output[start_idx + 1 : end_idx]
                query_str = raw_query_str.split("(")[1].split(")")[0]
                query_tasks.append(QueryTask(query_str, start_idx, end_idx))
        return query_tasks

    def format(self, output: str) -> str:
        """Format a query with structured output formatting instructions."""
        raise NotImplementedError
