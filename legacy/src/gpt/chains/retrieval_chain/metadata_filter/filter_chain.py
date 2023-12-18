"""Retriever that generates and executes structured queries over its own data source."""
import json
from typing import Any, Dict, List, Optional, Type, cast

from langchain import LLMChain
from langchain.callbacks.manager import CallbackManagerForRetrieverRun
from langchain.chains.query_constructor.base import load_query_constructor_chain
from langchain.chains.query_constructor.ir import StructuredQuery, Visitor
from langchain.chains.query_constructor.schema import AttributeInfo
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.pydantic_v1 import BaseModel, Field, root_validator
from langchain.retrievers.self_query.base import _get_builtin_translator
from langchain.schema import BaseRetriever, Document, StrOutputParser
from langchain.schema.language_model import BaseLanguageModel
from langchain.vectorstores import (
    VectorStore,
)

class QueryContext(BaseModel):
    original_query: Optional[str] = None
    modified_query: Optional[str] = None

    def get_query(self):
        return self.modified_query or self.original_query


class MetadataFilterRetriever(BaseRetriever, BaseModel):
    """Retriever that uses a vector store and an LLM to generate
    the vector store queries."""

    vectorstore: VectorStore
    """The underlying vector store from which documents will be retrieved."""
    llm_chain: LLMChain
    """The LLMChain for generating the vector store queries."""
    search_type: str = "similarity"
    """The search type to perform on the vector store."""
    search_kwargs: dict = Field(default_factory=dict)
    """Keyword arguments to pass in to the vector store search."""
    structured_query_translator: Visitor
    """Translator for turning internal query language into vectorstore search params."""
    verbose: bool = False
    """Use original query instead of the revised new query from LLM"""
    use_original_query: bool = False

    query_context: Optional[QueryContext] = None

    k = 4

    class Config:
        """Configuration for this pydantic object."""

        arbitrary_types_allowed = True

    @root_validator(pre=True)
    def validate_translator(cls, values: Dict) -> Dict:
        """Validate translator."""
        if "structured_query_translator" not in values:
            values["structured_query_translator"] = _get_builtin_translator(
                values["vectorstore"]
            )
        return values

    def _get_relevant_documents(
        self, query: str, *, run_manager: CallbackManagerForRetrieverRun
    ) -> List[Document]:
        """Get documents relevant for a query.

        Args:
            query: string to find relevant documents for

        Returns:
            List of relevant documents
        """
        inputs = self.llm_chain.prep_inputs({"query": query})
        structured_query = cast(
            StructuredQuery,
            self.llm_chain.predict(
                callbacks=run_manager.get_child(), **inputs
            ),
        )

        if self.verbose:
            print(structured_query)
        new_query, new_kwargs = self.structured_query_translator.visit_structured_query(
            structured_query
        )
        if structured_query.limit is not None:
            new_kwargs["k"] = structured_query.limit
        else:
            new_kwargs["k"] = self.k

        query_chain = (
            ChatPromptTemplate.from_template("""\
Rewrite the query to remove any information already present in the given filter.

Query: {query}   
Filter: {filter}  

New query without information already present in filter:""")
            | self.llm_chain.llm
            | StrOutputParser()
        )

        if structured_query.filter:
            if "filter" in new_kwargs:
                filter = new_kwargs["filter"]
            elif "filters" in new_kwargs:
                filter = new_kwargs["filters"]
            elif "where_filter" in new_kwargs:
                filter = new_kwargs["where_filter"]
            else:
                filter = {}

            if isinstance(filter, dict):
                filter = json.dumps(filter)

            new_query = query_chain.invoke({"query": query, "filter": filter})
            if self.verbose:
                print(f"Modified query: {new_query}")

        #if self.use_original_query:
        #    new_query = query

        if self.query_context:
            self.query_context.original_query = query
            self.query_context.modified_query = new_query

        search_kwargs = {**self.search_kwargs, **new_kwargs}
        docs = self.vectorstore.search(new_query, self.search_type, **search_kwargs)
        return docs

    @classmethod
    def from_llm(
        cls,
        llm: BaseLanguageModel,
        vectorstore: VectorStore,
        document_contents: str,
        metadata_field_info: List[AttributeInfo],
        structured_query_translator: Optional[Visitor] = None,
        chain_kwargs: Optional[Dict] = None,
        enable_limit: bool = False,
        use_original_query: bool = False,
        query_context: Optional[QueryContext] = None,
        **kwargs: Any,
    ) -> "MetadataFilterRetriever":
        if structured_query_translator is None:
            structured_query_translator = _get_builtin_translator(vectorstore)
        chain_kwargs = chain_kwargs or {}

        if "allowed_comparators" not in chain_kwargs:
            chain_kwargs[
                "allowed_comparators"
            ] = structured_query_translator.allowed_comparators
        if "allowed_operators" not in chain_kwargs:
            chain_kwargs[
                "allowed_operators"
            ] = structured_query_translator.allowed_operators
        llm_chain = load_query_constructor_chain(
            llm,
            document_contents,
            metadata_field_info,
            enable_limit=enable_limit,
            **chain_kwargs,
        )
        llm_chain.output_parser = llm_chain.prompt.output_parser
        return cls(
            llm_chain=llm_chain,
            vectorstore=vectorstore,
            use_original_query=use_original_query,
            structured_query_translator=structured_query_translator,
            query_context=query_context,
            **kwargs,
        )
