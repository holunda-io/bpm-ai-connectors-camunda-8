from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
from langchain.chat_models.base import BaseChatModel
from langchain.embeddings.base import Embeddings
from langchain.prompts import SystemMessagePromptTemplate
from langchain.retrievers import SelfQueryRetriever, MultiVectorRetriever, ContextualCompressionRetriever
from langchain.retrievers.document_compressors import DocumentCompressorPipeline
from langchain.schema import BaseStore
from langchain.tools import Tool, StructuredTool
from langchain.vectorstores import AzureSearch, VectorStore
from pydantic.fields import FieldInfo

from gpt.agents.common.agent.base import Agent
from gpt.agents.common.agent.openai_functions.openai_functions_agent import OpenAIFunctionsAgent

from langchain.pydantic_v1 import create_model
from typing import Dict, Any, Optional, Union, List

from gpt.agents.retrieval_agent.prompt import SYSTEM_MESSAGE
from gpt.config import get_document_store, get_embeddings, get_vector_store
from gpt.chains.retrieval_chain.llm_filter.filter import LLMDocumentFilter
from gpt.chains.retrieval_chain.metadata_filter.filter_chain import MetadataFilterRetriever, QueryContext
from gpt.chains.retrieval_chain.multiquery_retriever.retriever import create_multi_query_retriever
from gpt.chains.retrieval_chain.parent_document_retriever.retriever import ParentDocumentRetriever
from gpt.chains.retrieval_chain.reranker.cohere_reranker import CohereThresholdRerank
from gpt.util.functions import json_schema_from_shorthand
from gpt.util.query_constructor.azure_search_translator import AzureCognitiveSearchTranslator


def json_schema_to_pydantic_model(name: str, schema: Dict[str, Any]) -> Any:
    type_mapping = {
        'string': str,
        'integer': int,
        'number': float,
        'boolean': bool,
        'array': list,
    }

    fields = {}
    for field_name, field_info in schema.items():
        field_type_str = field_info.get('type')
        field_type = type_mapping.get(field_type_str)
        if not field_info.get('required', True):
            field_type = Optional[field_type]
        if field_type is None:
            raise ValueError(f"Unsupported field type: {field_type_str}")

        field_description = field_info.get('description', '')
        # In Pydantic, the field definition is a tuple (type, default value).
        # Since the JSON schema doesn't specify a default value, we'll just use None.
        fields[field_name] = (field_type, FieldInfo(..., description=field_description))

    return create_model(name, **fields)


