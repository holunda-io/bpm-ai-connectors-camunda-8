import logging
from typing import List

from langchain import LLMChain
from langchain.base_language import BaseLanguageModel
from langchain.chains.openai_functions.utils import get_llm_kwargs
from langchain.output_parsers.openai_functions import JsonKeyOutputFunctionsParser
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.retrievers import MultiQueryRetriever
from langchain.schema import BaseRetriever

from gpt.chains.support.sub_query_retriever.prompt import SYSTEM_MESSAGE_TEMPLATE
from gpt.util.functions import get_openai_function

logger = logging.getLogger(__name__)


def create_sub_query_chain(
    llm: BaseLanguageModel,
) -> LLMChain:
    questions_array = "questions"
    function = get_openai_function(
        "store_questions",
        "Stores an array of one or multiple questions.",
        {"q": "a (sub)-question"},
        array_name=questions_array,
        array_description="Array of questions"
    )
    output_parser = JsonKeyOutputFunctionsParser(key_name=questions_array)

    prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(
            SYSTEM_MESSAGE_TEMPLATE
        ),
        HumanMessagePromptTemplate.from_template(
            "{input}"
        )
    ])

    return LLMChain(
        llm=llm,
        prompt=prompt,
        llm_kwargs=get_llm_kwargs(function),
        output_parser=output_parser,
    )


class SubQueryRetriever(MultiQueryRetriever):

    """Given a user query, use an LLM to write a set of queries.
    Retrieve docs for each query. Rake the unique union of all retrieved docs."""

    @classmethod
    def from_llm(
        cls,
        retriever: BaseRetriever,
        llm: BaseLanguageModel,
    ) -> "SubQueryRetriever":
        return cls(
            retriever=retriever,
            llm_chain=create_sub_query_chain(llm),
        )

    def generate_queries(self, question: str) -> List[str]:
        """Generate queries based upon user input.

        Args:
            question: user query

        Returns:
            List of LLM generated queries that are similar to the user input
        """
        res = self.llm_chain(inputs={"input": question})
        questions = [x['q'] for x in res['text']]
        if self.verbose:
            logger.info(f"Generated queries: {questions}")
        return questions

