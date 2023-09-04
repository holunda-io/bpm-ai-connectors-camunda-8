from langchain.chains import RetrievalQA
from langchain.chat_models.base import BaseChatModel
from langchain.prompts import SystemMessagePromptTemplate
from langchain.retrievers import SelfQueryRetriever, MultiVectorRetriever
from langchain.tools import Tool, StructuredTool
from langchain.vectorstores import AzureSearch
from pydantic.fields import FieldInfo

from gpt.agents.common.agent.base import Agent
from gpt.agents.common.agent.openai_functions.openai_functions_agent import OpenAIFunctionsAgent

from langchain.pydantic_v1 import create_model
from typing import Dict, Any, Optional, Union, List

from gpt.chains.retrieval_chain.config import get_embeddings, get_vector_store, get_document_store
from gpt.chains.retrieval_chain.metadata_filter.filter_chain import MetadataFilterRetriever
from gpt.chains.retrieval_chain.multiquery_retriever.retriever import create_multi_query_retriever
from gpt.chains.retrieval_chain.parent_document_retriever.retriever import ParentDocumentRetriever
from gpt.util.functions import json_schema_from_shorthand
from gpt.util.query_constructor.azure_search_translator import AzureCognitiveSearchTranslator


def json_schema_to_pydantic_model(name: str, schema: Dict[str, Any]) -> Any:
    type_mapping = {
        'string': str,
        'integer': int,
        'number': float,
        'boolean': bool,
        'array': list
    }

    fields = {}
    for field_name, field_info in schema.items():
        field_type_str = field_info.get('type')
        field_type = type_mapping.get(field_type_str)
        if field_type is None:
            raise ValueError(f"Unsupported field type: {field_type_str}")

        field_description = field_info.get('description', '')
        # In Pydantic, the field definition is a tuple (type, default value).
        # Since the JSON schema doesn't specify a default value, we'll just use None.
        fields[field_name] = (field_type, FieldInfo(..., description=field_description))

    return create_model(name, **fields)

SYSTEM_MESSAGE = """\
Assistant is a helpful assistant that answers user questions and queries by calling functions to retrieve information from a document Q&A system.
The document Q&A system will answer given questions using available documents. 

Split up questions into multiple function calls where appropriate and combine the results.

If you can't find enough information to compile a meaningful and helpful answer for the user, don't say that the document or text does not provide enough information but just set the fields in store_final_result to null."""


def create_retrieval_agent(
    llm: BaseChatModel,
    database: str,
    database_url: str,
    embedding_provider: str,
    embedding_model: str,
    database_password: Optional[str] = None,
    output_schema: Optional[Dict[str, Union[str, dict]]] = None,
    multi_query_expansion: bool = False,
    metadata_field_info: Optional[List[dict]] = None,
    document_content_description: Optional[str] = None,
    parent_document_store: Optional[str] = None,
    parent_document_store_url: Optional[str] = None,
    parent_document_store_password: Optional[str] = None,
    parent_document_store_namespace: Optional[str] = None,
    parent_document_id_key: str = "parent_id",
) -> Agent:
    agent = OpenAIFunctionsAgent.create(
        system_prompt_template=SystemMessagePromptTemplate.from_template(SYSTEM_MESSAGE),
        llm=llm,
    )

    embeddings = get_embeddings(embedding_provider, embedding_model)
    vector_store = get_vector_store(database, database_url, embeddings, password=database_password)

    # self-query on given metadata fields
    if metadata_field_info:
        # others are built-in
        query_translator = AzureCognitiveSearchTranslator() if isinstance(vector_store, AzureSearch) else None
        retriever = MetadataFilterRetriever.from_llm(
            llm,
            vector_store,
            document_content_description or "document",
            metadata_field_info,
            k=15,
            structured_query_translator=query_translator,
            use_original_query=False,
            verbose=True
        )
    else:
        retriever = vector_store.as_retriever()

    # rephrase query multiple times and get union of docs
    if multi_query_expansion:
        retriever = create_multi_query_retriever(retriever=retriever, llm=llm)

    # resolve parent documents/larger chunks from embedded chunks
    if parent_document_store_url:
        store = get_document_store(
            parent_document_store,
            parent_document_store_url,
            parent_document_store_namespace,
            password=parent_document_store_password
        )
        retriever = ParentDocumentRetriever(
            child_retriever=retriever,
            docstore=store,
            id_key=parent_document_id_key,
        )

    # answer synthesizer
    retrieval_qa = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever
    )

    def query_docs(question: str) -> str:
        """Useful for when you need to answer questions about the content of documents. Input should be a fully formed question."""
        return retrieval_qa.run(question)

    agent.add_tools([
        StructuredTool.from_function(
            name="document_qa_system",
            func=query_docs,
            infer_schema=True
        ),
        StructuredTool.from_function(
            name="store_final_result",
            func=lambda x: x,
            description="Stores the final answer to the query.",
            return_direct=True,
            args_schema=json_schema_to_pydantic_model("final_result", json_schema_from_shorthand(output_schema) if output_schema else {"answer": {
                "description": "the answer text",
                "type": "string"
            }})
        )
    ])
    return agent
