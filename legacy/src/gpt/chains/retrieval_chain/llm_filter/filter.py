"""Filter that uses an LLM to drop documents that aren't relevant to the query."""
from typing import Any, Callable, Dict, Optional, Sequence

from langchain import LLMChain, PromptTemplate
from langchain.callbacks.manager import Callbacks
from langchain.chains.openai_functions import create_openai_fn_chain
from langchain.output_parsers.boolean import BooleanOutputParser
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.retrievers.document_compressors.base import BaseDocumentCompressor
from langchain.schema import BasePromptTemplate, Document
from langchain.schema.language_model import BaseLanguageModel
from pydantic import BaseModel, Field

SYSTEM_MESSAGE = """\
You are a genius context filtering AI that carefully filters context irrelevant to a given query for an LLM-based retrieval system.
Decide if the given context contains any information relevant to the query. The context does not need to contain the full answer to the query, but it should help answer it."""

HUMAN_MESSAGE = """\
QUERY:
"{question}"

CONTEXT:
\"\"\"
{context}
\"\"\""""


class RecordDecision(BaseModel):
    """Record whether the context is relevant"""
    context_is_relevant: bool = Field(..., description="whether the context contains any information relevant to the query")


class LLMDocumentFilter(BaseDocumentCompressor):
    """Filter that drops documents that aren't relevant to the query."""

    llm_chain: LLMChain

    skip_first: bool = True

    def compress_documents(
        self,
        documents: Sequence[Document],
        query: str,
        callbacks: Optional[Callbacks] = None,
    ) -> Sequence[Document]:
        """Filter down documents based on their relevance to the query."""
        if len(documents) == 0:
            return []
        if self.skip_first:
            print(f"Skipping first document '{documents[0].page_content[:24]}'")
            filtered_docs = [documents[0]]
            docs = documents[1:]
        else:
            filtered_docs = []
            docs = documents
        for doc in docs:
            _input = {"question": query, "context": doc.page_content}
            decision = self.llm_chain.run(
                **_input, callbacks=callbacks
            )
            if decision.context_is_relevant:
                filtered_docs.append(doc)
        return filtered_docs

    async def acompress_documents(
        self,
        documents: Sequence[Document],
        query: str,
        callbacks: Optional[Callbacks] = None,
    ) -> Sequence[Document]:
        """Filter down documents."""
        raise NotImplementedError()

    @classmethod
    def from_llm(
        cls,
        llm: BaseLanguageModel,
        **kwargs: Any
    ) -> "LLMDocumentFilter":
        """Create a LLMChainFilter from a language model.

        Args:
            llm: The language model to use for filtering.
            **kwargs: Additional arguments to pass to the constructor.

        Returns:
            A LLMChainFilter that uses the given language model.
        """
        prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(
                SYSTEM_MESSAGE
            ),
            HumanMessagePromptTemplate.from_template(
                HUMAN_MESSAGE
            )
        ])
        llm_chain = create_openai_fn_chain(
            [RecordDecision],
            llm=llm,
            prompt=prompt
        )
        return cls(llm_chain=llm_chain, **kwargs)
