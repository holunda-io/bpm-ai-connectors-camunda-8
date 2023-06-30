"""Answer inserter."""

from abc import ABC, abstractmethod
from typing import List, Optional, Any

from langchain import LLMChain
from langchain.base_language import BaseLanguageModel
from langchain.load.serializable import Serializable
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, SystemMessagePromptTemplate

from gpt.chains.retrieval_chain.flare_instruct.answer_inserter.prompt import DEFAULT_ANSWER_INSERT_PROMPT, HUMAN_MESSAGE_TEMPLATE
from gpt.chains.retrieval_chain.flare_instruct.schema import QueryTask


class BaseLookaheadAnswerInserter(ABC):
    """Lookahead answer inserter.

    These are responsible for insert answers into a lookahead answer template.

    E.g.
    lookahead answer: Red is for [Search(What is the meaning of Ghana's
        flag being red?)], green for forests, and gold for mineral wealth.
    query: What is the meaning of Ghana's flag being red?
    query answer: "the blood of those who died in the country's struggle
        for independence"
    final answer: Red is for the blood of those who died in the country's
        struggle for independence, green for forests, and gold for mineral wealth.

    """

    @abstractmethod
    def insert(
        self,
        response: str,
        query_tasks: List[QueryTask],
        answers: List[str],
        prev_response: Optional[str] = None,
    ) -> str:
        """Insert answers into response."""


class LLMLookaheadAnswerInserter(BaseLookaheadAnswerInserter, Serializable):
    """LLM Lookahead answer inserter.

    Takes in a lookahead response and a list of query tasks, and the
        lookahead answers, and inserts the answers into the lookahead response.
    """

    llm: BaseLanguageModel
    insert_chain: LLMChain

    @classmethod
    def from_llm(
        cls,
        llm: BaseLanguageModel,
        **kwargs: Any,
    ) -> "LLMLookaheadAnswerInserter":
        """Initialize from LLM."""
        prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(
                DEFAULT_ANSWER_INSERT_PROMPT
            ),
            HumanMessagePromptTemplate.from_template(
                HUMAN_MESSAGE_TEMPLATE
            )
        ])
        insert_chain = LLMChain(
            llm=llm,
            prompt=prompt
        )
        return cls(
            llm=llm,
            insert_chain=insert_chain,
            **kwargs
        )

    def insert(
        self,
        response: str,
        query_tasks: List[QueryTask],
        answers: List[str],
        prev_response: Optional[str] = None,
    ) -> str:
        """Insert answers into response."""
        prev_response = prev_response or ""

        query_answer_pairs = ""
        for query_task, answer in zip(query_tasks, answers):
            query_answer_pairs += f"Query: {query_task.query_str}\nAnswer: {answer}\n"

        response = self.insert_chain.run(
            lookahead_response=response,
            query_answer_pairs=query_answer_pairs,
            prev_response=prev_response,
        )
        return response


class DirectLookaheadAnswerInserter(BaseLookaheadAnswerInserter):
    """Direct lookahead answer inserter.

    Simple inserter module that directly inserts answers into
        the [Search(query)] tags in the lookahead response.

    Args:
        service_context (ServiceContext): Service context.

    """

    def insert(
        self,
        response: str,
        query_tasks: List[QueryTask],
        answers: List[str],
        prev_response: Optional[str] = None,
    ) -> str:
        """Insert answers into response."""
        for query_task, answer in zip(query_tasks, answers):
            response = (
                response[: query_task.start_idx]
                + answer
                + response[query_task.end_idx + 1 :]
            )
        return response
