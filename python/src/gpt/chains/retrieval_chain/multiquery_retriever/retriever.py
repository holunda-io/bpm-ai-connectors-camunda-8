from typing import List

from langchain import LLMChain
from langchain.callbacks.manager import CallbackManagerForRetrieverRun
from langchain.llms import BaseLLM
from langchain.output_parsers import PydanticOutputParser
from langchain.retrievers import MultiQueryRetriever
from langchain.retrievers.multi_query import LineList
from langchain.schema import Document, BaseRetriever

from gpt.chains.retrieval_chain.multiquery_retriever.prompt import MULTI_QUERY_PROMPT


class LineListOutputParser(PydanticOutputParser):
    """Output parser for a list of lines."""

    def __init__(self) -> None:
        super().__init__(pydantic_object=LineList)

    def parse(self, text: str) -> LineList:
        lines = text.strip().split("\n")
        lines = [l for l in lines if len(l.strip()) > 1]
        return LineList(lines=lines)


def create_multi_query_retriever(
        retriever: BaseRetriever,
        llm: BaseLLM,
) -> "MultiQueryRetriever":
    output_parser = LineListOutputParser()
    llm_chain = LLMChain(llm=llm, prompt=MULTI_QUERY_PROMPT, output_parser=output_parser)
    return MultiQueryRetriever(
        retriever=retriever,
        llm_chain=llm_chain
    )