def create_retrieval_agent(
    llm: BaseChatModel,
    vector_store: VectorStore,
    filter_llm: BaseChatModel = ChatOpenAI(temperature=0),
    summary_store: Optional[VectorStore] = None,
    output_schema: Optional[Dict[str, Union[str, dict]]] = None,
    multi_query_expansion: bool = False,
    reranker: Optional[str] = None,
    filter_metadata_field: Optional[str] = None,
    metadata_field_info: Optional[List[dict]] = None,
    document_content_description: Optional[str] = None,
    parent_document_store: Optional[BaseStore] = None,
    parent_document_id_key: str = "parent_id",
) -> Agent:
    if filter_metadata_field and summary_store:
        system_message = SYSTEM_MESSAGE.format(
            additional_instructions=f"If you can specify {filter_metadata_field} based on the input question, remove any mention of it from the query to document_qa_system.\n"
        )
    else:
        system_message = SYSTEM_MESSAGE.format(additional_instructions="")

    agent = OpenAIFunctionsAgent.create(
        system_prompt_template=SystemMessagePromptTemplate.from_template(system_message),
        llm=llm,
    )

    def query_docs(**query) -> str:
        # select child index to query using a summary index that contains a summary of the content of each child index
        if filter_metadata_field and summary_store and query[filter_metadata_field]:
            if isinstance(summary_store, AzureSearch):
                f = summary_store.hybrid_search
            else:
                f = summary_store.similarity_search

            summary_index_query = query[filter_metadata_field]
            result = f(query=summary_index_query, k=1)[0]

            filter_value = result.metadata[filter_metadata_field]
            filter = {filter_metadata_field: filter_value}
        else:
            filter = None

        retrieval_qa = create_retrieval_qa(
            llm=llm,
            filter_llm=filter_llm,
            vector_store=vector_store,
            filter=filter,
            multi_query_expansion=multi_query_expansion,
            parent_document_id_key=parent_document_id_key,
            parent_document_store=parent_document_store,
            reranker=reranker,
            metadata_field_info=metadata_field_info,
            document_content_description=document_content_description
        )

        return retrieval_qa.run(query["query"])

    if filter_metadata_field and summary_store:
        qa_tool = StructuredTool.from_function(
            name="document_qa_system",
            description=f"Useful when you need to answer questions about the content of documents. Input should be a fully formed question and, if available, the {filter_metadata_field} (in that case don't mention it in the query). If no {filter_metadata_field} is mentioned, set it to null.",
            args_schema=json_schema_to_pydantic_model("document_qa_system",
                                                      {
                                                          "query": {
                                                              "description": f"the query without any mention of {filter_metadata_field}",
                                                              "type": "string"
                                                          },
                                                          filter_metadata_field: {
                                                              "description": f"the {filter_metadata_field} - if mentioned, else null",
                                                              "type": "string",
                                                              "required": False
                                                          }
                                                      }
            ),
            func=query_docs
        )
    else:
        qa_tool = StructuredTool.from_function(
            name="document_qa_system",
            description="Useful when you need to answer questions about the content of documents. Input should be a fully formed question.",
            func=query_docs,
            args_schema=json_schema_to_pydantic_model("document_qa_system",
                                                      {
                                                          "query": {
                                                              "description": f"the query",
                                                              "type": "string"
                                                          }
                                                      }
            ),
        )

    agent.add_tools([
        qa_tool,
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


def create_retrieval_qa(
    llm: BaseChatModel,
    filter_llm: BaseChatModel,
    vector_store: VectorStore,
    filter: Optional[dict] = None,
    multi_query_expansion: bool = False,
    reranker: Optional[str] = None,
    metadata_field_info: Optional[List[dict]] = None,
    document_content_description: Optional[str] = None,
    parent_document_store: Optional[BaseStore] = None,
    parent_document_id_key: str = "parent_id",
):
    init_k = 50
    top_n = 3

    # self-query on given metadata fields
    if metadata_field_info:
        # others are built-in
        query_translator = AzureCognitiveSearchTranslator() if isinstance(vector_store, AzureSearch) else None
        retriever = MetadataFilterRetriever.from_llm(
            llm,
            vector_store,
            document_content_description or "document",
            metadata_field_info,
            k=init_k,
            structured_query_translator=query_translator,
            use_original_query=False,
            verbose=True
        )
    else:
        if isinstance(vector_store, AzureSearch):
            filter_dict = {'filters': f"{list(filter.keys())[0]} eq '{list(filter.values())[0]}'"}
        else:
            filter_dict = {'filter': filter}
        retriever = vector_store.as_retriever(
            search_kwargs={
                'k': init_k,
                **(filter_dict if filter else {})
            }
        )

    # rephrase query multiple times and get union of docs
    if multi_query_expansion:
        retriever = create_multi_query_retriever(retriever=retriever, llm=llm)

    # resolve parent documents/larger chunks from embedded chunks
    if parent_document_store:
        retriever = ParentDocumentRetriever(
            n=init_k,
            child_retriever=retriever,
            docstore=parent_document_store,
            id_key=parent_document_id_key,
        )

    transformers = []
    if reranker == 'cohere':
        cohere_reranker = CohereThresholdRerank(top_n=top_n)
        transformers.append(cohere_reranker)
    transformers.append(LLMDocumentFilter.from_llm(filter_llm))

    pipeline_compressor = DocumentCompressorPipeline(transformers=transformers)
    retriever = ContextualCompressionRetriever(
        base_compressor=pipeline_compressor,
        base_retriever=retriever
    )

    # answer synthesizer
    retrieval_qa = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever
    )
    return retrieval_qa
